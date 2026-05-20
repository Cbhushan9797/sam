from __future__ import annotations

from dotenv import load_dotenv

from src.llm.ollama_client import chat_with_ollama
from src.llm.prompts import healer_system_prompt
from src.use_cases.use_case_manager import get_use_case_paths, parse_use_case_args
from src.utils.file_utils import file_exists, read_text_file, write_text_file
from src.utils.logger import error, info, warn


def read_optional_file(file_path, fallback_message: str) -> str:
    if not file_exists(file_path):
        return fallback_message
    return read_text_file(file_path)


def main() -> None:
    load_dotenv()
    args = parse_use_case_args("Generate healing suggestions for a selected Teamcenter use case.")
    use_case_paths = get_use_case_paths(args.use_case)
    generated_code_path = use_case_paths.generated_code_path
    execution_log_path = use_case_paths.execution_log_path
    execution_report_path = use_case_paths.execution_report_path
    output_path = use_case_paths.healing_suggestions_path

    generated_code = read_optional_file(
        generated_code_path,
        "No generated Python Playwright file is available yet.",
    )
    execution_log = read_optional_file(
        execution_log_path,
        "No saved execution log is available yet.",
    )
    execution_report = read_optional_file(
        execution_report_path,
        "No execution report is available yet.",
    )

    if not file_exists(execution_report_path):
        warn("Healing was requested before an execution report was generated. Proceeding with limited context.")

    info("Generating healing suggestions from the available failure context.")
    response = chat_with_ollama(
        [
            {"role": "system", "content": healer_system_prompt},
            {
                "role": "user",
                "content": "\n".join(
                    [
                        "Analyze the following Teamcenter Python Playwright failure context and suggest fixes.",
                        "",
                        "## Generated Playwright Code",
                        generated_code,
                        "",
                        "## Latest Execution Log",
                        execution_log,
                        "",
                        "## Execution Report",
                        execution_report,
                    ]
                ),
            },
        ]
    )

    write_text_file(output_path, response.strip() + "\n")
    info(f"Saved healing suggestions to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as caught:
        error(f"Healer agent failed: {caught}")
        raise
