"""Codecs canônicos RFC 8259 e serialização segura para o projeto SPDA NBR 5419.

Garante:
1. Rejeição de marcas de ordem de byte (BOM UTF-8: \\xef\\xbb\\xbf / \\ufeff).
2. Rejeição estrita de números de ponto flutuante (proibição de float).
3. Rejeição de chaves duplicadas em objetos JSON.
4. Limite de profundidade de aninhamento (máximo 32 níveis).
5. Conversão bidirecional de grandezas racionais exatas (Fraction).
"""

from __future__ import annotations

from fractions import Fraction
import json
from typing import Any

from spda_nbr5419.models import (
    AreaExposicaoEquivalente,
    DimensionamentoAterramento,
    DimensionamentoCaptacao,
    DimensionamentoDescidas,
    Estrutura,
    GerenciamentoRisco,
    ResultadoDimensionamentoSPDA,
)

PROFUNDIDADE_MAXIMA_PERMITIDA = 32


class JSONCodecError(ValueError):
    """Erro em caso de violação de conformidade com o codec JSON canônico."""


def _verificar_profundidade(obj: Any, nivel_atual: int = 1) -> None:
    if nivel_atual > PROFUNDIDADE_MAXIMA_PERMITIDA:
        raise JSONCodecError(
            f"Profundidade excessiva de aninhamento ({nivel_atual} > {PROFUNDIDADE_MAXIMA_PERMITIDA})."
        )
    if isinstance(obj, dict):
        for valor in obj.values():
            _verificar_profundidade(valor, nivel_atual + 1)
    elif isinstance(obj, list):
        for item in obj:
            _verificar_profundidade(item, nivel_atual + 1)


def _rejeitar_float(valor: str) -> None:
    raise JSONCodecError(
        f"Ponto flutuante proibido pelo padrão de engenharia LOFRANO TECNOLOGIA: {valor!r}. "
        "Utilize inteiros ou frações exatas (ex: '25/2' ou {'num': 25, 'den': 2})."
    )


def _object_pairs_hook_sem_duplicatas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    resultado: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in resultado:
            raise JSONCodecError(f"Chave duplicada proibida no JSON: {chave!r}")
        resultado[chave] = valor
    return resultado


def parsear_fracao_segura(valor: Any) -> Fraction:
    """Converte int, str fracionária ('1/2') ou dict ({'num': 1, 'den': 2}) em Fraction."""
    if isinstance(valor, Fraction):
        return valor
    if isinstance(valor, int):
        return Fraction(valor, 1)
    if isinstance(valor, str):
        if "/" in valor:
            partes = valor.split("/")
            if len(partes) == 2 and partes[0].strip().lstrip("-").isdigit() and partes[1].strip().isdigit():
                return Fraction(int(partes[0].strip()), int(partes[1].strip()))
        if valor.strip().lstrip("-").isdigit():
            return Fraction(int(valor.strip()), 1)
        raise JSONCodecError(f"Formato de string fracionária inválido: {valor!r}")
    if isinstance(valor, dict) and "num" in valor and "den" in valor:
        num = valor["num"]
        den = valor["den"]
        if isinstance(num, int) and isinstance(den, int) and den != 0:
            return Fraction(num, den)
        raise JSONCodecError(f"Dicionário de fração com valores não inteiros: {valor!r}")
    raise JSONCodecError(f"Tipo não conversível em Fraction exata: {type(valor)} ({valor!r})")


def fracao_para_dict(fracao: Fraction) -> dict[str, int | str]:
    """Serializa Fraction em formato canônico com numerador, denominador e representação."""
    return {
        "num": fracao.numerator,
        "den": fracao.denominator,
        "str": f"{fracao.numerator}/{fracao.denominator}" if fracao.denominator != 1 else str(fracao.numerator),
    }


