# Copyright 2026 Jitesh Prakash Chaudhary
# Website: https://jiteshprakash.netlify.app/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dataclasses import dataclass
from typing import Optional


BLOCKED_EXTENSIONS = {
    ".exe",
    ".dll",
    ".bat",
    ".cmd",
    ".ps1",
    ".vbs",
    ".js1",
    ".reg",
    ".msi",
    ".scr",
}

ALLOWED_EXTENSIONS = {
    ".html",
    ".css",
    ".js",
    ".md",
    ".txt",
    ".json",
    ".svg",
}


@dataclass
class PathCheck:
    allowed: bool
    reason: str
    absolute_path: str


class SafeFileOps:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = os.path.abspath(base_dir or os.getcwd())

    def _resolve_under_base(self, relative_path: str) -> PathCheck:
        rel = relative_path.strip().replace("/", os.sep)
        if not rel:
            return PathCheck(False, "Empty path", "")
        if os.path.isabs(rel):
            return PathCheck(False, "Absolute paths are not allowed", "")
        if ":" in rel:
            return PathCheck(False, "Drive paths are not allowed", "")

        abs_path = os.path.abspath(os.path.join(self.base_dir, rel))
        base = self.base_dir.rstrip("\\/") + os.sep
        if not (abs_path + os.sep).startswith(base) and abs_path != self.base_dir:
            return PathCheck(False, "Path escapes base directory", abs_path)
        if ".." in os.path.normpath(rel).split(os.sep):
            return PathCheck(False, "Path traversal is not allowed", abs_path)
        return PathCheck(True, "OK", abs_path)

    def mkdir(self, relative_dir: str) -> None:
        check = self._resolve_under_base(relative_dir)
        if not check.allowed:
            raise RuntimeError(check.reason)
        os.makedirs(check.absolute_path, exist_ok=True)

    def write_text_file(self, relative_path: str, content: str, overwrite: bool = False) -> None:
        check = self._resolve_under_base(relative_path)
        if not check.allowed:
            raise RuntimeError(check.reason)

        _, ext = os.path.splitext(check.absolute_path)
        ext = ext.lower()
        if ext in BLOCKED_EXTENSIONS:
            raise RuntimeError(f"Blocked file extension: {ext}")
        if ext and ext not in ALLOWED_EXTENSIONS:
            raise RuntimeError(f"File extension not allowed: {ext}")

        parent = os.path.dirname(check.absolute_path)
        os.makedirs(parent, exist_ok=True)

        if os.path.exists(check.absolute_path) and not overwrite:
            raise RuntimeError("File exists (overwrite disabled)")

        with open(check.absolute_path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)

    def dir_is_nonempty(self, relative_dir: str) -> bool:
        check = self._resolve_under_base(relative_dir)
        if not check.allowed:
            raise RuntimeError(check.reason)
        if not os.path.isdir(check.absolute_path):
            return False
        return any(os.scandir(check.absolute_path))
