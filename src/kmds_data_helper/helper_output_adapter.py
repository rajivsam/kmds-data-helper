from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Optional

from kmds.ontology import kmds_ontology as ontology_model
from kmds.utils.load_utils import load_kb
from kmds.utils.natural_language_observation import log_text_as_observation, map_text_to_observation
from kmds.utils.summary_logger import log_exploratory_summary


JSON_EXTENSIONS = {".json", ".jsonld"}


def _read_source_text(source_path: Path) -> str:
    if source_path.suffix.lower() in JSON_EXTENSIONS:
        data = json.loads(source_path.read_text(encoding="utf-8"))
        return _extract_summary_text(data)
    return source_path.read_text(encoding="utf-8")


def _extract_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped:
            yield stripped
        return

    if isinstance(value, dict):
        for key, nested_value in value.items():
            if key in {"quality_score", "count", "metadata"}:
                continue
            yield from _extract_strings(nested_value)
        return

    if isinstance(value, list):
        for item in value:
            yield from _extract_strings(item)


def _extract_summary_text(payload: Any) -> str:
    if isinstance(payload, dict):
        preferred_keys = [
            "project_summary",
            "strategic_report",
            "summary",
            "exploratory_summary",
            "technical_observations",
            "data_quality_warnings",
            "model_justification",
            "performance_evaluation",
            "feature_engineering_notes",
            "production_roadmap",
        ]
        collected: list[str] = []
        for key in preferred_keys:
            if key in payload:
                collected.extend(_extract_strings(payload[key]))

        if not collected:
            collected.extend(_extract_strings(payload))

        unique_lines: list[str] = []
        seen: set[str] = set()
        for item in collected:
            normalized = re.sub(r"\s+", " ", item).strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_lines.append(normalized)

        return "\n\n".join(unique_lines)

    if isinstance(payload, str):
        return payload.strip()

    return str(payload).strip()


def _normalize_blocks(text: str) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n+", text) if block.strip()]
    findings: list[str] = []
    context_prefix = ""

    for block in blocks:
        stripped = block.strip()
        if stripped.startswith("#") or stripped.startswith("<") or len(stripped) < 40:
            context_prefix = f"{context_prefix} {stripped}".strip()
            continue

        candidate = f"{context_prefix} {stripped}".strip() if context_prefix else stripped
        context_prefix = ""

        if len(candidate) >= 20:
            findings.append(candidate)

    if not findings and text.strip():
        findings = [text.strip()]
    return findings


def _summarize_for_ingest(text: str) -> str:
    if not text.strip():
        raise ValueError("Input content must be non-empty")
    return text.strip()


def _ensure_create_target_available(project_path: Path, project_mode: str) -> None:
    if project_mode == "create" and project_path.exists():
        raise ValueError(
            f"Project file already exists: {project_path}. Use update mode to modify it."
        )


def _ingest_summary(
    *,
    summary_text: str,
    project_file_path: str,
    workflow_name: str,
    project_mode: str,
    workflow_type: Optional[str],
    no_prompt: bool,
    intent: Optional[str],
) -> str:
    project_path = Path(project_file_path)

    _ensure_create_target_available(project_path, project_mode)

    if project_mode == "update":
        if not project_path.exists():
            raise ValueError(f"Project file does not exist for update: {project_file_path}")
        if load_kb(str(project_path)) is None:
            raise ValueError(f"Could not load project knowledge base: {project_file_path}")
    elif project_mode != "create":
        raise ValueError("project_mode must be either 'create' or 'update'")

    workflow = log_exploratory_summary(
        project_summary=summary_text,
        workflow_name=workflow_name,
        workflow_type=workflow_type,
        prompt_on_ambiguity=not no_prompt,
        intent=intent,
    )

    project_path.parent.mkdir(parents=True, exist_ok=True)
    ontology_model.onto.save(file=str(project_path), format="rdfxml")

    action = "Created" if project_mode == "create" else "Updated"
    print(
        "{} project '{}' with workflow '{}' and {} exploratory observations at {}".format(
            action,
            project_path.name,
            workflow_name,
            len(workflow.has_exploratory_observations),
            project_path,
        )
    )
    return str(project_path)


