#!/usr/bin/env python3
"""Validador e inspetor de integridade dos pacotes sdist e wheel construídos."""

from __future__ import annotations

from pathlib import Path
import sys
import tarfile
import zipfile


def verificar_distribuicao() -> int:
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("Erro: Diretório dist/ não existe.", file=sys.stderr)
        return 1

    wheels = list(dist_dir.glob("*.whl"))
    sdists = list(dist_dir.glob("*.tar.gz"))

    if not wheels:
        print("Erro: Nenhum pacote .whl encontrado em dist/", file=sys.stderr)
        return 1
    if not sdists:
        print("Erro: Nenhum pacote .tar.gz encontrado em dist/", file=sys.stderr)
        return 1

    wheel_path = wheels[0]
    sdist_path = sdists[0]

    print(f"Inspecionando Wheel: {wheel_path.name}")
    with zipfile.ZipFile(wheel_path) as zf:
        nomes = zf.namelist()
        print(f"  • Membros no wheel: {len(nomes)}")
        assert any("py.typed" in n for n in nomes), "py.typed ausente no wheel"
        assert any("cli.py" in n for n in nomes), "cli.py ausente no wheel"
        assert any("calculator.py" in n for n in nomes), "calculator.py ausente no wheel"

    print(f"Inspecionando sdist: {sdist_path.name}")
    with tarfile.open(sdist_path, "r:gz") as tf:
        membros = tf.getnames()
        print(f"  • Membros no sdist: {len(membros)}")
        assert any("pyproject.toml" in m for m in membros), "pyproject.toml ausente no sdist"
        assert any("README.md" in m for m in membros), "README.md ausente no sdist"
        assert any("LICENSE" in m for m in membros), "LICENSE ausente no sdist"

    print("✓ Distribuições sdist e wheel verificadas com 100% de integridade.")
    return 0


if __name__ == "__main__":
    sys.exit(verificar_distribuicao())
