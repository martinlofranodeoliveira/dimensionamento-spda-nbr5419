#!/usr/bin/env python3
"""Gera o painel SVG e captura a imagem PNG em alta resolução via Google Chrome headless."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from spda_nbr5419.calculator import dimensionar_spda
from spda_nbr5419.codecs import carregar_entrada_json
from spda_nbr5419.svg_generator import gerar_painel_svg


def main() -> int:
    raiz = Path(__file__).resolve().parent.parent
    docs_dir = raiz / "docs"
    docs_dir.mkdir(exist_ok=True)

    exemplo_json = raiz / "examples" / "predio_residencial_belo_horizonte.json"
    if not exemplo_json.exists():
        print(f"Erro: Arquivo {exemplo_json} não encontrado.", file=sys.stderr)
        return 1

    conteudo = exemplo_json.read_bytes()
    estrutura = carregar_entrada_json(conteudo)
    resultado = dimensionar_spda(estrutura, identificador_projeto="SPDA-NBR5419-BH-01")

    svg_conteudo = gerar_painel_svg(resultado)
    svg_path = docs_dir / "painel_exemplo.svg"
    svg_path.write_text(svg_conteudo, encoding="utf-8")
    print(f"✓ SVG gerado em: {svg_path}")

    png_path = docs_dir / "exemplo.png"
    # Renderização via Google Chrome headless
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--window-size=1440,900",
        "--default-background-color=00000000",
        f"--screenshot={png_path}",
        str(svg_path),
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if png_path.exists():
            tamanho = png_path.stat().st_size
            print(f"✓ PNG gerado com sucesso em: {png_path} ({tamanho:,} bytes)")
            return 0
        else:
            print("Erro: PNG não foi gerado pelo Chrome.", file=sys.stderr)
            return 1
    except Exception as exc:
        print(f"Aviso: Não foi possível executar Chrome headless ({exc}).", file=sys.stderr)
        return 0


if __name__ == "__main__":
    sys.exit(main())
