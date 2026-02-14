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

import subprocess
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    return_code: int
    stdout: str
    stderr: str
    status: str


class CommandExecutor:
    def __init__(self, timeout_seconds: int = 60) -> None:
        self.timeout_seconds = timeout_seconds

    def execute(self, command: str) -> ExecutionResult:
        try:
            completed = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            status = "success" if completed.returncode == 0 else "failed"
            return ExecutionResult(
                return_code=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
                status=status,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                return_code=124,
                stdout="",
                stderr=f"Command timed out after {self.timeout_seconds}s",
                status="timeout",
            )
        except Exception as exc:
            return ExecutionResult(
                return_code=1,
                stdout="",
                stderr=f"Execution error: {exc}",
                status="error",
            )
