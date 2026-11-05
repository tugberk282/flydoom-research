import subprocess
import sys


def test_v2_reproduction_verification_command_passes():
    completed = subprocess.run(
        [sys.executable, "scripts/reproduce_publication_v2.py", "--skip-tests"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert '"status": "passed"' in completed.stdout
    assert '"evidence_records": 14' in completed.stdout
    assert '"v2_extension_figures": 2' in completed.stdout