def carregar_entrada_json(conteudo: str | bytes) -> Estrutura:
    """Carrega dados de entrada de uma estrutura rejeitando BOM, floats e duplicatas."""
    if isinstance(conteudo, bytes):
        if conteudo.startswith(b"\xef\xbb\xbf"):
            raise JSONCodecError("Marca de ordem de byte (BOM) UTF-8 rejeitada na entrada.")
        texto = conteudo.decode("utf-8")
    else:
        if conteudo.startswith("\ufeff"):
            raise JSONCodecError("Marca de ordem de byte (BOM) rejeitada na entrada.")
        texto = conteudo

    dados = json.loads(
        texto,
        object_pairs_hook=_object_pairs_hook_sem_duplicatas,
        parse_float=_rejeitar_float,
    )
    _verificar_profundidade(dados)

    if not isinstance(dados, dict):
        raise JSONCodecError("A raiz do JSON de entrada deve ser um objeto dicionário.")

    campos_obrigatorios = (
        "nome",
        "comprimento_m",
        "largura_m",
        "altura_m",
        "densidade_descargas_ng",
    )
    for campo in campos_obrigatorios:
        if campo not in dados:
            raise JSONCodecError(f"Campo obrigatório ausente no JSON: {campo!r}")

    nome = str(dados["nome"])
    comprimento = parsear_fracao_segura(dados["comprimento_m"])
    largura = parsear_fracao_segura(dados["largura_m"])
    altura = parsear_fracao_segura(dados["altura_m"])
    ng = parsear_fracao_segura(dados["densidade_descargas_ng"])

    localizacao = str(dados.get("localizacao_ambiental", "isolada_plano"))
    risco_incendio = str(dados.get("risco_incendio", "ordinario"))
    combate_incendio = str(dados.get("combate_incendio", "manual"))
    pessoas_em_risco = int(dados.get("pessoas_em_risco", 50))
    horas_ocupacao = int(dados.get("horas_ocupacao_ano", 8760))
    tipo_material = str(dados.get("tipo_material", "cobre"))
    nivel_forcado = dados.get("nivel_protecao_forcado")
    if nivel_forcado is not None:
        nivel_forcado = str(nivel_forcado)

    return Estrutura(
        nome=nome,
        comprimento_m=comprimento,
        largura_m=largura,
        altura_m=altura,
        densidade_descargas_ng=ng,
        localizacao_ambiental=localizacao,
        risco_incendio=risco_incendio,
        combate_incendio=combate_incendio,
        pessoas_em_risco=pessoas_em_risco,
        horas_ocupacao_ano=horas_ocupacao,
        tipo_material=tipo_material,
        nivel_protecao_forcado=nivel_forcado,
    )


