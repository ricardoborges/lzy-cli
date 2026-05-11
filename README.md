# 🐧 Lzy – Natural Language to Bash CLI

**Lzy** is a command-line tool that uses AI to translate natural language into Linux bash commands, explains what the command does, and lets you choose whether to run, edit, or abort the execution.

---

## ✨ Features

- 🔁 Translates natural language into valid Bash commands.
- 📘 Explains each command in natural language.
- 🛠️ Lets you review or edit the command before execution.
- 🔐 Works with multiple AI providers, including local **Ollama** models.
- 🧙 First-run interactive setup wizard — no env vars required.
- 🎨 Fancy terminal output with `rich`.

---

## 🎥 Demo

[![Watch the demo](https://img.youtube.com/vi/W9jMvZKNo4M/0.jpg)](https://www.youtube.com/watch?v=W9jMvZKNo4M)

Click the image above or [watch on YouTube](https://www.youtube.com/watch?v=W9jMvZKNo4M).

---

## 🚀 Installation

```bash
pip install lzycli
```

---

## 🔧 Configuration

The first time you run `lzy`, an interactive wizard will guide you through:

1. Choosing an AI provider.
2. Entering your API key (typed characters are masked with `*` for shoulder-surfing safety).
3. For **Ollama**, picking the host (default `http://localhost:11434`) and selecting one of the locally installed models — no API key needed.

Your selection is saved to `~/.lzy/config.json` (chmod `600` on Unix) and used on every subsequent run.

To reconfigure at any time:

```bash
lzy --setup
```

### Example `~/.lzy/config.json`

For a cloud provider (API key based):

```json
{
  "provider": "openai",
  "api_key": "sk-your-api-key-here"
}
```

For Ollama (local, no API key):

```json
{
  "provider": "ollama",
  "host": "http://localhost:11434",
  "model": "llama3.2"
}
```

### Supported Providers

| Provider    | Type        |
|-------------|-------------|
| `openai`    | API key     |
| `anthropic` | API key     |
| `gemini`    | API key     |
| `groq`      | API key     |
| `mistral`   | API key     |
| `together`  | API key     |
| `nvidia`    | API key     |
| `ollama`    | local (no API key) |

> **Ollama:** make sure `ollama serve` is running and you have pulled at least one model (e.g. `ollama pull llama3.2`) before running the setup.

---

## 🧪 Usage

```bash
lzy find all PDF files in the current directory
```

If no provider is configured yet, the setup wizard runs automatically.

You’ll get a result like this:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Command                             ┃ Description                                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ find . -name '*.pdf'                │ Searches for all PDF files in the current    │
│                                     │ directory and its subdirectories.            │
└─────────────────────────────────────┴──────────────────────────────────────────────┘
```

Then you're prompted to choose:

- `y`: run the command
- `e`: edit it first
- `n`: cancel

---

## 🧩 Dev Tip

You can also run directly via Python for debugging:

```bash
python lzy/cli.py delete all .DS_Store files in this folder
```

---

## 📦 Publishing

This repository is configured to publish distributions through GitHub Actions using PyPI Trusted Publishing.

### One-time setup

1. Create the GitHub environments `testpypi` and `pypi` in the repository settings.
2. Require manual approval for the `pypi` environment.
3. In TestPyPI, add a trusted publisher with:
  - Owner: `ricardoborges`
  - Repository: `lzy-cli`
  - Workflow file: `publish-to-pypi.yml`
  - Environment: `testpypi`
  - Project name: `lzycli`
4. In PyPI, add the same trusted publisher, but use environment `pypi`.

### Release flow

- Package versions now come from Git tags via `setuptools-scm`.
- Create and push the release tag you want to publish, such as `v1.0.1`.
- Pushes to `main` publish the current build to TestPyPI.
- Tags matching `v*` publish the tagged build to PyPI.

If this repository does not yet have a Git tag for the already published `1.0.0` release, create one on the matching commit before relying on automatic versioning. Otherwise, `setuptools-scm` will derive a development version from repository history instead.

Example release:

```bash
git tag v1.0.1
git push origin main --tags
```

---

## 📜 License

MIT License
