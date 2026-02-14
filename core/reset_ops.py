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

import glob
import os
import shutil
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ResetResult:
    deleted: List[str]
    skipped: List[Tuple[str, str]]  # (path, reason)


class ResetOps:
    def __init__(self, base_dir: str) -> None:
        self.base_dir = os.path.abspath(base_dir)

    def _under_base(self, path: str) -> bool:
        base = self.base_dir.rstrip("\\/") + os.sep
        ap = os.path.abspath(path)
        return ap == self.base_dir or ap.startswith(base)

    def _safe_delete_file(self, abs_path: str, result: ResetResult) -> None:
        if not self._under_base(abs_path):
            result.skipped.append((abs_path, "Escapes base dir"))
            return
        if not os.path.exists(abs_path):
            result.skipped.append((abs_path, "Not found"))
            return
        if os.path.isdir(abs_path):
            result.skipped.append((abs_path, "Is directory"))
            return
        os.remove(abs_path)
        result.deleted.append(abs_path)

    def _safe_delete_dir(self, abs_path: str, result: ResetResult) -> None:
        if not self._under_base(abs_path):
            result.skipped.append((abs_path, "Escapes base dir"))
            return
        if not os.path.exists(abs_path):
            result.skipped.append((abs_path, "Not found"))
            return
        if not os.path.isdir(abs_path):
            result.skipped.append((abs_path, "Not a directory"))
            return
        shutil.rmtree(abs_path)
        result.deleted.append(abs_path)

    def factory_reset(self) -> ResetResult:
        result = ResetResult(deleted=[], skipped=[])

        # Runtime state
        self._safe_delete_file(os.path.join(self.base_dir, "jarvis_user.json"), result)

        # Logs (including rotations)
        for p in glob.glob(os.path.join(self.base_dir, "jarvis_logs.txt*")):
            if os.path.isdir(p):
                continue
            self._safe_delete_file(p, result)

        # Generated projects
        self._safe_delete_dir(os.path.join(self.base_dir, "portfolio"), result)

        # Python caches
        for rel in [
            "__pycache__",
            os.path.join("ai", "__pycache__"),
            os.path.join("core", "__pycache__"),
            os.path.join("logger", "__pycache__"),
            os.path.join("security", "__pycache__"),
            os.path.join("utils", "__pycache__"),
        ]:
            self._safe_delete_dir(os.path.join(self.base_dir, rel), result)

        return result
