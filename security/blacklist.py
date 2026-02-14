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

from typing import List

BLACKLIST_KEYWORDS: List[str] = [
    "del",
    "erase",
    "rd",
    "rmdir",
    "format",
    "shutdown",
    "taskkill",
    "reg",
    "net user",
    "net localgroup",
    "powershell",
    "curl",
    "wget",
    "sc",
    "bcdedit",
    "diskpart",
    "cipher",
    "attrib",
    "takeown",
    "icacls",
    "vssadmin",
    "wmic",
    "fsutil",
]

HIGH_PRIV_COMMANDS: List[str] = [
    "net",
    "sc",
    "taskkill",
    "schtasks",
    "wmic",
    "reg",
    "takeown",
    "icacls",
]

HIGH_PRIV_PATH_KEYWORDS: List[str] = [
    "system32",
    "c:\\windows",
    "program files",
    "programdata",
    "boot",
]
