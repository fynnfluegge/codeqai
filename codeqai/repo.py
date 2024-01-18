import os
import subprocess

from git.repo import Repo


def get_git_root(path):
    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


def find_file_in_git_repo(file_name):
    git_root = get_git_root(os.getcwd())

    for root, dirs, files in os.walk(git_root):
        if any(blacklist in root for blacklist in BLACKLIST_DIR):
            continue
        for file in files:
            if file == file_name:
                return os.path.join(root, file)


def load_files():
    git_root = get_git_root(os.getcwd())
    file_list = []

    for root, dirs, files in os.walk(git_root):
        if any(blacklist in root for blacklist in BLACKLIST_DIR):
            continue
        for file in files:
            file_ext = os.path.splitext(file)[1]
            if any(whitelist == file_ext for whitelist in WHITELIST_FILES):
                file_list.append(os.path.join(root, file))

    return file_list


def get_commit_hash(file_path):
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
]
