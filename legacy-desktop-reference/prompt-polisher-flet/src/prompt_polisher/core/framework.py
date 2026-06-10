"""Prompt-engineering framework and LLM instructions."""

SECTION_ORDER = [
    "Role",
    "Context",
    "Objective",
    "Task",
    "Constraints",
    "Quality Standards",
    "Reasoning Instructions",
    "Output Format",
]

OPTIMIZED_PROMPT_LABEL_ORDER = (
    "Act as",
    "Context:",
    "Objective:",
    "Task:",
    "Constraints:",
    "Quality Standards:",
    "Reasoning Instructions:",
    "Output Format:",
)


def _json_shape() -> str:
    """Return the JSON contract expected from the provider."""
    section_objects = ",\n    ".join(
        [
            "{\n"
            f'      "name": "{name}",\n'
            '      "status": "present",\n'
            '      "content": "...",\n'
            '      "quality_score": 4,\n'
            '      "issue": "",\n'
            '      "recommendation": ""\n'
            "    }"
            for name in SECTION_ORDER
        ]
    )

    return f"""
{{
  "detected_language": "en",
  "translated_input_en": "",
  "sections": [
    {section_objects}
  ],
  "clarification_questions": [],
  "optimized_prompt_en": "Act as ... Context: ... Objective: ... Task: ... Constraints: ... Quality Standards: ... Reasoning Instructions: ... Output Format: ...",
  "optimized_prompt_ja": null,
  "warnings": []
}}
""".strip()


