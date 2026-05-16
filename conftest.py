"""Make repo root importable so `tests/` can `import generator`, `glue_jobs`, etc."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
