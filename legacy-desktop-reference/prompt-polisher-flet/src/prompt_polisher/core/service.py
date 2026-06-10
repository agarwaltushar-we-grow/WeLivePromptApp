"""Application service that coordinates detection, prompting, provider calls, and parsing."""

from prompt_polisher.core.framework import SECTION_ORDER, build_optimizer_messages, build_repair_messages
from prompt_polisher.core.language import detect_language
from prompt_polisher.core.models import PromptAnalysis, PromptSection, SectionStatus
from prompt_polisher.core.parser import parse_analysis
from prompt_polisher.core.quality_gate import assess_optimized_prompt
from prompt_polisher.providers.base import LLMProvider, ProviderError


QUALITY_THRESHOLD = 80


def empty_analysis(message: str = "Please enter a prompt.") -> PromptAnalysis:
    sections = [
        PromptSection(
            name=n,
            status=SectionStatus.missing,
            quality_score=0,
            issue=message,
            recommendation="Enter a prompt and run optimization.",
        )
        for n in SECTION_ORDER
    ]

    return PromptAnalysis(
        detected_language="unsupported",
        sections=sections,
        clarification_questions=[message],
        optimized_prompt_en="",
        warnings=[message],
    )


class PromptOptimizationService:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def optimize(
        self,
        prompt: str,
        model: str,
        clarification_answers: str = "",
    ) -> PromptAnalysis:
        clean_prompt = (prompt or "").strip()

        if not clean_prompt:
            return empty_analysis("Please enter or paste a prompt before running optimization.")

        detected = detect_language(clean_prompt)

        if detected == "unsupported":
            detected = "en"

        try:
            raw = self.provider.generate(
                build_optimizer_messages(clean_prompt, detected, clarification_answers),
                model,
            )
            first_result = parse_analysis(raw, detected, original_prompt=clean_prompt)
            first_report = assess_optimized_prompt(first_result.optimized_prompt_en)

            if first_report.score >= QUALITY_THRESHOLD:
                first_result.warnings.append(f"Prompt quality gate score: {first_report.score}/100.")
                return first_result

            # One repair pass is the highest-ROI quality improvement. It forces the
            # model to correct concrete weaknesses instead of hoping the first pass is enough.
            try:
                repaired_raw = self.provider.generate(
                    build_repair_messages(
                        original_prompt=clean_prompt,
                        detected_language=detected,
                        current_optimized_prompt=first_result.optimized_prompt_en,
                        quality_score=first_report.score,
                        quality_feedback=first_report.feedback,
                        clarification_answers=clarification_answers,
                    ),
                    model,
                )
                repaired_result = parse_analysis(repaired_raw, detected, original_prompt=clean_prompt)
                repaired_report = assess_optimized_prompt(repaired_result.optimized_prompt_en)

                if repaired_report.score >= first_report.score:
                    repaired_result.warnings.append(
                        f"Prompt quality gate score: {repaired_report.score}/100 after repair pass."
                    )
                    if repaired_report.score < QUALITY_THRESHOLD:
                        repaired_result.warnings.extend(
                            ["Quality gate still below 80/100:", *repaired_report.feedback]
                        )
                    return repaired_result

            except Exception as repair_exc:
                first_result.warnings.append(f"Repair pass failed; using first result. Details: {repair_exc}")

            first_result.warnings.append(f"Prompt quality gate score: {first_report.score}/100.")
            first_result.warnings.extend(["Quality gate below 80/100:", *first_report.feedback])
            return first_result

        except ProviderError:
            raise

        except Exception as exc:
            raise ProviderError(f"Unexpected optimization failure: {exc}") from exc
