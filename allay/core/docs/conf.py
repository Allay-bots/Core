import os
import shutil

# pylint: disable=invalid-name, redefined-builtin

# -- Project information -----------------------------------------------------

project = "Allay Core"
copyright = "2023, Gunivers"
author = "Z_runner, Leirof, Aeris One, ascpial, theogiraudet, fantomitechno,"\
    "Just_a_Player and Aragorn"

# The full version, including alpha/beta/rc tags
# release = ""

# -- General configuration ----------------------------------------------------

extensions = [
    'myst_parser',
    'sphinx_design',
    'sphinx_togglebutton',
    'sphinx_copybutton',
]
myst_heading_anchors = 6
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Options for HTML output -----------------------------------------------------

html_theme = 'pydata_sphinx_theme'

# html_css_files = [
#     'credits.css',
# ]

html_theme_options = {
    "github_url": "https://github.com/Allay-Bots/Core",
    "announcement": "⚠️ You are reading a doc of an undergoing development version."\
    "Information can be out of date and/or change at any time. ⚠️",
    "logo": {
        "image_dark": "_static/logo.png",
        "text": "Allay Core",  # Uncomment to try text with logo
    },
    "icon_links": [
        {
            "name": "Support us",
            "url": "https://utip.io/gunivers",
            "icon": "fa fa-heart",
        },
        {
            "name": "Gunivers",
            "url": "https://gunivers.net",
            "icon": "_static/logo-gunivers.png",
            "type": "local",
        },
        {
            "name": "Discord server",
            "url": "https://discord.gg/E8qq6tN",
            "icon": "_static/logo-discord.png",
            "type": "local",
        },
    ]
}

html_logo = "_static/logo.png"

html_static_path = ['_static']

html_css_files = [
    'css/stylesheet.css',
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    #"linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Plugin doc generation -------------------------------------------------------


CONTRIBUTE = """
```{admonition} 🤝 Help us to improve this documentation!
:class: tip
If you want to help us to improve this documentation, you can edit it on the [GitHub repo](https://github.com/Allay-Bots/Core/) or come and discuss with us on our [Discord server](https://discord.gg/E8qq6tN)!
```
"""

GITHUB_DISCUSSION_FOOTER = """
---
## 💬 Did it help you?
Feel free to leave your questions and feedbacks below!
<script src="https://giscus.app/client.js"
        data-repo="{orga}/{repo}"
        data-repo-id="R_kgDOHQph3g"
        data-category="Documentation"
        data-category-id="DIC_kwDOHQph3s4CUSnO"
        data-mapping="title"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="bottom"
        data-theme="light"
        data-lang="fr"
        data-loading="lazy"
        crossorigin="anonymous"
        async>
</script>
"""
