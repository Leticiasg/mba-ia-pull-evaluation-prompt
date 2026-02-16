"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt no formato "username/prompt_name"
        prompt_data: Dados do prompt (system_prompt, user_prompt, etc)

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "{bug_report}")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt),
        ])

        print(f"   Fazendo push para: {prompt_name}")
        hub.push(prompt_name, prompt_template, new_repo_is_public=True)
        print("   ✓ Push realizado com sucesso (público)")

        return True

    except Exception as e:
        print(f"   ❌ Erro ao fazer push: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt.
    Delega para validate_prompt_structure do utils.py.

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"

    raw_data = load_yaml(str(prompt_path))
    if not raw_data:
        print(f"❌ Falha ao carregar: {prompt_path}")
        return 1

    prompt_data = raw_data.get("bug_to_user_story_v2", raw_data)

    print(f"✓ Prompt carregado de: {prompt_path}")

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Validação estrutural OK")

    prompt_name = f"{username}/bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if success:
        print(f"\n✓ Prompt publicado em: https://smith.langchain.com/hub/{prompt_name}")
        print(f"   Tags: {prompt_data.get('tags', [])}")
        print(f"   Técnicas: {prompt_data.get('techniques_applied', [])}")
        return 0
    else:
        print("❌ Falha no push")
        return 1


if __name__ == "__main__":
    sys.exit(main())
