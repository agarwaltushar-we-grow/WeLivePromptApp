"""Deterministic quality gate for optimized prompts.

This is not a perfect semantic judge. Its purpose is to catch the common failure
mode where the model returns a short filled template instead of a consultant-grade
optimized prompt.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

REQUIRED_LABELS = [
    "Act as",
    "Context:",
    "Objective:",
    "Task:",
    "Constraints:",
    "Quality Standards:",
    "Reasoning Instructions:",
    "Output Format:",
]

WEAK_ROLE_TERMS = {
    "helpful assistant",
    "food recommendation guide",
    "general assistant",
    "ai assistant",
    "writing assistant",
}

SENIORITY_TERMS = {
    "senior",
    "expert",
    "specialist",
    "architect",
    "strategist",
    "consultant",
    "advisor",
    "analyst",
    "researcher",
    "engineer",
}

TASK_VERBS = {
    "analyze",
    "evaluate",
    "diagnose",
    "compare",
    "prioritize",
    "recommend",
    "design",
    "identify",
    "produce",
    "review",
    "assess",
    "develop",
    "create",
    "explain",
    "rank",
}

CONSTRAINT_TERMS = {
    "avoid",
    "do not",
    "must",
    "prioritize",
    "ensure",
    "assumption",
    "uncertain",
    "unsupported",
    "risk",
    "feasible",
    "accuracy",
}

OUTPUT_TERMS = {
    "table",
    "sections",
    "ranked",
    "checklist",
    "roadmap",
    "summary",
    "matrix",
    "format",
    "include",
    "order",
    "template",
}


@dataclass(frozen=True)
class QualityReport:
    score: int
    feedback: list[str]


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_'-]+", text.lower())


def _section_text(prompt: str, start_label: str, next_label: str | None) -> str:
    start = prompt.find(start_label)
    if start == -1:
        return ""
    start += len(start_label)
    end = len(prompt) if next_label is None else prompt.find(next_label, start)
    if end == -1:
        end = len(prompt)
    return prompt[start:end].strip()


def assess_optimized_prompt(prompt: str) -> QualityReport:
    text = " ".join((prompt or "").split())
    lowered = text.lower()
    feedback: list[str] = []
    score = 0

    # 1. Required structure and order: 24 points.
    label_positions = [text.find(label) for label in REQUIRED_LABELS]
    present_labels = sum(pos >= 0 for pos in label_positions)
    score += round((present_labels / len(REQUIRED_LABELS)) * 18)
    if present_labels < len(REQUIRED_LABELS):
        missing = [label for label, pos in zip(REQUIRED_LABELS, label_positions) if pos < 0]
        feedback.append("Missing required labels: " + ", ".join(missing))

    ordered = all(
        earlier >= 0 and later >= 0 and earlier < later
        for earlier, later in zip(label_positions, label_positions[1:])
    )
    if ordered:
        score += 6
    else:
        feedback.append("Required sections are missing or not in the required order.")

    # 2. Length and density: 10 points.
    word_count = len(_words(text))
    if word_count >= 180:
        score += 10
    elif word_count >= 140:
        score += 7
        feedback.append("Prompt is acceptable but still slightly short for consultant-grade optimization.")
    elif word_count >= 100:
        score += 4
        feedback.append("Prompt is too short; expand the objective, task, constraints, standards, and output format.")
    else:
        feedback.append("Prompt is far too short and likely just a filled template.")

    # 3. Specialized role: 12 points.
    role_text = _section_text(text, "Act as", "Context:")
    role_words = set(_words(role_text))
    if any(term in lowered for term in WEAK_ROLE_TERMS):
        feedback.append("Role is generic or weak; use a specialized senior domain role.")
    else:
        score += 4
    seniority_hits = sum(term in role_words for term in SENIORITY_TERMS)
    if seniority_hits >= 3 and len(role_words) >= 10:
        score += 8
    elif seniority_hits >= 2:
        score += 5
        feedback.append("Role is somewhat specialized but should include more domain expertise.")
    else:
        feedback.append("Role lacks enough seniority, specialization, or domain expertise.")

    # 4. Context quality: 9 points.
    context_text = _section_text(text, "Context:", "Objective:")
    context_words = _words(context_text)
    if len(context_words) >= 35:
        score += 5
    else:
        feedback.append("Context is shallow; explain situation, user, known facts, missing facts, and assumptions.")
    if any(term in context_text.lower() for term in ["unknown", "not specified", "missing", "assumption", "provided"]):
        score += 4
    else:
        feedback.append("Context should explicitly handle missing information or assumptions.")

    # 5. Objective quality: 8 points.
    objective_text = _section_text(text, "Objective:", "Task:")
    if len(_words(objective_text)) >= 18:
        score += 5
    else:
        feedback.append("Objective is too thin; define what success means.")
    if any(term in objective_text.lower() for term in ["outcome", "success", "highest", "improve", "optimize", "decision", "goal"]):
        score += 3
    else:
        feedback.append("Objective should state the target outcome or success criteria.")

    # 6. Task decomposition: 10 points.
    task_text = _section_text(text, "Task:", "Constraints:")
    task_words = set(_words(task_text))
    verb_hits = sum(verb in task_words for verb in TASK_VERBS)
    if verb_hits >= 5:
        score += 10
    elif verb_hits >= 3:
        score += 6
        feedback.append("Task is decent but should decompose the work into more concrete actions.")
    else:
        feedback.append("Task is too generic; add multiple concrete domain-specific actions.")

    # 7. Constraints: 8 points.
    constraints_text = _section_text(text, "Constraints:", "Quality Standards:")
    constraint_hits = sum(term in constraints_text.lower() for term in CONSTRAINT_TERMS)
    if constraint_hits >= 4 and len(_words(constraints_text)) >= 35:
        score += 8
    elif constraint_hits >= 2:
        score += 5
        feedback.append("Constraints need more operational guardrails and assumption rules.")
    else:
        feedback.append("Constraints are weak; add accuracy, risk, feasibility, exclusion, and assumption-handling rules.")

    # 8. Quality standards: 8 points.
    standards_text = _section_text(text, "Quality Standards:", "Reasoning Instructions:")
    standard_terms = ["specific", "useful", "feasible", "accurate", "prioritized", "clear", "actionable", "evidence", "risk"]
    standard_hits = sum(term in standards_text.lower() for term in standard_terms)
    if standard_hits >= 4 and len(_words(standards_text)) >= 25:
        score += 8
    elif standard_hits >= 2:
        score += 5
        feedback.append("Quality Standards section exists but lacks enough measurable standards.")
    else:
        feedback.append("Quality Standards section is weak or missing meaningful standards.")

    # 9. Reasoning instructions: 8 points.
    reasoning_text = _section_text(text, "Reasoning Instructions:", "Output Format:")
    if len(_words(reasoning_text)) >= 25 and any(
        term in reasoning_text.lower() for term in ["evaluate", "compare", "prioritize", "criteria", "tradeoff", "rank", "sequence"]
    ):
        score += 8
    else:
        feedback.append("Reasoning Instructions should define evaluation criteria or prioritization logic.")

    # 10. Output specificity: 13 points.
    output_text = _section_text(text, "Output Format:", None)
    output_hits = sum(term in output_text.lower() for term in OUTPUT_TERMS)
    if output_hits >= 5 and len(_words(output_text)) >= 35:
        score += 13
    elif output_hits >= 3:
        score += 8
        feedback.append("Output Format is present but should be more specific and immediately usable.")
    else:
        feedback.append("Output Format is too generic; specify exact sections, tables, ordering, and fields.")

    return QualityReport(score=min(score, 100), feedback=feedback[:8])
