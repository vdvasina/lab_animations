"""
Lorenz Attractor Model - Laboratory 1.

Implements the Lorenz system of differential equations:
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z

The system exhibits chaotic behaviour and creates a butterfly-shaped attractor
in the phase space.

References:
    Lorenz, E. N. (1963). "Deterministic Nonperiodic Flow".
    Journal of the Atmospheric Sciences, 20(2), 130-141.
"""

import numpy as np
from typing import List, Optional, Sequence


# Default starting point.  It must NOT be the origin: (0, 0, z) is an
# equilibrium point of the system, so a trajectory started there would have
# dx/dt = dy/dt = 0 and would stay in the middle of the picture forever.
DEFAULT_INITIAL_STATE = (0.0, 1.0, 1.05)


class LorenzAttractor:
    """
    Lorenz attractor model with Runge-Kutta 4 numerical integration.

    Attributes:
        sigma (float): Prandtl number (stretching of the flow)
        rho (float): Rayleigh number (convection intensity)
        beta (float): Geometric factor
        dt (float): Integration time step
        max_points (int): Maximum number of stored trajectory points
        state (np.ndarray): Current [x, y, z] state vector
        trajectory (List[np.ndarray]): All visited states
        trimmed (bool): True if old points were dropped on the last step
    """

    def __init__(
        self,
        sigma: float = 10.0,
        rho: float = 28.0,
        beta: float = 8.0 / 3.0,
        dt: float = 0.01,
        initial_state: Optional[Sequence[float]] = None,
        max_points: int = 20000
    ):
        """
        Initialize the Lorenz attractor.

        Args:
            sigma: Prandtl number
            rho: Rayleigh number
            beta: Geometric factor
            dt: Integration time step
            initial_state: Starting point [x, y, z]; defaults to
                (0.0, 1.0, 1.05) which lies off the equilibrium point
            max_points: Maximum number of stored trajectory points
        """
        self.sigma = sigma
        self.rho = rho
        self.beta = beta
        self.dt = dt
        self.max_points = max_points

        self.initial_state = np.array(
            initial_state if initial_state is not None else DEFAULT_INITIAL_STATE,
            dtype=np.float64
        )

        self.state = self.initial_state.copy()
        self.trajectory: List[np.ndarray] = [self.state.copy()]
        self.trimmed = False

    def _derivatives(self, state: np.ndarray) -> np.ndarray:
        """
        Calculate the derivative vector at a given state.

        Args:
            state: Current [x, y, z] state vector

        Returns:
            Derivative vector [dx/dt, dy/dt, dz/dt]
        """
        x, y, z = state

        dx_dt = self.sigma * (y - x)
        dy_dt = x * (self.rho - z) - y
        dz_dt = x * y - self.beta * z

        return np.array([dx_dt, dy_dt, dz_dt])

    def step(self) -> np.ndarray:
        """
        Advance the system by one time step using Runge-Kutta 4.

        Returns:
            Updated state vector [x, y, z]
        """
        h = self.dt

        # Classic RK4: weighted average of four slope estimates
        k1 = self._derivatives(self.state)
        k2 = self._derivatives(self.state + 0.5 * h * k1)
        k3 = self._derivatives(self.state + 0.5 * h * k2)
        k4 = self._derivatives(self.state + h * k3)

        self.state = self.state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

        self.trajectory.append(self.state.copy())
        self._trim()

        return self.state

    def advance(self, steps: int) -> np.ndarray:
        """
        Advance the system by several steps at once.

        Args:
            steps: Number of integration steps to perform

        Returns:
            Updated state vector [x, y, z]
        """
        for _ in range(max(0, int(steps))):
            self.step()
        return self.state

    def _trim(self) -> None:
        """Drop the oldest points when the trajectory grows too long."""
        excess = len(self.trajectory) - self.max_points
        if excess > 0:
            del self.trajectory[:excess]
            self.trimmed = True

    def get_xy_projection(self) -> np.ndarray:
        """
        Get the 2D (x, y) projection of the trajectory.

        Returns:
            Array of shape (N, 2) with (x, y) coordinates
        """
        if not self.trajectory:
            return np.empty((0, 2), dtype=np.float64)
        return np.array([state[:2] for state in self.trajectory], dtype=np.float64)

    def reset(self) -> None:
        """Restart the trajectory from the initial state."""
        self.state = self.initial_state.copy()
        self.trajectory = [self.state.copy()]
        self.trimmed = False

    def set_parameters(
        self,
        sigma: Optional[float] = None,
        rho: Optional[float] = None,
        beta: Optional[float] = None
    ) -> None:
        """
        Update the system parameters.

        Args:
            sigma: New Prandtl number (None keeps the current value)
            rho: New Rayleigh number (None keeps the current value)
            beta: New geometric factor (None keeps the current value)
        """
        if sigma is not None:
            self.sigma = float(sigma)
        if rho is not None:
            self.rho = float(rho)
        if beta is not None:
            self.beta = float(beta)
