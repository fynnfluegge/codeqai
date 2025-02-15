import os
import subprocess

from git.repo import Repo


def repo_name():
    """
    Retrieves the name of the current Git repository.

    This function gets the root directory of the current Git repository based on the current working directory,
    and extracts the repository name from the root directory path.

    Returns:
        str: The name of the current Git repository.
    """
    return get_git_root(os.getcwd()).split("/")[-1]


def get_git_root(path):
    """
    Retrieves the root directory of the Git repository for the given path.

    Args:
        path (str): The path to a directory within the Git repository.

    Returns:
        str: The root directory of the Git repository.
    """
    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def find_file_in_git_repo(file_name):
    """
    Searches for a file with the given name in the current Git repository.

    Args:
        file_name (str): The name of the file to search for.

    Returns:
        str or None: The full path to the file if found, otherwise None.
    """
    git_root = get_git_root(os.getcwd())

    for root, dirs, files in os.walk(git_root):
        if any(blacklist in root for blacklist in BLACKLIST_DIR):
            continue
        for file in files:
            if file == file_name:
                return os.path.join(root, file)


def load_files():
    """
    Loads files from the current Git repository based on whitelist and blacklist criteria.

    This function walks through the directory structure of the Git repository,
    and collects files that match the whitelist extensions and are not in the blacklist directories or files.

    Returns:
        list: A list of file paths that meet the criteria.
    """
    git_root = get_git_root(os.getcwd())
    file_list = []

    for root, dirs, files in os.walk(git_root):
        if any(blacklist in root for blacklist in BLACKLIST_DIR):
            continue
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if any(whitelist == file_ext for whitelist in WHITELIST_FILES):
                if file not in BLACKLIST_FILES:
                    file_list.append(os.path.join(root, file))

    return file_list


def get_commit_hash(file_path):
    """
    Retrieves the latest commit hash for the specified file.

    Args:
        file_path (str): The path to the file for which to retrieve the commit hash.

    Returns:
        str or None: The latest commit hash if found, otherwise None.
    """
    try:
        # Run the git log command
        result = subprocess.run(
            ["git", "log", "-n", "1", "--pretty=format:%H", "--", file_path],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        )

        # Extract the commit hash from the command output
        commit_hash = result.stdout.strip()
        return commit_hash

    except subprocess.CalledProcessError as e:
        print(f"Error executing git command: {e}")
        return None


BLACKLIST_DIR = [
    "__pycache__",
    ".pytest_cache",
    ".venv",
    ".git",
    ".idea",
    "venv",
    "env",
    "node_modules",
    "dist",
    "build",
    ".vscode",
    ".github",
    ".gitlab",
    ".angular",
    "cdk.out",
    ".aws-sam",
    ".terraform",
]
WHITELIST_FILES = [
    ".js",
    ".mjs",
    ".ts",
    ".tsx",
    ".css",
    ".scss",
    ".less",
    ".html",
    ".htm",
    ".json",
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".cs",
    ".go",
    ".php",
    ".rb",
    ".rs",
    ".swift",
    ".kt",
    ".scala",
    ".m",
    ".h",
    ".sh",
    ".pl",
    ".pm",
    ".lua",
    ".sql",
    ".yaml",
    ".yml",
    ".rst",
    ".md",
    ".hs",
    ".rb",
]
BLACKLIST_FILES = [
    "package-lock.json",
    "package.json",
    "__init__.py",
]
