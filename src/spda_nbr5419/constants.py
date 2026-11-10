"""Constantes e parâmetros normativos da ABNT NBR 5419:2015 (Partes 1 a 4).

Define parâmetros para gerenciamento de risco, dimensionamento de captação,
descidas, anéis de cintamento e subsistema de aterramento para SPDA.
Todos os valores operam estritamente com frações racionais exatas (Fraction)
e inteiros, garantindo precisão matemática absoluta sem ponto flutuante.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Final

# Aproximação racional exata de Pi (Zu Chongzhi: 355 / 113)
PI_RACIONAL: Final[Fraction] = Fraction(355, 113)

# Risco Tolerável Normativo (NBR 5419-2:2015, Tabela 4)
# Risco tolerável para perda de vida humana (R1)
RISCO_TOLERAVEL_R1: Final[Fraction] = Fraction(1, 100_000)  # 10^-5

# Níveis de Proteção contra Descargas Atmosféricas (NP I a IV)
# NBR 5419-1:2015 (Tabela 5) e NBR 5419-3:2015 (Tabelas 2 e 4)
NIVEIS_PROTECAO: Final[dict[str, dict[str, Fraction | int | str]]] = {
    "NP_I": {
        "codigo": "NP_I",
        "nome": "Nível de Proteção I (Máxima Proteção)",
        "eficiencia_minima": Fraction(98, 100),       # 98%
        "raio_esfera_rolante_m": 20,                 # 20 m
        "malha_comprimento_m": 5,                    # 5 m x 5 m
        "malha_largura_m": 5,
        "espacamento_descidas_m": 10,                # 10 m
        "espacamento_aneis_cintamento_m": 10,        # 10 m
        "probabilidade_dano_pb": Fraction(2, 100),   # 0,02 com SPDA
    },
    "NP_II": {
        "codigo": "NP_II",
        "nome": "Nível de Proteção II",
        "eficiencia_minima": Fraction(95, 100),       # 95%
        "raio_esfera_rolante_m": 30,                 # 30 m
        "malha_comprimento_m": 10,                   # 10 m x 10 m
        "malha_largura_m": 10,
        "espacamento_descidas_m": 10,                # 10 m
        "espacamento_aneis_cintamento_m": 10,        # 10 m
        "probabilidade_dano_pb": Fraction(5, 100),   # 0,05 com SPDA
    },
    "NP_III": {
        "codigo": "NP_III",
        "nome": "Nível de Proteção III (Padrão Usual)",
        "eficiencia_minima": Fraction(90, 100),       # 90%
        "raio_esfera_rolante_m": 45,                 # 45 m
        "malha_comprimento_m": 15,                   # 15 m x 15 m
        "malha_largura_m": 15,
        "espacamento_descidas_m": 15,                # 15 m
        "espacamento_aneis_cintamento_m": 20,        # 20 m
        "probabilidade_dano_pb": Fraction(10, 100),  # 0,10 com SPDA
    },
    "NP_IV": {
        "codigo": "NP_IV",
        "nome": "Nível de Proteção IV",
        "eficiencia_minima": Fraction(80, 100),       # 80%
        "raio_esfera_rolante_m": 60,                 # 60 m
        "malha_comprimento_m": 20,                   # 20 m x 20 m
        "malha_largura_m": 20,
        "espacamento_descidas_m": 20,                # 20 m
        "espacamento_aneis_cintamento_m": 20,        # 20 m
        "probabilidade_dano_pb": Fraction(20, 100),  # 0,20 com SPDA
    },
}

# Fator de Localização Ambiental Cd (NBR 5419-2:2015, Tabela A.1)
FATORES_LOCALIZACAO_CD: Final[dict[str, dict[str, str | Fraction]]] = {
    "isolada_colina": {
        "codigo": "isolada_colina",
        "descricao": "Estrutura isolada no topo de colina ou promontório",
        "fator": Fraction(2, 1),
    },
    "isolada_plano": {
        "codigo": "isolada_plano",
        "descricao": "Estrutura isolada em terreno plano sem árvores ou vizinhos",
        "fator": Fraction(1, 1),
    },
    "cercada_mesma_altura": {
        "codigo": "cercada_mesma_altura",
        "descricao": "Estrutura cercada por outras estruturas ou árvores da mesma altura",
        "fator": Fraction(1, 2),
    },
    "cercada_mais_altas": {
        "codigo": "cercada_mais_altas",
        "descricao": "Estrutura cercada por estruturas ou árvores mais altas",
        "fator": Fraction(1, 4),
    },
}

# Fator de Risco de Incêndio rf (NBR 5419-2:2015, Tabela A.4)
FATORES_RISCO_INCENDIO_RF: Final[dict[str, dict[str, str | Fraction]]] = {
    "explosivo": {
        "codigo": "explosivo",
        "descricao": "Risco de explosão ou alto risco com materiais inflamáveis",
        "fator": Fraction(1, 10),
    },
    "ordinario": {
        "codigo": "ordinario",
        "descricao": "Risco ordinário / comum (residencial, comercial, escritórios)",
        "fator": Fraction(1, 100),
    },
    "baixo": {
        "codigo": "baixo",
        "descricao": "Risco baixo (estruturas de concreto ou aço sem estoque combustível)",
        "fator": Fraction(1, 1000),
    },
    "nenhum": {
        "codigo": "nenhum",
        "descricao": "Nenhum risco de incêndio / incombustível",
        "fator": Fraction(0, 1),
    },
}

# Fator de Redução de Perdas por Proteção contra Incêndio rp (NBR 5419-2:2015, Tabela A.5)
FATORES_COMBATE_INCENDIO_RP: Final[dict[str, dict[str, str | Fraction]]] = {
    "nenhuma": {
        "codigo": "nenhuma",
        "descricao": "Nenhuma medida especial de proteção contra incêndio",
        "fator": Fraction(1, 1),
    },
    "manual": {
        "codigo": "manual",
        "descricao": "Extintores manuais ou hidrantes com operação manual",
        "fator": Fraction(1, 2),
    },
    "alarme_brigada": {
        "codigo": "alarme_brigada",
        "descricao": "Alarme automático ou brigada de incêndio permanente",
        "fator": Fraction(2, 5),
    },
    "sprinklers": {
        "codigo": "sprinklers",
        "descricao": "Sistema fixo de extinção automática (sprinklers)",
        "fator": Fraction(1, 5),
    },
}

# Materiais e Seções Mínimas de Condutores (NBR 5419-3:2015, Tabela 6)
# Áreas mínimas em mm²
CONDUTORES_NORMATIVOS: Final[dict[str, dict[str, int | str]]] = {
    "cobre_captor_descida": {
        "material": "Cobre eletrolítico ou estanhado",
        "uso": "Captores e condutores de descida",
        "secao_minima_mm2": 35,
        "diametro_minimo_mm": 7,
    },
    "cobre_aterramento": {
        "material": "Cobre eletrolítico ou estanhado",
        "uso": "Eletrodos de aterramento",
        "secao_minima_mm2": 50,
        "diametro_minimo_mm": 8,
    },
    "aluminio_captor_descida": {
        "material": "Alumínio",
        "uso": "Captores e condutores de descida (proibido enterrado)",
        "secao_minima_mm2": 70,
        "diametro_minimo_mm": 10,
    },
    "aco_galvanizado_captor_descida": {
        "material": "Aço galvanizado a fogo",
        "uso": "Captores e condutores de descida",
        "secao_minima_mm2": 50,
        "diametro_minimo_mm": 8,
    },
    "aco_galvanizado_aterramento": {
        "material": "Aço galvanizado a fogo",
        "uso": "Eletrodos de aterramento (haste ou fita)",
        "secao_minima_mm2": 80,
        "diametro_minimo_mm": 10,
    },
}

# Tipos de Edificações de Exemplo e Níveis Recomendados
TIPOS_ESTRUTURA_PADRAO: Final[dict[str, dict[str, str | Fraction | int]]] = {
    "predio_residencial": {
        "nome": "Edifício Residencial Multifamiliar",
        "densidade_pessoas_m2": Fraction(1, 20),
        "tempo_permanencia_h": 8760,
        "risco_incendio": "ordinario",
        "combate_incendio": "manual",
    },
    "escola_hospital": {
        "nome": "Escola ou Hospital",
        "densidade_pessoas_m2": Fraction(1, 5),
        "tempo_permanencia_h": 4000,
        "risco_incendio": "ordinario",
        "combate_incendio": "alarme_brigada",
    },
    "galpao_industrial": {
        "nome": "Galpão Industrial com Carga Combustível",
        "densidade_pessoas_m2": Fraction(1, 50),
        "tempo_permanencia_h": 3000,
        "risco_incendio": "explosivo",
        "combate_incendio": "sprinklers",
    },
}
