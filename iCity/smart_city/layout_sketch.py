"""Conversion from simple black road sketches to LayoutGraph.

Blender imports use OpenCV for fast thresholding and skeleton extraction.
Small pure-Python helpers remain available for deterministic unit tests.
"""

from __future__ import annotations

import math

NEIGHBOR_OFFSETS = (
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
)


def rgba_pixels_to_dark_mask(
    width: int,
    height: int,
    pixels,
    *,
    threshold: float = 0.45,
    max_dimension: int = 512,
) -> list[list[bool]]:
    """Convert flat RGBA float pixels into a downsampled dark-pixel mask."""

    width = int(width)
    height = int(height)
    if width <= 0 or height <= 0:
        raise ValueError("Sketch image has invalid dimensions.")
    expected_length = width * height * 4
    if len(pixels) < expected_length:
        raise ValueError("Sketch image pixel buffer is incomplete.")

    max_dimension = max(int(max_dimension), 16)
    scale = min(1.0, max_dimension / max(width, height))
    output_width = max(int(round(width * scale)), 1)
    output_height = max(int(round(height * scale)), 1)
    threshold = min(max(float(threshold), 0.0), 1.0)
    mask = []
    for output_y in range(output_height):
        source_y = min(int(output_y / scale), height - 1) if scale < 1.0 else output_y
        row = []
        for output_x in range(output_width):
            source_x = min(int(output_x / scale), width - 1) if scale < 1.0 else output_x
            offset = (source_y * width + source_x) * 4
            red, green, blue, alpha = pixels[offset : offset + 4]
            luminance = 0.2126 * float(red) + 0.7152 * float(green) + 0.0722 * float(blue)
            row.append(float(alpha) > 0.01 and luminance <= threshold)
        mask.append(row)
    return mask


def _active_neighbors(mask: list[list[bool]], x: int, y: int) -> list[tuple[int, int]]:
    height = len(mask)
    width = len(mask[0]) if height else 0
    return [
        (x + offset_x, y + offset_y)
        for offset_x, offset_y in NEIGHBOR_OFFSETS
        if 0 <= x + offset_x < width
        and 0 <= y + offset_y < height
        and mask[y + offset_y][x + offset_x]
    ]


def _transition_count(neighbor_values: list[bool]) -> int:
    return sum(
        1
        for index, value in enumerate(neighbor_values)
        if not value and neighbor_values[(index + 1) % len(neighbor_values)]
    )


def thin_binary_mask(mask: list[list[bool]], *, max_iterations: int = 256) -> list[list[bool]]:
    """Skeletonize a binary mask with the Zhang-Suen thinning algorithm."""

    result = [list(row) for row in mask]
    height = len(result)
    width = len(result[0]) if height else 0
    if width < 3 or height < 3:
        return result

    changed = True
    iteration = 0
    while changed and iteration < max(int(max_iterations), 1):
        iteration += 1
        changed = False
        for pass_index in (0, 1):
            remove = []
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if not result[y][x]:
                        continue
                    # Clockwise P2..P9 ordering required by Zhang-Suen.
                    p2 = result[y - 1][x]
                    p3 = result[y - 1][x + 1]
                    p4 = result[y][x + 1]
                    p5 = result[y + 1][x + 1]
                    p6 = result[y + 1][x]
                    p7 = result[y + 1][x - 1]
                    p8 = result[y][x - 1]
                    p9 = result[y - 1][x - 1]
                    neighbors = [p2, p3, p4, p5, p6, p7, p8, p9]
                    active_count = sum(neighbors)
                    if not 2 <= active_count <= 6 or _transition_count(neighbors) != 1:
                        continue
                    if pass_index == 0:
                        protected = p2 and p4 and p6 or p4 and p6 and p8
                    else:
                        protected = p2 and p4 and p8 or p2 and p6 and p8
                    if not protected:
                        remove.append((x, y))
            for x, y in remove:
                result[y][x] = False
            changed = changed or bool(remove)
    return result


def _require_opencv():
    """Import OpenCV/NumPy or fail immediately with Blender install guidance."""

    try:
        import cv2
        import numpy
    except ImportError as exc:
        raise RuntimeError(
            "OpenCV is required for sketch import. Install it into Blender's Python "
            "environment with: <Blender Python> -m pip install opencv-python"
        ) from exc
    return cv2, numpy


