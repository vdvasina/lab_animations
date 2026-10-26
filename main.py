"""
Animation Laboratory Works - Main Entry Point.

This program implements two laboratory works on animation and graphics programming:

Lab 1 (Simple Animation - Variant 4):
    Lorenz Attractor - A 2D visualization of the Lorenz system of differential
    equations showing chaotic dynamics. Includes interactive parameter controls.

Lab 2 (Complex Animation - Variant 4):
    Newton Fractal - An interactive visualization of Newton's method for finding
    polynomial roots in the complex plane. Beautiful fractal patterns emerge
    based on basin of attraction.

Run 'python main.py 1' for Lab 1 or 'python main.py 2' for Lab 2.
"""

import sys
import tkinter as tk
from pathlib import Path


def main():
    """Main entry point - choose which lab to run."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python main.py <lab_number>")
        print("  lab_number: 1 for Lab 1 (Lorenz), 2 for Lab 2 (Newton)")
        sys.exit(1)

    lab_num = sys.argv[1]

    if lab_num == "1":
        # Lab 1: Lorenz Attractor
        from lab1_lorenz import main as run_lab1
        run_lab1()
    elif lab_num == "2":
        # Lab 2: Newton Fractal
        from lab2_newton import main as run_lab2
        run_lab2()
    else:
        print(f"Invalid lab number: {lab_num}")
        print("Usage: python main.py <1|2>")
        sys.exit(1)


if __name__ == "__main__":
    main()
