"""Motor analítico e CLI para dimensionamento de SPDA segundo a ABNT NBR 5419:2015.

Padrão de Engenharia LOFRANO TECNOLOGIA:
- Zero dependências de terceiros (100% biblioteca padrão do Python 3.11+).
- Aritmética racional exata com Fraction e grandezas inteiras (zero ponto flutuante).
- Gerenciamento de risco R1, captação, descidas, anéis e aterramento perimetral.
"""

from __future__ import annotations

from spda_nbr5419.calculator import (
    avaliar_gerenciamento_risco,
    calcular_area_exposicao_equivalente,
    dimensionar_aterramento,
    dimensionar_captacao,
    dimensionar_descidas,
    dimensionar_spda,
)
from spda_nbr5419.codecs import (
    carregar_entrada_json,
    exportar_resultado_json,
    fracao_para_dict,
    parsear_fracao_segura,
)
from spda_nbr5419.constants import (
    CONDUTORES_NORMATIVOS,
    FATORES_COMBATE_INCENDIO_RP,
    FATORES_LOCALIZACAO_CD,
    FATORES_RISCO_INCENDIO_RF,
    NIVEIS_PROTECAO,
    PI_RACIONAL,
    RISCO_TOLERAVEL_R1,
)
from spda_nbr5419.exporters import (
    gerar_csv_sanitizado,
    gerar_pacote_zip_deterministico,
    gerar_relatorio_texto,
    sanitizar_campo_csv,
)
from spda_nbr5419.models import (
    AreaExposicaoEquivalente,
    DimensionamentoAterramento,
    DimensionamentoCaptacao,
    DimensionamentoDescidas,
    Estrutura,
    GerenciamentoRisco,
    ResultadoDimensionamentoSPDA,
)
from spda_nbr5419.svg_generator import gerar_painel_svg

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "AreaExposicaoEquivalente",
    "CONDUTORES_NORMATIVOS",
    "DimensionamentoAterramento",
    "DimensionamentoCaptacao",
    "DimensionamentoDescidas",
    "Estrutura",
    "FATORES_COMBATE_INCENDIO_RP",
    "FATORES_LOCALIZACAO_CD",
    "FATORES_RISCO_INCENDIO_RF",
    "GerenciamentoRisco",
    "NIVEIS_PROTECAO",
    "PI_RACIONAL",
    "RISCO_TOLERAVEL_R1",
    "ResultadoDimensionamentoSPDA",
    "avaliar_gerenciamento_risco",
    "calcular_area_exposicao_equivalente",
    "carregar_entrada_json",
    "dimensionar_aterramento",
    "dimensionar_captacao",
    "dimensionar_descidas",
    "dimensionar_spda",
    "exportar_resultado_json",
    "fracao_para_dict",
    "gerar_csv_sanitizado",
    "gerar_pacote_zip_deterministico",
    "gerar_painel_svg",
    "gerar_relatorio_texto",
    "parsear_fracao_segura",
    "sanitizar_campo_csv",
]
