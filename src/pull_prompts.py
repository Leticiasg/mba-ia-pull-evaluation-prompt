"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """
    Faz pull do prompt do LangSmith Hub e retorna como dicionário.

    Returns:
        dict com dados do prompt ou None se erro
    """
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")
    print(f"Puxando prompt: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print("   ✓ Prompt carregado com sucesso do Hub")

        # hub.pull() retorna um ChatPromptTemplate com uma lista de messages tipadas.
        # Iteramos para separar o system_prompt e user_prompt pelo tipo da mensagem.
        system_prompt = ""
        user_prompt = ""

        for message in prompt.messages:
            role = message.__class__.__name__
            if "System" in role:
                system_prompt = message.prompt.template
            elif "Human" in role:
                user_prompt = message.prompt.template

        # Se o prompt no Hub for um PromptTemplate simples (sem roles),
        # usa o template único como system_prompt.
        if not system_prompt and hasattr(prompt, "template"):
            system_prompt = prompt.template

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt or "{bug_report}",
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        return prompt_data

    except Exception as e:
        print(f"   ❌ Erro ao fazer pull: {e}")
        return None


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    prompt_data = pull_prompts_from_langsmith()
    if not prompt_data:
        print("❌ Falha ao obter prompts do LangSmith Hub")
        return 1

    output_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v1.yml"

    if save_yaml(prompt_data, str(output_path)):
        print(f"\n✓ Prompts salvos em: {output_path}")
        return 0
    else:
        print("❌ Falha ao salvar prompts")
        return 1


if __name__ == "__main__":
    sys.exit(main())