def _thin_opencv_binary(binary, numpy, *, max_iterations: int = 512):
    """Thin an OpenCV binary image without creating diagonal side branches.

    A morphological skeleton built with a cross-shaped kernel tends to leave
    repeated side branches along thick diagonal strokes. Those branches look
    like junctions to the graph tracer and create many false draft nodes.
    This vectorized Zhang-Suen implementation instead preserves one connected
    centerline while remaining fast enough for Blender-sized sketch images.
    """

    image = (binary > 0).astype(numpy.uint8)
    iterations = 0
    while iterations < max(int(max_iterations), 1):
        iterations += 1
        changed = False
        for pass_index in (0, 1):
            padded = numpy.pad(image, 1, mode="constant")
            p2 = padded[:-2, 1:-1]
            p3 = padded[:-2, 2:]
            p4 = padded[1:-1, 2:]
            p5 = padded[2:, 2:]
            p6 = padded[2:, 1:-1]
            p7 = padded[2:, :-2]
            p8 = padded[1:-1, :-2]
            p9 = padded[:-2, :-2]
            neighbors = (p2, p3, p4, p5, p6, p7, p8, p9)
            active_count = sum(neighbors)
            transitions = sum(
                (neighbors[index] == 0) & (neighbors[(index + 1) % 8] == 1)
                for index in range(8)
            )
            if pass_index == 0:
                protected = (p2 & p4 & p6) | (p4 & p6 & p8)
            else:
                protected = (p2 & p4 & p8) | (p2 & p6 & p8)
            remove = (
                (image == 1)
                & (active_count >= 2)
                & (active_count <= 6)
                & (transitions == 1)
                & (protected == 0)
            )
            if numpy.any(remove):
                image[remove] = 0
                changed = True
        if not changed:
            return image * 255, iterations
    raise RuntimeError("OpenCV sketch thinning exceeded its safety iteration limit.")


def opencv_image_to_skeleton_mask(
    filepath: str,
    *,
    threshold: float = 0.45,
    max_dimension: int = 512,
) -> tuple[list[list[bool]], dict]:
    """Read and skeletonize a sketch with fast OpenCV array operations."""

    cv2, numpy = _require_opencv()
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"OpenCV could not read sketch image: {filepath}")

    input_height, input_width = image.shape[:2]
    max_dimension = max(int(max_dimension), 32)
    scale = min(1.0, max_dimension / max(input_width, input_height))
    if scale < 1.0:
        image = cv2.resize(
            image,
            (max(int(round(input_width * scale)), 1), max(int(round(input_height * scale)), 1)),
            interpolation=cv2.INTER_AREA,
        )

    threshold_value = int(round(min(max(float(threshold), 0.0), 1.0) * 255.0))
    _, binary = cv2.threshold(image, threshold_value, 255, cv2.THRESH_BINARY_INV)
    nonzero = cv2.findNonZero(binary)
    if nonzero is None:
        raise ValueError("No dark road lines were detected in the sketch.")

    # Skeletonize only the active bounding box. This is substantially faster
    # for sparse road sketches with large white margins.
    x, y, width, height = cv2.boundingRect(nonzero)
    padding = 2
    x0 = max(x - padding, 0)
    y0 = max(y - padding, 0)
    x1 = min(x + width + padding, binary.shape[1])
    y1 = min(y + height + padding, binary.shape[0])
    roi = binary[y0:y1, x0:x1].copy()

    skeleton, iterations = _thin_opencv_binary(
        roi,
        numpy,
        max_iterations=max(roi.shape) * 2,
    )

    full_skeleton = numpy.zeros_like(binary)
    full_skeleton[y0:y1, x0:x1] = skeleton
    mask = (full_skeleton > 0).tolist()
    return mask, {
        "input_width": int(input_width),
        "input_height": int(input_height),
        "width": int(binary.shape[1]),
        "height": int(binary.shape[0]),
        "skeleton_iterations": iterations,
    }


def _connected_components(points: set[tuple[int, int]]) -> list[set[tuple[int, int]]]:
    components = []
    remaining = set(points)
    while remaining:
        start = remaining.pop()
        component = {start}
        stack = [start]
        while stack:
            x, y = stack.pop()
            for offset_x, offset_y in NEIGHBOR_OFFSETS:
                neighbor = (x + offset_x, y + offset_y)
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components