def exportar_resultado_json(resultado: ResultadoDimensionamentoSPDA) -> str:
    """Serializa ResultadoDimensionamentoSPDA em JSON canônico formatado."""
    dict_resultado: dict[str, Any] = {
        "norma_referencia": "ABNT NBR 5419:2015 (Partes 1 a 4)",
        "padrao_engenharia": "LOFRANO TECNOLOGIA",
        "identificador_projeto": resultado.identificador_projeto,
        "conforme": resultado.spda_conforme,
        "conclusao_tecnica": resultado.conclusao_tecnica,
        "estrutura": {
            "nome": resultado.estrutura.nome,
            "comprimento_m": fracao_para_dict(resultado.estrutura.comprimento_m),
            "largura_m": fracao_para_dict(resultado.estrutura.largura_m),
            "altura_m": fracao_para_dict(resultado.estrutura.altura_m),
            "densidade_descargas_ng": fracao_para_dict(resultado.estrutura.densidade_descargas_ng),
            "localizacao_ambiental": resultado.estrutura.localizacao_ambiental,
            "risco_incendio": resultado.estrutura.risco_incendio,
            "combate_incendio": resultado.estrutura.combate_incendio,
            "pessoas_em_risco": resultado.estrutura.pessoas_em_risco,
            "horas_ocupacao_ano": resultado.estrutura.horas_ocupacao_ano,
            "tipo_material": resultado.estrutura.tipo_material,
        },
        "area_exposicao": {
            "area_cobertura_m2": fracao_para_dict(resultado.area_exposicao.area_cobertura_m2),
            "perimetro_m": fracao_para_dict(resultado.area_exposicao.perimetro_m),
            "largura_faixa_protecao_m": fracao_para_dict(resultado.area_exposicao.largura_faixa_protecao_m),
            "area_lateral_m2": fracao_para_dict(resultado.area_exposicao.area_lateral_m2),
            "area_cantos_m2": fracao_para_dict(resultado.area_exposicao.area_cantos_m2),
            "area_total_ad_m2": fracao_para_dict(resultado.area_exposicao.area_total_ad_m2),
        },
        "gerenciamento_risco": {
            "fator_cd": fracao_para_dict(resultado.risco.fator_cd),
            "numero_eventos_nd": fracao_para_dict(resultado.risco.numero_eventos_nd),
            "fator_rf": fracao_para_dict(resultado.risco.fator_rf),
            "fator_rp": fracao_para_dict(resultado.risco.fator_rp),
            "perda_tipica_lt": fracao_para_dict(resultado.risco.perda_tipica_lt),
            "risco_r1_sem_spda": fracao_para_dict(resultado.risco.risco_r1_sem_spda),
            "risco_toleravel_rt": fracao_para_dict(resultado.risco.risco_toleravel_rt),
            "necessidade_spda": resultado.risco.necessidade_spda,
            "nivel_protecao_adotado": resultado.risco.nivel_protecao_adotado,
            "probabilidade_pb_adotada": fracao_para_dict(resultado.risco.probabilidade_pb_adotada),
            "risco_r1_com_spda": fracao_para_dict(resultado.risco.risco_r1_com_spda),
            "reducao_risco_percentual": fracao_para_dict(resultado.risco.reducao_risco_percentual),
        },
        "captacao": {
            "metodo_principal": resultado.captacao.metodo_principal,
            "nivel_protecao": resultado.captacao.nivel_protecao,
            "raio_esfera_m": resultado.captacao.raio_esfera_m,
            "malha_maxima_comprimento_m": resultado.captacao.malha_maxima_comprimento_m,
            "malha_maxima_largura_m": resultado.captacao.malha_maxima_largura_m,
            "quantidade_modulos_comprimento": resultado.captacao.quantidade_modulos_comprimento,
            "quantidade_modulos_largura": resultado.captacao.quantidade_modulos_largura,
            "total_modulos_malha": resultado.captacao.total_modulos_malha,
            "comprimento_cabos_captor_m": fracao_para_dict(resultado.captacao.comprimento_cabos_captor_m),
            "material_captor": resultado.captacao.material_captor,
            "secao_minima_captor_mm2": resultado.captacao.secao_minima_captor_mm2,
        },
        "descidas": {
            "espacamento_maximo_descidas_m": resultado.descidas.espacamento_maximo_descidas_m,
            "perimetro_edificacao_m": fracao_para_dict(resultado.descidas.perimetro_edificacao_m),
            "numero_minimo_descidas": resultado.descidas.numero_minimo_descidas,
            "numero_descidas_adotado": resultado.descidas.numero_descidas_adotado,
            "espacamento_real_descidas_m": fracao_para_dict(resultado.descidas.espacamento_real_descidas_m),
            "quantidade_aneis_cintamento": resultado.descidas.quantidade_aneis_cintamento,
            "alturas_aneis_cintamento_m": [fracao_para_dict(h) for h in resultado.descidas.alturas_aneis_cintamento_m],
            "comprimento_cabos_descida_m": fracao_para_dict(resultado.descidas.comprimento_cabos_descida_m),
            "material_descida": resultado.descidas.material_descida,
            "secao_minima_descida_mm2": resultado.descidas.secao_minima_descida_mm2,
        },
        "aterramento": {
            "tipo_eletrodo": resultado.aterramento.tipo_eletrodo,
            "perimetro_anel_m": fracao_para_dict(resultado.aterramento.perimetro_anel_m),
            "profundidade_minima_m": fracao_para_dict(resultado.aterramento.profundidade_minima_m),
            "numero_hastes_inspecao": resultado.aterramento.numero_hastes_inspecao,
            "comprimento_total_eletrodo_m": fracao_para_dict(resultado.aterramento.comprimento_total_eletrodo_m),
            "material_aterramento": resultado.aterramento.material_aterramento,
            "secao_minima_aterramento_mm2": resultado.aterramento.secao_minima_aterramento_mm2,
        },
        "comprimento_total_cabos_obra_m": fracao_para_dict(resultado.comprimento_total_cabos_obra_m),
    }

    return json.dumps(dict_resultado, indent=2, ensure_ascii=False)
