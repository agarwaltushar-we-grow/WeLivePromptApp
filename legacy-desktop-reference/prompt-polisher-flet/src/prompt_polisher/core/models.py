"""Typed internal models for prompt analysis and optimization."""
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

SectionName = Literal[
    "Role",
    "Context",
    "Objective",
    "Task",
    "Constraints",
    "Quality Standards",
    "Reasoning Instructions",
    "Output Format",
]


class SectionStatus(str, Enum):
    present = "present"
    missing = "missing"
    weak = "weak"
    unclear = "unclear"
    unsupported = "unsupported"


class PromptSection(BaseModel):
    name: SectionName
    status: SectionStatus
    content: str = ""
    quality_score: int = Field(default=0, ge=0, le=5)
    issue: str = ""
    recommendation: str = ""


class PromptAnalysis(BaseModel):
    detected_language: Literal["ja", "en", "unsupported"]
    translated_input_en: str = ""
    sections: list[PromptSection]
    clarification_questions: list[str] = []
    optimized_prompt_en: str = ""
    optimized_prompt_ja: str | None = None
    warnings: list[str] = []
