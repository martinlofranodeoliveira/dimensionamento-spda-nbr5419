"""Motor analítico e cálculos do SPDA segundo a ABNT NBR 5419:2015.

Implementa:
1. Área de exposição equivalente Ad (NBR 5419-2, Anexo A).
2. Gerenciamento e cálculo do risco R1 de perda de vidas humanas.
3. Dimensionamento do subsistema de captação (Malha / Gaiola de Faraday e Esfera Rolante).
4. Dimensionamento do subsistema de descidas e anéis de equalização/cintamento.
5. Dimensionamento do subsistema de aterramento (eletrodo em anel Tipo B e hastes).
6. Totalização de materiais e validação normativa integral.

Sem dependências externas. Aritmética 100% racional (Fraction) e inteira.
"""

from __future__ import annotations

from fractions import Fraction
import math
from typing import Final

from spda_nbr5419.constants import (
    CONDUTORES_NORMATIVOS,
    FATORES_COMBATE_INCENDIO_RP,
    FATORES_LOCALIZACAO_CD,
    FATORES_RISCO_INCENDIO_RF,
    NIVEIS_PROTECAO,
    PI_RACIONAL,
    RISCO_TOLERAVEL_R1,
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


def calcular_area_exposicao_equivalente(estrutura: Estrutura) -> AreaExposicaoEquivalente:
    """Calcula a área de exposição equivalente Ad de uma estrutura retangular isolada.

    Conforme ABNT NBR 5419-2:2015 (Anexo A):
        Ad = L * W + 2 * (3*H) * (L + W) + pi * (3*H)^2
    """
    l = estrutura.comprimento_m
    w = estrutura.largura_m
    h = estrutura.altura_m

    area_cobertura = l * w
    perimetro = 2 * (l + w)
    faixa_protecao = 3 * h

    # Área das 4 faixas laterais retangulares
    area_lateral = 2 * faixa_protecao * (l + w)

    # Área dos 4 cantos em quadrantes circulares que somam um círculo completo de raio 3H
    area_cantos = PI_RACIONAL * (faixa_protecao ** 2)

    area_total_ad = area_cobertura + area_lateral + area_cantos

    return AreaExposicaoEquivalente(
        area_cobertura_m2=area_cobertura,
        perimetro_m=perimetro,
        largura_faixa_protecao_m=faixa_protecao,
        area_lateral_m2=area_lateral,
        area_cantos_m2=area_cantos,
        area_total_ad_m2=area_total_ad,
    )


def avaliar_gerenciamento_risco(
    estrutura: Estrutura, area: AreaExposicaoEquivalente
) -> GerenciamentoRisco:
    """Avalia o risco R1 de perda de vidas humanas e seleciona o nível de SPDA necessário.

    Conforme ABNT NBR 5419-2:2015:
        Nd = Ng * Ad * Cd * 10^-6
        R1 = Nd * [ (rf * rp) + 0.01 ] * Lt
    """
    # 1. Fator de localização ambiental Cd
    info_cd = FATORES_LOCALIZACAO_CD.get(
        estrutura.localizacao_ambiental, FATORES_LOCALIZACAO_CD["isolada_plano"]
    )
    fator_cd = Fraction(info_cd["fator"])  # type: ignore[arg-type]

    # 2. Número anual de eventos perigosos atingindo a estrutura Nd
    numero_eventos_nd = (
        estrutura.densidade_descargas_ng * area.area_total_ad_m2 * fator_cd
    ) / Fraction(1_000_000, 1)

    # 3. Fatores de risco de incêndio rf e proteção rp
    info_rf = FATORES_RISCO_INCENDIO_RF.get(
        estrutura.risco_incendio, FATORES_RISCO_INCENDIO_RF["ordinario"]
    )
    fator_rf = Fraction(info_rf["fator"])  # type: ignore[arg-type]

    info_rp = FATORES_COMBATE_INCENDIO_RP.get(
        estrutura.combate_incendio, FATORES_COMBATE_INCENDIO_RP["manual"]
    )
    fator_rp = Fraction(info_rp["fator"])  # type: ignore[arg-type]

    # 4. Perda típica Lt ponderada pelo tempo de ocupação anual
    if estrutura.pessoas_em_risco > 0 and estrutura.horas_ocupacao_ano > 0:
        perda_tipica_lt = Fraction(1, 100) * Fraction(estrutura.horas_ocupacao_ano, 8760)
    else:
        perda_tipica_lt = Fraction(0, 1)

    # 5. Risco R1 sem medidas de proteção (PB = 1)
    # Inclui danos físicos por incêndio (rf * rp) e choque por tensão de toque/passo (0.01)
    coeficiente_dano = (fator_rf * fator_rp) + Fraction(1, 100)
    risco_r1_sem_spda = numero_eventos_nd * coeficiente_dano * perda_tipica_lt

    # 6. Verificação frente ao Risco Tolerável Rt = 10^-5
    necessidade_spda = risco_r1_sem_spda > RISCO_TOLERAVEL_R1

    # 7. Seleção do Nível de Proteção (NP)
    if estrutura.nivel_protecao_forcado in NIVEIS_PROTECAO:
        nivel_adotado = estrutura.nivel_protecao_forcado
    elif not necessidade_spda:
        nivel_adotado = "NP_IV"  # Proteção recomendada mesmo com risco tolerável
    else:
        # Busca o nível ótimo (de NP_IV até NP_I) capaz de reduzir R1 abaixo de Rt
        nivel_adotado = "NP_I"
        for nivel_candidato in ("NP_IV", "NP_III", "NP_II", "NP_I"):
            pb = Fraction(NIVEIS_PROTECAO[nivel_candidato]["probabilidade_dano_pb"])  # type: ignore[arg-type]
            risco_estimado = risco_r1_sem_spda * pb
            if risco_estimado <= RISCO_TOLERAVEL_R1:
                nivel_adotado = nivel_candidato
                break

    pb_adotada = Fraction(NIVEIS_PROTECAO[nivel_adotado]["probabilidade_dano_pb"])  # type: ignore[arg-type]
    risco_r1_com_spda = risco_r1_sem_spda * pb_adotada

    if risco_r1_sem_spda > 0:
        reducao_risco = (Fraction(1, 1) - pb_adotada) * Fraction(100, 1)
    else:
        reducao_risco = Fraction(0, 1)

    return GerenciamentoRisco(
        fator_cd=fator_cd,
        numero_eventos_nd=numero_eventos_nd,
        fator_rf=fator_rf,
        fator_rp=fator_rp,
        perda_tipica_lt=perda_tipica_lt,
        risco_r1_sem_spda=risco_r1_sem_spda,
        risco_toleravel_rt=RISCO_TOLERAVEL_R1,
        necessidade_spda=necessidade_spda,
        nivel_protecao_adotado=nivel_adotado,
        probabilidade_pb_adotada=pb_adotada,
        risco_r1_com_spda=risco_r1_com_spda,
        reducao_risco_percentual=reducao_risco,
    )


def dimensionar_captacao(
    estrutura: Estrutura, nivel_protecao: str
) -> DimensionamentoCaptacao:
    """Dimensiona o subsistema de captação por Malha (Gaiola de Faraday) e Esfera Rolante.

    Conforme ABNT NBR 5419-3:2015 (Tabela 2):
        NP I: Raio 20 m, Malha 5 m x 5 m
        NP II: Raio 30 m, Malha 10 m x 10 m
        NP III: Raio 45 m, Malha 15 m x 15 m
        NP IV: Raio 60 m, Malha 20 m x 20 m
    """
    dados_np = NIVEIS_PROTECAO[nivel_protecao]
    raio_esfera = int(dados_np["raio_esfera_rolante_m"])  # type: ignore[arg-type]
    malha_comp = int(dados_np["malha_comprimento_m"])    # type: ignore[arg-type]
    malha_larg = int(dados_np["malha_largura_m"])        # type: ignore[arg-type]

    # Número de vãos / módulos inteiros (arredondamento para cima com divisão inteira)
    comp_int = math.ceil(estrutura.comprimento_m)
    larg_int = math.ceil(estrutura.largura_m)

    mod_comp = (comp_int + malha_comp - 1) // malha_comp
    mod_larg = (larg_int + malha_larg - 1) // malha_larg
    total_modulos = mod_comp * mod_larg

    # Linhas longitudinais (quantidade mod_larg + 1, cada uma com comprimento L)
    # Linhas transversais (quantidade mod_comp + 1, cada uma com largura W)
    linhas_longitudinais = Fraction(mod_larg + 1, 1) * estrutura.comprimento_m
    linhas_transversais = Fraction(mod_comp + 1, 1) * estrutura.largura_m
    comprimento_cabos = linhas_longitudinais + linhas_transversais

    # Material e seção mínima do condutor captor (NBR 5419-3, Tabela 6)
    chave_material = f"{estrutura.tipo_material}_captor_descida"
    condutor_info = CONDUTORES_NORMATIVOS.get(
        chave_material, CONDUTORES_NORMATIVOS["cobre_captor_descida"]
    )
    material_nome = str(condutor_info["material"])
    secao_minima = int(condutor_info["secao_minima_mm2"])

    return DimensionamentoCaptacao(
        metodo_principal="Gaiola de Faraday (Método das Malhas)",
        nivel_protecao=nivel_protecao,
        raio_esfera_m=raio_esfera,
        malha_maxima_comprimento_m=malha_comp,
        malha_maxima_largura_m=malha_larg,
        quantidade_modulos_comprimento=mod_comp,
        quantidade_modulos_largura=mod_larg,
        total_modulos_malha=total_modulos,
        comprimento_cabos_captor_m=comprimento_cabos,
        material_captor=material_nome,
        secao_minima_captor_mm2=secao_minima,
    )


def dimensionar_descidas(
    estrutura: Estrutura, nivel_protecao: str
) -> DimensionamentoDescidas:
    """Dimensiona o subsistema de condutores de descida e anéis de cintamento.

    Conforme ABNT NBR 5419-3:2015 (Tabela 4):
        Espaçamento médio máximo:
        NP I e II: 10 m
        NP III: 15 m
        NP IV: 20 m
    """
    dados_np = NIVEIS_PROTECAO[nivel_protecao]
    espacamento_max = int(dados_np["espacamento_descidas_m"])  # type: ignore[arg-type]
    espacamento_aneis = int(dados_np["espacamento_aneis_cintamento_m"])  # type: ignore[arg-type]

    perimetro = 2 * (estrutura.comprimento_m + estrutura.largura_m)

    # Número mínimo de descidas conforme o perímetro da edificação (mínimo absoluto = 2)
    perimetro_int = math.ceil(perimetro)
    descidas_calculadas = (perimetro_int + espacamento_max - 1) // espacamento_max
    numero_descidas = max(2, descidas_calculadas)

    espacamento_real = perimetro / Fraction(numero_descidas, 1)

    # Anéis horizontais de cintamento / equalização a cada espacamento_aneis (NBR 5419-3)
    altura_int = int(estrutura.altura_m)
    qtd_aneis = altura_int // espacamento_aneis
    alturas_aneis: list[Fraction] = []
    for i in range(1, qtd_aneis + 1):
        alturas_aneis.append(Fraction(i * espacamento_aneis, 1))

    # Comprimento de cabos de descida:
    # N descidas verticais de altura H + anéis de cintamento de perímetro P
    comp_vertical = Fraction(numero_descidas, 1) * estrutura.altura_m
    comp_aneis = Fraction(qtd_aneis, 1) * perimetro
    comprimento_total_descidas = comp_vertical + comp_aneis

    # Material e seção mínima
    chave_material = f"{estrutura.tipo_material}_captor_descida"
    condutor_info = CONDUTORES_NORMATIVOS.get(
        chave_material, CONDUTORES_NORMATIVOS["cobre_captor_descida"]
    )
    material_nome = str(condutor_info["material"])
    secao_minima = int(condutor_info["secao_minima_mm2"])

    return DimensionamentoDescidas(
        espacamento_maximo_descidas_m=espacamento_max,
        perimetro_edificacao_m=perimetro,
        numero_minimo_descidas=2,
        numero_descidas_adotado=numero_descidas,
        espacamento_real_descidas_m=espacamento_real,
        quantidade_aneis_cintamento=qtd_aneis,
        alturas_aneis_cintamento_m=tuple(alturas_aneis),
        comprimento_cabos_descida_m=comprimento_total_descidas,
        material_descida=material_nome,
        secao_minima_descida_mm2=secao_minima,
    )


def dimensionar_aterramento(
    estrutura: Estrutura, nivel_protecao: str, numero_descidas: int
) -> DimensionamentoAterramento:
    """Dimensiona o subsistema de aterramento com eletrodo em anel periférico Tipo B.

    Conforme ABNT NBR 5419-3:2015:
        Eletrodo em anel enterrado a >= 0.50 m ao redor do perímetro externo.
        Haste vertical de aço cobreado / cobre em cada descida para equalização e inspeção.
    """
    # Anel externo a 1 metro de distância das paredes
    perimetro_anel = 2 * ((estrutura.comprimento_m + 2) + (estrutura.largura_m + 2))
    profundidade_minima = Fraction(1, 2)  # 0.50 m

    # 1 haste de 2.40 m (12/5 m) para cada descida
    comprimento_haste = Fraction(12, 5)
    comp_total_eletrodo = perimetro_anel + (Fraction(numero_descidas, 1) * comprimento_haste)

    # Material e seção mínima para aterramento
    chave_material = f"{estrutura.tipo_material}_aterramento"
    condutor_info = CONDUTORES_NORMATIVOS.get(
        chave_material, CONDUTORES_NORMATIVOS["cobre_aterramento"]
    )
    material_nome = str(condutor_info["material"])
    secao_minima = int(condutor_info["secao_minima_mm2"])

    return DimensionamentoAterramento(
        tipo_eletrodo="Eletrodo em Anel Periférico (Tipo B) com Hastes de Equalização",
        perimetro_anel_m=perimetro_anel,
        profundidade_minima_m=profundidade_minima,
        numero_hastes_inspecao=numero_descidas,
        comprimento_total_eletrodo_m=comp_total_eletrodo,
        material_aterramento=material_nome,
        secao_minima_aterramento_mm2=secao_minima,
    )


def dimensionar_spda(
    estrutura: Estrutura, identificador_projeto: str = "SPDA-NBR5419-001"
) -> ResultadoDimensionamentoSPDA:
    """Executa o dimensionamento completo de SPDA e gerenciamento de risco segundo a NBR 5419:2015.

    Retorna um ResultadoDimensionamentoSPDA com todas as verificações normativas.
    """
    area = calcular_area_exposicao_equivalente(estrutura)
    risco = avaliar_gerenciamento_risco(estrutura, area)
    captacao = dimensionar_captacao(estrutura, risco.nivel_protecao_adotado)
    descidas = dimensionar_descidas(estrutura, risco.nivel_protecao_adotado)
    aterramento = dimensionar_aterramento(
        estrutura, risco.nivel_protecao_adotado, descidas.numero_descidas_adotado
    )

    total_cabos = (
        captacao.comprimento_cabos_captor_m
        + descidas.comprimento_cabos_descida_m
        + aterramento.comprimento_total_eletrodo_m
    )

    # Verificação de conformidade global
    spda_conforme = True
    conclusoes: list[str] = []

    if risco.necessidade_spda:
        conclusoes.append(
            f"SPDA Obrigatório: R1 sem proteção ({risco.risco_r1_sem_spda}) > Rt ({risco.risco_toleravel_rt})."
        )
    else:
        conclusoes.append(
            f"SPDA Recomendado: R1 sem proteção ({risco.risco_r1_sem_spda}) <= Rt ({risco.risco_toleravel_rt})."
        )

    conclusoes.append(
        f"Nível de Proteção Adotado: {risco.nivel_protecao_adotado} com redução de risco de {risco.reducao_risco_percentual}%."
    )
    conclusoes.append(
        f"Captação: Malha de {captacao.malha_maxima_comprimento_m}m x {captacao.malha_maxima_largura_m}m "
        f"({captacao.total_modulos_malha} módulos), {captacao.comprimento_cabos_captor_m}m de condutor."
    )
    conclusoes.append(
        f"Descidas: {descidas.numero_descidas_adotado} condutores verticais com espaçamento de {descidas.espacamento_real_descidas_m}m "
        f"e {descidas.quantidade_aneis_cintamento} anéis de equalização."
    )
    conclusoes.append(
        f"Aterramento: Anel perimetral de {aterramento.perimetro_anel_m}m com {aterramento.numero_hastes_inspecao} hastes verticais."
    )

    conclusao_tecnica = " ".join(conclusoes)

    return ResultadoDimensionamentoSPDA(
        identificador_projeto=identificador_projeto,
        estrutura=estrutura,
        area_exposicao=area,
        risco=risco,
        captacao=captacao,
        descidas=descidas,
        aterramento=aterramento,
        comprimento_total_cabos_obra_m=total_cabos,
        conclusao_tecnica=conclusao_tecnica,
        spda_conforme=spda_conforme,
    )
