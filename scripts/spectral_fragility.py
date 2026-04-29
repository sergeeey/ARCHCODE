"""
Spectral Fragility Index (SFI) - Graph Laplacian analysis of contact map perturbations
"""

import numpy as np
from scipy.linalg import eigh
from scipy.spatial.distance import cosine


def contact_matrix_to_laplacian(contact_matrix):
    """Convert contact matrix to graph Laplacian"""
    # Normalize and symmetrize
    C = (contact_matrix + contact_matrix.T) / 2
    C = np.maximum(C, 0)  # ensure non-negative

    # Degree matrix
    D = np.diag(C.sum(axis=1))

    # Laplacian L = D - C
    L = D - C

    return L


def compute_spectral_fragility(contact_wt, contact_mut, k=10):
    """
    Compute Spectral Fragility Index between WT and MUT contact maps

    Args:
        contact_wt: WT contact matrix (NxN)
        contact_mut: MUT contact matrix (NxN)
        k: number of eigenmodes to analyze (default 10)

    Returns:
        sfi: Spectral Fragility Index
        components: dict with eigenvalue/eigenvector contributions
    """
    L_wt = contact_matrix_to_laplacian(contact_wt)
    L_mut = contact_matrix_to_laplacian(contact_mut)

    # Compute k smallest eigenvalues/eigenvectors (low-frequency modes)
    eigenvalues_wt, eigenvectors_wt = eigh(L_wt, subset_by_index=[0, k - 1])
    eigenvalues_mut, eigenvectors_mut = eigh(L_mut, subset_by_index=[0, k - 1])

    # Eigenvalue shifts (skip first trivial zero eigenvalue)
    delta_lambda = np.abs(eigenvalues_wt[1:] - eigenvalues_mut[1:])

    # Eigenvector subspace angles (cosine distance)
    theta = np.zeros(k - 1)
    for i in range(1, k):
        theta[i - 1] = cosine(eigenvectors_wt[:, i], eigenvectors_mut[:, i])

    # Weighted combination (emphasize low-frequency modes)
    weights = 1.0 / np.arange(1, k)  # higher weight for lower modes
    weights = weights / weights.sum()

    sfi = np.sum(weights * (delta_lambda + theta))

    components = {
        "eigenvalue_shifts": delta_lambda,
        "eigenvector_angles": theta,
        "weights": weights,
        "eigenvalues_wt": eigenvalues_wt[1:],
        "eigenvalues_mut": eigenvalues_mut[1:],
    }

    return sfi, components


def spectral_gap_disruption(contact_wt, contact_mut):
    """
    Compute disruption to spectral gap (λ2 - λ1)
    Large gap = well-connected structure
    Small gap = fragmented structure
    """
    L_wt = contact_matrix_to_laplacian(contact_wt)
    L_mut = contact_matrix_to_laplacian(contact_mut)

    eig_wt = eigh(L_wt, subset_by_index=[0, 2])[0]
    eig_mut = eigh(L_mut, subset_by_index=[0, 2])[0]

    gap_wt = eig_wt[2] - eig_wt[1]  # λ2 - λ1
    gap_mut = eig_mut[2] - eig_mut[1]

    delta_gap = abs(gap_wt - gap_mut)

    return delta_gap, gap_wt, gap_mut


# Example usage
if __name__ == "__main__":
    # Test on synthetic data
    n = 50

    # Synthetic WT contact matrix (block structure)
    C_wt = np.random.rand(n, n) * 0.1
    C_wt[:25, :25] += 0.5  # enhancer-promoter block
    C_wt = (C_wt + C_wt.T) / 2

    # MUT: perturb enhancer-promoter block
    C_mut = C_wt.copy()
    C_mut[:25, :25] *= 0.7  # 30% reduction

    sfi, components = compute_spectral_fragility(C_wt, C_mut, k=10)

    print(f"Spectral Fragility Index: {sfi:.4f}")
    print(f"Eigenvalue shifts: {components['eigenvalue_shifts'][:5]}")
    print(f"Eigenvector angles: {components['eigenvector_angles'][:5]}")

    delta_gap, gap_wt, gap_mut = spectral_gap_disruption(C_wt, C_mut)
    print(f"\nSpectral gap: WT={gap_wt:.4f}, MUT={gap_mut:.4f}, Δ={delta_gap:.4f}")
