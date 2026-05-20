from __future__ import annotations

from dotenv import load_dotenv

from src.knowledge.locator_registry import build_registry_prompt_context, get_locator_profile
from src.llm.ollama_client import chat_with_ollama
from src.llm.prompts import locator_system_prompt
from src.mcp.snapshot_artifact import require_valid_mcp_snapshot
from src.use_cases.use_case_manager import get_use_case_paths, load_use_case_config, parse_use_case_args
from src.utils.file_utils import file_exists, read_text_file, resolve_project_path, write_text_file
from src.utils.logger import error, info


def build_confirmation_todos(use_case_name: str) -> str:
    if use_case_name == "part_creation":
        todo_lines = [
            "- TODO: Confirm the login form labels against the live Teamcenter UI before promoting these locators to the page objects.",
            "- TODO: Confirm the exact Part Creation entry point in the home shell or menu drawer.",
            "- TODO: Confirm whether Part Type is a combobox, searchable dropdown, or native select.",
            "- TODO: Confirm the exact success toast or banner shown after saving a new part.",
        ]
    elif use_case_name == "bom_creation":
        todo_lines = [
            "- TODO: Confirm the exact BOM creation entry point in the Teamcenter navigation shell.",
            "- TODO: Confirm whether parent and child item selectors are free-text, search dialogs, or structured pickers.",
            "- TODO: Confirm how quantity and unit fields behave for editable BOM lines.",
            "- TODO: Confirm the save confirmation banner or status region after creating the BOM.",
        ]
    else:
        todo_lines = [
            "- TODO: Confirm the primary navigation entry point for this Teamcenter use case.",
            "- TODO: Confirm each form field type and accessible label in the live UI.",
            "- TODO: Confirm the success indicator shown after saving the record.",
            "- TODO: Confirm the validation and search surfaces used to verify the record afterward.",
        ]

    return "\n".join(["## Browser Confirmation TODOs", "", *todo_lines])


def main() -> None:
    load_dotenv()
    args = parse_use_case_args("Generate locator candidates for a selected Teamcenter use case.")
    use_case_paths = get_use_case_paths(args.use_case)
    use_case_config = load_use_case_config(args.use_case)
    test_plan_path = use_case_paths.test_plan_path
    mcp_snapshot_path = use_case_paths.mcp_snapshot_path
    locator_knowledge_path = resolve_project_path("src", "knowledge", "teamcenterLocators.md")
    output_path = use_case_paths.locator_candidates_path

    test_plan = read_text_file(test_plan_path)
    if not file_exists(mcp_snapshot_path):
        raise RuntimeError(
            "Playwright MCP snapshot file is missing. Run `python -m src.agents.mcp_snapshot_agent` before locator generation."
        )

    registry_context = build_registry_prompt_context()
    mcp_snapshot = require_valid_mcp_snapshot(
        read_text_file(mcp_snapshot_path),
        "Locator generation",
    )
    locator_knowledge = (
        read_text_file(locator_knowledge_path)
        if file_exists(locator_knowledge_path)
        else "No existing locator knowledge file was found."
    )

    info(
        "Generating Teamcenter locator candidates from the test plan, structured locator registry, "
        "locator knowledge, and required MCP snapshot."
    )
    response = chat_with_ollama(
        [
            {"role": "system", "content": locator_system_prompt},
            {
                "role": "user",
                "content": "\n".join(
                    [
                        (
                            "Use the following Teamcenter test plan and locator knowledge to propose "
                            f"stable Python Playwright locators for the `{use_case_config['displayName']}` use case."
                        ),
                        "",
                        "## Test Plan",
                        test_plan,
                        "",
                        "## Existing Locator Knowledge",
                        locator_knowledge,
                        "",
                        f"## Structured Locator Registry Profile\n{get_locator_profile()}",
                        "",
                        registry_context,
                        "",
                        "## Required Playwright MCP Browser Snapshot",
                        mcp_snapshot,
                    ]
                ),
            },
        ]
    )

    confirmation_todos = build_confirmation_todos(use_case_paths.use_case_name)

    write_text_file(output_path, response.strip() + "\n\n" + confirmation_todos + "\n")
    info(f"Saved locator candidates to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as caught:
        error(f"Locator agent failed: {caught}")
        raise
