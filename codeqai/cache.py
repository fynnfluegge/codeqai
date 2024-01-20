import json
import os
import platform
from pathlib import Path
from typing import Dict


class VectorCache:
    def __init__(self, filename, vector_ids, commit_hash):
        self.filename = filename
        self.vector_ids = vector_ids
        self.commit_hash = commit_hash

    @classmethod
    def from_json(cls, json_data) -> "VectorCache":
        filename = json_data.get("filename")
        vector_ids = json_data.get("vector_ids", [])
        commit_hash = json_data.get("commit_hash", "")
        return cls(filename, vector_ids, commit_hash)

    def to_json(self):
        return {
            "filename": self.filename,
            "commit_hash": self.commit_hash,
            "vector_ids": self.vector_ids,
        }


def load_vector_cache(filename) -> Dict[str, VectorCache]:
    with open(
        get_cache_path() + "/" + filename, "r", encoding="utf-8"
    ) as vector_cache_file:
        vector_cache_json = json.load(vector_cache_file)
    vector_cache = {}
    for key, value in vector_cache_json.items():
        vector_cache[key] = VectorCache.from_json(value)
    return vector_cache


def save_vector_cache(vector_cache, filename):
    with open(
        get_cache_path() + "/" + filename, "w", encoding="utf-8"
    ) as vector_cache_file:
        json.dump(vector_cache, default=VectorCache.to_json, fp=vector_cache_file)


def get_cache_path():
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, ".cache", "codeqai")
    elif system == "Windows":
        user_home = os.path.expanduser("~")
        cache_dir = os.path.join(user_home, "AppData", "Local", "codeqai")
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

    return cache_dir


def create_cache_dir():
    if not os.path.exists(get_cache_path()):
        path = Path(get_cache_path())
        path.mkdir(parents=True, exist_ok=True)
