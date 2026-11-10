from pathlib import Path
import sys

# Garante prioridade para o src local em testes
src_dir = str(Path(__file__).resolve().parent.parent / "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
