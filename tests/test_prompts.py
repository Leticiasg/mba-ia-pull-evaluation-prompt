"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure  # noqa: E402

PROMPT_PATH = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)
    return raw.get("bug_to_user_story_v2", raw)


class TestPrompts:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Carrega o prompt v2 antes de cada teste."""
        self.prompt = load_prompts(PROMPT_PATH)
        self.system_prompt = self.prompt.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        is_valid, errors = validate_prompt_structure(self.prompt)
        assert is_valid, f"Estrutura do prompt inválida: {errors}"
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' não encontrado no YAML"
        assert len(self.system_prompt.strip()) > 0, "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        text = self.system_prompt.lower()
        role_keywords = ["você é um", "você é uma", "atue como", "seu papel é"]
        assert any(kw in text for kw in role_keywords), (
            "Prompt não define uma persona. Esperado algum dos termos: "
            + ", ".join(role_keywords)
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        text = self.system_prompt.lower()
        format_keywords = ["como um", "eu quero", "para que", "user story", "given-when-then", "dado que"]
        assert any(kw in text for kw in format_keywords), (
            "Prompt não menciona formato de User Story ou Markdown"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        text = self.system_prompt.lower()
        example_keywords = ["exemplo", "input", "output", "bug simples", "bug médio", "bug complexo"]
        assert any(kw in text for kw in example_keywords), (
            "Prompt não contém exemplos de entrada/saída (few-shot)"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum [TODO] no texto."""
        full_text = yaml.dump(self.prompt)
        assert "[TODO]" not in full_text, "Prompt ainda contém marcadores [TODO]"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)} ({techniques})"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