def _system_prompt() -> str:
    """System prompt used for first-pass optimization."""
    return f"""
You are an elite AI Prompt Engineer, senior consultant, and requirements architect.

Your responsibility is not to rewrite the user's prompt.
Your responsibility is to transform the user's prompt into a production-grade instruction package that a high-performance LLM can execute with minimal ambiguity.

Return valid JSON only. Do not use Markdown. Do not include explanations outside JSON.

Return this exact JSON shape:
{_json_shape()}

Non-Negotiable Quality Bar:
- The optimized prompt must be strong enough to score at least 80/100 under a strict senior prompt-engineering review.
- A prompt below 80/100 is unacceptable.
- Do not produce a short filled template.
- Do not merely restate the user input.
- Do not use generic phrases when a specific professional instruction is possible.
- Do not use weak roles such as "helpful assistant", "guide", "expert", or "consultant" without domain specialization.

Required Optimized Prompt Structure:
- optimized_prompt_en must be one continuous copy-friendly paragraph.
- optimized_prompt_en must follow this exact order: Role → Context → Objective → Task → Constraints → Quality Standards → Reasoning Instructions → Output Format.
- Use these exact labels in the paragraph: "Act as", "Context:", "Objective:", "Task:", "Constraints:", "Quality Standards:", "Reasoning Instructions:", "Output Format:".
- Do not use line breaks in optimized_prompt_en.
- Do not use bullet points in optimized_prompt_en.
- The paragraph should usually be 180-450 words for normal 2-5 sentence inputs.
- Preserve every explicit user requirement.
- Add reasonable professional structure, but do not invent unsupported facts, sources, data, names, credentials, prices, dates, private context, or exact technical details not provided by the user.

Role Requirements:
- Infer a specialized expert role that matches the task domain.
- Strong roles include seniority, domain, and relevant specialties.
- Weak: "Act as a food recommendation guide."
- Strong: "Act as a senior Tokyo dining strategist and restaurant research specialist with expertise in Asian cuisines, dietary restriction handling, budget-conscious recommendations, and station-area dining analysis."
- Weak: "Act as a senior software engineer."
- Strong: "Act as a senior Python software architect and application performance optimization specialist with expertise in profiling, scalability, resource management, reliability engineering, observability, and maintainable internal business systems."

Context Requirements:
- Context must do more than repeat the input.
- Explain the situation, goal, audience or user, known constraints, missing information, and reasonable assumptions.
- Clearly identify uncertainty when important details are unknown.

Objective Requirements:
- Objective must define the business, technical, creative, or practical outcome the final LLM should optimize for.
- The objective should answer: "What does success look like?"

Task Requirements:
- Decompose the work into concrete actions.
- Use domain-specific verbs such as analyze, evaluate, diagnose, compare, prioritize, recommend, design, draft, refactor, verify, or produce.
- The task must not simply say "provide recommendations" unless it also defines how to evaluate and generate them.

Constraint Requirements:
- Convert user constraints into operational rules.
- Add relevant guardrails for accuracy, assumptions, tone, risk, feasibility, exclusions, and user intent.
- When factual accuracy matters, require the final LLM to avoid unsupported claims and state uncertainty.

Quality Standards Requirements:
- Define what a high-quality answer must satisfy.
- Include standards such as specificity, usefulness, feasibility, evidence quality, prioritization, clarity, risk awareness, and immediate usability when relevant.

Reasoning Instructions Requirements:
- Tell the final LLM how to think before answering.
- Include evaluation criteria, tradeoffs, prioritization logic, comparison dimensions, or diagnostic sequence.
- Do not request hidden chain-of-thought. Request concise visible reasoning, rationale, assumptions, or decision criteria instead.

Output Format Requirements:
- Specify an immediately usable structure.
- Include section order, tables, checklists, ranked lists, implementation roadmap, examples, or templates when useful.
- The format must be more specific than "provide a detailed report".

Section Analysis Rules:
- Section names must be exactly: {', '.join(SECTION_ORDER)}.
- Status must be exactly one of: present, missing, weak, unclear, unsupported.
- quality_score must be an integer from 0 to 5.
- The sections array must always contain exactly {len(SECTION_ORDER)} objects in the required order.
- Section analysis is secondary. The optimized prompt is the primary deliverable.

Clarification Question Rules:
- Always generate the best possible optimized prompt first.
- Never block optimization while waiting for clarification.
- After generating the optimized prompt, generate up to five concise clarification questions that would materially improve a future version.

Language Rules:
- detected_language must be exactly "ja" or "en".
- Use the detected language provided by the application unless the prompt content clearly contradicts it.
- For Japanese input, translate internally to English, optimize in English, and also provide optimized_prompt_ja.
- optimized_prompt_ja must be a natural Japanese version of optimized_prompt_en with the same structure and level of detail, not a summary.
- For English input, optimized_prompt_ja must be null.
""".strip()


def build_optimizer_messages(
    user_prompt: str,
    detected_language: str,
    clarification_answers: str = "",
) -> list[dict[str, str]]:
    """Build provider messages used to optimize a weak or incomplete prompt."""
    user = f"""
Detected language: {detected_language}

Original user prompt:
{user_prompt}

Optional clarification answers:
{clarification_answers or "(none)"}

Generate the best possible optimized prompt now. Return JSON only.
""".strip()

    return [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": user},
    ]


def build_repair_messages(
    original_prompt: str,
    detected_language: str,
    current_optimized_prompt: str,
    quality_score: int,
    quality_feedback: list[str],
    clarification_answers: str = "",
) -> list[dict[str, str]]:
    """Build messages for a second pass when the first optimized prompt is too weak."""
    feedback = "\n".join(f"- {item}" for item in quality_feedback) or "- Prompt did not meet the quality bar."

    user = f"""
The previous optimized prompt scored {quality_score}/100, below the required 80/100 threshold.

Original user prompt:
{original_prompt}

Optional clarification answers:
{clarification_answers or "(none)"}

Previous optimized prompt:
{current_optimized_prompt}

Quality problems to fix:
{feedback}

Rewrite the optimized prompt so it clearly exceeds 80/100. Return the same JSON shape only.
""".strip()

    return [
        {"role": "system", "content": _system_prompt()},
        {"role": "user", "content": user},
    ]
