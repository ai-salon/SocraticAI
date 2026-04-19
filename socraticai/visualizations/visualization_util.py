import matplotlib.pyplot as plt
import numpy as np


def create_letter_vertices(letter):
    letter = letter.upper()
    letter_definitions = {
        'A': [
            [(-0.5, -1), (0, 1), (0.5, -1)],
            [(-0.3, 0), (0.3, 0)]
        ],
        'B': [
            [(-0.5, -1), (-0.5, 1), (0.3, 1), (0.5, 0.7), (0.3, 0.5), (-0.5, 0.5)],
            [(-0.5, 0.5), (0.3, 0.5), (0.5, 0.3), (0.5, -0.7), (0.3, -1), (-0.5, -1)]
        ],
        'C': [
            [(0.5, 0.7), (0.3, 1), (-0.3, 1), (-0.5, 0.7), (-0.5, -0.7), (-0.3, -1), (0.3, -1), (0.5, -0.7)]
        ],
        'D': [
            [(-0.5, -1), (-0.5, 1), (0.3, 1), (0.5, 0.7), (0.5, -0.7), (0.3, -1), (-0.5, -1)]
        ],
        'E': [
            [(-0.5, -1), (-0.5, 1), (0.5, 1)],
            [(-0.5, 0), (0.3, 0)],
            [(-0.5, -1), (0.5, -1)]
        ],
        'F': [
            [(-0.5, -1), (-0.5, 1), (0.5, 1)],
            [(-0.5, 0), (0.3, 0)]
        ],
        'G': [
            [(0.5, 0.7), (0.3, 1), (-0.3, 1), (-0.5, 0.7), (-0.5, -0.7), (-0.3, -1), (0.3, -1), (0.5, -0.7), (0.5, 0), (0, 0)]
        ],
        'H': [
            [(-0.5, -1), (-0.5, 1)],
            [(0.5, -1), (0.5, 1)],
            [(-0.5, 0), (0.5, 0)]
        ],
        'I': [
            [(0, -1), (0, 1)],
            [(-0.4, 1), (0.4, 1)],
            [(-0.4, -1), (0.4, -1)]
        ],
        'J': [
            [(0.5, 1), (0.5, -0.7), (0.3, -1), (-0.3, -1), (-0.5, -0.7)]
        ],
        'K': [
            [(-0.5, -1), (-0.5, 1)],
            [(-0.5, 0), (0.5, 1)],
            [(-0.5, 0), (0.5, -1)]
        ],
        'L': [
            [(-0.5, 1), (-0.5, -1), (0.5, -1)]
        ],
        'M': [
            [(-0.5, -1), (-0.5, 1), (0, 0), (0.5, 1), (0.5, -1)]
        ],
        'N': [
            [(-0.5, -1), (-0.5, 1), (0.5, -1), (0.5, 1)]
        ],
        'O': [
            [(0, -1), (0.5, -0.7), (0.5, 0.7), (0, 1), (-0.5, 0.7), (-0.5, -0.7), (0, -1)]
        ],
        'P': [
            [(-0.5, -1), (-0.5, 1), (0.3, 1), (0.5, 0.7), (0.5, 0.3), (0.3, 0), (-0.5, 0)]
        ],
        'Q': [
            [(0, -1), (0.5, -0.7), (0.5, 0.7), (0, 1), (-0.5, 0.7), (-0.5, -0.7), (0, -1)],
            [(0.2, -0.7), (0.5, -1)]
        ],
        'R': [
            [(-0.5, -1), (-0.5, 1), (0.3, 1), (0.5, 0.7), (0.5, 0.3), (0.3, 0), (-0.5, 0)],
            [(0.3, 0), (0.5, -1)]
        ],
        'S': [
            [(0.5, 0.7), (0.3, 1), (-0.3, 1), (-0.5, 0.7), (-0.5, 0.3), (0.5, -0.3), (0.5, -0.7), (0.3, -1), (-0.3, -1), (-0.5, -0.7)]
        ],
        'T': [
            [(-0.5, 1), (0.5, 1)],
            [(0, 1), (0, -1)]
        ],
        'U': [
            [(-0.5, 1), (-0.5, -0.7), (-0.3, -1), (0.3, -1), (0.5, -0.7), (0.5, 1)]
        ],
        'V': [
            [(-0.5, 1), (0, -1), (0.5, 1)]
        ],
        'W': [
            [(-0.5, 1), (-0.3, -1), (0, 0), (0.3, -1), (0.5, 1)]
        ],
        'X': [
            [(-0.5, -1), (0.5, 1)],
            [(-0.5, 1), (0.5, -1)]
        ],
        'Y': [
            [(-0.5, 1), (0, 0), (0.5, 1)],
            [(0, 0), (0, -1)]
        ],
        'Z': [
            [(-0.5, 1), (0.5, 1), (-0.5, -1), (0.5, -1)]
        ]
    }
    return letter_definitions.get(letter, [])


