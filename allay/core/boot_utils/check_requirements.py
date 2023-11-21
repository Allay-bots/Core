import sys

import pkg_resources  # deprecated, use importlib.resources instead


def check_requirements():
    "Check Python version and installed libs"

    # Check python version --------------------------------------------------------
    py_version = sys.version_info
    if py_version.major != 3 or py_version.minor < 10:
        print("⚠️ \033[33mGipsy require Python 3.10 or more.\033[1m")
        sys.exit(1)

    # Check installed modules -----------------------------------------------------

    # TODO : update this
    with open("requirements.txt", "r", encoding='utf-8') as file:
        packages = pkg_resources.parse_requirements(file.readlines())
    try:
        pkg_resources.working_set.resolve(packages)
    except pkg_resources.VersionConflict as exc:
        print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
        print(f"\n⚠️ \033[33m{type(exc).__name__}: {exc}\033[0m\n ")
        print("\n\n Please run \"pip install -r requirements.txt\"")
    except Exception as exc: # pylint: disable=broad-exception-caught
        print("\n🤕 \033[31mOops, there is a problem in the dependencies.\033[0m")
        print(f"\n⛔ \u001b[41m\u001b[37;1m{type(exc).__name__}\033[0m: \033[31m{exc}\033[0m\n")
        print("\n\n Please run \"pip install -r requirements.txt\"")
