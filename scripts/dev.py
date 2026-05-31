import sys
from scripts.manager import DockerDevManager


def main():
    manager = DockerDevManager()

    # بدون آرگومان: منوی تعاملی
    if len(sys.argv) < 2:
        manager.interactive_menu()
        return

    action = sys.argv[1].lower()
    # آرگومان‌های بعدی نام سرویس‌ها هستند (اختیاری)
    names = [a.lower() for a in sys.argv[2:]] or None

    if action in ("up", "down"):
        manager.run(action, names)
    elif action == "restart":
        manager.restart(names)
    elif action == "create":
        # python dev.py create alireza.ir
        domain = sys.argv[2] if len(sys.argv) > 2 else None
        manager.create_site(domain)
    else:
        print(f"Unknown command: {action}")
        print("Usage: python dev.py [up|down|restart|create] [args ...]")


if __name__ == "__main__":
    main()
