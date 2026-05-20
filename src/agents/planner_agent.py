from __future__ import annotations

from dotenv import load_dotenv

from src.llm.ollama_client import chat_with_ollama
from src.llm.prompts import planner_system_prompt
from src.use_cases.use_case_manager import get_use_case_paths, parse_use_case_args
from src.utils.file_utils import read_text_file, write_text_file
from src.utils.logger import error, info


def main() -> None:
    load_dotenv()
    args = parse_use_case_args("Generate a structured Teamcenter test plan for a selected use case.")
    use_case_paths = get_use_case_paths(args.use_case)
    manual_steps_path = use_case_paths.manual_steps_path
    output_path = use_case_paths.test_plan_path

    info(f"Reading manual steps from {manual_steps_path}")
    manual_steps = read_text_file(manual_steps_path)

    response = chat_with_ollama(
        [
            {"role": "system", "content": planner_system_prompt},
            {
                "role": "user",
                "content": (
                    "Create a structured Teamcenter test plan from the following manual test steps:\n\n"
                    f"{manual_steps}"
                ),
            },
        ]
    )

    write_text_file(output_path, response.strip() + "\n")
    info(f"Saved generated test plan to {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as caught:
        error(f"Planner agent failed: {caught}")
        raise
