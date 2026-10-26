"""
Reusable tkinter widgets for controlling animation parameters.

Provides a labelled slider with a live numeric read-out and a small container
that groups several sliders together.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional


class ParameterSlider(ttk.Frame):
    """
    A labelled slider with a live value read-out.

    Attributes:
        variable (tk.DoubleVar): Current slider value
        slider (ttk.Scale): The scale widget itself
        value_label (ttk.Label): Read-out showing the current value
    """

    def __init__(
        self,
        parent: tk.Widget,
        label: str,
        from_: float,
        to: float,
        default: float,
        on_change: Optional[Callable[[float], None]] = None,
        decimals: int = 2
    ):
        """
        Create the slider.

        Args:
            parent: Parent widget
            label: Text shown above the slider
            from_: Minimum value
            to: Maximum value
            default: Initial value
            on_change: Callback invoked with the new value
            decimals: Number of digits after the decimal point
        """
        super().__init__(parent)

        self.on_change = on_change
        self.decimals = decimals
        self.variable = tk.DoubleVar(value=default)

        header = ttk.Frame(self)
        header.pack(fill=tk.X)

        ttk.Label(header, text=label).pack(side=tk.LEFT)

        self.value_label = ttk.Label(header, text=self._format(default))
        self.value_label.pack(side=tk.RIGHT)

        self.slider = ttk.Scale(
            self,
            from_=from_,
            to=to,
            variable=self.variable,
            orient=tk.HORIZONTAL,
            command=self._handle_change
        )
        self.slider.pack(fill=tk.X)

        # Clicking anywhere on the trough should jump to that value
        self.slider.bind("<Button-1>", self._jump_to_click)

    def _format(self, value: float) -> str:
        """
        Format a value for display.

        Args:
            value: Numeric value

        Returns:
            Formatted string
        """
        if self.decimals <= 0:
            return str(int(round(value)))
        return f"{value:.{self.decimals}f}"

    def _handle_change(self, _value: str) -> None:
        """React to slider movement."""
        value = self.variable.get()
        self.value_label.config(text=self._format(value))
        if self.on_change is not None:
            self.on_change(value)

    def _jump_to_click(self, event) -> None:
        """Move the slider handle to the clicked position."""
        try:
            fraction = event.x / max(1, self.slider.winfo_width())
            fraction = min(1.0, max(0.0, fraction))
            low = float(self.slider.cget("from"))
            high = float(self.slider.cget("to"))
            self.variable.set(low + (high - low) * fraction)
            self._handle_change("")
        except (tk.TclError, ValueError):
            pass

    def get_value(self) -> float:
        """
        Current slider value.

        Returns:
            The value as a float
        """
        return float(self.variable.get())

    def set_value(self, value: float) -> None:
        """
        Set the slider programmatically.

        Args:
            value: New value
        """
        self.variable.set(value)
        self._handle_change("")


class ControlPanel(ttk.LabelFrame):
    """
    Group of parameter sliders.

    Attributes:
        sliders (Dict[str, ParameterSlider]): Sliders indexed by name
    """

    def __init__(self, parent: tk.Widget, title: str = "Параметры"):
        """
        Create the panel.

        Args:
            parent: Parent widget
            title: Frame title
        """
        super().__init__(parent, text=title, padding=6)
        self.sliders: Dict[str, ParameterSlider] = {}

    def add_slider(
        self,
        name: str,
        label: str,
        from_: float,
        to: float,
        default: float,
        on_change: Optional[Callable[[float], None]] = None,
        decimals: int = 2
    ) -> ParameterSlider:
        """
        Add a slider to the panel.

        Args:
            name: Internal identifier
            label: Display label
            from_: Minimum value
            to: Maximum value
            default: Initial value
            on_change: Callback invoked with the new value
            decimals: Digits after the decimal point

        Returns:
            The created slider
        """
        slider = ParameterSlider(
            self, label, from_, to, default, on_change, decimals
        )
        slider.pack(fill=tk.X, pady=4)
        self.sliders[name] = slider
        return slider

    def get_value(self, name: str) -> float:
        """
        Read a slider value by name.

        Args:
            name: Slider identifier

        Returns:
            Current value
        """
        return self.sliders[name].get_value()
