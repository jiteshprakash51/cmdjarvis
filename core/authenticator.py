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

import getpass
import sys
from typing import Optional


class Authenticator:
    def __init__(self, max_attempts: int = 3) -> None:
        self.max_attempts = max_attempts

    @staticmethod
    def _prompt_masked(label: str) -> str:
        # Some terminals/runners do not support getpass properly.
        # Fall back to visible input if masking is not possible.
        try:
            return getpass.getpass(label)
        except (EOFError, KeyboardInterrupt):
            raise
        except Exception:
            if not sys.stdin or not sys.stdin.isatty():
                raise
            return input(label)

    @staticmethod
    def _is_valid_api_key(value: str) -> bool:
        key = value.strip()
        return key.startswith("sk-or-v1-") and len(key) >= 20

    def prompt_api_key(self, label: str = "Enter OpenRouter API key: ") -> Optional[str]:
        for attempt in range(1, self.max_attempts + 1):
            try:
                entered = self._prompt_masked(label).strip()
            except (EOFError, KeyboardInterrupt):
                return None
            if self._is_valid_api_key(entered):
                return entered
            print(f"Invalid API key format ({attempt}/{self.max_attempts})")
        return None

    def create_password(
        self,
        new_label: str = "Create password: ",
        confirm_label: str = "Confirm password: ",
    ) -> Optional[str]:
        for attempt in range(1, self.max_attempts + 1):
            try:
                password = self._prompt_masked(new_label)
                confirm = self._prompt_masked(confirm_label)
            except (EOFError, KeyboardInterrupt):
                return None
            if len(password) < 6:
                print("Password must be at least 6 characters.")
                continue
            if password != confirm:
                print(f"Password mismatch ({attempt}/{self.max_attempts})")
                continue
            return password
        return None

    def authenticate_password(self, verify_callback, label: str = "Enter password: ") -> bool:
        for attempt in range(1, self.max_attempts + 1):
            try:
                entered = self._prompt_masked(label)
            except (EOFError, KeyboardInterrupt):
                return False
            if verify_callback(entered):
                return True
            print(f"Authentication failed ({attempt}/{self.max_attempts})")
        return False

    def secondary_authenticate(self, verify_callback) -> bool:
        try:
            entered = self._prompt_masked("High-risk action. Enter password: ")
        except (EOFError, KeyboardInterrupt):
            return False
        return verify_callback(entered)
