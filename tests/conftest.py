import subprocess
import sys

from tests.fixtures.vector_entries import (file_names, modified_vector_entries,
                                           vector_cache, vector_entries)


def pytest_configure(config):
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "faiss-cpu",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error during faiss installation: {e}")
