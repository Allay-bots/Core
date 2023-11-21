
# Standard libs ---------------------------------------------------------------

import os

# Modules ---------------------------------------------------------------------

PATH = "allay/builtins"
all_modules: list[str] = []

for plugin in os.listdir(PATH):

    if not os.path.isdir(os.path.join(PATH, plugin)):
        continue
    if plugin.startswith("_"):
        continue

    all_modules.append(plugin)
