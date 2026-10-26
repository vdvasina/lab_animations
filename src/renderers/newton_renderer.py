"""
Renderer for Newton Fractal visualization using tkinter.

Displays the Newton fractal computed from a complex polynomial.
Uses RGB coloring based on which root converges.
"""

import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


class NewtonRenderer:
    """
    Tkinter-based renderer for Newton fractal.

    Attributes:
        canvas: tkinter Canvas widget
        width (int): Canvas width
        height (int): Canvas height
    """

    def __init__(self, canvas: tk.Canvas, width: int = 800, height: int = 600):
        """
        Initialize renderer.

        Args:
            canvas: tkinter Canvas widget
            width: Canvas width in pixels
            height: Canvas height in pixels
        """
        self.canvas = canvas
        self.width = width
        self.height = height

        self.image = None
        self.photo_image = None

    def clear(self) -> None:
        """Clear the canvas."""
        self.canvas.delete("all")
        self.canvas.config(bg="#000000")

    def draw_fractal(self, fractal_data: np.ndarray) -> None:
        """
        Draw the fractal on canvas.

        Args:
            fractal_data: Array of shape (height, width, 3) with RGB values
        """
        # Ensure data is uint8
        fractal_uint8 = fractal_data.astype(np.uint8)

        # Create PIL Image
        self.image = Image.fromarray(fractal_uint8, mode='RGB')

        # Convert to PhotoImage
        self.photo_image = ImageTk.PhotoImage(self.image)

        # Draw on canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW)
        self.canvas.config(width=self.width, height=self.height)

    def get_image(self) -> Image.Image:
        """
        Get the current fractal as PIL Image.

        Returns:
            PIL Image object
        """
        return self.image if self.image is not None else Image.new('RGB', (self.width, self.height))
