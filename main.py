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
import sys
import time
from typing import Dict, List, Optional

from colorama import Fore, Style, init

from ai.openrouter_client import OpenRouterClient
from core.authenticator import Authenticator
from core.executor import CommandExecutor
from core.file_ops import SafeFileOps
from core.reset_ops import ResetOps
from logger.activity_logger import ActivityLogger
from security.validator import CommandValidator
from utils.helpers import safe_truncate
from utils.user_store import UserStore


MAKER = "Jitesh Prakash Chaudhary"
WEBSITE = "https://jiteshprakash.netlify.app/"


HELP_TEXT = """
Available commands:
  help                 Show this message
  history              Show session command history
  clear history        Clear session history
  status               Show session and system status

  account              Show account options
  change api key       Change stored OpenRouter API key
  change password      Change login password
  reset account        Delete local credentials (requires password + RESET)
  factory reset        Fresh start: wipe local state/logs/portfolio/caches (safe)

  models               Show allowed AI models and last used
  model status         Show model preference
  model auto           Reset model preference to AUTO
  model set <n|name>   Pin a preferred model

  privacy on/off       Redact prompts/commands/output in logs
  dryrun on/off        Preview only; do not execute commands

  doctor               Health check (profile + OpenRouter key validation)
  lock                 Lock this session (requires unlock)
  unlock               Unlock session with password

  create portfolio     Guided portfolio website generator into ./portfolio

  exit / quit          Graceful shutdown

All other input is sent to OpenRouter for command generation.
""".strip()


ACCOUNT_HELP = """
Account commands:
  change api key       Verify password, validate new key online, then save
  change password      Verify current password, then set a new password
  reset account        Delete local credentials (jarvis_user.json)
  factory reset        Wipe local state/logs/portfolio/caches
""".strip()

def print_banner() -> None:
    print(Fore.CYAN + "=" * 66)
    print(" JARVIS - Windows AI CMD Assistant (Online, Secure)")
    print(f" Made by {MAKER}")
    print(f" Website: {WEBSITE}")
    print("=" * 66 + Style.RESET_ALL)


def print_status(
    stats: Dict[str, int],
    history: List[str],
    logger_obj: ActivityLogger,
    started_at: float,
    *,
    privacy_mode: bool,
    dryrun_mode: bool,
    preferred_model: Optional[str],
    last_model: str,
) -> None:
    uptime = int(time.time() - started_at)
    print(Fore.YELLOW + "Session Status" + Style.RESET_ALL)
    print(f"Uptime: {uptime}s")
    print(f"Total inputs: {stats['total_inputs']}")
    print(f"Executed: {stats['executed']}")
    print(f"Blocked: {stats['blocked']}")
    print(f"Failed: {stats['failed']}")
    print(f"API errors: {stats['api_errors']}")
    print(f"High-risk prompts: {stats['high_risk']}")
    print(f"Dry runs: {stats.get('dry_run', 0)}")
    print(f"History size: {len(history)}")
    print(f"Privacy mode: {'ON' if privacy_mode else 'OFF'}")
    print(f"Dry-run mode: {'ON' if dryrun_mode else 'OFF'}")
    print(f"Model preference: {preferred_model if preferred_model else 'AUTO'}")
    print(f"Last model used: {last_model}")
    print(f"Log file size: {logger_obj.current_size_mb()} MB")


def apply_model_preference(ai_client: OpenRouterClient, preferred_model: Optional[str]) -> None:
    if not preferred_model:
        return
    if preferred_model not in ai_client.models:
        return
    ai_client.models = [preferred_model] + [m for m in ai_client.models if m != preferred_model]


def _ask(label: str, default: str = "") -> str:
    prompt = label
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    try:
        value = input(prompt).strip()
    except EOFError:
        return default
    return value if value else default

