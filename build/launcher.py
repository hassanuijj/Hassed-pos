from pathlib import Path
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Prefer the project's real application entry point when present.
    candidates = [
        root / "app.py",
        root / "main.py",
        root / "run.py",
    ]

    for path in candidates:
        if path.exists():
            namespace = {"__name__": "__main__", "__file__": str(path)}
            exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
            return 0

    print("Hassed POS: application entry point not found.")
    print("Expected one of: app.py, main.py, run.py")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
