"""
Графовые утилиты для ATR Framework

Включает:
- Spectral graph analysis
- Laplacian eigenmodes
- Percolation metrics
- Contact graph operations
"""

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class SpectralProperties:
    """Спектральные свойства графа"""

    eigenvalues: np.ndarray
    eigenvectors: np.ndarray
    algebraic_connectivity: float  # λ₂
    fiedler_vector: np.ndarray  # v₂
    modularity: float
    num_components: int


def compute_laplacian(adjacency: np.ndarray, normalized: bool = False) -> np.ndarray:
    """
    Вычислить Лапласиан графа

    Parameters
    ----------
    adjacency : np.ndarray, shape (N, N)
        Матрица смежности (веса рёбер)
    normalized : bool
        Если True, вычисляет нормализованный Лапласиан

    Returns
    -------
    laplacian : np.ndarray, shape (N, N)
        L = D - A (unnormalized)
        или L = I - D^{-1/2} A D^{-1/2} (normalized)

    Notes
    -----
    [ESTABLISHED] Спектр Лапласиана кодирует:
    - λ₁ = 0 всегда (для связного графа кратность 1)
    - λ₂ = algebraic connectivity (чем больше, тем связнее)
    - Eigenvectors определяют сообщества/домены
    """
    N = adjacency.shape[0]
    degree = np.sum(adjacency, axis=1)
    D = np.diag(degree)

    if normalized:
        # Избежать деления на 0
        D_inv_sqrt = np.diag(1.0 / np.sqrt(degree + 1e-8))
        L = np.eye(N) - D_inv_sqrt @ adjacency @ D_inv_sqrt
    else:
        L = D - adjacency

    return L


def spectral_decomposition(laplacian: np.ndarray, k: int = 10) -> Tuple[np.ndarray, np.ndarray]:
    """
    Вычислить k наименьших собственных значений и векторов

    Parameters
    ----------
    laplacian : np.ndarray
        Матрица Лапласиана
    k : int
        Число собственных пар

    Returns
    -------
    eigenvalues : np.ndarray, shape (k,)
        Собственные значения (sorted)
    eigenvectors : np.ndarray, shape (N, k)
        Собственные векторы

    Notes
    -----
    [VERIFIED-CODE] Используем eigsh для симметричных матриц (быстрее).
    """
    # Для плотных матриц
    if laplacian.shape[0] < 1000:
        eigenvalues, eigenvectors = np.linalg.eigh(laplacian)
        # Сортируем по возрастанию
        idx = np.argsort(eigenvalues)
        eigenvalues = eigenvalues[idx[:k]]
        eigenvectors = eigenvectors[:, idx[:k]]
    else:
        # Для разреженных — используем sparse solver
        L_sparse = sp.csr_matrix(laplacian)
        eigenvalues, eigenvectors = eigsh(L_sparse, k=k, which="SM")

    return eigenvalues, eigenvectors


def algebraic_connectivity(laplacian: np.ndarray) -> float:
    """
    Вычислить algebraic connectivity (λ₂)

    Notes
    -----
    [ESTABLISHED] λ₂ характеризует:
    - Насколько граф "связный"
    - Устойчивость к разделению
    - Скорость диффузии/консенсуса

    λ₂ = 0 → граф не связный
    λ₂ большое → сильно связный граф
    """
    eigenvalues, _ = spectral_decomposition(laplacian, k=3)
    # λ₁ должно быть ≈ 0, λ₂ — второе
    return eigenvalues[1]


def fiedler_vector(laplacian: np.ndarray) -> np.ndarray:
    """
    Вычислить Fiedler vector (v₂)

    Returns
    -------
    v2 : np.ndarray
        Собственный вектор, соответствующий λ₂

    Notes
    -----
    [ESTABLISHED] Fiedler vector разделяет граф на два сообщества:
    - узлы с v₂ > 0 → сообщество 1
    - узлы с v₂ < 0 → сообщество 2

    Используется для spectral clustering.
    """
    _, eigenvectors = spectral_decomposition(laplacian, k=3)
    return eigenvectors[:, 1]


