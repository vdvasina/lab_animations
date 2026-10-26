"""
Лабораторная 2: Сложная анимация - Фрактал Ньютона (вариант 4).

Интерактивная визуализация метода Ньютона поиска корней многочлена
в комплексной плоскости. Каждый пиксель - комплексное число, для которого
выполняется итерация

    z(n+1) = z(n) - f(z(n)) / f'(z(n))

Многочлен: f(z) = z^3 - 1, корни - кубические корни из единицы:
    красный  - z = 1
    зелёный  - z = exp(2*pi*i/3)
    синий    - z = exp(4*pi*i/3)

Яркость точки зависит от числа итераций до сходимости.

Управление:
    левый клик по холсту - увеличить область в 2 раза
    клавиша R            - вернуть исходный вид
    слайдер итераций     - глубина прорисовки деталей
"""

import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.newton_fractal import NewtonFractal
from renderers.newton_renderer import NewtonRenderer
from widgets.sliders import ParameterSlider


# ----------------------------------------------------------------------
# Параметры окна
# ----------------------------------------------------------------------
WINDOW_WIDTH = 1120
WINDOW_HEIGHT = 720

CANVAS_WIDTH = 760
CANVAS_HEIGHT = 600

DEFAULT_MAX_ITERATIONS = 200
DEFAULT_TOLERANCE = 1e-6
ZOOM_FACTOR = 2.0


class NewtonApp:
    """
    Главное окно приложения для фрактала Ньютона.

    Хранит модель, рендерер и элементы интерфейса.
    """

    def __init__(self, root: tk.Tk):
        """
        Создать интерфейс и построить первое изображение.

        Args:
            root: Корневое окно tkinter
        """
        self.root = root
        self.root.title("Лабораторная 2 - Фрактал Ньютона (вариант 4)")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(950, 650)

        self.zoom_level = 1.0

        self.model = NewtonFractal(
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            max_iterations=DEFAULT_MAX_ITERATIONS,
            tolerance=DEFAULT_TOLERANCE
        )

        self._build_ui()

        self.renderer = NewtonRenderer(
            self.canvas, CANVAS_WIDTH, CANVAS_HEIGHT
        )

        self._bind_keys()
        self.recompute()

    # ------------------------------------------------------------------
    # Интерфейс
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        """Создать все виджеты окна."""
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- холст ---------------------------------------------------
        left = ttk.LabelFrame(container, text="Фрактал Ньютона")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            left,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#000000",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(padx=5, pady=5)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # --- правая панель -------------------------------------------
        right = ttk.Frame(container, width=280)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        info = ttk.LabelFrame(right, text="Задача")
        info.pack(fill=tk.X)

        ttk.Label(
            info,
            text=(
                "f(z) = z^3 - 1\n"
                "f'(z) = 3*z^2\n\n"
                "z(n+1) = z(n) - f(z)/f'(z)\n\n"
                "Корни:\n"
                "  красный  1\n"
                "  зелёный  exp(2pi i/3)\n"
                "  синий    exp(4pi i/3)"
            ),
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=8, pady=8)

        # --- слайдеры -------------------------------------------------
        controls = ttk.LabelFrame(right, text="Параметры")
        controls.pack(fill=tk.X, pady=(10, 0))

        self.iter_slider = ParameterSlider(
            controls,
            "итераций",
            30, 500, DEFAULT_MAX_ITERATIONS,
            self._on_iterations_change,
            decimals=0
        )
        self.iter_slider.pack(fill=tk.X, padx=6, pady=6)

        # --- кнопки ---------------------------------------------------
        buttons = ttk.LabelFrame(right, text="Управление")
        buttons.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            buttons, text="Пересчитать", command=self.recompute
        ).pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(
            buttons, text="Исходный вид (R)", command=self.reset_view
        ).pack(fill=tk.X, padx=6, pady=4)

        ttk.Button(
            buttons, text="Сохранить PNG", command=self.save_png
        ).pack(fill=tk.X, padx=6, pady=4)

        # --- состояние ------------------------------------------------
        status = ttk.LabelFrame(right, text="Состояние")
        status.pack(fill=tk.X, pady=(10, 0))

        self.status_label = ttk.Label(status, text="готово", justify=tk.LEFT)
        self.status_label.pack(anchor=tk.W, padx=8, pady=4)

        self.view_label = ttk.Label(status, text="", justify=tk.LEFT)
        self.view_label.pack(anchor=tk.W, padx=8, pady=(0, 8))

    def _bind_keys(self) -> None:
        """Привязать горячие клавиши."""
        self.root.bind("<r>", lambda _e: self.reset_view())
        self.root.bind("<R>", lambda _e: self.reset_view())

    # ------------------------------------------------------------------
    # Обработчики
    # ------------------------------------------------------------------
    def _on_iterations_change(self, value: float) -> None:
        """Изменить максимальное число итераций."""
        self.model.max_iterations = max(10, int(value))

    def _on_canvas_click(self, event) -> None:
        """
        Увеличить область вокруг точки клика.

        Args:
            event: Событие мыши tkinter
        """
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())

        # Переводим пиксель в координаты комплексной плоскости
        fx = event.x / width
        fy = event.y / height

        center_x = self.model.x_min + (self.model.x_max - self.model.x_min) * fx
        center_y = self.model.y_min + (self.model.y_max - self.model.y_min) * fy

        self.model.zoom(center_x, center_y, ZOOM_FACTOR)
        self.zoom_level *= ZOOM_FACTOR
        self.recompute()

    def reset_view(self) -> None:
        """Вернуть исходный вид фрактала."""
        self.model.reset_view()
        self.zoom_level = 1.0
        self.recompute()

    def recompute(self) -> None:
        """Пересчитать фрактал и показать его на холсте."""
        self.status_label.config(text="вычисление...")
        self.root.update_idletasks()

        data = self.model.compute()
        self.renderer.draw_fractal(data)

        self.status_label.config(text="готово")
        self.view_label.config(
            text=(
                f"зум: x{self.zoom_level:.1f}\n"
                f"итераций: {self.model.max_iterations}\n"
                f"x: {self.model.x_min:.3f} .. {self.model.x_max:.3f}\n"
                f"y: {self.model.y_min:.3f} .. {self.model.y_max:.3f}"
            )
        )

    def save_png(self) -> None:
        """Сохранить текущее изображение в файл."""
        from tkinter import filedialog

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile="newton_fractal.png"
        )
        if not path:
            return

        image = self.renderer.get_image()
        if image is not None:
            image.save(path)
            self.status_label.config(text="сохранено")

    def on_closing(self) -> None:
        """Закрыть окно."""
        self.root.destroy()


def main():
    """Точка входа."""
    root = tk.Tk()
    app = NewtonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
