"""Interface de Linha de Comando (CLI) para dimensionamento de SPDA (ABNT NBR 5419:2015).

Comandos disponíveis:
  calcular       Dimensiona o SPDA a partir de arquivo de entrada JSON.
  catalogo       Exibe parâmetros, níveis de proteção e condutores normativos.
  gerar-exemplo  Gera modelo JSON canônico para testes e projetos reais.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from spda_nbr5419 import __version__
from spda_nbr5419.calculator import dimensionar_spda
from spda_nbr5419.codecs import (
    JSONCodecError,
    carregar_entrada_json,
    exportar_resultado_json,
)
from spda_nbr5419.constants import (
    CONDUTORES_NORMATIVOS,
    FATORES_COMBATE_INCENDIO_RP,
    FATORES_LOCALIZACAO_CD,
    FATORES_RISCO_INCENDIO_RF,
    NIVEIS_PROTECAO,
    TIPOS_ESTRUTURA_PADRAO,
)
from spda_nbr5419.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
)
from spda_nbr5419.svg_generator import gerar_painel_svg


def criar_parser() -> argparse.ArgumentParser:
    """Cria o analisador de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        prog="spda-nbr5419",
        description="Dimensionamento analítico de SPDA e gerenciamento de risco (ABNT NBR 5419:2015).",
    )
    parser.add_argument(
        "--versao",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Exibe a versão instalada do programa.",
    )

    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando: calcular
    parser_calc = subparsers.add_parser("calcular", help="Dimensiona o SPDA a partir de JSON.")
    parser_calc.add_argument("arquivo", type=str, help="Caminho do arquivo JSON de entrada.")
    parser_calc.add_argument(
        "--formato",
        "-f",
        choices=["texto", "json", "csv", "svg", "zip"],
        default="texto",
        help="Formato do resultado de saída (padrão: texto).",
    )
    parser_calc.add_argument(
        "--saida",
        "-o",
        type=str,
        default=None,
        help="Arquivo de destino (se omitido, imprime no terminal).",
    )
    parser_calc.add_argument(
        "--projeto",
        "-p",
        type=str,
        default="SPDA-NBR5419-001",
        help="Identificador do projeto.",
    )

    # Comando: catalogo
    parser_cat = subparsers.add_parser("catalogo", help="Exibe parâmetros normativos da NBR 5419.")
    parser_cat.add_argument(
        "--secao",
        "-s",
        choices=["todos", "niveis", "fatores", "condutores"],
        default="todos",
        help="Seção do catálogo a exibir (padrão: todos).",
    )

    # Comando: gerar-exemplo
    parser_ex = subparsers.add_parser("gerar-exemplo", help="Gera arquivo de entrada JSON de exemplo.")
    parser_ex.add_argument(
        "--tipo",
        "-t",
        choices=["predio-residencial", "escola-hospital", "galpao-industrial"],
        default="predio-residencial",
        help="Tipo de edificação para o modelo de exemplo.",
    )
    parser_ex.add_argument(
        "--saida",
        "-o",
        type=str,
        default=None,
        help="Arquivo de destino (se omitido, imprime no terminal).",
    )

    return parser


def comando_catalogo(secao: str) -> int:
    """Exibe tabelas e especificações normativas no terminal."""
    if secao in ("todos", "niveis"):
        print("=" * 70)
        print("ABNT NBR 5419:2015 · NÍVEIS DE PROTEÇÃO (NP I A NP IV)")
        print("=" * 70)
        for codigo, dados in NIVEIS_PROTECAO.items():
            print(f"Código: {codigo} | {dados['nome']}")
            print(f"  • Eficiência mínima: {dados['eficiencia_minima'] * 100}%")
            print(f"  • Raio da esfera rolante: {dados['raio_esfera_rolante_m']} m")
            print(f"  • Malha máxima (Faraday): {dados['malha_comprimento_m']}m x {dados['malha_largura_m']}m")
            print(f"  • Espaçamento médio de descidas: {dados['espacamento_descidas_m']} m")
            print(f"  • Espaçamento de anéis de equalização: {dados['espacamento_aneis_cintamento_m']} m")
            print()

    if secao in ("todos", "fatores"):
        print("=" * 70)
        print("FATORES AMBIENTAIS E DE RISCO (NBR 5419-2)")
        print("=" * 70)
        print("Fator de Localização Cd:")
        for cod, d in FATORES_LOCALIZACAO_CD.items():
            print(f"  • {cod:25}: Cd={d['fator']} ({d['descricao']})")
        print("\nFator de Risco de Incêndio rf:")
        for cod, d in FATORES_RISCO_INCENDIO_RF.items():
            print(f"  • {cod:25}: rf={d['fator']} ({d['descricao']})")
        print("\nFator de Combate a Incêndio rp:")
        for cod, d in FATORES_COMBATE_INCENDIO_RP.items():
            print(f"  • {cod:25}: rp={d['fator']} ({d['descricao']})")
        print()

    if secao in ("todos", "condutores"):
        print("=" * 70)
        print("MATERIAIS E SEÇÕES MÍNIMAS DE CONDUTORES (NBR 5419-3, TABELA 6)")
        print("=" * 70)
        for chave, c in CONDUTORES_NORMATIVOS.items():
            print(f"Item: {chave}")
            print(f"  • Material: {c['material']}")
            print(f"  • Aplicação: {c['uso']}")
            print(f"  • Seção mínima: {c['secao_minima_mm2']} mm²")
            print()

    return 0


