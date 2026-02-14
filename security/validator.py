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

import re
from dataclasses import dataclass

from security.blacklist import BLACKLIST_KEYWORDS, HIGH_PRIV_COMMANDS, HIGH_PRIV_PATH_KEYWORDS


@dataclass
class ValidationResult:
    allowed: bool
    reason: str
    normalized_command: str
    risk_level: str


class CommandValidator:
    def __init__(self) -> None:
        self.block_tokens = [
            "&&",
            "||",
            "|",
            ">>",
            ">",
            "<",
            "^",
            "%",
            "..",
            "$()",
            "`",
            "{",
            "}",
            "[",
            "]",
            "cmd /c",
            "powershell -c",
        ]
        self.block_regex = [
            re.compile(r"\b[a-zA-Z0-9+/]{40,}={0,2}\b"),
            re.compile(r"\b(?:0x)?[a-fA-F0-9]{32,}\b"),
            re.compile(r"[\r\n]"),
            re.compile(r";"),
        ]

    def _normalize(self, command: str) -> str:
        return " ".join(command.strip().split())

    def _contains_blacklist(self, command: str) -> bool:
        cmd = command.lower()
        for keyword in BLACKLIST_KEYWORDS:
            if keyword in cmd:
                return True
        return False

    def is_high_privilege(self, command: str) -> bool:
        cmd = command.lower().strip()
        for prefix in HIGH_PRIV_COMMANDS:
            if cmd.startswith(prefix + " ") or cmd == prefix:
                return True
        for path_word in HIGH_PRIV_PATH_KEYWORDS:
            if path_word in cmd:
                return True
        return False

    def validate(self, command: str) -> ValidationResult:
        normalized = self._normalize(command)
        if not normalized:
            return ValidationResult(False, "Empty command", normalized, "HIGH")

        if "\n" in command or "\r" in command:
            return ValidationResult(False, "Multi-line output blocked", normalized, "HIGH")

        lower_cmd = normalized.lower()

        for token in self.block_tokens:
            if token in lower_cmd:
                return ValidationResult(False, f"Blocked token detected: {token}", normalized, "HIGH")

        for pattern in self.block_regex:
            if pattern.search(normalized):
                return ValidationResult(False, "Encoded or chained command pattern blocked", normalized, "HIGH")

        if self._contains_blacklist(normalized):
            return ValidationResult(False, "Blacklisted command detected", normalized, "HIGH")

        risk = "HIGH" if self.is_high_privilege(normalized) else "NORMAL"
        return ValidationResult(True, "Command validated", normalized, risk)
