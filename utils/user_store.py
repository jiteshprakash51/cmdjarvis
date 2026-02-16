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
import stat
import platform
from typing import Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class UserStore:
    def __init__(self, path: str = "jarvis_user.json") -> None:
        self.path = path
        self.encryption_salt_key = "jarvis_encryption"  # Fixed salt for key derivation

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> Optional[Dict[str, str]]:
        if not self.exists():
            return None
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        required = {"api_key", "password_hash", "password_salt"}
        if not required.issubset(set(data.keys())):
            return None
        return data

    def delete_profile(self) -> None:
        if self.exists():
            self._secure_delete(self.path)

    @staticmethod
    def _secure_delete(file_path: str) -> None:
        """Securely delete file by overwriting before deletion."""
        try:
            # Overwrite file with random data before deletion
            file_size = os.path.getsize(file_path)
            with open(file_path, "wb") as f:
                f.write(os.urandom(file_size))
            os.remove(file_path)
        except Exception:
            # Fallback: just delete if overwrite fails
            os.remove(file_path)

    def _derive_encryption_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.encryption_salt_key.encode("utf-8"),
            iterations=100000,
        )
        key = kdf.derive(password.encode("utf-8"))
        return base64.urlsafe_b64encode(key)

    def _encrypt_api_key(self, api_key: str, password: str) -> str:
        """Encrypt API key using password-derived key."""
        encryption_key = self._derive_encryption_key(password)
        cipher = Fernet(encryption_key)
        encrypted = cipher.encrypt(api_key.encode("utf-8"))
        return base64.b64encode(encrypted).decode("ascii")

    def _decrypt_api_key(self, encrypted_api_key: str, password: str) -> str:
        """Decrypt API key using password-derived key."""
        try:
            encryption_key = self._derive_encryption_key(password)
            cipher = Fernet(encryption_key)
            encrypted_bytes = base64.b64decode(encrypted_api_key)
            decrypted = cipher.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception:
            raise ValueError("Failed to decrypt API key. Password may be incorrect.")

    @staticmethod
    def _build_password_hash(password: str) -> Dict[str, str]:
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200000)
        return {
            "password_hash": base64.b64encode(key).decode("ascii"),
            "password_salt": base64.b64encode(salt).decode("ascii"),
        }

    @staticmethod
    def _set_file_permissions(file_path: str) -> None:
        """Set strict file permissions (Windows & Unix compatible)."""
        try:
            if platform.system() == "Windows":
                # Windows: Remove all permissions and grant only to current user
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
            else:
                # Unix: Owner read/write only (600)
                os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        except Exception as e:
            print(f"Warning: Could not set strict file permissions: {e}")

    def save(self, api_key: str, password: str) -> None:
        password_data = self._build_password_hash(password)
        encrypted_api_key = self._encrypt_api_key(api_key, password)
        payload = {
            "api_key": encrypted_api_key,
            "password_hash": password_data["password_hash"],
            "password_salt": password_data["password_salt"],
        }
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=True)
        self._set_file_permissions(self.path)

    def update_api_key(self, new_api_key: str, password: str) -> None:
        data = self.load()
        if not data:
            raise RuntimeError("User profile missing")
        encrypted_api_key = self._encrypt_api_key(new_api_key, password)
        data["api_key"] = encrypted_api_key
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=True)
        self._set_file_permissions(self.path)

    def update_password(self, old_password: str, new_password: str) -> None:
        data = self.load()
        if not data:
            raise RuntimeError("User profile missing")
        # Decrypt API key with old password, re-encrypt with new password
        try:
            old_encrypted_api_key = data["api_key"]
            api_key = self._decrypt_api_key(old_encrypted_api_key, old_password)
            new_encrypted_api_key = self._encrypt_api_key(api_key, new_password)
            password_data = self._build_password_hash(new_password)
            data["api_key"] = new_encrypted_api_key
            data["password_hash"] = password_data["password_hash"]
            data["password_salt"] = password_data["password_salt"]
            with open(self.path, "w", encoding="utf-8") as handle:
                json.dump(data, handle, ensure_ascii=True)
            self._set_file_permissions(self.path)
        except Exception as e:
            raise RuntimeError(f"Failed to update password: {e}")

    def get_decrypted_api_key(self, password: str) -> Optional[str]:
        """Load and decrypt API key. Returns None on failure."""
        data = self.load()
        if not data:
            return None
        try:
            return self._decrypt_api_key(data["api_key"], password)
        except Exception:
            return None

    @staticmethod
    def verify_password(entered_password: str, password_hash: str, password_salt: str) -> bool:
        salt = base64.b64decode(password_salt.encode("ascii"))
        expected = base64.b64decode(password_hash.encode("ascii"))
        computed = hashlib.pbkdf2_hmac("sha256", entered_password.encode("utf-8"), salt, 200000)
        return hmac.compare_digest(expected, computed)
