from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .helper_output_adapter import ingest_helper_output


REQUIRED_FOLDERS = ("documents", "notebooks", "data_dictionary", "output")
DEFAULT_INPUT_FILES = (
    "output/full_service_report.json",
    "output/kmds_summary.json",
    "output/kmds_strategic_summary.json",
)


def _validate_structure(workspace: Path) -> None:
    missing = [name for name in REQUIRED_FOLDERS if not (workspace / name).is_dir()]
    if missing:
        raise ValueError(
            "Workspace is missing required folder(s): " + ", ".join(missing)
        )


def _discover_input_files(workspace: Path) -> list[Path]:
    discovered = [workspace / rel_path for rel_path in DEFAULT_INPUT_FILES if (workspace / rel_path).exists()]
    if discovered:
        return discovered

    raise ValueError(
        "No helper output files found. Expected at least one of: "
        + ", ".join(DEFAULT_INPUT_FILES)
    )


def run_kb_aggregation(
    *,
    workspace: Path,
    project_file: Path,
    workflow_name: str,
    mode: str,
    workflow_type: Optional[str],
) -> str:
    _validate_structure(workspace)
    input_files = _discover_input_files(workspace)

    print(f"--- KMDS Knowledge Graph Aggregation in {workspace} ---")
    print(f"Using helper output artifacts: {[p.name for p in input_files]}")

    for index, input_file in enumerate(input_files):
        project_mode = "create" if index == 0 and not project_file.exists() else "update"
        ingest_helper_output(
            input_path=str(input_file),
            project_file_path=str(project_file),
            workflow_name=workflow_name,
            project_mode=project_mode,
            mode=mode,
            workflow_type=workflow_type,
            no_prompt=True,
        )

    print(f"Knowledge graph written to: {project_file}")
    return str(project_file)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ingest kmds-helper output artifacts into a KMDS knowledge graph."
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Repository root containing documents, notebooks, data_dictionary, and output",
    )
    parser.add_argument(
        "--project-file",
        default="project_knowledge_graph.xml",
        help="Output KMDS knowledge graph path",
    )
    parser.add_argument(
        "--workflow-name",
        default="kmds_project_workflow",
        help="Workflow name used for KMDS ingestion",
    )
    parser.add_argument(
        "--mode",
        choices=["auto", "summary", "observations"],
        default="auto",
        help="How to ingest helper outputs",
    )
    parser.add_argument(
        "--workflow-type",
        choices=["application", "experimental"],
        default="application",
        help="Optional explicit workflow type",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    workspace = Path(args.workspace).resolve()
    project_file = Path(args.project_file)
    if not project_file.is_absolute():
        project_file = workspace / project_file

    run_kb_aggregation(
        workspace=workspace,
        project_file=project_file,
        workflow_name=args.workflow_name,
        mode=args.mode,
        workflow_type=args.workflow_type,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
