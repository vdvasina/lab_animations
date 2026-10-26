"""
Laboratory 1: Simple Animation - Lorenz Attractor (Variant 4).

The program integrates the Lorenz system of ordinary differential equations
and animates its two-dimensional (x, y) projection, producing the classic
butterfly-shaped attractor.

Controls:
    sigma slider  - Prandtl number, controls how strongly the flow is stretched
    rho slider    - Rayleigh number, controls convection intensity
    beta slider   - geometric factor
    speed slider  - how many integration steps are made per frame
    scale slider  - zoom level
    Pause/Resume  - freeze or continue the animation
    Reset         - restart the trajectory from the initial point
    Clear         - wipe the canvas

Keyboard shortcuts:
    Space - pause / resume
    R     - reset
    C     - clear
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.lorenz_attractor import LorenzAttractor
from renderers.lorenz_renderer import LorenzRenderer
from widgets.sliders import ParameterSlider


# ----------------------------------------------------------------------
# Window and animation settings
# ----------------------------------------------------------------------
WINDOW_WIDTH = 1060
WINDOW_HEIGHT = 700

CANVAS_WIDTH = 780
CANVAS_HEIGHT = 620

DEFAULT_SIGMA = 10.0
DEFAULT_RHO = 28.0
DEFAULT_BETA = 8.0 / 3.0

FRAME_DELAY_MS = 16        # ~60 frames per second
DEFAULT_STEPS_PER_FRAME = 12
TRAIL_LENGTH = 20000

DEFAULT_SCALE = 8.0


class LorenzApp:
    """
    Main application window for the Lorenz attractor animation.

    Owns the model, the renderer and all interface widgets.
    """

    def __init__(self, root: tk.Tk):
        """
        Build the interface and start the animation loop.

        Args:
            root: Root tkinter window
        """
        self.root = root
        self.root.title("Лабораторная 1 - Аттрактор Лоренца (вариант 4)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(900, 640)

        self.model = LorenzAttractor(
            sigma=DEFAULT_SIGMA,
            rho=DEFAULT_RHO,
            beta=DEFAULT_BETA,
            max_points=TRAIL_LENGTH
        )
        self.steps_per_frame = DEFAULT_STEPS_PER_FRAME
        self._build_ui()

        self.renderer = LorenzRenderer(
            self.canvas, CANVAS_WIDTH, CANVAS_HEIGHT, trail_length=TRAIL_LENGTH
        )

        self.is_running = True
        self.after_id = None

        # Warm up: the trajectory needs a few hundred steps before it settles
        # onto the attractor, otherwise the first frames look like a straight
        # line running away from the origin.
        self.model.advance(1500)
        self.renderer.draw_trajectory(self.model.get_xy_projection())

        self._bind_keys()
        self._animate()

    # ------------------------------------------------------------------
    # Interface
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Create all widgets."""
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- canvas -------------------------------------------------
        left = ttk.LabelFrame(container, text="Фазовый портрет (проекция x-y)")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            left,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#000000",
            highlightthickness=0
        )
        self.canvas.pack(padx=5, pady=5)

        # --- right panel --------------------------------------------
        right = ttk.Frame(container, width=250)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        info = ttk.LabelFrame(right, text="Система уравнений")
        info.pack(fill=tk.X)

        ttk.Label(
            info,
            text=(
                "dx/dt = s(y - x)\n"
                "dy/dt = x(r - z) - y\n"
                "dz/dt = x*y - b*z\n\n"
                "s = 10, r = 28, b = 8/3"
            ),
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=8, pady=8)

        # --- sliders -------------------------------------------------
        controls = ttk.LabelFrame(right, text="Параметры")
        controls.pack(fill=tk.X, pady=(10, 0))

        self.sigma_slider = ParameterSlider(
            controls, "sigma", 0.5, 20.0, DEFAULT_SIGMA, self._on_sigma_change
        )
        self.sigma_slider.pack(fill=tk.X, padx=6, pady=4)

        self.rho_slider = ParameterSlider(
            controls, "rho", 1.0, 60.0, DEFAULT_RHO, self._on_rho_change
        )
        self.rho_slider.pack(fill=tk.X, padx=6, pady=4)

        self.beta_slider = ParameterSlider(
            controls, "beta", 0.5, 5.0, DEFAULT_BETA, self._on_beta_change
        )
        self.beta_slider.pack(fill=tk.X, padx=6, pady=4)

        self.scale_slider = ParameterSlider(
            controls, "scale", 2.0, 16.0, DEFAULT_SCALE, self._on_scale_change
        )
        self.scale_slider.pack(fill=tk.X, padx=6, pady=4)

        self.speed_slider = ParameterSlider(
            controls, "speed", 1, 40, DEFAULT_STEPS_PER_FRAME,
            self._on_speed_change, decimals=0
        )
        self.speed_slider.pack(fill=tk.X, padx=6, pady=4)

        # --- buttons -------------------------------------------------
        buttons = ttk.LabelFrame(right, text="Управление")
        buttons.pack(fill=tk.X, pady=(10, 0))

        self.pause_button = ttk.Button(
            buttons, text="Пауза (Space)", command=self.toggle_pause
        )
        self.pause_button.pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(buttons, text="Сброс (R)", command=self.reset).pack(
            fill=tk.X, padx=6, pady=4
        )
        ttk.Button(buttons, text="Очистить (C)", command=self.clear).pack(
            fill=tk.X, padx=6, pady=4
        )

        # --- status --------------------------------------------------
        status = ttk.LabelFrame(right, text="Состояние")
        status.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status, text="точек: 0", justify=tk.LEFT)
        self.status_label.pack(anchor=tk.W, padx=8, pady=8)

    def _bind_keys(self) -> None:
        """Attach keyboard shortcuts."""
        self.root.bind("<space>", lambda _e: self.toggle_pause())
        self.root.bind("<r>", lambda _e: self.reset())
        self.root.bind("<R>", lambda _e: self.reset())
        self.root.bind("<c>", lambda _e: self.clear())
        self.root.bind("<C>", lambda _e: self.clear())

    # ------------------------------------------------------------------
    # Slider callbacks
    # ------------------------------------------------------------------
    def _on_sigma_change(self, value: float) -> None:
        """Update the Prandtl number."""
        self.model.set_parameters(sigma=value)

    def _on_rho_change(self, value: float) -> None:
        """Update the Rayleigh number."""
        self.model.set_parameters(rho=value)

    def _on_beta_change(self, value: float) -> None:
        """Update the geometric factor."""
        self.model.set_parameters(beta=value)

    def _on_scale_change(self, value: float) -> None:
        """Change the zoom level and redraw the existing trajectory."""
        self.renderer.set_scale(value)
        self.renderer.draw_trajectory(self.model.get_xy_projection())

    def _on_speed_change(self, value: float) -> None:
        """Change how many integration steps happen per frame."""
        self.steps_per_frame = max(1, int(value))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def toggle_pause(self) -> None:
        """Pause or resume the animation."""
        self.is_running = not self.is_running
        self.pause_button.config(
            text="Продолжить (Space)" if not self.is_running else "Пауза (Space)"
        )
        if self.is_running:
            self._animate()

    def reset(self) -> None:
        """Restart the trajectory from the initial state."""
        self.model.reset()
        self.model.advance(600)
        self.renderer.draw_trajectory(self.model.get_xy_projection())
        self._update_status()

    def clear(self) -> None:
        """Clear the canvas without resetting the model."""
        self.renderer.clear()
        self._update_status()

    def _update_status(self) -> None:
        """Refresh the status label."""
        self.status_label.config(
            text=(
                f"точек: {len(self.model.trajectory)}\n"
                f"шагов за кадр: {self.steps_per_frame}\n"
                f"масштаб: {self.renderer.scale:.1f}"
            )
        )

    # ------------------------------------------------------------------
    # Animation loop
    # ------------------------------------------------------------------
    def _animate(self) -> None:
        """One animation frame: integrate, then draw the new segments."""
        if not self.is_running:
            return

        steps = getattr(self, "steps_per_frame", DEFAULT_STEPS_PER_FRAME)
        previous = self.model.state.copy()

        for _ in range(steps):
            before = self.model.state.copy()
            after = self.model.step()
            self.renderer.draw_step(
                float(before[0]), float(before[1]),
                float(after[0]), float(after[1])
            )
            previous = after

        self._update_status()
        self.after_id = self.root.after(FRAME_DELAY_MS, self._animate)

    def on_closing(self) -> None:
        """Stop the animation and close the window."""
        self.is_running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
        self.root.destroy()


def main():
    """Start the application."""
    root = tk.Tk()
    app = LorenzApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