def draw_letter_base(letter, ax):
    segments = create_letter_vertices(letter)
    for segment in segments:
        x = [point[0] for point in segment]
        y = [point[1] for point in segment]
        ax.plot(x, y, 'w-', alpha=0.5, linewidth=0.5)


def generate_points_along_segments(segments, num_points, thickness=0.2, rng=None):
    all_points = []
    total_length = 0
    for segment in segments:
        for i in range(len(segment) - 1):
            start, end = segment[i], segment[i + 1]
            total_length += np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)

    for segment in segments:
        for i in range(len(segment) - 1):
            start, end = segment[i], segment[i + 1]
            length = np.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            proportion = length / total_length
            segment_num_points = int(num_points * proportion)
            t = rng.random(segment_num_points // len(segments) // (len(segment) - 1))
            x = start[0] + t * (end[0] - start[0])
            y = start[1] + t * (end[1] - start[1])

            dx, dy = end[0] - start[0], end[1] - start[1]
            length = np.sqrt(dx ** 2 + dy ** 2)
            normal_x, normal_y = -dy / length, dx / length

            offsets = rng.uniform(-thickness / 2, thickness / 2, len(x))
            x += offsets * normal_x
            y += offsets * normal_y

            all_points.extend(zip(x, y))

    return np.array(all_points)


def define_point_connections(points, rng, max_connection_distance=0.2, max_nearby=5, possible_connection_points=None):
    if possible_connection_points is None:
        possible_connection_points = points
    point_connections = []
    for i, (x, y) in enumerate(points):
        distances = np.sqrt(
            (possible_connection_points[:, 0] - x) ** 2 + (possible_connection_points[:, 1] - y) ** 2
        )
        nearby_points = np.where((distances < max_connection_distance) & (distances > 0))[0]
        nearby_points = rng.choice(nearby_points, size=min(max_nearby, len(nearby_points)), replace=False)
        nearby_points = [possible_connection_points[j] for j in nearby_points]
        point_connections.append(((x, y), nearby_points))
    return point_connections


def plot_points(point_connections, ax, points_color=False, point_size=1, point_size_std=0,
                line_color='white', linewidth=0.25, alpha=1):
    for (x, y), connections in point_connections:
        for connection in connections:
            ax.plot([x, connection[0]], [y, connection[1]], c=line_color, alpha=alpha, linewidth=linewidth)
    points = [i[0] for i in point_connections]
    if points_color is not False:
        sizes = point_size
        if point_size_std > 0:
            rng = np.random.default_rng()
            sizes = np.maximum(0.5, rng.normal(point_size, point_size_std, len(points)))
        ax.scatter(*zip(*points), c=points_color, s=sizes)


def create_letter_network(letter, num_points=200, max_connection_distance=0.2, max_nearby=5,
                          thickness=0.2, points_color=False, point_size=1, point_size_std=0,
                          line_color='white', linewidth=0.25, alpha=1, seed=42, ax=None):
    rng = np.random.default_rng(seed)

    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='black')
    ax.set_facecolor('black')

    segments = create_letter_vertices(letter)
    if len(segments) == 0:
        return
    points = generate_points_along_segments(segments, num_points, thickness, rng=rng)
    points = np.array(points) + rng.normal(0, 0.01, (len(points), 2))

    point_connections = define_point_connections(points, rng, max_connection_distance, max_nearby, None)
    plot_points(point_connections, ax, points_color, point_size, point_size_std, line_color, linewidth, alpha)


