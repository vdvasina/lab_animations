"""
Renderer for the Lorenz attractor.

Draws the 2D (x, y) projection of the trajectory on a tkinter canvas.

The renderer works incrementally: each animation frame only the newly added
segments are drawn as separate canvas items, so the picture does not have to
be rebuilt from scratch sixty times per second.
"""

import tkinter as tk
from typing import List, Optional, Sequence

import numpy as np


class LorenzRenderer:
    """
    Tkinter renderer for the Lorenz attractor.

    Attributes:
        canvas (tk.Canvas): Target canvas
        width (int): Canvas width in pixels
        height (int): Canvas height in pixels
        scale (float): Pixels per unit of phase space
        offset_x (float): Horizontal shift of the centre in pixels
        offset_y (float): Vertical shift of the centre in pixels
        trail_length (int): How many recent points are kept on screen
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        width: int = 800,
        height: int = 600,
        trail_length: int = 20000
    ):
        """
        Initialize the renderer.

        Args:
            canvas: tkinter Canvas widget to draw on
            width: Canvas width in pixels
            height: Canvas height in pixels
            trail_length: Maximum number of trailing points to keep
        """
        self.canvas = canvas
        self.width = width
        self.height = height

        self.scale = 8.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.trail_length = trail_length

        self.segment_ids: List[int] = []
        self.head_id: Optional[int] = None
        self.points_drawn = 0

        self.bg_color = "#000000"
        self.line_color = "#22D67A"
        self.head_color = "#FFD400"

        self.canvas.configure(bg=self.bg_color)

    # ------------------------------------------------------------------
    # Coordinate conversion
    # ------------------------------------------------------------------
    def _to_pixels(self, x: float, y: float) -> tuple:
        """
        Convert phase-space coordinates to canvas pixels.

        Args:
            x: Phase-space x coordinate
            y: Phase-space y coordinate

        Returns:
            Tuple (px, py) in canvas pixels
        """
        px = self.width / 2 + (x + self.offset_x) * self.scale
        py = self.height / 2 - (y + self.offset_y) * self.scale  # flip Y axis
        return px, py

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def clear(self) -> None:
        """Remove everything from the canvas."""
        self.canvas.delete("all")
        self.segment_ids.clear()
        self.head_id = None
        self.points_drawn = 0

    def draw_trajectory(self, trajectory: np.ndarray) -> None:
        """
        Draw (or redraw) the whole trajectory in one go.

        Used after parameter changes, when the picture must be rebuilt.

        Args:
            trajectory: Array of shape (N, 2) with (x, y) points
        """
        self.clear()

        if trajectory is None or len(trajectory) < 2:
            if trajectory is not None and len(trajectory) == 1:
                self._update_head(float(trajectory[0][0]), float(trajectory[0][1]))
            return

        points = trajectory[-self.trail_length:]
        coords = []
        for x, y in points:
            coords.extend(self._to_pixels(float(x), float(y)))

        line_id = self.canvas.create_line(
            *coords,
            fill=self.line_color,
            width=1,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND,
            smooth=False
        )
        self.segment_ids.append(line_id)
        self.points_drawn = len(points)

        self._update_head(float(points[-1][0]), float(points[-1][1]))

    def draw_step(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """
        Draw a single new segment (called every animation frame).

        Args:
            x1: Start x in phase space
            y1: Start y in phase space
            x2: End x in phase space
            y2: End y in phase space
        """
        px1, py1 = self._to_pixels(x1, y1)
        px2, py2 = self._to_pixels(x2, y2)

        line_id = self.canvas.create_line(
            px1, py1, px2, py2,
            fill=self.line_color,
            width=1,
            capstyle=tk.ROUND
        )
        self.segment_ids.append(line_id)
        self.points_drawn += 1

        # Drop the oldest segments so the canvas does not grow forever
        while len(self.segment_ids) > self.trail_length:
            old_id = self.segment_ids.pop(0)
            self.canvas.delete(old_id)
            self.points_drawn -= 1

        self._update_head(x2, y2)

    def _update_head(self, x: float, y: float) -> None:
        """
        Move the marker that shows the current position.

        Args:
            x: Current x coordinate
            y: Current y coordinate
        """
        px, py = self._to_pixels(x, y)
        r = 5
        if self.head_id is None:
            self.head_id = self.canvas.create_oval(
                px - r, py - r, px + r, py + r,
                fill=self.head_color,
                outline="#FFF7AE"
            )
        else:
            self.canvas.coords(self.head_id, px - r, py - r, px + r, py + r)
            self.canvas.tag_raise(self.head_id)

    # ------------------------------------------------------------------
    # View settings
    # ------------------------------------------------------------------
    def set_scale(self, scale: float) -> None:
        """
        Set zoom level.

        Args:
            scale: Pixels per unit of phase space
        """
        self.scale = max(0.5, float(scale))

    def set_offset(self, offset_x: float, offset_y: float) -> None:
        """
        Shift the centre of the view.

        Args:
            offset_x: Horizontal shift in phase-space units
            offset_y: Vertical shift in phase-space units
        """
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    def set_line_color(self, color: str) -> None:
        """
        Change the trajectory colour.

        Args:
            color: Any tkinter colour string
        """
        self.line_color = color
