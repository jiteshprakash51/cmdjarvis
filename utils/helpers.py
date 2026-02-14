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
import re
from datetime import datetime
from typing import Optional


def utc_timestamp() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def mask_secret(secret: str, visible: int = 3) -> str:
    if not secret:
        return ""
    if len(secret) <= visible:
        return "*" * len(secret)
    return "*" * (len(secret) - visible) + secret[-visible:]


def clean_single_line(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\r", " ").replace("\n", " ")).strip()


def safe_truncate(text: str, limit: int = 4000) -> str:
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]"


def file_size_mb(path: str) -> Optional[float]:
    if not os.path.exists(path):
        return None
    size_bytes = os.path.getsize(path)
    return round(size_bytes / (1024 * 1024), 2)