def spectral_perturbation(
    L_original: np.ndarray, L_perturbed: np.ndarray, k: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Вычислить изменение спектра при возмущении графа

    Parameters
    ----------
    L_original : np.ndarray
        Исходный Лапласиан
    L_perturbed : np.ndarray
        Возмущённый Лапласиан (после SNP/mutation)
    k : int
        Число собственных значений для сравнения

    Returns
    -------
    delta_eigenvalues : np.ndarray
        Δλ = λ_perturbed - λ_original
    delta_eigenvectors : np.ndarray
        Изменение собственных векторов (через dot product)

    Notes
    -----
    [HYPOTHESIS-D1] GWAS SNPs действуют через Δλ, особенно Δλ₂.

    [INFERRED] Малое изменение одного ребра может дать большое Δλ₂,
    если ребро находится в "критической" позиции (cut edge).
    """
    eig_orig, vec_orig = spectral_decomposition(L_original, k=k)
    eig_pert, vec_pert = spectral_decomposition(L_perturbed, k=k)

    delta_eigenvalues = eig_pert - eig_orig

    # Для векторов: измеряем изменение через |v_pert^T v_orig|
    # (должен быть близок к 1 если векторы похожи)
    delta_eigenvectors = np.zeros(k)
    for i in range(k):
        overlap = abs(np.dot(vec_orig[:, i], vec_pert[:, i]))
        delta_eigenvectors[i] = 1.0 - overlap  # 0 = no change, 1 = complete change

    return delta_eigenvalues, delta_eigenvectors


def modularity(adjacency: np.ndarray, communities: np.ndarray) -> float:
    """
    Вычислить модульность Q

    Parameters
    ----------
    adjacency : np.ndarray
        Матрица смежности
    communities : np.ndarray
        Метки сообществ для каждого узла

    Returns
    -------
    Q : float
        Модульность (от -1 до 1)
        Q > 0.3 обычно считается сильным разделением

    Notes
    -----
    [ESTABLISHED] Q = (1/2m) Σ[A_ij - k_i k_j / 2m] δ(c_i, c_j)

    где:
    - m = число рёбер
    - k_i = степень узла i
    - δ(c_i, c_j) = 1 если узлы в одном сообществе
    """
    N = adjacency.shape[0]
    m = np.sum(adjacency) / 2  # число рёбер (для неориентированного)

    if m == 0:
        return 0.0

    degree = np.sum(adjacency, axis=1)

    Q = 0.0
    for i in range(N):
        for j in range(N):
            if communities[i] == communities[j]:
                expected = degree[i] * degree[j] / (2 * m)
                Q += adjacency[i, j] - expected

    Q /= 2 * m
    return Q


def percolation_giant_component(adjacency: np.ndarray) -> Tuple[int, float]:
    """
    Найти размер гигантской компоненты (для перколяции)

    Returns
    -------
    size : int
        Размер гигантской компоненты
    fraction : float
        S = size / N (order parameter перколяции)

    Notes
    -----
    [HYPOTHESIS-T3] Катенационная перколяция возникает при p > p_c,
    где S резко растёт.

    [ESTABLISHED] Фазовый переход: S = 0 при p < p_c, S > 0 при p > p_c.
    """
    N = adjacency.shape[0]

    # BFS для поиска компонент связности
    visited = np.zeros(N, dtype=bool)
    component_sizes = []

    for start in range(N):
        if visited[start]:
            continue

        # BFS от узла start
        queue = [start]
        visited[start] = True
        size = 0

        while queue:
            node = queue.pop(0)
            size += 1

            # Соседи
            neighbors = np.where(adjacency[node, :] > 0)[0]
            for neighbor in neighbors:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    queue.append(neighbor)

        component_sizes.append(size)

    if component_sizes:
        giant_size = max(component_sizes)
        fraction = giant_size / N
    else:
        giant_size = 0
        fraction = 0.0

    return giant_size, fraction


def contact_graph_from_hic(
    hic_matrix: np.ndarray, threshold: Optional[float] = None, percentile: float = 90
) -> np.ndarray:
    """
    Преобразовать Hi-C матрицу в контактный граф

    Parameters
    ----------
    hic_matrix : np.ndarray
        Hi-C contact frequency matrix
    threshold : float, optional
        Порог для бинаризации (если None, используется percentile)
    percentile : float
        Процентиль для автоматического порога

    Returns
    -------
    adjacency : np.ndarray
        Бинарная или взвешенная матрица смежности

    Notes
    -----
    [INFERRED] Выбор порога критичен:
    - Слишком низкий → плотный граф, шум
    - Слишком высокий → разреженный граф, потеря сигнала

    [VERIFIED-DOCS] Типичный выбор: 90-95 percentile.
    """
    if threshold is None:
        # Вычислить threshold как percentile
        # Игнорируем диагональ и нули
        mask = ~np.eye(hic_matrix.shape[0], dtype=bool)
        values = hic_matrix[mask]
        values = values[values > 0]
        threshold = np.percentile(values, percentile)

    # Бинаризация
    adjacency = (hic_matrix > threshold).astype(float)

    # Или взвешенная версия
    # adjacency = np.where(hic_matrix > threshold, hic_matrix, 0)

    return adjacency


def tad_boundaries_from_laplacian(laplacian: np.ndarray, num_tads: int = 5) -> np.ndarray:
    """
    Определить границы TAD через spectral clustering

    Parameters
    ----------
    laplacian : np.ndarray
        Лапласиан контактного графа
    num_tads : int
        Ожидаемое число TAD

    Returns
    -------
    labels : np.ndarray
        Метки TAD для каждого bin

    Notes
    -----
    [DERIVED-INFERENCE] TAD = плотно связные подграфы в контактном графе.
    Spectral clustering их хорошо разделяет.
    """
    from sklearn.cluster import KMeans

    # Вычислить k+1 eigenvectors
    k = num_tads
    _, eigenvectors = spectral_decomposition(laplacian, k=k + 1)

    # Пропустить первый (константный)
    features = eigenvectors[:, 1 : k + 1]

    # K-means clustering
    kmeans = KMeans(n_clusters=num_tads, random_state=42)
    labels = kmeans.fit_predict(features)

    return labels


# ============================================================
# Для D1: GWAS SNP perturbation
# ============================================================


def snp_edge_perturbation(
    adjacency: np.ndarray, snp_bin: int, enhancer_bin: int, delta_weight: float = -0.3
) -> np.ndarray:
    """
    Моделировать эффект SNP на контактный граф

    Parameters
    ----------
    adjacency : np.ndarray
        Исходная матрица смежности
    snp_bin : int
        Индекс bin, где находится SNP
    enhancer_bin : int
        Индекс энхансера, на который SNP влияет
    delta_weight : float
        Изменение веса ребра (обычно отрицательное для risk SNP)

    Returns
    -------
    adjacency_perturbed : np.ndarray
        Возмущённая матрица

    Notes
    -----
    [HYPOTHESIS-D1] Risk SNP ослабляет enhancer-promoter contact.

    [INFERRED] Δweight зависит от:
    - Сколько TF motifs disrupted
    - ATAC-seq signal change
    - Cell-type context
    """
    adjacency_pert = adjacency.copy()

    # Симметричное изменение (для неориентированного графа)
    adjacency_pert[snp_bin, enhancer_bin] += delta_weight
    adjacency_pert[enhancer_bin, snp_bin] += delta_weight

    # Clip чтобы остаться в [0, max]
    adjacency_pert = np.clip(adjacency_pert, 0, None)

    return adjacency_pert


if __name__ == "__main__":
    # Smoke test
    print("Graph utils loaded successfully")

    # Test 1: простой граф
    N = 10
    # Ring lattice
    A = np.zeros((N, N))
    for i in range(N):
        A[i, (i + 1) % N] = 1
        A[(i + 1) % N, i] = 1

    L = compute_laplacian(A)
    lambda2 = algebraic_connectivity(L)
    print(f"Ring lattice λ₂ = {lambda2:.3f}")

    # Test 2: spectral decomposition
    eig, vec = spectral_decomposition(L, k=5)
    print(f"First 5 eigenvalues: {eig}")

    # Test 3: perturbation
    A_pert = A.copy()
    A_pert[0, 5] = 1  # добавляем shortcut
    A_pert[5, 0] = 1
    L_pert = compute_laplacian(A_pert)

    delta_eig, delta_vec = spectral_perturbation(L, L_pert, k=5)
    print(f"Δλ from shortcut: {delta_eig}")
    print(f"λ₂ change: {delta_eig[1]:.4f}")
