import subprocess
import sys
import os
import re
import shutil
import logging
from pathlib import Path
from typing import Optional

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)


class Color:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    RESET  = "\033[0m"


def info(msg: str)       -> None: print(f"{Color.GRAY}{msg}{Color.RESET}")
def warn(msg: str)       -> None: print(f"{Color.YELLOW}⚠  {msg}{Color.RESET}")
def success(msg: str)    -> None: print(f"{Color.GREEN}✅ {msg}{Color.RESET}")
def error(msg: str)      -> None: print(f"{Color.RED}✖  {msg}{Color.RESET}", file=sys.stderr)
def docker_line(msg: str)-> None: print(f"{Color.BLUE}{msg}{Color.RESET}")
def header(msg: str)     -> None: print(f"\n{Color.BOLD}{Color.CYAN}{'═'*50}\n  {msg}\n{'═'*50}{Color.RESET}")


class DockerDevManager:
    def __init__(self):
        self.root_dir    = Path(__file__).resolve().parent.parent
        self.dev_dir     = self.root_dir / "development"
        self.sites_dir   = self.root_dir / "sites"
        self.compose_cmd = self._check_docker()

        # سرویس‌های زیرساخت به ترتیب اولویت
        self.services = [
            {"name": "traefik", "path": self.dev_dir / "traefik"},
            {"name": "mysql",   "path": self.dev_dir / "mysql"},
        ]

    # ══════════════════════════════════════════════════════════════
    # Docker Environment Check
    # ══════════════════════════════════════════════════════════════

    def _check_docker(self) -> list[str]:
        """بررسی نصب و اجرای Docker و Docker Compose."""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True)
        except FileNotFoundError:
            error("'docker' command not found in PATH.")
            sys.exit(1)

        if result.returncode != 0:
            error("Docker daemon is not running. Please start Docker.")
            sys.exit(1)

        for cmd in [["docker", "compose"], ["docker-compose"]]:
            try:
                r = subprocess.run(cmd + ["version"], capture_output=True)
                if r.returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue

        error("Docker Compose (v2 or v1) not found.")
        sys.exit(1)

    # ══════════════════════════════════════════════════════════════
    # Network Management
    # ══════════════════════════════════════════════════════════════

    def _manage_network(self, net_name: str = "traefik-public") -> None:
        """شبکه خارجی Docker را در صورت نبود می‌سازد."""
        result = subprocess.run(
            ["docker", "network", "ls", "--format", "{{.Name}}"],
            capture_output=True, text=True
        )
        existing = result.stdout.splitlines()
        if net_name not in existing:
            info(f"Creating external network: {net_name} ...")
            r = subprocess.run(["docker", "network", "create", net_name], capture_output=True)
            if r.returncode != 0:
                error(f"Failed to create network '{net_name}'.")
            else:
                success(f"Network '{net_name}' created.")

    # ══════════════════════════════════════════════════════════════
    # Service Resolution
    # ══════════════════════════════════════════════════════════════

    def _resolve_services(self, names: Optional[list[str]] = None) -> list[dict]:
        """نام سرویس‌ها را به دیکشنری متناظر تبدیل می‌کند. None یعنی همه."""
        if not names:
            return list(self.services)

        valid = {s["name"]: s for s in self.services}
        resolved = []
        for name in names:
            name = name.lower()
            if name not in valid:
                warn(f"Unknown service '{name}', skipping.")
            else:
                resolved.append(valid[name])
        return resolved

    # ══════════════════════════════════════════════════════════════
    # Core Actions: up / down / restart
    # ══════════════════════════════════════════════════════════════

    def run(self, action: str, names: Optional[list[str]] = None) -> None:
        """سرویس‌های انتخابی را اجرا یا متوقف می‌کند."""
        self._manage_network()

        selected = self._resolve_services(names)
        if not selected:
            warn("No valid services selected.")
            return

        labels   = {"up": "Starting", "down": "Stopping"}
        label    = labels.get(action, action.capitalize())
        # برای down ترتیب معکوس است
        services = selected if action != "down" else list(reversed(selected))

        for svc in services:
            info(f"--- {label} {svc['name']} ---")
            cmd = self.compose_cmd + [action]
            if action == "up":
                cmd.append("-d")

            result = subprocess.run(
                cmd,
                cwd=svc["path"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in result.stdout.splitlines():
                if line.strip():
                    docker_line(line)

            if result.returncode != 0:
                error(f"Service '{svc['name']}' failed during '{action}'.")

    def restart(self, names: Optional[list[str]] = None) -> None:
        self.run("down", names)
        self.run("up", names)

    # ══════════════════════════════════════════════════════════════
    # Site Creation
    # ══════════════════════════════════════════════════════════════

    def create_site(self, domain: Optional[str] = None) -> None:
        """از روی template یک پروژه لاراول جدید می‌سازد."""
        if not domain:
            domain = input("Enter site domain (e.g. myapp.localhost): ").strip()

        if not domain:
            error("No domain provided.")
            return

        # نام پوشه: alireza.ir -> alireza_ir
        folder_name = re.sub(r"[^a-zA-Z0-9]+", "_", domain).strip("_").lower()
        if not folder_name:
            error("Invalid domain name.")
            return

        # ── پیدا کردن template (case-insensitive) ──────────────────
        template_base = self.root_dir / "template"
        template_dir  = None
        for candidate in ["laravel", "Laravel"]:
            path = template_base / candidate
            if path.is_dir():
                template_dir = path
                break

        if template_dir is None:
            error(f"Template not found in: {template_base}")
            return

        # ── بررسی وجود سایت ───────────────────────────────────────
        self.sites_dir.mkdir(parents=True, exist_ok=True)
        target_dir = self.sites_dir / folder_name
        if target_dir.exists():
            error(f"Site already exists: {target_dir}")
            return

        # ── کپی template ───────────────────────────────────────────
        info(f"Creating site '{folder_name}' from template ...")
        shutil.copytree(template_dir, target_dir)

        # ── ویرایش .env ────────────────────────────────────────────
        env_src  = target_dir / ".env.example"
        env_file = target_dir / ".env"

        # اگر .env وجود نداشت از .env.example بسازش
        if not env_file.exists() and env_src.exists():
            shutil.copy(env_src, env_file)

        if env_file.is_file():
            content = env_file.read_text(encoding="utf-8")
            content = re.sub(r"(?m)^CONTAINER_NAME=.*$", f"CONTAINER_NAME={folder_name}", content)
            content = re.sub(r"(?m)^DOMAIN_DEV=.*$",     f"DOMAIN_DEV={domain}",          content)
            # حذف DOMAIN= مستقیم (اگر وجود داشت)
            content = re.sub(r"(?m)^DOMAIN=.*\n?", "", content)
            env_file.write_text(content, encoding="utf-8")
            success(f".env configured for '{domain}'")
        else:
            warn(f".env/.env.example not found in template: {target_dir}")

        success(f"Site created at: {target_dir}")
        info(f"  → cd sites/{folder_name} && make up")

    # ══════════════════════════════════════════════════════════════
    # Site Listing
    # ══════════════════════════════════════════════════════════════

    def list_sites(self) -> None:
        """لیست سایت‌های موجود در پوشه sites/ را نمایش می‌دهد."""
        if not self.sites_dir.exists() or not any(self.sites_dir.iterdir()):
            info("No sites found. Use 'create' to add one.")
            return

        print(f"\n{Color.BOLD}Available sites:{Color.RESET}")
        for site in sorted(self.sites_dir.iterdir()):
            if site.is_dir():
                env = site / ".env"
                domain = "?"
                if env.exists():
                    for line in env.read_text(encoding="utf-8").splitlines():
                        if line.startswith("DOMAIN_DEV="):
                            domain = line.split("=", 1)[1].strip()
                            break
                print(f"  {Color.CYAN}{site.name:<25}{Color.RESET}  https://{domain}")
        print()

    # ══════════════════════════════════════════════════════════════
    # Interactive Menu
    # ══════════════════════════════════════════════════════════════

    def interactive_menu(self) -> None:
        header("Docker Dev Manager")

        actions = ["up", "down", "restart", "create site", "list sites"]
        print("Select action:")
        for i, act in enumerate(actions, 1):
            print(f"  {i}) {act}")
        action = self._prompt_choice(actions, "Action")

        if action == "create site":
            print()
            self.create_site()
            return

        if action == "list sites":
            self.list_sites()
            return

        # انتخاب سرویس‌ها
        print("\nSelect services:")
        print("  0) all")
        for i, svc in enumerate(self.services, 1):
            print(f"  {i}) {svc['name']}")

        raw   = input("Services (e.g. '0' or '1,2'): ").strip()
        names = self._parse_service_selection(raw)

        print()
        if action == "restart":
            self.restart(names)
        else:
            self.run(action, names)

    # ══════════════════════════════════════════════════════════════
    # Helpers
    # ══════════════════════════════════════════════════════════════

    def _prompt_choice(self, options: list[str], label: str) -> str:
        while True:
            raw = input(f"{label} [1-{len(options)}]: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return options[int(raw) - 1]
            warn("Invalid choice, try again.")

    def _parse_service_selection(self, raw: str) -> Optional[list[str]]:
        if not raw or raw == "0":
            return None  # همه سرویس‌ها
        names = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit() and 1 <= int(part) <= len(self.services):
                names.append(self.services[int(part) - 1]["name"])
        return names or None