def _ingest_observations(
    *,
    source_text: str,
    project_file_path: str,
    workflow_name: str,
    project_mode: str,
    workflow_type: Optional[str],
) -> str:
    project_path = Path(project_file_path)

    _ensure_create_target_available(project_path, project_mode)

    if project_mode == "update":
        if not project_path.exists():
            raise ValueError(f"Project file does not exist for update: {project_file_path}")
        if load_kb(str(project_path)) is None:
            raise ValueError(f"Could not load project knowledge base: {project_file_path}")
    elif project_mode != "create":
        raise ValueError("project_mode must be either 'create' or 'update'")

    findings = _normalize_blocks(source_text)
    valid_findings: list[tuple[str, Any]] = []
    skipped = 0

    for finding in findings:
        mapping = map_text_to_observation(finding)
        if mapping.validation_passed:
            valid_findings.append((finding, mapping))
        else:
            skipped += 1

    if not valid_findings:
        print("Selected ingest mode: summary (fallback)")
        return _ingest_summary(
            summary_text=source_text,
            project_file_path=project_file_path,
            workflow_name=workflow_name,
            project_mode=project_mode,
            workflow_type=workflow_type,
            no_prompt=True,
            intent=None,
        )

    print("Selected ingest mode: observations")
    for index, (finding, mapping) in enumerate(valid_findings):
        mode = "create" if index == 0 and project_mode == "create" and not project_path.exists() else "update"
        log_text_as_observation(
            text=finding,
            workflow_name=workflow_name,
            project_file_path=str(project_path),
            project_mode=mode,
            workflow_type=workflow_type or ("application" if mapping.workflow_family != "experimental" else "experimental"),
        )

    print(
        f"Ingested {len(valid_findings)} structured observation(s) from {len(findings)} candidate block(s); skipped {skipped}."
    )
    return str(project_path)


def ingest_helper_output(
    *,
    input_path: str,
    project_file_path: str,
    workflow_name: str = "kmds_project_workflow",
    project_mode: str = "update",
    mode: str = "auto",
    workflow_type: Optional[str] = None,
    intent: Optional[str] = None,
    no_prompt: bool = True,
) -> str:
    source_path = Path(input_path)
    if not source_path.exists():
        raise ValueError(f"Input file does not exist: {source_path}")

    source_text = _read_source_text(source_path)

    if mode == "summary":
        print("Selected ingest mode: summary")
        return _ingest_summary(
            summary_text=_summarize_for_ingest(source_text),
            project_file_path=project_file_path,
            workflow_name=workflow_name,
            project_mode=project_mode,
            workflow_type=workflow_type,
            no_prompt=no_prompt,
            intent=intent,
        )

    if mode == "observations":
        return _ingest_observations(
            source_text=source_text,
            project_file_path=project_file_path,
            workflow_name=workflow_name,
            project_mode=project_mode,
            workflow_type=workflow_type,
        )

    if mode != "auto":
        raise ValueError("mode must be one of: auto, summary, observations")

    observation_blocks = _normalize_blocks(source_text)
    if len(observation_blocks) <= 2 and any(len(block) >= 120 for block in observation_blocks):
        print("Selected ingest mode: summary")
        return _ingest_summary(
            summary_text=_summarize_for_ingest(source_text),
            project_file_path=project_file_path,
            workflow_name=workflow_name,
            project_mode=project_mode,
            workflow_type=workflow_type,
            no_prompt=no_prompt,
            intent=intent,
        )

    return _ingest_observations(
        source_text=source_text,
        project_file_path=project_file_path,
        workflow_name=workflow_name,
        project_mode=project_mode,
        workflow_type=workflow_type,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generic KMDS adapter for arbitrary kmds-helper outputs."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a kmds-helper output file (.json, .md, .txt, etc.)",
    )
    parser.add_argument(
        "--project-file",
        required=True,
        help="Project knowledge graph file path (.xml recommended)",
    )
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--create-project", action="store_true")
    mode_group.add_argument("--update-project", action="store_true")
    parser.add_argument(
        "--workflow-name",
        default="kmds_project_workflow",
        help="Workflow name for the created or updated workflow",
    )
    parser.add_argument(
        "--workflow-type",
        choices=["application", "experimental"],
        default=None,
        help="Optional explicit workflow type to skip inference",
    )
    parser.add_argument(
        "--intent",
        default=None,
        help="Optional intent tag applied to summary-mode observations",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "summary", "observations"],
        default="auto",
        help="Choose how to ingest the input",
    )
    parser.add_argument(
        "--no-prompt",
        action="store_true",
        help="Do not prompt on ambiguity when summary-mode is used",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project_mode = "create" if args.create_project else "update"

    ingest_helper_output(
        input_path=args.input,
        project_file_path=args.project_file,
        workflow_name=args.workflow_name,
        project_mode=project_mode,
        mode=args.mode,
        workflow_type=args.workflow_type,
        intent=args.intent,
        no_prompt=args.no_prompt,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