def create_portfolio_wizard(file_ops: SafeFileOps, logger_obj: ActivityLogger) -> None:
    print(Fore.CYAN + "Portfolio Generator" + Style.RESET_ALL)
    print("This will create a simple static portfolio in ./portfolio")

    try:
        if file_ops.dir_is_nonempty("portfolio"):
            confirm = input(Fore.YELLOW + "portfolio folder is not empty. Overwrite files? (Y/N): " + Style.RESET_ALL)
            if confirm.strip().lower() not in {"y", "yes"}:
                print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
                return
    except Exception as exc:
        print(Fore.RED + f"Portfolio check failed: {exc}" + Style.RESET_ALL)
        return

    name = _ask("Your name", MAKER)
    title = _ask("Title (e.g., Backend Engineer)", "Backend Engineer")
    tagline = _ask("Short tagline", "I build secure, reliable systems.")
    email = _ask("Contact email", "")
    primary = _ask("Primary color (hex)", "#0B3D91")

    projects: List[str] = []
    for i in range(1, 6):
        p = _ask(f"Project {i} (leave empty to stop)", "")
        if not p:
            break
        projects.append(p)

    project_items = "\n".join([f"        <li>{p}</li>" for p in projects]) or "        <li>Your first project</li>"

    index_html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{name} | Portfolio</title>
  <link rel=\"stylesheet\" href=\"styles.css\">
</head>
<body>
  <header class=\"hero\">
    <div class=\"hero-inner\">
      <div class=\"kicker\">JARVIS Portfolio</div>
      <h1>{name}</h1>
      <p class=\"title\">{title}</p>
      <p class=\"tagline\">{tagline}</p>
      <div class=\"cta\">
        <a class=\"btn\" href=\"#projects\">View Projects</a>
        <a class=\"btn btn-ghost\" href=\"#contact\">Contact</a>
      </div>
    </div>
  </header>

  <main class=\"wrap\">
    <section id=\"projects\" class=\"card\">
      <h2>Projects</h2>
      <ul class=\"projects\">
{project_items}
      </ul>
    </section>

    <section id=\"about\" class=\"card\">
      <h2>About</h2>
      <p>This site was generated locally by JARVIS.</p>
      <p>Made by {MAKER}. Website: <span class=\"mono\">{WEBSITE}</span></p>
    </section>

    <section id=\"contact\" class=\"card\">
      <h2>Contact</h2>
      <p>Email: <span class=\"mono\">{email if email else "add-your-email@example.com"}</span></p>
    </section>
  </main>

  <footer class=\"footer\">Generated by JARVIS</footer>
  <script src=\"script.js\"></script>
</body>
</html>
"""

    styles_css = f""":root {{
  --bg: #0b0f16;
  --fg: #e9eef6;
  --muted: rgba(233,238,246,0.7);
  --card: rgba(255,255,255,0.06);
  --border: rgba(255,255,255,0.14);
  --accent: {primary};
}}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  color: var(--fg);
  background:
    radial-gradient(900px 500px at 20% 10%, rgba(11,61,145,0.35), transparent 60%),
    radial-gradient(900px 500px at 80% 30%, rgba(0,160,180,0.25), transparent 60%),
    var(--bg);
}}

.hero {{ padding: 56px 18px 28px; }}
.hero-inner {{ max-width: 980px; margin: 0 auto; }}
.kicker {{ display: inline-block; padding: 6px 10px; border: 1px solid var(--border); border-radius: 999px; background: rgba(0,0,0,0.18); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }}

h1 {{ margin: 14px 0 4px; font-size: clamp(36px, 6vw, 62px); line-height: 1.05; }}
.title {{ margin: 0; color: var(--muted); font-weight: 600; }}
.tagline {{ margin: 14px 0 0; max-width: 68ch; opacity: 0.92; }}

.cta {{ margin-top: 18px; display: flex; gap: 10px; flex-wrap: wrap; }}
.btn {{ display: inline-block; padding: 10px 14px; border-radius: 10px; text-decoration: none; color: var(--fg); background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.04)); border: 1px solid var(--border); }}
.btn-ghost {{ background: transparent; }}

.wrap {{ max-width: 980px; margin: 0 auto; padding: 0 18px 48px; display: grid; gap: 14px; }}
.card {{ border: 1px solid var(--border); background: var(--card); border-radius: 16px; padding: 18px; backdrop-filter: blur(6px); }}

h2 {{ margin: 0 0 10px; font-size: 18px; }}
.projects {{ margin: 0; padding-left: 18px; }}

.mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
.footer {{ padding: 14px 18px 24px; text-align: center; color: var(--muted); }}
"""

    script_js = """(function () {
  const links = document.querySelectorAll('a[href^="#"]');
  for (const a of links) {
    a.addEventListener('click', function (e) {
      const id = a.getAttribute('href');
      const el = document.querySelector(id);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
})();
"""

    readme = """# Portfolio

Generated by JARVIS.

Open `index.html` in a browser.
"""

    try:
        file_ops.mkdir("portfolio")
        file_ops.write_text_file("portfolio/index.html", index_html, overwrite=True)
        file_ops.write_text_file("portfolio/styles.css", styles_css, overwrite=True)
        file_ops.write_text_file("portfolio/script.js", script_js, overwrite=True)
        file_ops.write_text_file("portfolio/README.md", readme, overwrite=True)
    except Exception as exc:
        print(Fore.RED + f"Portfolio creation failed: {exc}" + Style.RESET_ALL)
        return

    print(Fore.GREEN + "Portfolio created in ./portfolio" + Style.RESET_ALL)
    logger_obj.log_event(
        {
            "user_input": "create portfolio",
            "generated_command": "N/A",
            "risk_level": "NORMAL",
            "execution_result": "portfolio_created",
            "model": "none",
            "command_output": "Created portfolio files in ./portfolio",
        }
    )


def run_doctor(api_key: str, user_store: UserStore, logger_obj: ActivityLogger) -> None:
    print(Fore.CYAN + "JARVIS Doctor" + Style.RESET_ALL)
    profile_ok = user_store.load() is not None
    print(f"User profile: {'OK' if profile_ok else 'MISSING/CORRUPT'}")
    print(f"Log size: {logger_obj.current_size_mb()} MB")

    print("Testing OpenRouter API key...")
    client = OpenRouterClient(api_key=api_key)
    try:
        asyncio.run(client.validate_api_key())
        print(Fore.GREEN + "OpenRouter: OK" + Style.RESET_ALL)
    except Exception as exc:
        print(Fore.RED + f"OpenRouter: FAILED ({exc})" + Style.RESET_ALL)

def first_run_setup(authenticator: Authenticator, user_store: UserStore) -> str:
    print(Fore.YELLOW + "First-time setup detected." + Style.RESET_ALL)
    api_key = authenticator.prompt_api_key()
    if not api_key:
        raise RuntimeError("Access denied. Exiting.")

    print(Fore.CYAN + "Checking API key with OpenRouter..." + Style.RESET_ALL)
    client = OpenRouterClient(api_key=api_key)
    asyncio.run(client.validate_api_key())

    password = authenticator.create_password()
    if not password:
        raise RuntimeError("Password setup failed. Exiting.")

    user_store.save(api_key=api_key, password=password)
    print(Fore.GREEN + "Setup complete. Credentials saved for this user." + Style.RESET_ALL)
    return api_key


def existing_user_login(authenticator: Authenticator, user_store: UserStore) -> str:
    user_data = user_store.load()
    if not user_data:
        raise RuntimeError("User profile is missing or corrupted.")

    verified = authenticator.authenticate_password(
        lambda password: user_store.verify_password(
            password,
            user_data["password_hash"],
            user_data["password_salt"],
        )
    )
    if not verified:
        raise RuntimeError("Access denied. Exiting.")

    api_key = user_data["api_key"].strip()
    print(Fore.CYAN + "Checking stored API key with OpenRouter..." + Style.RESET_ALL)
    client = OpenRouterClient(api_key=api_key)
    asyncio.run(client.validate_api_key())

    return api_key


def verify_current_password(authenticator: Authenticator, user_store: UserStore, prompt: str) -> bool:
    user_data = user_store.load() or {}
    password_hash = user_data.get("password_hash", "")
    password_salt = user_data.get("password_salt", "")
    if not password_hash or not password_salt:
        return False
    return authenticator.authenticate_password(
        lambda password: user_store.verify_password(password, password_hash, password_salt),
        label=prompt,
    )


def handle_change_api_key(authenticator: Authenticator, user_store: UserStore, logger_obj: ActivityLogger) -> str:
    print(Fore.YELLOW + "Change API key requested." + Style.RESET_ALL)
    if not verify_current_password(authenticator, user_store, "Enter current password to change API key: "):
        print(Fore.RED + "Password verification failed." + Style.RESET_ALL)
        logger_obj.log_event(
            {
                "user_input": "change api key",
                "generated_command": "N/A",
                "risk_level": "HIGH",
                "execution_result": "account_change_denied",
                "model": "none",
                "command_output": "Password verification failed",
            }
        )
        return (user_store.load() or {}).get("api_key", "")

    new_key = authenticator.prompt_api_key("Enter new OpenRouter API key: ")
    if not new_key:
        print(Fore.RED + "API key update cancelled." + Style.RESET_ALL)
        return (user_store.load() or {}).get("api_key", "")

    print(Fore.CYAN + "Validating new API key with OpenRouter..." + Style.RESET_ALL)
    client = OpenRouterClient(api_key=new_key)
    try:
        asyncio.run(client.validate_api_key())
    except Exception as exc:
        print(Fore.RED + f"API key validation failed: {exc}" + Style.RESET_ALL)
        logger_obj.log_event(
            {
                "user_input": "change api key",
                "generated_command": "N/A",
                "risk_level": "HIGH",
                "execution_result": "account_change_failed",
                "model": "none",
                "command_output": f"API key validation failed: {exc}",
            }
        )
        return (user_store.load() or {}).get("api_key", "")

    user_store.update_api_key(new_key)
    print(Fore.GREEN + "API key updated successfully." + Style.RESET_ALL)
    logger_obj.log_event(
        {
            "user_input": "change api key",
            "generated_command": "N/A",
            "risk_level": "HIGH",
            "execution_result": "account_change_success",
            "model": "none",
            "command_output": "API key updated successfully",
        }
    )
    return new_key


def handle_change_password(authenticator: Authenticator, user_store: UserStore, logger_obj: ActivityLogger) -> None:
    print(Fore.YELLOW + "Change password requested." + Style.RESET_ALL)
    if not verify_current_password(authenticator, user_store, "Enter current password: "):
        print(Fore.RED + "Current password verification failed." + Style.RESET_ALL)
        logger_obj.log_event(
            {
                "user_input": "change password",
                "generated_command": "N/A",
                "risk_level": "HIGH",
                "execution_result": "account_change_denied",
                "model": "none",
                "command_output": "Current password verification failed",
            }
        )
        return

    new_password = authenticator.create_password("Create new password: ", "Confirm new password: ")
    if not new_password:
        print(Fore.RED + "Password update cancelled." + Style.RESET_ALL)
        return

    user_store.update_password(new_password)
    print(Fore.GREEN + "Password updated successfully." + Style.RESET_ALL)
    logger_obj.log_event(
        {
            "user_input": "change password",
            "generated_command": "N/A",
            "risk_level": "HIGH",
            "execution_result": "account_change_success",
            "model": "none",
            "command_output": "Password updated successfully",
        }
    )

def main() -> int:
    init(autoreset=True)
    print_banner()

    if not sys.stdin or not sys.stdin.isatty():
        print(Fore.RED + "Interactive terminal required. Run in CMD/PowerShell/Windows Terminal." + Style.RESET_ALL)
        return 1

    authenticator = Authenticator(max_attempts=3)
    user_store = UserStore(path="jarvis_user.json")

    try:
        if user_store.exists():
            api_key = existing_user_login(authenticator, user_store)
        else:
            api_key = first_run_setup(authenticator, user_store)
    except Exception as exc:
        print(Fore.RED + str(exc) + Style.RESET_ALL)
        return 1

    validator = CommandValidator()
    executor = CommandExecutor(timeout_seconds=90)
    logger_obj = ActivityLogger(log_file="jarvis_logs.txt")

    locked = False
    dryrun_mode = False
    privacy_mode = False
    preferred_model: Optional[str] = None
    last_model = "none"

    logger_obj.set_privacy_mode(privacy_mode)

    ai_client = OpenRouterClient(api_key=api_key)
    apply_model_preference(ai_client, preferred_model)

    file_ops = SafeFileOps()

    history: List[str] = []
    stats: Dict[str, int] = {
        "total_inputs": 0,
        "executed": 0,
        "blocked": 0,
        "failed": 0,
        "api_errors": 0,
        "high_risk": 0,
        "dry_run": 0,
    }
    started_at = time.time()

    print(Fore.GREEN + "Authentication successful. Type 'help' for options." + Style.RESET_ALL)

    while True:
        try:
            user_input = input(Fore.CYAN + "\nYou> " + Style.RESET_ALL).strip()
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nKeyboard interrupt received. Shutting down..." + Style.RESET_ALL)
            break
        except EOFError:
            print(Fore.YELLOW + "\nEOF received. Shutting down..." + Style.RESET_ALL)
            break

        if not user_input:
            continue

        stats["total_inputs"] += 1
        history.append(user_input)

        lowered = user_input.lower().strip()

        if locked and lowered not in {"help", "status", "unlock", "exit", "quit"}:
            print(Fore.YELLOW + "Session is locked. Type 'unlock' or 'help'." + Style.RESET_ALL)
            continue

        if lowered in {"exit", "quit"}:
            break

        if lowered == "help":
            print(HELP_TEXT)
            continue

        if lowered == "history":
            print(Fore.YELLOW + "Session History" + Style.RESET_ALL)
            for idx, item in enumerate(history, start=1):
                print(f"{idx}. {item}")
            continue

        if lowered in {"clear history", "clear"}:
            confirm = input(Fore.YELLOW + "Clear session history? (Y/N): " + Style.RESET_ALL).strip().lower()
            if confirm in {"y", "yes"}:
                history.clear()
                print(Fore.GREEN + "History cleared." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
            continue

        if lowered == "status":
            print_status(
                stats,
                history,
                logger_obj,
                started_at,
                privacy_mode=privacy_mode,
                dryrun_mode=dryrun_mode,
                preferred_model=preferred_model,
                last_model=last_model,
            )
            continue

        if lowered == "account":
            print(ACCOUNT_HELP)
            continue

        if lowered in {"change api key", "change key", "update api key"}:
            api_key = handle_change_api_key(authenticator, user_store, logger_obj)
            ai_client = OpenRouterClient(api_key=api_key)
            apply_model_preference(ai_client, preferred_model)
            continue

        if lowered in {"change password", "update password"}:
            handle_change_password(authenticator, user_store, logger_obj)
            continue

        if lowered in {"reset account", "reset"}:
            print(Fore.RED + "WARNING: This will delete local credentials (jarvis_user.json)." + Style.RESET_ALL)
            if not verify_current_password(authenticator, user_store, "Enter password to reset account: "):
                print(Fore.RED + "Password verification failed." + Style.RESET_ALL)
                continue
            confirm = input(Fore.YELLOW + "Type RESET to confirm: " + Style.RESET_ALL).strip()
            if confirm != "RESET":
                print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
                continue
            user_store.delete_profile()
            logger_obj.log_event(
                {
                    "user_input": "reset account",
                    "generated_command": "N/A",
                    "risk_level": "HIGH",
                    "execution_result": "account_reset",
                    "model": "none",
                    "command_output": "Deleted jarvis_user.json",
                }
            )
            print(Fore.YELLOW + "Account reset complete. Restart JARVIS to set up again." + Style.RESET_ALL)
            break

        if lowered in {"factory reset", "fresh start", "reset program"}:
            print(
                Fore.RED
                + "WARNING: Factory reset will delete: jarvis_user.json, jarvis_logs.txt*, ./portfolio, and __pycache__ folders."
                + Style.RESET_ALL
            )
            if not verify_current_password(authenticator, user_store, "Enter password to factory reset: "):
                print(Fore.RED + "Password verification failed." + Style.RESET_ALL)
                continue
            confirm = input(Fore.YELLOW + "Type FACTORY RESET to confirm: " + Style.RESET_ALL).strip()
            if confirm != "FACTORY RESET":
                print(Fore.YELLOW + "Cancelled." + Style.RESET_ALL)
                continue

            ops = ResetOps(base_dir=".")
            result = ops.factory_reset()
            logger_obj.log_event(
                {
                    "user_input": "factory reset",
                    "generated_command": "N/A",
                    "risk_level": "HIGH",
                    "execution_result": "factory_reset",
                    "model": "none",
                    "command_output": f"Deleted={len(result.deleted)} Skipped={len(result.skipped)}",
                }
            )
            print(Fore.YELLOW + "Factory reset complete. Restart JARVIS for a fresh first-run setup." + Style.RESET_ALL)
            break

        if lowered == "models":
            print(Fore.CYAN + "Allowed models:" + Style.RESET_ALL)
            for model_name in ai_client.models:
                print(f"- {model_name}")
            print(f"Preferred: {preferred_model if preferred_model else 'AUTO'}")
            print(f"Last used: {last_model}")
            continue

        if lowered.startswith("model"):
            parts = user_input.strip().split()
            if len(parts) == 1 or (len(parts) >= 2 and parts[1].lower() in {"status", "show"}):
                print(Fore.YELLOW + f"Model preference: {preferred_model if preferred_model else 'AUTO'}" + Style.RESET_ALL)
                print(Fore.CYAN + "Available:" + Style.RESET_ALL)
                for idx, model_name in enumerate(ai_client.models, start=1):
                    print(f"{idx}. {model_name}")
                continue

            sub = parts[1].lower()
            if sub == "auto":
                preferred_model = None
                ai_client = OpenRouterClient(api_key=api_key)
                apply_model_preference(ai_client, preferred_model)
                print(Fore.GREEN + "Model preference set to AUTO." + Style.RESET_ALL)
                continue

            if sub == "set" and len(parts) >= 3:
                choice = " ".join(parts[2:]).strip()
                selected = None
                if choice.isdigit():
                    i = int(choice)
                    if 1 <= i <= len(ai_client.models):
                        selected = ai_client.models[i - 1]
                else:
                    for mname in ai_client.models:
                        if choice.lower() in mname.lower():
                            selected = mname
                            break

                if not selected:
                    print(Fore.RED + "Invalid model selection. Use 'models' to list." + Style.RESET_ALL)
                    continue

                preferred_model = selected
                ai_client = OpenRouterClient(api_key=api_key)
                apply_model_preference(ai_client, preferred_model)
                print(Fore.GREEN + f"Preferred model set: {preferred_model}" + Style.RESET_ALL)
                continue

            print(Fore.YELLOW + "Usage: model status | model auto | model set <number|name>" + Style.RESET_ALL)
            continue

        if lowered.startswith("privacy"):
            if lowered in {"privacy on", "privacy enable", "privacy true"}:
                privacy_mode = True
                logger_obj.set_privacy_mode(privacy_mode)
                print(Fore.YELLOW + "Privacy mode ON: logs will be redacted." + Style.RESET_ALL)
            elif lowered in {"privacy off", "privacy disable", "privacy false"}:
                privacy_mode = False
                logger_obj.set_privacy_mode(privacy_mode)
                print(Fore.YELLOW + "Privacy mode OFF: full logs enabled." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Privacy mode: {'ON' if privacy_mode else 'OFF'}" + Style.RESET_ALL)
            continue

        if lowered.startswith("dryrun"):
            if lowered in {"dryrun on", "dryrun enable", "dryrun true"}:
                dryrun_mode = True
                print(Fore.YELLOW + "Dry-run ON: commands will NOT be executed." + Style.RESET_ALL)
            elif lowered in {"dryrun off", "dryrun disable", "dryrun false"}:
                dryrun_mode = False
                print(Fore.YELLOW + "Dry-run OFF: normal execution enabled." + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Dry-run: {'ON' if dryrun_mode else 'OFF'}" + Style.RESET_ALL)
            continue

        if lowered == "doctor":
            run_doctor(api_key, user_store, logger_obj)
            continue

        if lowered == "lock":
            locked = True
            print(Fore.YELLOW + "Session locked. Type 'unlock' to continue." + Style.RESET_ALL)
            continue

        if lowered == "unlock":
            if not locked:
                print(Fore.YELLOW + "Session is already unlocked." + Style.RESET_ALL)
                continue
            if verify_current_password(authenticator, user_store, "Enter password to unlock: "):
                locked = False
                print(Fore.GREEN + "Unlocked." + Style.RESET_ALL)
            else:
                print(Fore.RED + "Unlock failed." + Style.RESET_ALL)
            continue

        if lowered == "create portfolio":
            create_portfolio_wizard(file_ops, logger_obj)
            continue

        # AI command generation
        try:
            generated_cmd, selected_model = asyncio.run(ai_client.generate_command(user_input))
            last_model = selected_model
        except Exception as exc:
            stats["api_errors"] += 1
            stats["failed"] += 1
            err = f"AI processing error: {exc}"
            print(Fore.RED + err + Style.RESET_ALL)
            logger_obj.log_event(
                {
                    "user_input": user_input,
                    "generated_command": "",
                    "risk_level": "HIGH",
                    "execution_result": "api_error",
                    "model": "none",
                    "command_output": err,
                }
            )
            continue

        validation = validator.validate(generated_cmd)
        risk_level = validation.risk_level

        if risk_level == "HIGH":
            stats["high_risk"] += 1

        if not validation.allowed:
            stats["blocked"] += 1
            msg = f"Dangerous command blocked: {validation.reason}"
            print(Fore.RED + msg + Style.RESET_ALL)
            print(Fore.YELLOW + "Tip: rephrase as read-only/diagnostic, or use 'create portfolio'." + Style.RESET_ALL)
            logger_obj.log_event(
                {
                    "user_input": user_input,
                    "generated_command": validation.normalized_command,
                    "risk_level": risk_level,
                    "execution_result": "blocked",
                    "model": selected_model,
                    "command_output": msg,
                }
            )
            continue

        command_to_run = validation.normalized_command
        print(Fore.MAGENTA + f"JARVIS wants to run: {command_to_run}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"Risk level: {risk_level}" + Style.RESET_ALL)

        if dryrun_mode:
            stats["dry_run"] += 1
            msg = "Dry run: command was not executed."
            print(Fore.YELLOW + msg + Style.RESET_ALL)
            logger_obj.log_event(
                {
                    "user_input": user_input,
                    "generated_command": command_to_run,
                    "risk_level": risk_level,
                    "execution_result": "dry_run",
                    "model": selected_model,
                    "command_output": msg,
                }
            )
            continue

        if risk_level == "HIGH":
            user_data = user_store.load() or {}
            password_hash = user_data.get("password_hash", "")
            password_salt = user_data.get("password_salt", "")
            if not authenticator.secondary_authenticate(
                lambda password: user_store.verify_password(password, password_hash, password_salt)
            ):
                stats["blocked"] += 1
                print(Fore.RED + "Secondary authentication failed. Command blocked." + Style.RESET_ALL)
                logger_obj.log_event(
                    {
                        "user_input": user_input,
                        "generated_command": command_to_run,
                        "risk_level": risk_level,
                        "execution_result": "secondary_auth_failed",
                        "model": selected_model,
                        "command_output": "Secondary authentication failed",
                    }
                )
                continue

        confirm = input(Fore.CYAN + "Execute? (Y/N): " + Style.RESET_ALL).strip().lower()
        if confirm not in {"y", "yes"}:
            stats["blocked"] += 1
            print(Fore.YELLOW + "Execution cancelled by user." + Style.RESET_ALL)
            logger_obj.log_event(
                {
                    "user_input": user_input,
                    "generated_command": command_to_run,
                    "risk_level": risk_level,
                    "execution_result": "cancelled",
                    "model": selected_model,
                    "command_output": "User cancelled execution",
                }
            )
            continue

        run_result = executor.execute(command_to_run)
        execution_out = (run_result.stdout + "\n" + run_result.stderr).strip()

        if run_result.status == "success":
            stats["executed"] += 1
            print(Fore.GREEN + "Command executed successfully." + Style.RESET_ALL)
        else:
            stats["failed"] += 1
            print(Fore.RED + f"Command finished with status: {run_result.status}" + Style.RESET_ALL)

        if execution_out:
            print(Style.BRIGHT + execution_out + Style.RESET_ALL)

        logger_obj.log_event(
            {
                "user_input": user_input,
                "generated_command": command_to_run,
                "risk_level": risk_level,
                "execution_result": run_result.status,
                "model": selected_model,
                "command_output": safe_truncate(execution_out, 8000),
            }
        )

    print(Fore.YELLOW + "\nGraceful shutdown complete." + Style.RESET_ALL)
    print_status(
        stats,
        history,
        logger_obj,
        started_at,
        privacy_mode=privacy_mode,
        dryrun_mode=dryrun_mode,
        preferred_model=preferred_model,
        last_model=last_model,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
