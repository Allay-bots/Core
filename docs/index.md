---
html_theme.sidebar_secondary.remove: true
html_theme.sidebar_primary.remove: true
sd_hide_title: true
---

# Home page

<div align=center>
<div style="max-width:800px">

```{image} _static/banner.png
:class: dark-light
```

</div>
</div>

## 🔎 What is it?

Allay Core is the base of the Allay Bots. It allow all the Allay projects to go straight to the point by provinding a set of tools that simplify the development of bot features and faster the implementation.

Allay Core, such as other Allay projects, is free and open-source. It is written in Python and uses the Discord.py library and is managed by the [Gunivers](https://gunivers.net) community.

```{button-link} getting_started.html
:color: primary
:align: center
:shadow:

🚀 Create an Allay bot!
```

## 🏃 Motivation

As Discord bot developers we noticed that there is a lot of different service bots, and a lot of tool to create your own bots, but nothing in between. We wanted to create a bot that would be easy to use and to configure, but also powerful and customizable.

This project has then 2 objectives:
- On the core side, the goal is to design a system that allow to simplify as much as possible the creation of plugins, and to make them as customizable as possible.
- On the plugin side, the goal is to create a lot of small bots, focused on a special feature or type of feature, that can be used by anyone and can be easily configured to fit the needs of the server.

## 📦 Current Allay Bots

```{include} plugins_grid.md
```


## 🤝 Follow and/or contribute

You can come on [our Discord](https://discord.gg/E8qq6tN) server to talk with us and/or take part of the project!

If you want to contribute, please read at least the "Getting started" section in the ["Contributing" page](https://glib-core.readthedocs.io/en/latest/contributing.html) that contain all the development convention used in this project.


```{toctree}
:maxdepth: 3
:caption: Info
:hidden:

getting_started
user_guide
developer_guide
faq
changelog
special_thanks
```

<!-- End plugins documentation -->

