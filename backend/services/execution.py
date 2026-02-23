import subprocess
import json
from backend import config

def execute_script() -> dict:
    """
    Run tests/test.spec.js with Playwright and return JSON result or error.
    """
    test_file = str(config.TESTS_DIR / "test.spec.js")

    cmd = ["npx", "playwright", "test", test_file, "--reporter=json"]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=False
    )

    try:
        return json.loads(result.stdout)
    except Exception:
        return {
            "error": "Could not parse test result JSON.",
            "raw_output": result.stdout,
            "stderr": result.stderr,
        }

def execute_uploaded_script() -> dict:
    return execute_script()