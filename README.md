# JARVIS - Windows AI CMD Assistant

JARVIS is a security-focused, online-only AI assistant for Windows CMD. It converts natural language into one CMD command using OpenRouter free models and executes only after strict validation and user confirmation.

Made by Jitesh Prakash Chaudhary
Website: https://jiteshprakash.netlify.app/

## Highlights
- Online-only: uses OpenRouter (no local AI models)
- One-command policy: generates exactly one CMD command per request
- Multi-layer validation: blocks chaining, redirection, encoded payloads, and blacklisted tools
- Interactive safety: shows the command + risk level and asks Y/N before executing
- First-run setup: API key verification + local password creation
- Account controls: change API key, change password, reset account, factory reset
- Privacy mode: redact prompts/commands/output in logs
- Dry-run mode: preview generated commands without executing
- Built-in project wizard: `create portfolio` generates a static site into `./portfolio`

## Allowed Models
JARVIS uses only these OpenRouter free models (with fallback):
- `liquid/lfm-2.5-1.2b-thinking:free`
- `liquid/lfm-2.5-1.2b:free`
- `stepfun-ai/step-3.5-flash:free`

## Quick Start
1. Install Python 3.10+.
2. Run `start_jarvis.bat` or:
   - `pip install -r requirements.txt`
   - `python main.py`
3. First run:
   - Enter OpenRouter API key (masked).
   - JARVIS verifies the key online.
   - Create and confirm a local password.

## Commands (In JARVIS)
Type `help` to see the live list. Common commands:
- `account`: show account options
- `change api key`: verify password, validate new key online, then save
- `change password`: verify current password, then set a new password
- `models`: show allowed models and last used
- `model status` / `model auto` / `model set <number|name>`: choose model preference
- `privacy on` / `privacy off` / `privacy status`: control log redaction
- `dryrun on` / `dryrun off` / `dryrun`: preview-only mode
- `create portfolio`: guided portfolio generator into `./portfolio`
- `doctor`: health check (profile + OpenRouter key validation)
- `lock` / `unlock`: lock session until password is entered
- `clear history`: clear in-memory session history
- `reset account`: delete local credentials (`jarvis_user.json`) with confirmation
- `factory reset`: wipe local state/logs/portfolio/caches with confirmation
- `exit` / `quit`: shutdown

## Security Notes
- JARVIS intentionally blocks many powerful commands and symbols (chaining, pipes, redirection, encodings). If you hit a block, rephrase your request as read-only/diagnostic.
- Password is stored as a salted PBKDF2-HMAC-SHA256 hash.
- API key is validated online before first save and again at startup.
- High-risk actions require password re-entry.

## Logging
- Logs are written to `jarvis_logs.txt` (rotated automatically).
- If you enable privacy mode (`privacy on`), logs remain but redact sensitive fields.

## Project Structure
- `main.py`
- `ai/openrouter_client.py`
- `core/authenticator.py`
- `core/executor.py`
- `core/file_ops.py`
- `core/reset_ops.py`
- `logger/activity_logger.py`
- `security/blacklist.py`
- `security/validator.py`
- `utils/helpers.py`
- `utils/user_store.py`
- `requirements.txt`
- `start_jarvis.bat`
- `SETUP.md`

## Public Repo Checklist
- Do not commit secrets: `.env` and `jarvis_user.json` are excluded by `.gitignore`.
- First run requires an OpenRouter API key and creates a local password.
- If you need a clean slate, use `factory reset` inside JARVIS.

## License
Licensed under the Apache License 2.0. See LICENSE and NOTICE.
