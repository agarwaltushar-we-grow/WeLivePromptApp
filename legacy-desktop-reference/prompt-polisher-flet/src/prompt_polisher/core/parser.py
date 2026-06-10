"""Parsing and fallback handling for LLM output.

Product rule:
The optimized prompt is the primary deliverable.
If structured analysis fails, still show a usable optimized prompt.
"""

import json
import re

from pydantic import ValidationError

from prompt_polisher.core.framework import SECTION_ORDER
from prompt_polisher.core.models import PromptAnalysis, PromptSection, SectionStatus


def _extract_json(text: str) -> str:
    stripped = (text or "").strip()

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        return fenced.group(1)

    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in provider response.")

    return match.group(0)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _normalize_optimized_prompt(text: str) -> str:
    """Keep optimized prompts copy-friendly even when providers add line breaks."""
    return _clean_text(text)


def _fallback_optimized_prompt(user_prompt: str, raw_text: str = "") -> str:
    cleaned_raw = _clean_text(raw_text)

    if len(cleaned_raw) > 160 and "Act as" in cleaned_raw and "Output Format:" in cleaned_raw:
        return cleaned_raw

    cleaned_user_prompt = _clean_text(user_prompt)

    return _normalize_optimized_prompt(
        f"Act as a senior AI prompt engineer and requirements architect specializing in transforming incomplete, vague, or poorly structured user requests into precise, production-grade instructions for modern large language models. Context: The user provided the following prompt: '{cleaned_user_prompt}'. The prompt may contain useful intent but likely lacks complete role definition, context, objective, operational constraints, quality standards, reasoning instructions, and output structure. Objective: Produce a directly usable optimized prompt that preserves the user's explicit intent while raising the instruction quality to a professional standard. Task: Analyze the user's request, infer the most suitable expert role, clarify the situation and missing information, define the desired outcome, convert the request into concrete actions, add practical constraints, specify quality standards, define visible reasoning criteria, and choose a useful output format. Constraints: Do not invent unsupported facts, private context, names, dates, prices, sources, metrics, or claims; infer only generic task structure, reasonable professional expertise, practical guardrails, and copy-friendly formatting rules. Quality Standards: The optimized prompt should be specific, actionable, complete, feasible, clear, risk-aware, and immediately usable in another LLM without further editing. Reasoning Instructions: The final LLM should identify assumptions, evaluate tradeoffs, prioritize high-impact actions, and explain recommendations using concise visible rationale rather than hidden chain-of-thought. Output Format: Provide one continuous optimized prompt paragraph in the exact order Role → Context → Objective → Task → Constraints → Quality Standards → Reasoning Instructions → Output Format, using the labels Act as, Context, Objective, Task, Constraints, Quality Standards, Reasoning Instructions, and Output Format."
    )


def _fallback_sections() -> list[PromptSection]:
    status_by_name = {
        "Role": SectionStatus.weak,
        "Context": SectionStatus.weak,
        "Objective": SectionStatus.weak,
        "Task": SectionStatus.present,
        "Constraints": SectionStatus.weak,
        "Quality Standards": SectionStatus.weak,
        "Reasoning Instructions": SectionStatus.weak,
        "Output Format": SectionStatus.weak,
    }

    return [
        PromptSection(
            name=name,
            status=status_by_name.get(name, SectionStatus.weak),
            quality_score=3,
            content="Recovered from fallback handling.",
            issue="Structured provider analysis could not be fully parsed.",
            recommendation="Use the optimized prompt as the main result, then add any missing domain-specific details.",
        )
        for name in SECTION_ORDER
    ]


def _fallback_analysis(
    detected_language: str,
    optimized_prompt: str,
    warning: str,
) -> PromptAnalysis:
    return PromptAnalysis(
        detected_language=detected_language if detected_language in {"ja", "en"} else "en",
        sections=_fallback_sections(),
        clarification_questions=[
            "What specific result should the AI produce?",
            "Who is the target audience or user?",
            "Which constraints, exclusions, tone, length, language, or format requirements matter most?",
        ],
        optimized_prompt_en=optimized_prompt,
        optimized_prompt_ja=None,
        warnings=[warning],
    )


def _ensure_sections(result: PromptAnalysis) -> None:
    """Make old five-section provider responses compatible with the expanded framework."""
    by_name = {section.name: section for section in result.sections or []}
    sections: list[PromptSection] = []

    for name in SECTION_ORDER:
        existing = by_name.get(name)
        if existing:
            sections.append(existing)
            continue

        sections.append(
            PromptSection(
                name=name,
                status=SectionStatus.missing,
                quality_score=0,
                content="",
                issue=f"The provider did not return a {name} section.",
                recommendation=f"Add a clear {name} section to improve optimized prompt quality.",
            )
        )

    result.sections = sections


def parse_analysis(text: str, detected_language: str, original_prompt: str = "") -> PromptAnalysis:
    try:
        data = json.loads(_extract_json(text))
        result = PromptAnalysis.model_validate(data)

        if result.detected_language not in {"ja", "en"}:
            result.detected_language = detected_language if detected_language in {"ja", "en"} else "en"

        _ensure_sections(result)

        if result.clarification_questions is None:
            result.clarification_questions = []

        if result.warnings is None:
            result.warnings = []

        if not result.optimized_prompt_en:
            result.optimized_prompt_en = _fallback_optimized_prompt(original_prompt, text)
            result.warnings.append("Provider response parsed, but optimized_prompt_en was empty.")

        result.optimized_prompt_en = _normalize_optimized_prompt(result.optimized_prompt_en)
        if result.optimized_prompt_ja:
            result.optimized_prompt_ja = _normalize_optimized_prompt(result.optimized_prompt_ja)

        return result

    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        optimized_prompt = _fallback_optimized_prompt(original_prompt, text)
        return _fallback_analysis(
            detected_language=detected_language,
            optimized_prompt=optimized_prompt,
            warning=f"Structured analysis could not be parsed, but a usable optimized prompt was still generated. Details: {exc}",
        )
