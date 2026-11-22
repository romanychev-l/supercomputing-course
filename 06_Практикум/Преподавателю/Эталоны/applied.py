"""Small executable specifications. No performance or statistical-quality claim."""
import argparse
import cmath
import json
import math


def fft(x):
    n = len(x)
    if n < 1 or n & (n - 1):
        raise ValueError("FFT requires a positive power of two")
    a = list(map(complex, x))
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    width = 2
    while width <= n:
        root = cmath.exp(-2j * math.pi / width)
        for start in range(0, n, width):
            w = 1 + 0j
            for k in range(width // 2):
                u = a[start + k]
                v = w * a[start + k + width // 2]
                a[start + k] = u + v
                a[start + k + width // 2] = u - v
                w *= root
        width *= 2
    return a


def dft(x):
    n = len(x)
    return [sum(z * cmath.exp(-2j * math.pi * k * j / n) for j, z in enumerate(x)) for k in range(n)]


def ar_scan(eps, coefficient=0.75):
    # Each affine map f(y)=a*y+b is composed with the preceding prefix.
    # Each stage reads only the old stage. A parallel implementation may
    # distribute the inner loop and synchronize once between stages.
    pairs = [(coefficient, e) for e in eps]
    stride = 1
    while stride < len(pairs):
        old = pairs
        pairs = old.copy()
        for i in range(stride, len(old)):
            a, b = old[i]
            c, d = old[i - stride]
            pairs[i] = (a * c, a * d + b)
        stride *= 2
    return [b for _, b in pairs]  # initial y[-1] = 0


def ma(eps):
    weights = (0.5, 0.3, 0.2)
    return [sum(w * eps[i-k] for k, w in enumerate(weights) if i >= k) for i in range(len(eps))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("fft", "ar", "ma"))
    parser.add_argument("n", type=int)
    args = parser.parse_args()
    if not 1 <= args.n <= 256:
        parser.error("reference sizes: 1..256")
    eps = [(i % 5) - 2 for i in range(args.n)]
    if args.mode == "fft":
        if args.n & (args.n - 1):
            parser.error("FFT requires a power of two")
        actual, expected = fft(eps), dft(eps)
        error = max(abs(a-b) for a,b in zip(actual,expected))
        values = [[z.real, z.imag] for z in actual]
    elif args.mode == "ar":
        actual = ar_scan(eps)
        expected, previous = [], 0.0
        for e in eps:
            previous = 0.75 * previous + e
            expected.append(previous)
        error = max(abs(a-b) for a,b in zip(actual,expected))
        values = actual
    else:
        values = ma(eps)
        error = None  # independently tested by verify.py; do not invent an oracle
    print(json.dumps({"mode": args.mode, "n": args.n, "values": values, "max_error": error}))


if __name__ == "__main__":
    main()