def comando_gerar_exemplo(tipo: str, saida: str | None) -> int:
    """Gera dados de exemplo estruturados em JSON."""
    mapa_tipos = {
        "predio-residencial": {
            "nome": "Edifício Residencial Belo Horizonte",
            "comprimento_m": "32",
            "largura_m": "18",
            "altura_m": "42",
            "densidade_descargas_ng": "9",
            "localizacao_ambiental": "isolada_plano",
            "risco_incendio": "ordinario",
            "combate_incendio": "manual",
            "pessoas_em_risco": 80,
            "horas_ocupacao_ano": 8760,
            "tipo_material": "cobre",
        },
        "escola-hospital": {
            "nome": "Hospital Regional São Lucas",
            "comprimento_m": "60",
            "largura_m": "30",
            "altura_m": "24",
            "densidade_descargas_ng": "10",
            "localizacao_ambiental": "isolada_plano",
            "risco_incendio": "ordinario",
            "combate_incendio": "alarme_brigada",
            "pessoas_em_risco": 250,
            "horas_ocupacao_ano": 8760,
            "tipo_material": "cobre",
        },
        "galpao-industrial": {
            "nome": "Centro de Logística e Armazenagem",
            "comprimento_m": "100",
            "largura_m": "50",
            "altura_m": "14",
            "densidade_descargas_ng": "8",
            "localizacao_ambiental": "cercada_mesma_altura",
            "risco_incendio": "explosivo",
            "combate_incendio": "sprinklers",
            "pessoas_em_risco": 40,
            "horas_ocupacao_ano": 4000,
            "tipo_material": "aluminio",
        },
    }

    import json
    dados = mapa_tipos.get(tipo, mapa_tipos["predio-residencial"])
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"

    if saida:
        Path(saida).write_text(conteudo, encoding="utf-8")
        print(f"Exemplo JSON salvo com sucesso em: {saida}")
    else:
        print(conteudo, end="")

    return 0


def comando_calcular(arquivo: str, formato: str, saida: str | None, projeto: str) -> int:
    """Executa a rotina analítica de dimensionamento."""
    caminho = Path(arquivo)
    if not caminho.exists():
        sys.stderr.write(f"Erro: Arquivo de entrada inexistente: {arquivo}\n")
        return 1

    try:
        conteudo_bytes = caminho.read_bytes()
        estrutura = carregar_entrada_json(conteudo_bytes)
        resultado = dimensionar_spda(estrutura, identificador_projeto=projeto)

        if formato == "texto":
            texto = gerar_relatorio_texto(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Relatório técnico salvo em: {saida}")
            else:
                print(texto, end="")
        elif formato == "json":
            texto = exportar_resultado_json(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Resultado JSON salvo em: {saida}")
            else:
                print(texto)
        elif formato == "csv":
            texto = gerar_csv_sanitizado(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Dados CSV salvos em: {saida}")
            else:
                print(texto, end="")
        elif formato == "svg":
            texto = gerar_painel_svg(resultado)
            if saida:
                Path(saida).write_text(texto, encoding="utf-8")
                print(f"Painel vetorial SVG salvo em: {saida}")
            else:
                print(texto, end="")
        elif formato == "zip":
            if not saida:
                sys.stderr.write("Erro: Parâmetro --saida é obrigatório para exportação em formato ZIP.\n")
                return 1
            gerar_pacote_zip_deterministico(resultado, saida)
            print(f"Pacote determinístico ZIP salvo em: {saida}")

        return 0

    except JSONCodecError as exc:
        sys.stderr.write(f"Erro de conformidade JSON: {exc}\n")
        return 2
    except Exception as exc:
        sys.stderr.write(f"Erro no processamento do dimensionamento: {exc}\n")
        return 3


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada principal da CLI."""
    parser = criar_parser()
    args = parser.parse_args(argv)

    if not args.comando:
        parser.print_help()
        return 0

    if args.comando == "catalogo":
        return comando_catalogo(args.secao)
    elif args.comando == "gerar-exemplo":
        return comando_gerar_exemplo(args.tipo, args.saida)
    elif args.comando == "calcular":
        return comando_calcular(args.arquivo, args.formato, args.saida, args.projeto)

    return 0


if __name__ == "__main__":
    sys.exit(main())
