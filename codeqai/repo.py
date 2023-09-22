import os

from git.repo import Repo


def get_git_root(path):
    git_repo = Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return git_root


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
]
