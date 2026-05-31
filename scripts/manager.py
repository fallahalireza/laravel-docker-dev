import subprocess
import sys
import os
import re
import shutil
from pathlib import Path

import os

class Color:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

def info(msg):
    print(f"{Color.GRAY}{msg}{Color.RESET}")


def warn(msg):
    print(f"{Color.YELLOW}{msg}{Color.RESET}")


def error(msg):
    print(f"{Color.RED}{msg}{Color.RESET}")

def docker_line(msg):
    print(f"{Color.BLUE}{msg}{Color.RESET}")



class DockerDevManager:
    def __init__(self):
        # از scripts/ به ریشه پروژه (..) می‌رویم
        self.root_dir = Path(__file__).resolve().parent.parent
        self.dev_dir = self.root_dir / "development"
        self.compose_cmd = self._check_docker()

        # تعریف سرویس‌ها به ترتیب اولویت بالا آمدن
        self.services = [
            {"name": "traefik", "path": self.dev_dir / "traefik"},
            {"name": "mysql", "path": self.dev_dir / "mysql"}
        ]

    def _check_docker(self):
        # بررسی نصب بودن داکر در PATH
        try:
            info = subprocess.run(["docker", "info"], capture_output=True)
        except FileNotFoundError:
            print("Error: 'docker' command not found in PATH.")
            sys.exit(1)

        # بررسی اجرا بودن Docker Daemon
        if info.returncode != 0:
            print("Error: Docker daemon is not running. Please start Docker.")
            sys.exit(1)

        # تست برای docker compose (v2) یا docker-compose (v1)
        for cmd in [["docker", "compose"], ["docker-compose"]]:
            try:
                if subprocess.run(cmd + ["version"], capture_output=True).returncode == 0:
                    return cmd
            except FileNotFoundError:
                continue

        print("Error: Docker Compose (v2 or v1) not found.")
        sys.exit(1)

    def _manage_network(self):
        net_name = "traefik-public"
        result = subprocess.run(
            ["docker", "network", "ls", "--format", "{{.Name}}"],
            capture_output=True, text=True
        )
        existing = result.stdout.split()
        if net_name not in existing:
            print(f"Creating external network: {net_name}...")
            subprocess.run(["docker", "network", "create", net_name])

    def _resolve_services(self, names=None):
        """نام سرویس‌ها را به دیکشنری متناظر تبدیل می‌کند. None یعنی همه."""
        if not names:
            return list(self.services)

        resolved = []
        valid_names = {s["name"] for s in self.services}
        for name in names:
            name = name.lower()
            if name not in valid_names:
                print(f"Warning: unknown service '{name}', skipping.")
                continue
            resolved.append(next(s for s in self.services if s["name"] == name))
        return resolved

    def run(self, action, names=None):
        self._manage_network()

        selected = self._resolve_services(names)
        if not selected:
            warn("No valid services selected.")
            return

        labels = {"up": "Starting", "down": "Stopping"}
        label = labels.get(action, action.capitalize())

        services_to_run = selected if action != "down" else list(reversed(selected))

        for service in services_to_run:
            info(f"--- {label} {service['name']} ---")
            cmd = self.compose_cmd + [action]
            if action == "up":
                cmd.append("-d")

            result = subprocess.run(
                cmd,
                cwd=service['path'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            for line in result.stdout.splitlines():
                if line.strip():
                    docker_line(line)


    def restart(self, names=None):
        self.run("down", names)
        self.run("up", names)

    def interactive_menu(self):
        print("\n=== Docker Dev Manager ===\n")

        # انتخاب اکشن
        actions = ["up", "down", "restart", "create site"]
        print("Select action:")
        for i, act in enumerate(actions, 1):
            print(f"  {i}) {act}")
        action = self._prompt_choice(actions, "Action")

        # ساخت سایت نیازی به انتخاب سرویس ندارد
        if action == "create site":
            print()
            self.create_site()
            return

        # انتخاب سرویس‌ها
        print("\nSelect services:")
        print("  0) all")
        for i, svc in enumerate(self.services, 1):
            print(f"  {i}) {svc['name']}")

        raw = input("Services (e.g. '0' or '1,2'): ").strip()
        names = self._parse_service_selection(raw)

        print()
        if action == "restart":
            self.restart(names)
        else:
            self.run(action, names)

    def _prompt_choice(self, options, label):
        while True:
            raw = input(f"{label} [1-{len(options)}]: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(options):
                return options[int(raw) - 1]
            print("Invalid choice, try again.")

    def _parse_service_selection(self, raw):
        if not raw or raw == "0":
            return None  # همه

        names = []
        for part in raw.split(","):
            part = part.strip()
            if part.isdigit() and 1 <= int(part) <= len(self.services):
                names.append(self.services[int(part) - 1]["name"])
        return names or None

    def create_site(self, domain=None):
        if not domain:
            domain = input("Enter site domain (e.g. alireza.ir): ").strip()

        if not domain:
            error("No domain provided.")
            return

        # تبدیل دامنه به نام پوشه: alireza.ir -> alireza_ir
        folder_name = re.sub(r"[^a-zA-Z0-9]+", "_", domain).strip("_").lower()
        if not folder_name:
            error("Invalid domain name.")
            return

        template_dir = self.root_dir / "template" / "Laravel"
        if not template_dir.is_dir():
            error(f"Template not found: {template_dir}")
            return

        target_dir = self.root_dir / "sites" / folder_name
        if target_dir.exists():
            error(f"Site already exists: {target_dir}")
            return

        info(f"--- Creating site '{folder_name}' ---")
        shutil.copytree(template_dir, target_dir)

        # ویرایش فایل .env سایت جدید
        env_file = target_dir / ".env"
        if env_file.is_file():
            new_lines = []
            for line in env_file.read_text(encoding="utf-8").splitlines():
                stripped = line.strip()
                if stripped.startswith("CONTAINER_NAME="):
                    new_lines.append(f"CONTAINER_NAME={folder_name}")
                elif stripped.startswith("DOMAIN_DEV="):
                    new_lines.append(f"DOMAIN_DEV={domain}")
                elif stripped.startswith("DOMAIN="):
                    # این خط حذف می‌شود
                    continue
                else:
                    new_lines.append(line)
            env_file.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            info(f".env configured for '{domain}'")
        else:
            warn(f".env not found in template: {env_file}")

        info(f"Site created at: {target_dir}")


