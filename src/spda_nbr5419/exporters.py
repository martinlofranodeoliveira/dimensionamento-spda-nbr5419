"""Exportadores de dados, relatórios e pacotes determinísticos para SPDA NBR 5419.

Garante:
1. Geração de relatório técnico textual tabular completo.
2. Sanitização estrita de CSV contra injeção de fórmulas (=, +, -, @, \\t, \\r).
3. Criação de arquivo ZIP determinístico com carimbo fixo (2026-01-01 00:00:00)
   e garantia de não sobrescrita atômica via os.O_EXCL.
"""

from __future__ import annotations

import csv
from io import StringIO
import os
from pathlib import Path
import zipfile

from spda_nbr5419.codecs import exportar_resultado_json
from spda_nbr5419.models import ResultadoDimensionamentoSPDA

TIMESTAMP_DETERMINISTICO = (2026, 1, 1, 0, 0, 0)
CARACTERES_INJECAO_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def sanitizar_campo_csv(valor: object) -> str:
    """Sanitiza campos de texto para evitar execução indevida de fórmulas em planilhas."""
    texto = str(valor)
    if texto.startswith(CARACTERES_INJECAO_FORMULA):
        return f"'{texto}"
    return texto


def gerar_relatorio_texto(resultado: ResultadoDimensionamentoSPDA) -> str:
    """Gera relatório técnico analítico em texto plano com formatação tabular."""
    linhas = [
        "=" * 78,
        "LAUDO TÉCNICO DE DIMENSIONAMENTO DE SPDA - ABNT NBR 5419:2015",
        "PADRÃO DE ENGENHARIA: LOFRANO TECNOLOGIA (ARITMÉTICA EXATA RACIONAL)",
        "=" * 78,
        f"Projeto: {resultado.identificador_projeto}",
        f"Edificação: {resultado.estrutura.nome}",
        f"Dimensões: {resultado.estrutura.comprimento_m}m x {resultado.estrutura.largura_m}m x {resultado.estrutura.altura_m}m",
        f"Densidade de Descargas (Ng): {resultado.estrutura.densidade_descargas_ng} raios/km²/ano",
        f"Ambiente: {resultado.estrutura.localizacao_ambiental} | Material Adotado: {resultado.estrutura.tipo_material}",
        "-" * 78,
        "1. ÁREA DE EXPOSIÇÃO EQUIVALENTE (Ad - NBR 5419-2, ANEXO A)",
        "-" * 78,
        f"Área de Cobertura (L x W):          {resultado.area_exposicao.area_cobertura_m2} m²",
        f"Perímetro da Edificação:            {resultado.area_exposicao.perimetro_m} m",
        f"Faixa de Proteção Perimetral (3H):  {resultado.area_exposicao.largura_faixa_protecao_m} m",
        f"Área Lateral (2 x 3H x (L+W)):      {resultado.area_exposicao.area_lateral_m2} m²",
        f"Área dos Cantos (pi x (3H)²):       {resultado.area_exposicao.area_cantos_m2} m²",
        f"ÁREA TOTAL EQUIVALENTE (Ad):        {resultado.area_exposicao.area_total_ad_m2} m²",
        "-" * 78,
        "2. GERENCIAMENTO DE RISCO R1 (NBR 5419-2)",
        "-" * 78,
        f"Fator de Localização (Cd):          {resultado.risco.fator_cd}",
        f"Eventos Anuais Estimados (Nd):      {resultado.risco.numero_eventos_nd} eventos/ano",
        f"Fator de Risco de Incêndio (rf):    {resultado.risco.fator_rf}",
        f"Fator de Combate a Incêndio (rp):   {resultado.risco.fator_rp}",
        f"Perda Típica Ponderada (Lt):        {resultado.risco.perda_tipica_lt}",
        f"Risco Calculado Sem SPDA (R1):      {resultado.risco.risco_r1_sem_spda}",
        f"Risco Tolerável Normativo (Rt):     {resultado.risco.risco_toleravel_rt} (1,0 x 10^-5)",
        f"Necessidade Mandatória de SPDA:     {'SIM (R1 > Rt)' if resultado.risco.necessidade_spda else 'NÃO (R1 <= Rt)'}",
        f"Nível de Proteção Adotado (NP):     {resultado.risco.nivel_protecao_adotado}",
        f"Probabilidade de Dano (PB):         {resultado.risco.probabilidade_pb_adotada}",
        f"Risco Residual Com SPDA (R1'):      {resultado.risco.risco_r1_com_spda}",
        f"Redução Efetiva de Risco:          {resultado.risco.reducao_risco_percentual}%",
        "-" * 78,
        "3. SUBSISTEMA DE CAPTAÇÃO (NBR 5419-3)",
        "-" * 78,
        f"Método de Dimensionamento:          {resultado.captacao.metodo_principal}",
        f"Raio da Esfera Rolante:             {resultado.captacao.raio_esfera_m} m",
        f"Malha Máxima Normativa:             {resultado.captacao.malha_maxima_comprimento_m}m x {resultado.captacao.malha_maxima_largura_m}m",
        f"Módulos Executivos da Malha:        {resultado.captacao.quantidade_modulos_comprimento} x {resultado.captacao.quantidade_modulos_largura} ({resultado.captacao.total_modulos_malha} módulos)",
        f"Condutor da Malha de Captação:      {resultado.captacao.material_captor} (mín. {resultado.captacao.secao_minima_captor_mm2} mm²)",
        f"Comprimento Total de Cabos Captor:  {resultado.captacao.comprimento_cabos_captor_m} m",
        "-" * 78,
        "4. SUBSISTEMA DE DESCIDAS E ANÉIS DE CINTAMENTO (NBR 5419-3)",
        "-" * 78,
        f"Espaçamento Médio Máximo:           {resultado.descidas.espacamento_maximo_descidas_m} m",
        f"Número de Descidas Adotado:         {resultado.descidas.numero_descidas_adotado} condutores verticais",
        f"Espaçamento Real entre Descidas:    {resultado.descidas.espacamento_real_descidas_m} m",
        f"Anéis de Equalização (Cintamento):  {resultado.descidas.quantidade_aneis_cintamento} anéis",
        f"Comprimento de Cabos de Descida:    {resultado.descidas.comprimento_cabos_descida_m} m",
        f"Condutor de Descida:                {resultado.descidas.material_descida} (mín. {resultado.descidas.secao_minima_descida_mm2} mm²)",
        "-" * 78,
        "5. SUBSISTEMA DE ATERRAMENTO (NBR 5419-3)",
        "-" * 78,
        f"Tipo de Eletrodo de Aterramento:    {resultado.aterramento.tipo_eletrodo}",
        f"Perímetro do Anel Enterrado:        {resultado.aterramento.perimetro_anel_m} m",
        f"Profundidade Mínima:                {resultado.aterramento.profundidade_minima_m} m",
        f"Hastes de Equalização / Inspeção:   {resultado.aterramento.numero_hastes_inspecao} unidades",
        f"Comprimento Total do Eletrodo:      {resultado.aterramento.comprimento_total_eletrodo_m} m",
        f"Condutor de Aterramento:            {resultado.aterramento.material_aterramento} (mín. {resultado.aterramento.secao_minima_aterramento_mm2} mm²)",
        "=" * 78,
        "6. RESUMO DE QUANTITATIVOS DE CONDUTORES DA OBRA",
        "=" * 78,
        f"Cabos de Captação (Cobertura):      {resultado.captacao.comprimento_cabos_captor_m} m",
        f"Cabos de Descida e Cintamento:      {resultado.descidas.comprimento_cabos_descida_m} m",
        f"Cabos de Aterramento e Hastes:      {resultado.aterramento.comprimento_total_eletrodo_m} m",
        f"TOTAL GERAL DE CONDUTORES:          {resultado.comprimento_total_cabos_obra_m} m",
        "=" * 78,
        f"PARECER TÉCNICO CONCLUSIVO: {resultado.conclusao_tecnica}",
        "=" * 78,
    ]
    return "\n".join(linhas) + "\n"


