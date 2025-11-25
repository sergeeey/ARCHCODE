"""
Export phase diagrams for 3D visualization.

Converts ARCHCODE phase diagram data into structured format
suitable for 3D immersive visualization (Three.js, WebGL).
"""

import numpy as np
from typing import Any


def export_rs09_phase_map(data: dict[str, Any]) -> dict[str, Any]:
    """
    Export RS-09 Processivity Phase Diagram for 3D visualization.

    Args:
        data: Dictionary from run_rs09_summary() with:
            - phase_diagram: {processivity: {phase, stability}}
            - critical_points: {collapse_threshold, stable_threshold}
            - stability_metrics: {mean, std, min, max}

    Returns:
        Dictionary with:
            - nodes: list of 3D points (x=processivity, y=0, z=stability)
            - edges: connections between adjacent points
            - values: phase categories and stability scores
            - mesh: triangulated mesh for surface rendering
            - metadata: {critical_points, phase_regions, ...}
    """
    phase_diagram = data.get("phase_diagram", {})
    critical_points = data.get("critical_points", {})

    # Extract data
    processivity_values = []
    stability_values = []
    phase_labels = []

    for proc_str, phase_data in phase_diagram.items():
        proc = float(proc_str)
        processivity_values.append(proc)
        stability_values.append(phase_data.get("stability", 0.0))
        phase_labels.append(phase_data.get("phase", "unknown"))

    # Create nodes (3D points)
    nodes = []
    for i, (proc, stab) in enumerate(zip(processivity_values, stability_values)):
        nodes.append({
            "id": i,
            "x": float(proc),
            "y": 0.0,  # 2D projection in 3D space
            "z": float(stab),
            "processivity": float(proc),
            "stability": float(stab),
            "phase": phase_labels[i],
        })

    # Create edges (connections between adjacent points)
    edges = []
    for i in range(len(nodes) - 1):
        edges.append({
            "source": i,
            "target": i + 1,
            "weight": 1.0,
        })

    # Create mesh (triangulated surface)
    # Simple 1D curve → 2D surface by adding width
    mesh_vertices = []
    mesh_faces = []
    width = 0.1

    for i, node in enumerate(nodes):
        # Create quad around each point
        x, z = node["x"], node["z"]
        mesh_vertices.extend([
            [x - width, 0.0, z],  # Left
            [x + width, 0.0, z],  # Right
        ])

    # Create faces
    for i in range(len(mesh_vertices) // 2 - 1):
        base = i * 2
        mesh_faces.append([base, base + 1, base + 2])
        mesh_faces.append([base + 1, base + 3, base + 2])

    # Values for coloring
    values = {
        "processivity": processivity_values,
        "stability": stability_values,
        "phase": phase_labels,
        "color_map": {
            "collapse": [1.0, 0.0, 0.0],  # Red
            "transition": [1.0, 1.0, 0.0],  # Yellow
            "stable": [0.0, 1.0, 0.0],  # Green
        },
    }

    # Metadata
    metadata = {
        "critical_points": critical_points,
        "phase_regions": {
            "collapse": [p for p, l in zip(processivity_values, phase_labels) if l == "collapse"],
            "transition": [p for p, l in zip(processivity_values, phase_labels) if l == "transition"],
            "stable": [p for p, l in zip(processivity_values, phase_labels) if l == "stable"],
        },
        "stability_metrics": data.get("stability_metrics", {}),
        "num_points": len(nodes),
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "values": values,
        "mesh": {
            "vertices": mesh_vertices,
            "faces": mesh_faces,
        },
        "metadata": metadata,
    }


def export_rs10_threshold_curve(data: dict[str, Any]) -> dict[str, Any]:
    """
    Export RS-10 Bookmarking Threshold Curve for 3D visualization.

    Args:
        data: Dictionary from run_rs10_summary() with:
            - bookmarking_grid: {fraction: {final_jaccard, mean_drift, entropy}}
            - drift_curves: {fraction: [drift_per_cycle]}
            - estimated_threshold: critical bookmarking fraction

    Returns:
        Dictionary with:
            - nodes: 3D points (x=bookmarking, y=cycle, z=jaccard/drift)
            - edges: connections
            - values: jaccard, drift, entropy
            - mesh: surface mesh
            - metadata: {threshold, phase_regions}
    """
    bookmarking_grid = data.get("bookmarking_grid", {})
    drift_curves = data.get("drift_curves", {})
    estimated_threshold = data.get("estimated_threshold")

    # Extract data
    bookmarking_values = []
    jaccard_values = []
    drift_values = []

    for frac_str, metrics in bookmarking_grid.items():
        frac = float(frac_str)
        bookmarking_values.append(frac)
        jaccard_values.append(metrics.get("final_jaccard", 0.0))
        drift_values.append(metrics.get("mean_drift", 0.0))

    # Create nodes (3D: bookmarking × cycle × jaccard)
    nodes = []
    node_id = 0

    for i, (frac, jaccard) in enumerate(zip(bookmarking_values, jaccard_values)):
        # Add nodes for each cycle if drift_curves available
        if frac_str := str(frac):
            cycle_drifts = drift_curves.get(frac_str, [])
            for cycle, drift in enumerate(cycle_drifts):
                nodes.append({
                    "id": node_id,
                    "x": float(frac),
                    "y": float(cycle),
                    "z": float(jaccard - drift),  # Adjusted jaccard
                    "bookmarking": float(frac),
                    "cycle": cycle,
                    "jaccard": float(jaccard),
                    "drift": float(drift),
                })
                node_id += 1
        else:
            # Fallback: single node per bookmarking value
            nodes.append({
                "id": node_id,
                "x": float(frac),
                "y": 0.0,
                "z": float(jaccard),
                "bookmarking": float(frac),
                "jaccard": float(jaccard),
            })
            node_id += 1

    # Create edges (connect adjacent bookmarking values)
    edges = []
    prev_nodes = {}
    for node in nodes:
        frac = node["bookmarking"]
        cycle = node.get("cycle", 0)

        if frac in prev_nodes and cycle in prev_nodes[frac]:
            edges.append({
                "source": prev_nodes[frac][cycle],
                "target": node["id"],
                "weight": 1.0,
            })

        if frac not in prev_nodes:
            prev_nodes[frac] = {}
        prev_nodes[frac][cycle] = node["id"]

    # Create mesh (2D surface: bookmarking × cycle)
    mesh_vertices = []
    mesh_faces = []

    # Group nodes by bookmarking
    nodes_by_frac = {}
    for node in nodes:
        frac = node["bookmarking"]
        if frac not in nodes_by_frac:
            nodes_by_frac[frac] = []
        nodes_by_frac[frac].append(node)

    # Create surface
    fracs_sorted = sorted(nodes_by_frac.keys())
    for i in range(len(fracs_sorted) - 1):
        frac1_nodes = sorted(nodes_by_frac[fracs_sorted[i]], key=lambda n: n.get("cycle", 0))
        frac2_nodes = sorted(nodes_by_frac[fracs_sorted[i + 1]], key=lambda n: n.get("cycle", 0))

        # Create quads between adjacent bookmarking values
        for j in range(min(len(frac1_nodes), len(frac2_nodes)) - 1):
            v1 = frac1_nodes[j]
            v2 = frac1_nodes[j + 1]
            v3 = frac2_nodes[j]
            v4 = frac2_nodes[j + 1]

            mesh_vertices.extend([
                [v1["x"], v1["y"], v1["z"]],
                [v2["x"], v2["y"], v2["z"]],
                [v3["x"], v3["y"], v3["z"]],
                [v4["x"], v4["y"], v4["z"]],
            ])

            base = len(mesh_vertices) - 4
            mesh_faces.append([base, base + 1, base + 2])
            mesh_faces.append([base + 1, base + 3, base + 2])

    # Values
    values = {
        "bookmarking": bookmarking_values,
        "jaccard": jaccard_values,
        "drift": drift_values,
        "entropy": [bookmarking_grid.get(str(f), {}).get("entropy", 0.0) for f in bookmarking_values],
    }

    # Metadata
    metadata = {
        "estimated_threshold": float(estimated_threshold) if estimated_threshold else None,
        "phase_regions": {
            "memory_loss": [f for f, j in zip(bookmarking_values, jaccard_values) if j < 0.5],
            "memory_retention": [f for f, j in zip(bookmarking_values, jaccard_values) if j >= 0.5],
        },
        "num_cycles": len(drift_curves.get(str(bookmarking_values[0]), [])) if bookmarking_values else 0,
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "values": values,
        "mesh": {
            "vertices": mesh_vertices,
            "faces": mesh_faces,
        },
        "metadata": metadata,
    }


def export_rs11_memory_surface(data: dict[str, Any]) -> dict[str, Any]:
    """
    Export RS-11 Multichannel Memory Surface for 3D visualization.

    Args:
        data: Dictionary from run_rs11_summary() with:
            - memory_matrix: 2D array [epigenetic][bookmarking]
            - bookmarking_values: list of bookmarking fractions
            - epigenetic_values: list of epigenetic strengths
            - critical_surface: points on critical line

    Returns:
        Dictionary with:
            - nodes: 3D points (x=bookmarking, y=epigenetic, z=memory)
            - edges: connections
            - values: memory retention matrix
            - mesh: 3D surface mesh
            - metadata: {critical_line, phase_regimes}
    """
    memory_matrix = np.array(data.get("memory_matrix", []))
    bookmarking_values = data.get("bookmarking_values", [])
    epigenetic_values = data.get("epigenetic_values", [])
    critical_surface = data.get("critical_surface", {})

    if len(memory_matrix) == 0:
        return {
            "nodes": [],
            "edges": [],
            "values": {},
            "mesh": {"vertices": [], "faces": []},
            "metadata": {},
        }

    # Create nodes (3D: bookmarking × epigenetic × memory)
    nodes = []
    node_id = 0

    for i, epi_val in enumerate(epigenetic_values):
        for j, book_val in enumerate(bookmarking_values):
            memory_val = memory_matrix[i, j] if i < len(memory_matrix) and j < len(memory_matrix[i]) else 0.0

            nodes.append({
                "id": node_id,
                "x": float(book_val),
                "y": float(epi_val),
                "z": float(memory_val),
                "bookmarking": float(book_val),
                "epigenetic": float(epi_val),
                "memory": float(memory_val),
            })
            node_id += 1

    # Create edges (connect adjacent points in grid)
    edges = []
    for i in range(len(epigenetic_values)):
        for j in range(len(bookmarking_values)):
            node_idx = i * len(bookmarking_values) + j

            # Connect to right neighbor
            if j < len(bookmarking_values) - 1:
                edges.append({
                    "source": node_idx,
                    "target": node_idx + 1,
                    "weight": 1.0,
                })

            # Connect to bottom neighbor
            if i < len(epigenetic_values) - 1:
                edges.append({
                    "source": node_idx,
                    "target": node_idx + len(bookmarking_values),
                    "weight": 1.0,
                })

    # Create mesh (triangulated surface)
    mesh_vertices = []
    mesh_faces = []

    for i in range(len(epigenetic_values)):
        for j in range(len(bookmarking_values)):
            node = nodes[i * len(bookmarking_values) + j]
            mesh_vertices.append([node["x"], node["y"], node["z"]])

    # Create faces (triangles)
    for i in range(len(epigenetic_values) - 1):
        for j in range(len(bookmarking_values) - 1):
            base = i * len(bookmarking_values) + j

            # Two triangles per quad
            mesh_faces.append([base, base + 1, base + len(bookmarking_values)])
            mesh_faces.append([base + 1, base + len(bookmarking_values) + 1, base + len(bookmarking_values)])

    # Values for coloring
    values = {
        "memory_matrix": [[float(x) for x in row] for row in memory_matrix],
        "bookmarking": bookmarking_values,
        "epigenetic": epigenetic_values,
        "color_map": {
            "drift": [1.0, 0.0, 0.0],  # Red (low memory)
            "partial": [1.0, 1.0, 0.0],  # Yellow (medium memory)
            "stable": [0.0, 1.0, 0.0],  # Green (high memory)
        },
    }

    # Metadata
    phase_regimes = data.get("phase_regimes", {})
    metadata = {
        "critical_surface": critical_surface,
        "critical_line": data.get("critical_line", []),
        "phase_regimes": phase_regimes,
        "processivity": data.get("processivity", 0.9),
        "num_cycles": data.get("num_cycles", 0),
        "grid_size": {
            "bookmarking": len(bookmarking_values),
            "epigenetic": len(epigenetic_values),
        },
    }

    return {
        "nodes": nodes,
        "edges": edges,
        "values": values,
        "mesh": {
            "vertices": mesh_vertices,
            "faces": mesh_faces,
        },
        "metadata": metadata,
    }