def generate_circle_data(num_points=1000, circle_radius=0.8, circle_width=0.1, seed=42):
    """Return (main_points, outer_points, inner_points, rng) without plotting.

    Replicates the point-generation logic of create_network_circle so animations
    can access each ring separately.
    """
    rng = np.random.default_rng(seed)

    r = rng.uniform(circle_radius - circle_width / 2, circle_radius + circle_width / 2, num_points)
    theta = rng.uniform(0, 2 * np.pi, num_points)
    main_points = np.column_stack([r * np.cos(theta), r * np.sin(theta)])

    n_edge = num_points // 10

    outer_r = circle_radius + circle_width / 1.6
    outer_w = circle_radius * 0.1
    r = rng.uniform(outer_r - outer_w / 2, outer_r + outer_w / 2, n_edge)
    theta = rng.uniform(0, 2 * np.pi, n_edge)
    outer_points = np.column_stack([r * np.cos(theta), r * np.sin(theta)])

    inner_r = circle_radius - circle_width / 1.7
    inner_w = circle_radius * 0.1
    r = rng.uniform(inner_r - inner_w / 2, inner_r + inner_w / 2, n_edge)
    theta = rng.uniform(0, 2 * np.pi, n_edge)
    inner_points = np.column_stack([r * np.cos(theta), r * np.sin(theta)])

    return main_points, outer_points, inner_points, rng


def create_network_circle(num_points=1000, circle_radius=0.8, circle_width=0.1,
                          max_connection_distance=0.2, max_nearby=5, points_color=None,
                          point_size=1, point_size_std=0, line_color='white', linewidth=0.25,
                          alpha=1, seed=42, ax=None):
    rng = np.random.default_rng(seed)
    if points_color is None:
        points_color = [1, 1, 1]

    r = rng.uniform(circle_radius - circle_width / 2, circle_radius + circle_width / 2, num_points)
    theta = rng.uniform(0, 2 * np.pi, num_points)
    x = r * np.cos(theta)
    y = r * np.sin(theta)

    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='black')
        ax.set_facecolor('black')
    ax.set_aspect('equal')
    ax.axis('off')

    points = np.array(list(zip(x, y)))
    point_connections = list(define_point_connections(points, rng, max_connection_distance, max_nearby, None))

    edge_points = num_points // 10
    outer_circle_radius = circle_radius + circle_width / 1.6
    outer_circle_width = circle_radius * 0.1
    r = rng.uniform(outer_circle_radius - outer_circle_width / 2, outer_circle_radius + outer_circle_width / 2, edge_points)
    theta = rng.uniform(0, 2 * np.pi, edge_points)
    new_points = np.array(list(zip(r * np.cos(theta), r * np.sin(theta))))
    point_connections += list(define_point_connections(new_points, rng, max_connection_distance, 1, points))

    inner_circle_radius = circle_radius - circle_width / 1.7
    inner_circle_width = circle_radius * 0.1
    r = rng.uniform(inner_circle_radius - inner_circle_width / 2, inner_circle_radius + inner_circle_width / 2, edge_points)
    theta = rng.uniform(0, 2 * np.pi, edge_points)
    new_points = np.array(list(zip(r * np.cos(theta), r * np.sin(theta))))
    point_connections += list(define_point_connections(new_points, rng, max_connection_distance, 1, points))

    plot_points(point_connections, ax, points_color, point_size, point_size_std, line_color, linewidth, alpha)
    return point_connections
