--

# MarkDownPost — Posts to Telegram and Telegraph

> **`mdp`** — a CLI tool for instantly publishing Markdown files to Telegram and Telegraph while preserving formatting.
> Easily post, edit, and manage content directly from your source files.

* 📺 [YouTube — Installation & Examples](https://www.youtube.com/@markdownpost)
* 💬 [Telegram community](https://t.me/markdownpost)

---

### 🧩 Overview

**MarkdownPost** is a command-line utility that allows you to **turn Markdown files into formatted posts**:

* **Posts to Telegram** — with full Markdown formatting, images, and links.
* **Pages in Telegraph** — with Markdown support and proper HTML rendering.
* **Editing existing posts or pages** — update text, titles, links directly from source files.
* **Local file integration** — work in `.md` files inside your repo, and the tool publishes/synchronizes them automatically.

#### Key Features

* Markdown parsing and escaping — ensures Telegram accepts your message without formatting errors.
* Metadata support — titles, preview images, publication dates.
* Automatic saving of `message_id` and `page_id` for later editing.
* Scriptable — perfect for automation, CI/CD, or content pipelines.

---

### 🏷️ Why MarkDownPost

* For **developers, bloggers**, and **content creators** who store text as Markdown and want to publish instantly.
* **Automation-first**: no need to open Telegram or Telegraph manually.
* **Content control**: re-edit or re-publish directly from Markdown.
* **Unified tool**: Telegram + Telegraph = one workflow.

---

## 📘 Main CLI Commands

| Command    | Description                                                    |
| ---------- | -------------------------------------------------------------- |
| `gr`       | Commands for **TeleGraph**                                     |
| `tg`       | Commands for **Telegram**                                      |
| `tgh`      | Commands for **csimultaneous posting** to both TG and Telegraph |
| `help-all` | Show help for all commands and subcommands                     |

---

## 🧩 `gr` — Telegraph Commands

| Subcommand                                               | Arguments                       | Description                                                  |
| -------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------ |
| `gr post <md_path> [--title <text>]`                     | `md_path` — Markdown file path  | Create a new Telegraph page                                  |
| `gr edit <page_path> <md_path>`                          | `page_path`, `md_path`          | Edit an existing Telegraph page                              |
| `gr get-pages-list [--output-path <path>] [--limit <n>]` | optional: output file and limit | Get list of pages for the account (print or export to Excel) |
| `gr rm <path>`                                           | `path` — page path              | Delete a Telegraph page                                      |

---

## 💬 `tg` — Telegram Commands

| Subcommand                                    | Arguments                         | Description                                                    |
| --------------------------------------------- | --------------------------------- | -------------------------------------------------------------- |
| `tg post <md_path>`                           | `md_path` — Markdown file path    | Post a message to Telegram channel and store its ID            |
| `tg edit <msg_id> <md_path>`                  | `msg_id`, `md_path`               | Edit a message in the Telegram channel                         |
| `tg rm <msg_id>`                              | `msg_id` — message ID             | Delete a message from Telegram channel                         |
| `tg img-post <photo_path> [--md-path <path>]` | `photo_path` — file or HTTPS link | Post an image with an optional Markdown caption                |
| `tg img-edit <post_id> [--md-path <path>]`    | `post_id` — message ID            | Edit the caption of an existing image post (image not changed) |

---

## 🔗 `tgh` — Combined Posting (Telegraph + Telegram)

| Subcommand                            | Arguments            | Description                                           |
| ------------------------------------- | -------------------- | ----------------------------------------------------- |
| `tgh post <md_path> [--title <text>]` | `md_path` — Markdown | Create a Telegraph page and post its link to Telegram |

---

## ⚙️ System Command

| Command    | Description                                |
| ---------- | ------------------------------------------ |
| `help-all` | Show help for all commands and subcommands |

---

# 🧭 Installation Guide

Below are installation instructions for **Windows**, **macOS**, and **Linux**.

---

## 💻 Windows

### 1. Install Python and Git Bash

* Download and install [Python 3.12.3 64-bit](https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe).
* Download and install [Git Bash](https://git-scm.com/downloads/win) (recommended terminal).

---

### 2. Install pipx

Run in **Git Bash**:

```bash
python -m pip install --user pipx
```

Restart Git Bash after installation to activate the `pipx` command.

---

### 3. Install the Application

Using pipx directly from GitHub:

```bash
pipx install git+https://github.com/s1vv/MarkDownPost.git
```

Or install manually:

```bash
# Clone or download ZIP
git clone https://github.com/s1vv/MarkDownPost.git
cd MarkDownPost

# Install via pipx
pipx install .
```

> `pipx` creates an isolated environment and makes the `mdp` command globally available.

---

### 4. Verify Installation

```bash
mdp --help
```

or

```bash
mdp help-all
```

You should see all available commands.

---

### 5. Configure Environment

Create a text file similar to `env_template.txt`, fill in your tokens and author info, then apply it:

```bash
mdp env init path/to/file.txt --apply
```

> This sets tokens, author name, and other configuration parameters in your system environment.

---

### 6. Update

To update to the latest version:

```bash
pipx upgrade mdp
```

---

## 🍏 macOS

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then add it to your PATH:

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

### 2. Install Python & pipx

```bash
brew install python3 pipx
pipx ensurepath
```

Restart Terminal and check:

```bash
python3 --version
pipx --version
```

### 3. Install MarkDownPost

```bash
pipx install git+https://github.com/s1vv/MarkDownPost.git
```

---

## 🐧 Linux

### 1. Install Python and pipx

For Debian/Ubuntu:

```bash
sudo apt update
sudo apt install pipx
pipx ensurepath
```

For Arch Linux:

```bash
sudo pacman -S python python-pipx
pipx ensurepath
```

Restart the terminal.

---

### 2. Install MarkDownPost

```bash
pipx install git+https://github.com/s1vv/MarkDownPost.git
```

---

### 3. Verify

```bash
mdp --help
```

---

## 🧾 Example Usage

```bash
mdp tgh post article.md --title "CLI Automation with MarkdownPost"
```

```bash
mdp gr get-pages-list --output-path pages.xlsx
```

---

## 💡 Quick Links

* 📘 [Project Repository](https://github.com/s1vv/MarkDownPost)
* 💬 [Telegram Support](https://t.me/rs_py)
* 📺 [YouTube — Setup & Usage](https://youtu.be/sw2zhOAxWmM)

---

**MarkDownPost** — publish Markdown to Telegram & Telegraph effortlessly.

---

