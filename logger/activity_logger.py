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

import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

from utils.helpers import utc_timestamp


class ActivityLogger:
    def __init__(self, log_file: str = "jarvis_logs.txt", max_bytes: int = 10 * 1024 * 1024) -> None:
        self.log_file = log_file
        self.logger = logging.getLogger("jarvis_activity")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()

        handler = RotatingFileHandler(self.log_file, maxBytes=max_bytes, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.privacy_mode = False

    def set_privacy_mode(self, enabled: bool) -> None:
        self.privacy_mode = bool(enabled)

    def log_event(self, payload: Dict[str, Any]) -> None:
        if self.privacy_mode:
            payload = dict(payload)
            for k in ("user_input", "generated_command", "command_output"):
                if k in payload:
                    payload[k] = "[REDACTED]"

        event = {"timestamp": utc_timestamp(), **payload}
        self.logger.info(json.dumps(event, ensure_ascii=False))

    def current_size_mb(self) -> float:
        if not os.path.exists(self.log_file):
            return 0.0
        return round(os.path.getsize(self.log_file) / (1024 * 1024), 2)
