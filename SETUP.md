# SETUP GUIDE

## 1. Prerequisites
- Windows 10/11
- Python 3.10 or newer
- OpenRouter account + API key

## 2. Installation
1. Open CMD in project folder.
2. Install dependencies:
   - `pip install -r requirements.txt`

## 3. Start JARVIS
- `python main.py`
- or run `start_jarvis.bat`

## 4. First-Run Setup
1. Enter your OpenRouter API key (masked input).
2. JARVIS verifies key validity by calling OpenRouter.
3. Create a password.
4. Confirm the password.
5. JARVIS stores API key + password hash locally in `jarvis_user.json`.

## 5. Returning User Login
- Enter your password (masked input).
- JARVIS auto-validates the stored API key at startup.
- Max attempts: 3

## 6. Account Management
- `account`: show account commands.
- `change api key`: verify password, validate new key online, then save.
- `change password`: verify current password, then set and confirm a new password.

## 7. Command Execution Security
- Type natural language requests in any language.
- JARVIS generates one CMD command.
- JARVIS validates command security.
- Review command and risk level.
- Confirm with `Y` to execute.
- High-risk commands require password re-entry.

Built-in commands:\r\n- create portfolio\r\n- `help`
- `account`
- `change api key`
- `change password`
- `history`
- `status`
- `exit`

## 8. Logs
- Primary log file: `jarvis_logs.txt`
- Auto-rotation at 10 MB.
- Includes timestamp, prompt, generated command, risk, result, output.

## 9. Troubleshooting
- Invalid key: re-enter a valid `sk-or-v1-...` key.
- Stored key rejected: run `change api key` or delete `jarvis_user.json` and run setup again.
- Rate limit errors: retries and backoff are automatic.
- Network failures: check internet/proxy/firewall.
- Timeout: reduce request complexity and retry.

