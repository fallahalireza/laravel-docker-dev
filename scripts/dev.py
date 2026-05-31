"""
Laravel Docker Dev - CLI Entry Point
Usage:
    python dev.py                          # interactive menu
    python dev.py up [service ...]        # start services
    python dev.py down [service ...]      # stop services
    python dev.py restart [service ...]   # restart services
    python dev.py create [domain]         # create a new Laravel site
    python dev.py list                    # list existing sites
"""
import sys
from scripts.manager import DockerDevManager, error


USAGE = """\
Usage: python dev.py [command] [args ...]

Commands:
  (no args)              Interactive menu
  up    [service ...]   Start infrastructure services
  down  [service ...]   Stop infrastructure services
  restart [service ...] Restart infrastructure services
  create  [domain]      Create a new Laravel site
  list                  List existing sites
"""


def main():
    manager = DockerDevManager()

    if len(sys.argv) < 2:
        manager.interactive_menu()
        return

    action = sys.argv[1].lower()

    if action in ("up", "down"):
        names = [a.lower() for a in sys.argv[2:]] or None
        manager.run(action, names)

    elif action == "restart":
        names = [a.lower() for a in sys.argv[2:]] or None
        manager.restart(names)

    elif action == "create":
        domain = sys.argv[2] if len(sys.argv) > 2 else None
        manager.create_site(domain)

    elif action in ("list", "ls"):
        manager.list_sites()

    elif action in ("-h", "--help", "help"):
        print(USAGE)

    else:
        error(f"Unknown command: '{action}'")
        print(USAGE)
        sys.exit(1)


if __name__ == "__main__":
    main()
