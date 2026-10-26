"""
Newton Fractal Model - Laboratory 2.

Implements Newton's method for finding roots of polynomials in the complex plane.
Each pixel represents a complex number, colored by which root converges and
how many iterations it takes.

The Newton iteration is: z_{n+1} = z_n - f(z_n) / f'(z_n)

For the polynomial f(z) = z^3 - 1:
    f'(z) = 3z^2

The three roots are the cube roots of unity.

References:
    - Newton-Raphson method for complex polynomials
"""

import numpy as np
from typing import Tuple, Optional


class NewtonFractal:
    """
    Newton fractal generator for complex plane.

    Attributes:
        width (int): Image width in pixels
        height (int): Image height in pixels
        max_iterations (int): Maximum iterations per pixel
        tolerance (float): Convergence tolerance
    """

    def __init__(
        self,
        width: int = 800,
        height: int = 600,
        max_iterations: int = 256,
        tolerance: float = 1e-6
    ):
        """
        Initialize Newton fractal generator.

        Args:
            width: Canvas width in pixels
            height: Canvas height in pixels
            max_iterations: Max iterations for convergence
            tolerance: Distance threshold for convergence
        """
        self.width = width
        self.height = height
        self.max_iterations = max_iterations
        self.tolerance = tolerance

        # Real and imaginary limits of the viewing window
        self.x_min, self.x_max = -2.0, 2.0
        self.y_min, self.y_max = -1.5, 1.5

        # Pre-computed roots of z^3 - 1 = 0
        # These are the cube roots of unity
        self.roots = np.array([
            1.0 + 0.0j,  # 1
            -0.5 + 0.866025j,  # exp(2πi/3)
            -0.5 - 0.866025j   # exp(4πi/3)
        ])

        # Pre-compute colors for roots
        self.root_colors = np.array([
            [255, 0, 0],      # Red for root 1
            [0, 255, 0],      # Green for root 2
            [0, 0, 255]       # Blue for root 3
        ])

        self.fractal_data = None

    def _polynomial(self, z: np.ndarray) -> np.ndarray:
        """
        Evaluate f(z) = z^3 - 1.

        Args:
            z: Complex number(s)

        Returns:
            f(z) value(s)
        """
        return z**3 - 1.0

    def _derivative(self, z: np.ndarray) -> np.ndarray:
        """
        Evaluate f'(z) = 3z^2.

        Args:
            z: Complex number(s)

        Returns:
            f'(z) value(s)
        """
        return 3.0 * z**2

    def _find_root_index(self, z: np.ndarray) -> int:
        """
        Determine which root the value is closest to.

        Args:
            z: Converged complex number

        Returns:
            Index of closest root (0, 1, or 2)
        """
        distances = np.abs(z - self.roots)
        return np.argmin(distances)

    def compute(self) -> np.ndarray:
        """
        Compute Newton fractal.

        Returns:
            Array of shape (height, width, 3) with RGB colors
        """
        # Create coordinate grids
        x_coords = np.linspace(
            self.x_min, self.x_max, self.width, dtype=np.float64
        )
        y_coords = np.linspace(
            self.y_min, self.y_max, self.height, dtype=np.float64
        )

        # Initialize output
        fractal = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Process each pixel
        for iy, y in enumerate(y_coords):
            for ix, x in enumerate(x_coords):
                z = complex(x, y)

                # Newton iteration
                for iteration in range(self.max_iterations):
                    f_z = self._polynomial(z)

                    # Check convergence
                    if abs(f_z) < self.tolerance:
                        root_idx = self._find_root_index(z)

                        # Color based on iteration count
                        intensity = int(255 * (1.0 - iteration / self.max_iterations))
                        base_color = self.root_colors[root_idx]

                        fractal[iy, ix] = (base_color * intensity // 255).astype(np.uint8)
                        break

                    # Newton step
                    f_prime = self._derivative(z)
                    if abs(f_prime) < 1e-10:  # Avoid division by zero
                        break

                    z_next = z - f_z / f_prime

                    # Check for divergence
                    if abs(z_next) > 100.0:
                        break

                    z = z_next
                else:
                    # Did not converge
                    fractal[iy, ix] = [0, 0, 0]

        self.fractal_data = fractal
        return fractal

    def zoom(self, center_x: float, center_y: float, zoom_factor: float) -> None:
        """
        Zoom into a region of the fractal.

        Args:
            center_x: X coordinate of zoom center
            center_y: Y coordinate of zoom center
            zoom_factor: Zoom multiplier (>1 zooms in)
        """
        width = self.x_max - self.x_min
        height = self.y_max - self.y_min

        # New bounds
        self.x_min = center_x - width / (2.0 * zoom_factor)
        self.x_max = center_x + width / (2.0 * zoom_factor)
        self.y_min = center_y - height / (2.0 * zoom_factor)
        self.y_max = center_y + height / (2.0 * zoom_factor)

    def reset_view(self) -> None:
        """Reset to default view."""
        self.x_min, self.x_max = -2.0, 2.0
        self.y_min, self.y_max = -1.5, 1.5
