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

import asyncio
from typing import Dict, List, Tuple

import aiohttp

from utils.helpers import clean_single_line


class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, timeout_seconds: int = 25) -> None:
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds
        self.models: List[str] = [
            "liquid/lfm-2.5-1.2b-thinking:free",
            "liquid/lfm-2.5-1.2b:free",
            "stepfun-ai/step-3.5-flash:free",
        ]

        # This prompt is intentionally detailed to align model output with the local
        # command validator. If the model violates these constraints, JARVIS will block.
        self.system_prompt = (
            "You are JARVIS, an AI Windows CMD assistant running in cmd.exe on Windows 10/11.\n"
            "Your job: convert the user's natural-language request into EXACTLY ONE safe Windows CMD command.\n"
            "\n"
            "OUTPUT FORMAT (MANDATORY):\n"
            "- Output ONLY the raw command\n"
            "- NO explanations, NO markdown, NO backticks\n"
            "- Single line only\n"
            "- DO NOT output multiple commands\n"
            "\n"
            "SAFETY AND VALIDATION (CRITICAL):\n"
            "- Your output will be validated and blocked if it contains chaining, redirection, pipes, or suspicious tokens.\n"
            "- NEVER include any of these tokens/characters: &&, ||, |, >, >>, <, ;, ^, %, .., $(), `, { }, [ ]\n"
            "- NEVER output: cmd /c, powershell, curl, wget, del, erase, rd, rmdir, format, shutdown, reg, sc, diskpart, bcdedit, wmic, vssadmin, fsutil, takeown, icacls\n"
            "- Do not attempt encoded or obfuscated commands (base64/hex blobs).\n"
            "\n"
            "RISK POLICY:\n"
            "- If the user request is unsafe, destructive, illegal, privacy-invasive, credential-harvesting, persistence/backdoor related, or unclear: output EXACTLY:\n"
            "  echo I cannot process that request, sir\n"
            "\n"
            "PREFERRED SAFE COMMANDS (when applicable):\n"
            "- Prefer read-only, diagnostic, and informational commands that do not modify the system.\n"
            "- Examples: dir, cd, type, echo, where, whoami, hostname, ipconfig, ping, systeminfo, tasklist, ver\n"
            "\n"
            "QUALITY RULES:\n"
            "- Use CMD syntax (not PowerShell).\n"
            "- Be specific and minimal: choose the single most direct command that satisfies the request.\n"
            "- If the user asks about JARVIS itself, respond with a safe CMD output using echo (no redirection).\n"
        )

    async def _post_with_retry(
        self, session: aiohttp.ClientSession, payload: Dict, retries: int = 3
    ) -> Dict:
        delay = 1
        for attempt in range(1, retries + 1):
            try:
                async with session.post(self.BASE_URL, json=payload) as response:
                    if response.status == 401:
                        raise RuntimeError("Invalid API key (401)")
                    if response.status == 429:
                        if attempt == retries:
                            raise RuntimeError("Rate limited (429) after retries")
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    if response.status >= 500:
                        if attempt == retries:
                            raise RuntimeError(f"Server error ({response.status})")
                        await asyncio.sleep(delay)
                        delay *= 2
                        continue
                    if response.status >= 400:
                        body = await response.text()
                        raise RuntimeError(f"API error {response.status}: {body}")

                    return await response.json()
            except asyncio.TimeoutError:
                if attempt == retries:
                    raise RuntimeError("API timeout")
                await asyncio.sleep(delay)
                delay *= 2
            except aiohttp.ClientError as exc:
                if attempt == retries:
                    raise RuntimeError(f"Network failure: {exc}")
                await asyncio.sleep(delay)
                delay *= 2
        raise RuntimeError("Unknown API failure")

    @staticmethod
    def _extract_command(data: Dict) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise RuntimeError("Empty/invalid API response")

        if not isinstance(content, str):
            raise RuntimeError("Non-text API output")

        line = clean_single_line(content)
        if not line:
            raise RuntimeError("Model returned empty command")

        return line.splitlines()[0].strip()

    async def validate_api_key(self) -> bool:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        payload = {
            "model": self.models[0],
            "messages": [{"role": "user", "content": "echo key_validation"}],
            "temperature": 0.0,
            "max_tokens": 8,
        }

        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            _ = await self._post_with_retry(session, payload)
        return True

    async def generate_command(self, user_input: str) -> Tuple[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
            last_error = ""
            for model in self.models:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    "temperature": 0.1,
                }
                try:
                    data = await self._post_with_retry(session, payload)
                    command = self._extract_command(data)
                    return command, model
                except Exception as exc:
                    last_error = str(exc)
                    continue

        raise RuntimeError(last_error or "All models failed")
