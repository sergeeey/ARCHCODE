"""
7-Pass Hypothesis Generator - Research Breakthrough Architect.

Implements the full 7-pass framework:
1. Project Map
2. Leverage Lenses (6 lenses)
3. Generate 10 Hypotheses
4. DeepConf Scoring
5. Top-3 Research Proposals
6. MVP Architecture
7. 14-Day Plan

Uses Claude API for generation + memory graph for cross-project transfer.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment
load_dotenv()


class SevenPassGenerator:
    """7-pass research architecture discovery framework."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet

    def _build_prompt(self, project_context: Dict[str, Any]) -> str:
        """
        Build 7-pass analysis prompt from project context.

        Args:
            project_context: {
                "name": "ARCHCODE",
                "domain": "genomics",
                "readme": "...",
                "decisions": "...",
                "code_samples": [...],
                "current_status": "..."
            }
        """
        prompt = f"""# PROMPT: Research Breakthrough Architect

## Роль

Ты — междисциплинарный исследовательский архитектор уровня principal scientist + principal engineer.

Твоя специализация:
- prompt engineering / context engineering
- агентные LLM-системы
- KDS / OSINT / RAG / knowledge graph
- экспериментальная валидация гипотез
- безопасная computational science
- поиск неочевидных архитектурных улучшений

## Проект для анализа

**Название:** {project_context['name']}
**Домен:** {project_context['domain']}

**README:**
```
{project_context.get('readme', 'Not available')}
```

**Текущий статус (decisions.md):**
```
{project_context.get('decisions', 'Not available')}
```

**Ключевые файлы:**
{self._format_code_samples(project_context.get('code_samples', []))}

## Задача

Выполни анализ в 7 проходов:

### Проход 1 — Карта проекта

Реконструируй проект как систему. Выведи таблицу:

| Компонент | Что есть сейчас | Скрытый потенциал | Главный риск | Как измерить |
|---|---|---|---|---|

### Проход 2 — Поиск неочевидных рычагов (6 линз)

Найди рычаги усиления через 6 линз:
1. Memory leverage
2. Reasoning leverage
3. Evaluation leverage
4. Discovery leverage
5. Automation leverage
6. Scientific leverage

Для каждой линзы:
- Идея (1-2 предложения)
- Почему неочевидно
- Минимальный эксперимент
- Метрика успеха

### Проход 3 — Генерация 10 гипотез

Сгенерируй таблицу:

| ID | Гипотеза | Почему может сработать | Минимальный тест | Метрика | Риск |
|---|---|---|---|---|---|

Гипотезы типов: архитектурные, алгоритмические, исследовательские, продуктовые, benchmark, safety, discovery.

### Проход 4 — DeepConf фильтрация

Оцени каждую гипотезу (1-5):
- Novelty, Feasibility, Evidence fit, Impact, Testability, Safety

Выведи топ-3.

### Проход 5 — Топ-3 в research proposals

Для каждой из топ-3:
- Формулировка
- Что известно / неизвестно
- Минимальный эксперимент
- Dataset / Baseline / Treatment
- Метрики + критерии успеха/провала
- Риски

### Проход 6 — MVP архитектура

Для самой сильной гипотезы:
- 10-module system architecture
- Input → Modules → Output → Metrics → Feedback loop
- Repository structure

### Проход 7 — 14-дневный план

| День | Цель | Действие | Артефакт | Метрика готовности |
|---|---|---|---|---|

## Ограничения

- Используй evidence markers: `<fact>`, `<hypothesis>`, `<unknown>`, `<risk>`
- Каждая рекомендация должна иметь проверку
- Не предлагай небезопасные биологические действия
- Формат: сжатая проверяемая логика (тезис → основание → проверка → риск)

## Формат ответа

Ответ выведи в JSON:

```json
{{
  "project_map": {{"table": "markdown table"}},
  "leverage_lenses": [
    {{"lens": "Memory", "idea": "...", "why_nonobvious": "...", "experiment": "...", "metric": "..."}}
  ],
  "hypotheses": [
    {{"id": "H1", "text": "...", "why": "...", "test": "...", "metric": "...", "risk": "..."}}
  ],
  "deepconf_scores": [
    {{"id": "H1", "novelty": 4, "feasibility": 4, "evidence": 3, "impact": 5, "testability": 4, "safety": 5, "total": 25}}
  ],
  "top3_proposals": [
    {{"hypothesis": "H1", "formulation": "...", "experiment": "...", "metrics": "...", "risks": "..."}}
  ],
  "mvp_architecture": {{"modules": [...], "flow": "..."}},
  "plan_14days": [
    {{"day": 1, "goal": "...", "action": "...", "artifact": "...", "metric": "..."}}
  ]
}}
```

ВАЖНО: JSON должен быть валидным (no trailing commas, proper escaping).
"""
        return prompt

    def _format_code_samples(self, samples: List[Path]) -> str:
        """Format code file paths for prompt."""
        if not samples:
            return "(No code samples available)"

        lines = []
        for i, path in enumerate(samples[:5], 1):  # Max 5 samples
            lines.append(f"{i}. {path.name}")
        return "\n".join(lines)

    def generate(self, project_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run 7-pass analysis on project.

        Returns:
            Full analysis result (JSON format from Claude)
        """
        prompt = self._build_prompt(project_context)

        logger.info(f"Running 7-pass analysis on {project_context['name']}")
        logger.info(f"Prompt length: {len(prompt)} chars")

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=16000,  # Long output expected
            temperature=1.0,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract response
        output_text = response.content[0].text

        # Parse JSON (Claude should return JSON)
        try:
            result = json.loads(output_text)
            logger.info("✓ Successfully parsed JSON response")
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON, returning raw text: {e}")
            result = {"raw_output": output_text, "parse_error": str(e)}

        # Add metadata
        result["metadata"] = {
            "project": project_context["name"],
            "domain": project_context["domain"],
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
        }

        return result

    def save_result(self, result: Dict[str, Any], output_path: Path):
        """Save analysis result to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ Analysis saved to {output_path}")


def main():
    """CLI entrypoint for testing."""
    import argparse
    import sys

    # Add parent to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    from src.acquisition.project_parser import ProjectParser

    parser = argparse.ArgumentParser(description="7-pass hypothesis generator")
    parser.add_argument("--project", type=Path, required=True, help="Project directory")
    parser.add_argument("--output", type=Path, default=Path("experiments"), help="Output directory")

    args = parser.parse_args()

    # Parse project
    logger.info("=" * 60)
    logger.info("7-PASS ANALYSIS")
    logger.info("=" * 60)

    proj_parser = ProjectParser(args.project)
    metadata = proj_parser.parse()
    key_files = proj_parser.get_key_files()

    # Build context
    context = {
        "name": metadata["name"],
        "domain": metadata["domain"],
        "readme": key_files["readme"].read_text(encoding="utf-8") if key_files["readme"] else None,
        "decisions": key_files["decisions"].read_text(encoding="utf-8")[:5000]
        if key_files["decisions"]
        else None,  # First 5K chars
        "code_samples": key_files["code_files"],
    }

    # Generate
    generator = SevenPassGenerator()
    result = generator.generate(context)

    # Save
    args.output.mkdir(parents=True, exist_ok=True)
    output_file = (
        args.output / f"{metadata['name']}_7pass_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    generator.save_result(result, output_file)

    # Print summary
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Project: {metadata['name']}")
    print(f"Domain: {metadata['domain']}")
    print(f"Hypotheses generated: {len(result.get('hypotheses', []))}")
    print(f"Output: {output_file}")
    print()

    if "metadata" in result:
        meta = result["metadata"]
        print(f"Tokens: {meta['prompt_tokens']} input, {meta['completion_tokens']} output")
        print(
            f"Cost estimate: ${(meta['prompt_tokens'] * 0.003 + meta['completion_tokens'] * 0.015) / 1000:.3f}"
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    main()
