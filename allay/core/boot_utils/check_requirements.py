import os
import sys

from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import Version

from allay.plugins import all_modules


def check_requirements(print_debug: bool = False):
    "Check Python version and installed libs"

    # Check python version --------------------------------------------------------
    py_version = sys.version_info
    if py_version.major != 3 or py_version.minor < 10:
        print("⚠️ \033[33mGipsy require Python 3.10 or more.\033[1m")
        sys.exit(1)

    # Check installed modules -----------------------------------------------------

    core_requirements = _get_requirements_from_file("requirements.txt")
    if not _check_requirements_versions(core_requirements, print_debug=print_debug):
        print("\n\n Please run \"pip install -r requirements.txt\"")
        sys.exit(1)
    all_plugins_satisfied = True
    for plugin_requirements_file in _get_plugins_requirements_files():
        plugin_requirements = _get_requirements_from_file(plugin_requirements_file)
        if not _check_requirements_versions(plugin_requirements, print_debug=print_debug):
            all_plugins_satisfied = False
            print(f"\n Please run \"pip install -r {plugin_requirements_file}\"")
    if not all_plugins_satisfied:
        sys.exit(1)
    elif not print_debug:
        print("✅ \033[32mAll requirements are correctly installed.\033[0m")

def _get_plugins_requirements_files():
    "Get the relative path of all plugin requirements"
    requirements_files: list[str] = []
    for plugin in all_modules:
        path = f"allay/plugins/{plugin}/requirements.txt"
        if os.path.isfile(path):
            requirements_files.append(path)
    return requirements_files

def _get_requirements_from_file(filepath: str):
    "Get a list of requirements from a given requirements.txt file"
    requirements: list[Requirement] = []
    with open(filepath, "r", encoding="utf8") as file:
        for line in file.readlines():
            try:
                requirements.append(Requirement(line))
            except InvalidRequirement:
                print(f"⚠️ \033[33mInvalid requirement: {line}\033[0m")
    return requirements

def _check_requirements_versions(requirements: list[Requirement], print_debug: bool = False):
    "Check if the requirements are correctly installed"
    # list installed packages
    lst = os.popen('pip list --format=freeze')
    pack_list = lst.read().split("\n")
    # map installed packages to their parsed version
    packages_map: dict[str, Version] = {}
    for pack in pack_list:
        if not pack.strip():
            continue
        pack_name, raw_version = pack.split("==")
        packages_map[pack_name.lower()] = Version(raw_version)
    # check if requirements are installed
    all_satisfied = True
    for req in requirements:
        req_name = req.name.lower()
        if req_name not in packages_map:
            print(f"⚠️ \033[33m{req_name} is not installed.\033[0m")
            all_satisfied = False
            continue
        if req.specifier.contains(packages_map[req_name]):
            if print_debug:
                print(f"✅ \033[32m{req_name} is correctly installed.\033[0m")
        else:
            print(f"⚠️ \033[33m{req_name} is not correctly installed.\033[0m")
            print(f"\t\033[33m{req_name} {req.specifier} is required.\033[0m")
            print(f"\t\033[33m{req_name} {packages_map[req_name]} is installed.\033[0m")
            all_satisfied = False
    return all_satisfied