def _is_turn_pixel(mask: list[list[bool]], point: tuple[int, int]) -> bool:
    """Return whether a degree-two skeleton pixel changes direction."""

    x, y = point
    neighbors = _active_neighbors(mask, x, y)
    if len(neighbors) != 2:
        return False
    first_offset = (neighbors[0][0] - x, neighbors[0][1] - y)
    second_offset = (neighbors[1][0] - x, neighbors[1][1] - y)
    return first_offset != (-second_offset[0], -second_offset[1])


def _point_line_distance(
    point: tuple[int, int],
    start: tuple[int, int],
    end: tuple[int, int],
) -> float:
    """Return pixel distance from a point to an infinite line segment."""

    delta_x = end[0] - start[0]
    delta_y = end[1] - start[1]
    if delta_x == 0 and delta_y == 0:
        return ((point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2) ** 0.5
    parameter = (
        (point[0] - start[0]) * delta_x + (point[1] - start[1]) * delta_y
    ) / (delta_x * delta_x + delta_y * delta_y)
    parameter = min(max(parameter, 0.0), 1.0)
    nearest_x = start[0] + parameter * delta_x
    nearest_y = start[1] + parameter * delta_y
    return ((point[0] - nearest_x) ** 2 + (point[1] - nearest_y) ** 2) ** 0.5


def simplify_pixel_path(
    points: list[tuple[int, int]],
    *,
    tolerance: float = 1.5,
) -> list[tuple[int, int]]:
    """Simplify a traced skeleton path with Ramer-Douglas-Peucker."""

    if len(points) <= 2:
        return list(points)
    maximum_distance = 0.0
    split_index = 0
    for index, point in enumerate(points[1:-1], start=1):
        distance = _point_line_distance(point, points[0], points[-1])
        if distance > maximum_distance:
            maximum_distance = distance
            split_index = index
    if maximum_distance <= max(float(tolerance), 0.0):
        return [points[0], points[-1]]
    first = simplify_pixel_path(points[: split_index + 1], tolerance=tolerance)
    second = simplify_pixel_path(points[split_index:], tolerance=tolerance)
    return first[:-1] + second


def _pixel_path_length(points: list[tuple[int, int]]) -> float:
    return sum(
        ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** 0.5
        for start, end in zip(points, points[1:])
    )


def simplify_collinear_graph(
    graph: dict,
    *,
    maximum_turn_degrees: float = 20.0,
) -> tuple[dict, int]:
    """Remove degree-two nodes that only subdivide an almost-straight road.

    Skeleton extraction can leave small direction changes or former branch
    roots along an otherwise straight stroke. They are useful while tracing
    pixels, but they should not become editable layout nodes. Endpoints,
    junctions, and visible corners are preserved by the degree and angle
    checks.
    """

    nodes = {str(node["id"]): dict(node) for node in graph.get("nodes", [])}
    edges = [dict(edge) for edge in graph.get("edges", [])]
    maximum_turn_radians = math.radians(max(float(maximum_turn_degrees), 0.0))
    straight_dot_limit = -math.cos(maximum_turn_radians)
    removed_nodes = 0

    while True:
        adjacency = {node_id: [] for node_id in nodes}
        for edge_index, edge in enumerate(edges):
            start = str(edge.get("start", ""))
            end = str(edge.get("end", ""))
            if start in adjacency and end in adjacency and start != end:
                adjacency[start].append((edge_index, end))
                adjacency[end].append((edge_index, start))

        candidate = None
        for node_id, connections in adjacency.items():
            if len(connections) != 2:
                continue
            first_edge_index, first_neighbor_id = connections[0]
            second_edge_index, second_neighbor_id = connections[1]
            if first_neighbor_id == second_neighbor_id:
                continue
            node = nodes[node_id]
            first_neighbor = nodes[first_neighbor_id]
            second_neighbor = nodes[second_neighbor_id]
            first_vector = (
                float(first_neighbor.get("x", 0.0)) - float(node.get("x", 0.0)),
                float(first_neighbor.get("y", 0.0)) - float(node.get("y", 0.0)),
            )
            second_vector = (
                float(second_neighbor.get("x", 0.0)) - float(node.get("x", 0.0)),
                float(second_neighbor.get("y", 0.0)) - float(node.get("y", 0.0)),
            )
            first_length = (first_vector[0] ** 2 + first_vector[1] ** 2) ** 0.5
            second_length = (second_vector[0] ** 2 + second_vector[1] ** 2) ** 0.5
            if first_length <= 1e-9 or second_length <= 1e-9:
                continue
            normalized_dot = (
                first_vector[0] * second_vector[0] + first_vector[1] * second_vector[1]
            ) / (first_length * second_length)
            if normalized_dot <= straight_dot_limit:
                candidate = (
                    node_id,
                    first_edge_index,
                    second_edge_index,
                    first_neighbor_id,
                    second_neighbor_id,
                )
                break

        if candidate is None:
            break
        node_id, first_edge_index, second_edge_index, first_neighbor_id, second_neighbor_id = candidate
        source_edge = edges[min(first_edge_index, second_edge_index)]
        edges = [
            edge
            for edge_index, edge in enumerate(edges)
            if edge_index not in {first_edge_index, second_edge_index}
        ]
        if not any(
            {str(edge.get("start", "")), str(edge.get("end", ""))}
            == {first_neighbor_id, second_neighbor_id}
            for edge in edges
        ):
            replacement = dict(source_edge)
            replacement["start"] = first_neighbor_id
            replacement["end"] = second_neighbor_id
            replacement["source_index"] = -1
            edges.append(replacement)
        del nodes[node_id]
        removed_nodes += 1

    surviving_nodes = list(nodes.values())
    for index, edge in enumerate(edges):
        edge["id"] = f"e{index}"
    simplified = {
        "version": int(graph.get("version", 1)),
        "source": str(graph.get("source", "Sketch Image")),
        "nodes": surviving_nodes,
        "edges": edges,
        "faces": [],
    }
    return simplified, removed_nodes


def snap_nearby_endpoints(
    graph: dict,
    *,
    snap_distance: float = 0.0,
) -> tuple[dict, int]:
    """Merge nearby degree-one sketch endpoints without touching other nodes.

    Computer drawing tools and skeletonization may produce two endpoints a few
    pixels apart where strokes visually meet. Restricting this operation to
    degree-one nodes avoids the broad behavior of the general Draft merge
    distance and preserves existing corners and junctions.
    """

    snap_distance = max(float(snap_distance), 0.0)
    nodes = {str(node["id"]): dict(node) for node in graph.get("nodes", [])}
    edges = [dict(edge) for edge in graph.get("edges", [])]
    merged_endpoints = 0

    while snap_distance > 0.0:
        adjacency = {node_id: [] for node_id in nodes}
        for edge_index, edge in enumerate(edges):
            start = str(edge.get("start", ""))
            end = str(edge.get("end", ""))
            if start in adjacency and end in adjacency and start != end:
                adjacency[start].append((edge_index, end))
                adjacency[end].append((edge_index, start))
        endpoint_ids = [node_id for node_id, connections in adjacency.items() if len(connections) == 1]

        pair = None
        for first_index, first_id in enumerate(endpoint_ids):
            first = nodes[first_id]
            for second_id in endpoint_ids[first_index + 1 :]:
                # The two ends of one short road are not duplicate endpoints.
                if adjacency[first_id][0][1] == second_id:
                    continue
                second = nodes[second_id]
                distance = (
                    (float(first.get("x", 0.0)) - float(second.get("x", 0.0))) ** 2
                    + (float(first.get("y", 0.0)) - float(second.get("y", 0.0))) ** 2
                    + (float(first.get("z", 0.0)) - float(second.get("z", 0.0))) ** 2
                ) ** 0.5
                if distance <= snap_distance:
                    pair = first_id, second_id
                    break
            if pair is not None:
                break
        if pair is None:
            break

        target_id, removed_id = pair
        target = nodes[target_id]
        removed = nodes[removed_id]
        target["x"] = (float(target.get("x", 0.0)) + float(removed.get("x", 0.0))) / 2.0
        target["y"] = (float(target.get("y", 0.0)) + float(removed.get("y", 0.0))) / 2.0
        target["z"] = (float(target.get("z", 0.0)) + float(removed.get("z", 0.0))) / 2.0
        for edge in edges:
            if str(edge.get("start", "")) == removed_id:
                edge["start"] = target_id
            if str(edge.get("end", "")) == removed_id:
                edge["end"] = target_id
        del nodes[removed_id]
        merged_endpoints += 1

    clean_edges = []
    seen_pairs = set()
    for edge in edges:
        start = str(edge.get("start", ""))
        end = str(edge.get("end", ""))
        pair = tuple(sorted((start, end)))
        if start not in nodes or end not in nodes or start == end or pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        edge["id"] = f"e{len(clean_edges)}"
        clean_edges.append(edge)
    snapped = {
        "version": int(graph.get("version", 1)),
        "source": str(graph.get("source", "Sketch Image")),
        "nodes": list(nodes.values()),
        "edges": clean_edges,
        "faces": [],
    }
    return snapped, merged_endpoints


def _pixel_to_layout(
    x: float,
    y: float,
    width: int,
    height: int,
    world_width: float,
) -> tuple[float, float]:
    world_width = max(float(world_width), 0.01)
    world_height = world_width * height / max(width, 1)
    layout_x = ((x / max(width - 1, 1)) - 0.5) * world_width
    layout_y = (0.5 - (y / max(height - 1, 1))) * world_height
    return layout_x, layout_y


def skeleton_to_layout_graph(
    mask: list[list[bool]],
    *,
    world_width: float = 120.0,
    simplify_tolerance: float = 1.5,
    minimum_segment_pixels: float = 2.0,
    endpoint_snap_distance: float = 0.0,
    maximum_turn_degrees: float = 20.0,
) -> tuple[dict, dict]:
    """Trace a one-pixel road skeleton into nodes and undirected edges."""

    height = len(mask)
    width = len(mask[0]) if height else 0
    active_pixels = {
        (x, y)
        for y, row in enumerate(mask)
        for x, active in enumerate(row)
        if active
    }
    if not active_pixels:
        raise ValueError("No dark road lines were detected in the sketch.")

    # Endpoints and junction clusters are structural nodes. Ordinary degree-two
    # pixels, including diagonal staircase pixels, are traced as paths instead
    # of becoming hundreds of false road nodes.
    node_pixels = {
        point
        for point in active_pixels
        if len(_active_neighbors(mask, point[0], point[1])) != 2
    }
    # A completely closed component has no endpoint or junction. In that case,
    # use visible direction changes as nodes so rectangles and polygons remain
    # representable.
    for component in _connected_components(active_pixels):
        if component.isdisjoint(node_pixels):
            node_pixels.update(point for point in component if _is_turn_pixel(mask, point))
    if not node_pixels:
        raise ValueError("No endpoints, junctions, or visible road corners were detected.")

    node_components = _connected_components(node_pixels)
    pixel_to_node = {}
    nodes = []
    for index, component in enumerate(node_components):
        center_x = sum(point[0] for point in component) / len(component)
        center_y = sum(point[1] for point in component) / len(component)
        layout_x, layout_y = _pixel_to_layout(center_x, center_y, width, height, world_width)
        node_id = f"n{index}"
        nodes.append(
            {
                "id": node_id,
                "source_index": -1,
                "x": layout_x,
                "y": layout_y,
                "z": 0.0,
            }
        )
        for point in component:
            pixel_to_node[point] = node_id

    visited_steps = set()
    edge_pairs = set()
    edges = []
    for component in node_components:
        start_node_id = pixel_to_node[next(iter(component))]
        for start_pixel in component:
            for next_pixel in _active_neighbors(mask, start_pixel[0], start_pixel[1]):
                if next_pixel in component:
                    continue
                first_step = frozenset((start_pixel, next_pixel))
                if first_step in visited_steps:
                    continue
                visited_steps.add(first_step)
                previous = start_pixel
                current = next_pixel
                path = [start_pixel, next_pixel]
                while current not in pixel_to_node:
                    options = [
                        point
                        for point in _active_neighbors(mask, current[0], current[1])
                        if point != previous
                    ]
                    if not options:
                        break
                    following = options[0]
                    visited_steps.add(frozenset((current, following)))
                    previous, current = current, following
                    path.append(current)
                end_node_id = pixel_to_node.get(current)
                if end_node_id is None or end_node_id == start_node_id:
                    continue
                if _pixel_path_length(path) < max(float(minimum_segment_pixels), 0.0):
                    continue
                simplified_path = simplify_pixel_path(path, tolerance=simplify_tolerance)
                chain_node_ids = [start_node_id]
                for point in simplified_path[1:-1]:
                    layout_x, layout_y = _pixel_to_layout(
                        point[0],
                        point[1],
                        width,
                        height,
                        world_width,
                    )
                    node_id = f"n{len(nodes)}"
                    nodes.append(
                        {
                            "id": node_id,
                            "source_index": -1,
                            "x": layout_x,
                            "y": layout_y,
                            "z": 0.0,
                        }
                    )
                    chain_node_ids.append(node_id)
                chain_node_ids.append(end_node_id)
                for chain_start, chain_end in zip(chain_node_ids, chain_node_ids[1:]):
                    pair = tuple(sorted((chain_start, chain_end)))
                    if chain_start == chain_end or pair in edge_pairs:
                        continue
                    edge_pairs.add(pair)
                    edges.append(
                        {
                            "id": f"e{len(edges)}",
                            "source_index": -1,
                            "start": chain_start,
                            "end": chain_end,
                            "enabled_as_road": True,
                        }
                    )

    if not edges:
        raise ValueError("Road endpoints were detected, but no connected road segments could be traced.")
    used_node_ids = {edge["start"] for edge in edges} | {edge["end"] for edge in edges}
    nodes = [node for node in nodes if node["id"] in used_node_ids]
    graph = {
        "version": 1,
        "source": "Sketch Image",
        "nodes": nodes,
        "edges": edges,
        "faces": [],
    }
    graph, removed_collinear_nodes = simplify_collinear_graph(
        graph,
        maximum_turn_degrees=maximum_turn_degrees,
    )
    graph, snapped_endpoints = snap_nearby_endpoints(
        graph,
        snap_distance=endpoint_snap_distance,
    )
    # Snapping two endpoints can turn their shared node into a degree-two
    # subdivision. Remove it only when the resulting road remains near-straight.
    graph, removed_after_snap = simplify_collinear_graph(
        graph,
        maximum_turn_degrees=maximum_turn_degrees,
    )
    stats = {
        "width": width,
        "height": height,
        "dark_pixels": len(active_pixels),
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "removed_collinear_nodes": removed_collinear_nodes + removed_after_snap,
        "snapped_endpoints": snapped_endpoints,
    }
    return graph, stats


def image_pixels_to_layout_graph(
    width: int,
    height: int,
    pixels,
    *,
    threshold: float = 0.45,
    max_dimension: int = 512,
    world_width: float = 120.0,
    endpoint_snap_distance: float = 0.0,
    maximum_turn_degrees: float = 20.0,
) -> tuple[dict, dict]:
    """Complete first-version sketch recognition pipeline."""

    dark_mask = rgba_pixels_to_dark_mask(
        width,
        height,
        pixels,
        threshold=threshold,
        max_dimension=max_dimension,
    )
    skeleton = thin_binary_mask(dark_mask)
    graph, stats = skeleton_to_layout_graph(
        skeleton,
        world_width=world_width,
        endpoint_snap_distance=endpoint_snap_distance,
        maximum_turn_degrees=maximum_turn_degrees,
    )
    stats["input_width"] = int(width)
    stats["input_height"] = int(height)
    return graph, stats


def image_file_to_layout_graph(
    filepath: str,
    *,
    threshold: float = 0.45,
    max_dimension: int = 512,
    world_width: float = 120.0,
    endpoint_snap_distance: float = 0.0,
    maximum_turn_degrees: float = 20.0,
) -> tuple[dict, dict]:
    """Fast Blender-facing OpenCV pipeline from image file to LayoutGraph."""

    skeleton, image_stats = opencv_image_to_skeleton_mask(
        filepath,
        threshold=threshold,
        max_dimension=max_dimension,
    )
    graph, graph_stats = skeleton_to_layout_graph(
        skeleton,
        world_width=world_width,
        endpoint_snap_distance=endpoint_snap_distance,
        maximum_turn_degrees=maximum_turn_degrees,
    )
    graph_stats.update(image_stats)
    return graph, graph_stats
