"""Modelos de dados imutáveis para dimensionamento de SPDA segundo a ABNT NBR 5419:2015.

Todas as classes utilizam dataclasses imutáveis (frozen=True) e tipos puramente
racionais (Fraction) ou inteiros, eliminando ponto flutuante em conformidade
com os padrões de engenharia da Lofrano Tecnologia.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Optional


@dataclass(frozen=True)
class Estrutura:
    """Parâmetros físicos e ambientais de uma edificação para análise de SPDA."""

    nome: str
    comprimento_m: Fraction
    largura_m: Fraction
    altura_m: Fraction
    densidade_descargas_ng: Fraction  # raios / km² / ano
    localizacao_ambiental: str        # chave em FATORES_LOCALIZACAO_CD
    risco_incendio: str               # chave em FATORES_RISCO_INCENDIO_RF
    combate_incendio: str             # chave em FATORES_COMBATE_INCENDIO_RP
    pessoas_em_risco: int
    horas_ocupacao_ano: int           # até 8760 h
    tipo_material: str                # "cobre", "aluminio" ou "aco_galvanizado"
    nivel_protecao_forcado: Optional[str] = None  # força nível específico se desejado

    def __post_init__(self) -> None:
        if self.comprimento_m <= 0:
            raise ValueError("O comprimento da estrutura deve ser positivo.")
        if self.largura_m <= 0:
            raise ValueError("A largura da estrutura deve ser positiva.")
        if self.altura_m <= 0:
            raise ValueError("A altura da estrutura deve ser positiva.")
        if self.densidade_descargas_ng <= 0:
            raise ValueError("A densidade de descargas Ng deve ser positiva.")
        if self.pessoas_em_risco < 0:
            raise ValueError("O número de pessoas em risco não pode ser negativo.")
        if not (0 <= self.horas_ocupacao_ano <= 8760):
            raise ValueError("As horas de ocupação anual devem estar no intervalo [0, 8760].")


@dataclass(frozen=True)
class AreaExposicaoEquivalente:
    """Área de exposição equivalente Ad conforme ABNT NBR 5419-2:2015 (Anexo A)."""

    area_cobertura_m2: Fraction
    perimetro_m: Fraction
    largura_faixa_protecao_m: Fraction  # 3 * H
    area_lateral_m2: Fraction           # 2 * 3H * (L + W)
    area_cantos_m2: Fraction            # pi * (3H)^2
    area_total_ad_m2: Fraction


@dataclass(frozen=True)
class GerenciamentoRisco:
    """Avaliação de risco R1 (perda de vidas humanas) e necessidade de SPDA."""

    fator_cd: Fraction
    numero_eventos_nd: Fraction
    fator_rf: Fraction
    fator_rp: Fraction
    perda_tipica_lt: Fraction
    risco_r1_sem_spda: Fraction
    risco_toleravel_rt: Fraction
    necessidade_spda: bool
    nivel_protecao_adotado: str
    probabilidade_pb_adotada: Fraction
    risco_r1_com_spda: Fraction
    reducao_risco_percentual: Fraction


@dataclass(frozen=True)
class DimensionamentoCaptacao:
    """Subsistema de captação conforme ABNT NBR 5419-3:2015."""

    metodo_principal: str
    nivel_protecao: str
    raio_esfera_m: int
    malha_maxima_comprimento_m: int
    malha_maxima_largura_m: int
    quantidade_modulos_comprimento: int
    quantidade_modulos_largura: int
    total_modulos_malha: int
    comprimento_cabos_captor_m: Fraction
    material_captor: str
    secao_minima_captor_mm2: int


@dataclass(frozen=True)
class DimensionamentoDescidas:
    """Subsistema de condutores de descida e anéis de cintamento."""

    espacamento_maximo_descidas_m: int
    perimetro_edificacao_m: Fraction
    numero_minimo_descidas: int
    numero_descidas_adotado: int
    espacamento_real_descidas_m: Fraction
    quantidade_aneis_cintamento: int
    alturas_aneis_cintamento_m: tuple[Fraction, ...]
    comprimento_cabos_descida_m: Fraction
    material_descida: str
    secao_minima_descida_mm2: int


@dataclass(frozen=True)
class DimensionamentoAterramento:
    """Subsistema de aterramento (eletrodo em anel tipo B e hastes de inspeção)."""

    tipo_eletrodo: str
    perimetro_anel_m: Fraction
    profundidade_minima_m: Fraction
    numero_hastes_inspecao: int
    comprimento_total_eletrodo_m: Fraction
    material_aterramento: str
    secao_minima_aterramento_mm2: int


@dataclass(frozen=True)
class ResultadoDimensionamentoSPDA:
    """Resultado analítico global do dimensionamento de SPDA conforme ABNT NBR 5419:2015."""

    identificador_projeto: str
    estrutura: Estrutura
    area_exposicao: AreaExposicaoEquivalente
    risco: GerenciamentoRisco
    captacao: DimensionamentoCaptacao
    descidas: DimensionamentoDescidas
    aterramento: DimensionamentoAterramento
    comprimento_total_cabos_obra_m: Fraction
    conclusao_tecnica: str
    spda_conforme: bool
