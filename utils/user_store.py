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

import base64
import hashlib
import hmac
import json
import os
from typing import Dict, Optional


class UserStore:
    def __init__(self, path: str = "jarvis_user.json") -> None:
        self.path = path

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def delete_profile(self) -> None:
        if self.exists():
            os.remove(self.path)

    def load(self) -> Optional[Dict[str, str]]:
        if not self.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        required = {"api_key", "password_hash", "password_salt"}
        if not required.issubset(set(data.keys())):
            return None
        return data

    @staticmethod
    def _build_password_hash(password: str) -> Dict[str, str]:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
        return {
            "password_hash": base64.b64encode(key).decode("ascii"),
            "password_salt": base64.b64encode(salt).decode("ascii"),
        }

    def save(self, api_key: str, password: str) -> None:
        password_data = self._build_password_hash(password)
        payload = {
            "api_key": api_key,
            "password_hash": password_data["password_hash"],
            "password_salt": password_data["password_salt"],
        }
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True)

    def update_api_key(self, new_api_key: str) -> None:
        data = self.load()
        if not data:
            raise RuntimeError("User profile missing")
        data["api_key"] = new_api_key
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=True)

    def update_password(self, new_password: str) -> None:
        data = self.load()
        if not data:
            raise RuntimeError("User profile missing")
        password_data = self._build_password_hash(new_password)
        data["password_hash"] = password_data["password_hash"]
        data["password_salt"] = password_data["password_salt"]
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=True)

    @staticmethod
    def verify_password(entered_password: str, password_hash: str, password_salt: str) -> bool:
        salt = base64.b64decode(password_salt.encode("ascii"))
        expected = base64.b64decode(password_hash.encode("ascii"))
        computed = hashlib.pbkdf2_hmac("sha256", entered_password.encode("utf-8"), salt, 200000)
        return hmac.compare_digest(expected, computed)
