import sys

from src.cli import run_cli


def main():
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        sys.exit(0)


if __name__ == "__main__":
    main()
