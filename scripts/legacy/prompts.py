"""
Arquivo de compatibilidade para a versão antiga dos prompts.
Este arquivo redireciona para a nova estrutura de prompts.
"""
import os
import sys

# Adiciona o diretório raiz ao path para importações relativas
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa os prompts da nova estrutura
from src.config.prompts import PROMPT_CLASSIFICADOR, PROMPT_BRAINSTORM

# Mantém os nomes originais para compatibilidade
prompt_classificador = PROMPT_CLASSIFICADOR
prompt_brainstorm = PROMPT_BRAINSTORM
    