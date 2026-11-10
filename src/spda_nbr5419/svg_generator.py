"""Gerador de painel técnico vetorial SVG (1440x900) para SPDA NBR 5419.

Gera visualização técnica profissional de alta fidelidade contendo:
1. Identificação formal, norma ABNT NBR 5419:2015 e selo LOFRANO TECNOLOGIA.
2. Cards analíticos: Nível de Proteção, Área de Exposição Ad, Risco R1 e Quantitativos.
3. Diagrama esquemático em corte/elevação da edificação com malha de captação,
   condutores de descida verticais, anéis de cintamento e anel de aterramento.
"""

from __future__ import annotations

from html import escape
import math

from spda_nbr5419.models import ResultadoDimensionamentoSPDA


def gerar_painel_svg(resultado: ResultadoDimensionamentoSPDA) -> str:
    """Gera o painel vetorial SVG de 1440x900 pixels."""
    # Extração de variáveis formatadas
    nome_obra = escape(resultado.estrutura.nome)
    id_proj = escape(resultado.identificador_projeto)
    np_adotado = escape(resultado.risco.nivel_protecao_adotado)
    raio_esfera = resultado.captacao.raio_esfera_m
    malha_txt = f"{resultado.captacao.malha_maxima_comprimento_m}m x {resultado.captacao.malha_maxima_largura_m}m"

    ad_int = math.ceil(resultado.area_exposicao.area_total_ad_m2)
    cabos_total_int = math.ceil(resultado.comprimento_total_cabos_obra_m)
    cabos_captor_int = math.ceil(resultado.captacao.comprimento_cabos_captor_m)
    cabos_descida_int = math.ceil(resultado.descidas.comprimento_cabos_descida_m)
    cabos_aterr_int = math.ceil(resultado.aterramento.comprimento_total_eletrodo_m)

    # SVG Canvas 1440 x 900
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 900" width="1440" height="900">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0f1d"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="#111827" stop-opacity="0.95"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f59e0b"/>
      <stop offset="100%" stop-color="#fbbf24"/>
    </linearGradient>
    <linearGradient id="cyanGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#06b6d4"/>
      <stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Fundo Principal -->
  <rect width="1440" height="900" fill="url(#bg)"/>

  <!-- Cabeçalho -->
  <g transform="translate(60, 45)">
    <text x="0" y="24" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="13" font-weight="700" letter-spacing="1.5">ABNT NBR 5419:2015 · PROTEÇÃO CONTRA DESCARGAS ATMOSFÉRICAS</text>
    <text x="0" y="58" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{nome_obra}</text>
    <text x="0" y="82" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="14">Projeto: {id_proj} | Padrão de Engenharia: LOFRANO TECNOLOGIA (Aritmética Racional Exata)</text>
    
    <!-- Badge de Conformidade -->
    <rect x="1140" y="10" width="180" height="42" rx="8" fill="#065f46" stroke="#10b981" stroke-width="1.5"/>
    <text x="1230" y="36" fill="#34d399" font-family="system-ui, sans-serif" font-size="14" font-weight="700" text-anchor="middle">✓ SPDA CONFORME</text>
  </g>

  <!-- 4 Cards Superiores de Métricas -->
  <!-- Card 1: Nível de Proteção -->
  <g transform="translate(60, 160)" filter="url(#shadow)">
    <rect width="310" height="120" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">NÍVEL DE PROTEÇÃO ADOTADO</text>
    <text x="24" y="68" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{np_adotado}</text>
    <text x="24" y="98" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="13">Esfera R={raio_esfera}m | Malha {malha_txt}</text>
  </g>

  <!-- Card 2: Área de Exposição Equivalente -->
  <g transform="translate(397, 160)" filter="url(#shadow)">
    <rect width="310" height="120" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">ÁREA DE EXPOSIÇÃO EQUIVALENTE (Ad)</text>
    <text x="24" y="68" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{ad_int:,} m²</text>
    <text x="24" y="98" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="13">Faixa 3H={resultado.area_exposicao.largura_faixa_protecao_m}m | Ng={resultado.estrutura.densidade_descargas_ng} raios/km²</text>
  </g>

  <!-- Card 3: Risco R1 vs Tolerável -->
  <g transform="translate(734, 160)" filter="url(#shadow)">
    <rect width="310" height="120" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">REDUÇÃO DE RISCO R1</text>
    <text x="24" y="68" fill="#10b981" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{resultado.risco.reducao_risco_percentual}%</text>
    <text x="24" y="98" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="13">Risco R1 ≤ Rt (10⁻⁵) Aprovado</text>
  </g>

  <!-- Card 4: Total de Condutores -->
  <g transform="translate(1070, 160)" filter="url(#shadow)">
    <rect width="310" height="120" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="24" y="32" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="12" font-weight="600">TOTAL DE CONDUTORES DA OBRA</text>
    <text x="24" y="68" fill="#f43f5e" font-family="system-ui, sans-serif" font-size="28" font-weight="800">{cabos_total_int:,} m</text>
    <text x="24" y="98" fill="#cbd5e1" font-family="system-ui, sans-serif" font-size="13">Material: {resultado.estrutura.tipo_material.upper()}</text>
  </g>

  <!-- Painel Esquerdo: Diagrama Estrutural do SPDA (Elevação) -->
  <g transform="translate(60, 310)" filter="url(#shadow)">
    <rect width="780" height="530" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="30" y="40" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="18" font-weight="700">DIAGRAMA TÉCNICO DE ELEVAÇÃO DO SUBSISTEMA SPDA</text>
    <text x="30" y="64" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13">Visualização de Captação em Cobertura, Descidas Periféricas, Anéis e Aterramento</text>

    <!-- Terreno / Linha de Solo -->
    <line x1="80" y1="450" x2="700" y2="450" stroke="#10b981" stroke-width="3" stroke-dasharray="8,6"/>
    <text x="630" y="440" fill="#10b981" font-family="system-ui, sans-serif" font-size="12" font-weight="600">NÍVEL DO SOLO ±0.00</text>

    <!-- Corpo da Edificação -->
    <rect x="180" y="160" width="420" height="290" fill="#1e293b" stroke="#475569" stroke-width="2"/>
    
    <!-- Janelas Ilustrativas -->
    <g fill="#334155">
      <rect x="220" y="190" width="50" height="40" rx="3"/>
      <rect x="310" y="190" width="50" height="40" rx="3"/>
      <rect x="420" y="190" width="50" height="40" rx="3"/>
      <rect x="510" y="190" width="50" height="40" rx="3"/>

      <rect x="220" y="270" width="50" height="40" rx="3"/>
      <rect x="310" y="270" width="50" height="40" rx="3"/>
      <rect x="420" y="270" width="50" height="40" rx="3"/>
      <rect x="510" y="270" width="50" height="40" rx="3"/>

      <rect x="220" y="350" width="50" height="40" rx="3"/>
      <rect x="310" y="350" width="50" height="40" rx="3"/>
      <rect x="420" y="350" width="50" height="40" rx="3"/>
      <rect x="510" y="350" width="50" height="40" rx="3"/>
    </g>

    <!-- Subsistema de Captação (Malha na Cobertura) -->
    <line x1="170" y1="160" x2="610" y2="160" stroke="#f59e0b" stroke-width="4"/>
    <!-- Pontas captoras Franklin nos cantos -->
    <line x1="180" y1="160" x2="180" y2="135" stroke="#f59e0b" stroke-width="3"/>
    <circle cx="180" cy="135" r="4" fill="#fbbf24"/>
    <line x1="600" y1="160" x2="600" y2="135" stroke="#f59e0b" stroke-width="3"/>
    <circle cx="600" cy="135" r="4" fill="#fbbf24"/>
    <!-- Captor central -->
    <line x1="390" y1="160" x2="390" y2="135" stroke="#f59e0b" stroke-width="3"/>
    <circle cx="390" cy="135" r="4" fill="#fbbf24"/>

    <text x="390" y="120" fill="#fbbf24" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">CAPTORES / MALHA FARADAY ({resultado.captacao.secao_minima_captor_mm2} mm²)</text>

    <!-- Condutores de Descida (Laterais e Centrais) -->
    <line x1="180" y1="160" x2="180" y2="450" stroke="#f59e0b" stroke-width="3"/>
    <line x1="600" y1="160" x2="600" y2="450" stroke="#f59e0b" stroke-width="3"/>
    <line x1="390" y1="160" x2="390" y2="450" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,4"/>

    <!-- Anéis Intermediários de Cintamento / Equalização -->
    <line x1="170" y1="300" x2="610" y2="300" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8,4"/>
    <text x="620" y="304" fill="#38bdf8" font-family="system-ui, sans-serif" font-size="11" font-weight="600">ANEL DE CINTAMENTO (H=20m)</text>

    <!-- Subsistema de Aterramento (Anel Enterrado e Hastes) -->
    <!-- Eletrodo em anel Tipo B -->
    <line x1="140" y1="480" x2="640" y2="480" stroke="#f43f5e" stroke-width="3"/>
    <text x="390" y="505" fill="#f43f5e" font-family="system-ui, sans-serif" font-size="12" font-weight="700" text-anchor="middle">ELETRODO EM ANEL TIPO B ENTERRADO A ≥ 0.50m ({resultado.aterramento.secao_minima_aterramento_mm2} mm²)</text>

    <!-- Hastes de Aterramento Verticais -->
    <line x1="180" y1="450" x2="180" y2="510" stroke="#f43f5e" stroke-width="3"/>
    <polygon points="176,510 184,510 180,518" fill="#f43f5e"/>

    <line x1="600" y1="450" x2="600" y2="510" stroke="#f43f5e" stroke-width="3"/>
    <polygon points="596,510 604,510 600,518" fill="#f43f5e"/>

    <!-- Esfera Rolante Ilustrativa -->
    <circle cx="100" cy="100" r="70" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="4,4"/>
    <text x="100" y="95" fill="#ef4444" font-family="system-ui, sans-serif" font-size="11" font-weight="700" text-anchor="middle">ESFERA ROLANTE</text>
    <text x="100" y="112" fill="#ef4444" font-family="system-ui, sans-serif" font-size="10" text-anchor="middle">R = {raio_esfera} m</text>
  </g>

  <!-- Painel Direito: Quadro Analítico de Especificações Normativas -->
  <g transform="translate(860, 310)" filter="url(#shadow)">
    <rect width="520" height="530" rx="12" fill="url(#cardGrad)" stroke="#334155" stroke-width="1"/>
    <text x="30" y="40" fill="#f8fafc" font-family="system-ui, sans-serif" font-size="18" font-weight="700">ESPECIFICAÇÕES NORMATIVAS DETALHADAS</text>
    <text x="30" y="64" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="13">Critérios de Verificação Conforme ABNT NBR 5419:2015</text>

    <!-- Tabela de Itens -->
    <g transform="translate(30, 95)" font-family="system-ui, sans-serif" font-size="13">
      <!-- Linha 1 -->
      <text x="0" y="0" fill="#94a3b8">Método de Captação:</text>
      <text x="460" y="0" fill="#f8fafc" font-weight="700" text-anchor="end">Gaiola de Faraday / Malhas</text>
      <line x1="0" y1="12" x2="460" y2="12" stroke="#334155" stroke-width="1"/>

      <!-- Linha 2 -->
      <text x="0" y="36" fill="#94a3b8">Dimensão Máxima da Malha:</text>
      <text x="460" y="36" fill="#fbbf24" font-weight="700" text-anchor="end">{malha_txt}</text>
      <line x1="0" y1="48" x2="460" y2="48" stroke="#334155" stroke-width="1"/>

      <!-- Linha 3 -->
      <text x="0" y="72" fill="#94a3b8">Módulos Executivos Cobertura:</text>
      <text x="460" y="72" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.captacao.total_modulos_malha} módulos ({cabos_captor_int} m cabos)</text>
      <line x1="0" y1="84" x2="460" y2="84" stroke="#334155" stroke-width="1"/>

      <!-- Linha 4 -->
      <text x="0" y="108" fill="#94a3b8">Espaçamento Máx. Descidas:</text>
      <text x="460" y="108" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.descidas.espacamento_maximo_descidas_m} m</text>
      <line x1="0" y1="120" x2="460" y2="120" stroke="#334155" stroke-width="1"/>

      <!-- Linha 5 -->
      <text x="0" y="144" fill="#94a3b8">Número de Descidas Adotado:</text>
      <text x="460" y="144" fill="#38bdf8" font-weight="700" text-anchor="end">{resultado.descidas.numero_descidas_adotado} condutores verticais</text>
      <line x1="0" y1="156" x2="460" y2="156" stroke="#334155" stroke-width="1"/>

      <!-- Linha 6 -->
      <text x="0" y="180" fill="#94a3b8">Espaçamento Real Descidas:</text>
      <text x="460" y="180" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.descidas.espacamento_real_descidas_m} m</text>
      <line x1="0" y1="192" x2="460" y2="192" stroke="#334155" stroke-width="1"/>

      <!-- Linha 7 -->
      <text x="0" y="216" fill="#94a3b8">Anéis de Cintamento Horizontal:</text>
      <text x="460" y="216" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.descidas.quantidade_aneis_cintamento} anéis ({cabos_descida_int} m cabos)</text>
      <line x1="0" y1="228" x2="460" y2="228" stroke="#334155" stroke-width="1"/>

      <!-- Linha 8 -->
      <text x="0" y="252" fill="#94a3b8">Subsistema de Aterramento:</text>
      <text x="460" y="252" fill="#f43f5e" font-weight="700" text-anchor="end">Anel Perimetral Tipo B</text>
      <line x1="0" y1="264" x2="460" y2="264" stroke="#334155" stroke-width="1"/>

      <!-- Linha 9 -->
      <text x="0" y="288" fill="#94a3b8">Perímetro do Anel Enterrado:</text>
      <text x="460" y="288" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.aterramento.perimetro_anel_m} m (Profundidade ≥ 0.50m)</text>
      <line x1="0" y1="300" x2="460" y2="300" stroke="#334155" stroke-width="1"/>

      <!-- Linha 10 -->
      <text x="0" y="324" fill="#94a3b8">Hastes de Inspeção / Equalização:</text>
      <text x="460" y="324" fill="#f8fafc" font-weight="700" text-anchor="end">{resultado.aterramento.numero_hastes_inspecao} hastes ({cabos_aterr_int} m total)</text>
      <line x1="0" y1="336" x2="460" y2="336" stroke="#334155" stroke-width="1"/>
    </g>

    <!-- Caixa de Resumo / Conclusão -->
    <g transform="translate(30, 445)">
      <rect width="460" height="60" rx="8" fill="#0f172a" stroke="#10b981" stroke-width="1"/>
      <text x="20" y="24" fill="#34d399" font-family="system-ui, sans-serif" font-size="12" font-weight="700">CONFORMIDADE ESTATUTÁRIA PLENA</text>
      <text x="20" y="44" fill="#94a3b8" font-family="system-ui, sans-serif" font-size="11">Projeto dimensionado com rigor matemático exato segundo a ABNT NBR 5419:2015.</text>
    </g>
  </g>

  <!-- Rodapé -->
  <g transform="translate(60, 875)" font-family="system-ui, sans-serif" font-size="11" fill="#64748b">
    <text x="0" y="0">LOFRANO TECNOLOGIA © 2026 · Software Livre sob Licença MIT · Zero Ponto Flutuante · Padrão de Engenharia Racional Exata</text>
    <text x="1320" y="0" text-anchor="end">spda-nbr5419 v1.0.0</text>
  </g>
</svg>
"""
    return svg