def gerar_csv_sanitizado(resultado: ResultadoDimensionamentoSPDA) -> str:
    """Gera dados de saída em CSV sanitizado contra injeção de fórmulas."""
    buffer = StringIO()
    escritor = csv.writer(buffer, lineterminator="\n")

    escritor.writerow([
        sanitizar_campo_csv("Item"),
        sanitizar_campo_csv("Parametro"),
        sanitizar_campo_csv("Valor"),
        sanitizar_campo_csv("Unidade"),
        sanitizar_campo_csv("Norma_Referencia"),
    ])

    linhas_dados = [
        ("Edificacao", "Nome da Obra", resultado.estrutura.nome, "-", "ABNT NBR 5419:2015"),
        ("Edificacao", "Comprimento", str(resultado.estrutura.comprimento_m), "m", "NBR 5419-2"),
        ("Edificacao", "Largura", str(resultado.estrutura.largura_m), "m", "NBR 5419-2"),
        ("Edificacao", "Altura", str(resultado.estrutura.altura_m), "m", "NBR 5419-2"),
        ("Exposicao", "Area Cobertura", str(resultado.area_exposicao.area_cobertura_m2), "m2", "NBR 5419-2"),
        ("Exposicao", "Area Equivalente Ad", str(resultado.area_exposicao.area_total_ad_m2), "m2", "NBR 5419-2"),
        ("Risco", "Eventos Anuais Nd", str(resultado.risco.numero_eventos_nd), "eventos/ano", "NBR 5419-2"),
        ("Risco", "Risco R1 Sem SPDA", str(resultado.risco.risco_r1_sem_spda), "-", "NBR 5419-2"),
        ("Risco", "Risco Toleravel Rt", str(resultado.risco.risco_toleravel_rt), "-", "NBR 5419-2"),
        ("Risco", "Nivel de Protecao", resultado.risco.nivel_protecao_adotado, "-", "NBR 5419-1"),
        ("Risco", "Risco R1 Com SPDA", str(resultado.risco.risco_r1_com_spda), "-", "NBR 5419-2"),
        ("Captacao", "Metodo", resultado.captacao.metodo_principal, "-", "NBR 5419-3"),
        ("Captacao", "Raio Esfera Rolante", str(resultado.captacao.raio_esfera_m), "m", "NBR 5419-3"),
        ("Captacao", "Malha Maxima", f"{resultado.captacao.malha_maxima_comprimento_m}x{resultado.captacao.malha_maxima_largura_m}", "m", "NBR 5419-3"),
        ("Captacao", "Cabos Captor", str(resultado.captacao.comprimento_cabos_captor_m), "m", "NBR 5419-3"),
        ("Captacao", "Secao Minima Captor", str(resultado.captacao.secao_minima_captor_mm2), "mm2", "NBR 5419-3"),
        ("Descidas", "Numero Descidas", str(resultado.descidas.numero_descidas_adotado), "condutores", "NBR 5419-3"),
        ("Descidas", "Espacamento Real", str(resultado.descidas.espacamento_real_descidas_m), "m", "NBR 5419-3"),
        ("Descidas", "Cabos Descida", str(resultado.descidas.comprimento_cabos_descida_m), "m", "NBR 5419-3"),
        ("Descidas", "Secao Minima Descida", str(resultado.descidas.secao_minima_descida_mm2), "mm2", "NBR 5419-3"),
        ("Aterramento", "Tipo Eletrodo", resultado.aterramento.tipo_eletrodo, "-", "NBR 5419-3"),
        ("Aterramento", "Perimetro Anel", str(resultado.aterramento.perimetro_anel_m), "m", "NBR 5419-3"),
        ("Aterramento", "Hastes Inspecao", str(resultado.aterramento.numero_hastes_inspecao), "unid", "NBR 5419-3"),
        ("Aterramento", "Cabos Aterramento", str(resultado.aterramento.comprimento_total_eletrodo_m), "m", "NBR 5419-3"),
        ("Aterramento", "Secao Minima Aterramento", str(resultado.aterramento.secao_minima_aterramento_mm2), "mm2", "NBR 5419-3"),
        ("Totais", "Total Cabos Obra", str(resultado.comprimento_total_cabos_obra_m), "m", "LOFRANO"),
    ]

    for item, param, val, unid, norma in linhas_dados:
        escritor.writerow([
            sanitizar_campo_csv(item),
            sanitizar_campo_csv(param),
            sanitizar_campo_csv(val),
            sanitizar_campo_csv(unid),
            sanitizar_campo_csv(norma),
        ])

    return buffer.getvalue()


def gerar_pacote_zip_deterministico(
    resultado: ResultadoDimensionamentoSPDA, caminho_destino: Path | str
) -> None:
    """Cria arquivo ZIP determinístico com carimbo fixo e proteção contra sobrescrita atômica."""
    caminho = Path(caminho_destino)
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY

    fd = os.open(caminho, flags, 0o644)
    with open(fd, "wb", closefd=True) as f_out:
        with zipfile.ZipFile(f_out, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            conteudos = {
                "relatorio_spda.txt": gerar_relatorio_texto(resultado).encode("utf-8"),
                "dados_dimensionamento.csv": gerar_csv_sanitizado(resultado).encode("utf-8"),
                "resultado_spda.json": exportar_resultado_json(resultado).encode("utf-8"),
            }
            for nome_arquivo, dados_bytes in conteudos.items():
                info = zipfile.ZipInfo(filename=nome_arquivo, date_time=TIMESTAMP_DETERMINISTICO)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                zf.writestr(info, dados_bytes)
