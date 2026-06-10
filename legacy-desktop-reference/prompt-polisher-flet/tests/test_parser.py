import json
from prompt_polisher.core.framework import SECTION_ORDER
from prompt_polisher.core.parser import parse_analysis
from prompt_polisher.core.quality_gate import assess_optimized_prompt


def make_sections():
    return [
        {"name": name, "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""}
        for name in SECTION_ORDER
    ]


def test_parse_valid_analysis():
    payload = {
        "detected_language": "en",
        "translated_input_en": "Write an email.",
        "sections": make_sections(),
        "clarification_questions": ["Who is the recipient?"],
        "optimized_prompt_en": "Act as a senior business writing specialist. Context: The user needs a professional email. Objective: Produce a clear useful email. Task: Draft the email. Constraints: Preserve intent and avoid unsupported claims. Quality Standards: Be clear and specific. Reasoning Instructions: Use concise visible rationale where needed. Output Format: Provide the email body.",
        "optimized_prompt_ja": None,
        "warnings": [],
    }
    result = parse_analysis(json.dumps(payload), "en")
    assert result.detected_language == "en"
    assert len(result.sections) == len(SECTION_ORDER)


def test_parse_normalizes_multiline_optimized_prompt():
    payload = {
        "detected_language": "en",
        "translated_input_en": "",
        "sections": make_sections(),
        "clarification_questions": [],
        "optimized_prompt_en": "Act as an expert.\n\nContext: Test.\nObjective: Improve it.\nTask: Do it.",
        "optimized_prompt_ja": None,
        "warnings": [],
    }
    result = parse_analysis(json.dumps(payload), "en")
    assert "\n" not in result.optimized_prompt_en
    assert "  " not in result.optimized_prompt_en


def test_parse_json_inside_code_fence():
    payload = {
        "detected_language": "en",
        "translated_input_en": "",
        "sections": make_sections(),
        "clarification_questions": [],
        "optimized_prompt_en": "Act as a senior expert. Context: Test. Objective: Improve it. Task: Do it. Constraints: Be precise. Quality Standards: Be useful. Reasoning Instructions: Compare options. Output Format: Paragraph.",
        "optimized_prompt_ja": None,
        "warnings": [],
    }
    result = parse_analysis("```json\n" + json.dumps(payload) + "\n```", "en")
    assert result.optimized_prompt_en.startswith("Act as")


def test_parse_old_five_section_response_is_upgraded():
    old_sections = [
        {"name": "Role", "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""},
        {"name": "Context", "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""},
        {"name": "Task", "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""},
        {"name": "Constraints", "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""},
        {"name": "Output Format", "status": "present", "content": "x", "quality_score": 3, "issue": "", "recommendation": ""},
    ]
    payload = {
        "detected_language": "en",
        "translated_input_en": "",
        "sections": old_sections,
        "clarification_questions": [],
        "optimized_prompt_en": "Act as a senior expert. Context: Test. Task: Do it. Constraints: Be precise. Output Format: Paragraph.",
        "optimized_prompt_ja": None,
        "warnings": [],
    }
    result = parse_analysis(json.dumps(payload), "en")
    assert [section.name for section in result.sections] == SECTION_ORDER


def test_quality_gate_penalizes_weak_prompt():
    weak = "Act as a food recommendation guide. Context: User wants food. Task: Recommend food. Constraints: Be helpful. Output Format: List."
    report = assess_optimized_prompt(weak)
    assert report.score < 80
    assert report.feedback


def test_quality_gate_rewards_structured_prompt():
    strong = (
        "Act as a senior Python software architect and application performance optimization specialist with expertise in profiling, scalability, resource management, reliability engineering, observability, maintainability, and internal business systems. "
        "Context: The user has a Python application used internally by employees, and it has become slow as data volume increased while some users report occasional crashes; the architecture, database design, hosting setup, traffic patterns, and exact failure modes are not specified, so the response must identify assumptions and request missing details only after providing useful guidance. "
        "Objective: Identify the highest-impact improvements that can increase performance, stability, and maintainability without requiring a complete rewrite or disrupting existing employee workflows. "
        "Task: Analyze likely bottlenecks, evaluate code-level inefficiencies, diagnose database and I/O risks, assess memory and concurrency issues, review logging and observability gaps, prioritize quick wins, recommend medium-term refactors, and produce an implementation roadmap. "
        "Constraints: Preserve existing functionality, avoid unsupported claims about the unseen codebase, prioritize low-risk high-impact changes, state assumptions clearly, separate immediate fixes from architectural improvements, and avoid major refactoring unless the expected benefit is clear. "
        "Quality Standards: Recommendations should be specific, actionable, technically feasible, risk-aware, prioritized by impact and effort, aligned with Python best practices, and useful to a developer who needs to make real code improvements. "
        "Reasoning Instructions: Evaluate each recommendation by performance impact, stability impact, implementation effort, regression risk, user disruption, maintainability benefit, and confidence level before ranking it. "
        "Output Format: Provide an executive summary, a prioritized findings table with severity and effort, quick wins, medium-term improvements, long-term architectural recommendations, testing and monitoring steps, and a final implementation roadmap."
    )
    report = assess_optimized_prompt(strong)
    assert report.score >= 80
