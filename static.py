# cosine.py

import numpy as np

def print_cosine(x: np.ndarray) -> None:
    with np.printoptions(precision=3, suppress=True):
        print(np.cos(x))

x = np.linspace(0, 2 * np.pi, 9)
print_cosine(x)


