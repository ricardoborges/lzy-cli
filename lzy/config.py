import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.box import SIMPLE_HEAVY
from rich.align import Align

CONFIG_DIR = Path.home() / ".lzy"
CONFIG_FILE = CONFIG_DIR / "config.json"

PROVIDERS = [
    {"key": "openai", "label": "OpenAI", "needs_key": True},
    {"key": "anthropic", "label": "Anthropic", "needs_key": True},
    {"key": "gemini", "label": "Gemini", "needs_key": True},
    {"key": "groq", "label": "Groq", "needs_key": True},
    {"key": "mistral", "label": "Mistral", "needs_key": True},
    {"key": "together", "label": "Together", "needs_key": True},
    {"key": "nvidia", "label": "Nvidia", "needs_key": True},
    {"key": "ollama", "label": "Ollama (local)", "needs_key": False},
]

OLLAMA_DEFAULT_HOST = "http://localhost:11434"

console = Console()


def load_config():
    if not CONFIG_FILE.exists():
        return None
    try:
        with CONFIG_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with CONFIG_FILE.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def masked_input(prompt_text: str) -> str:
    """Read a line from stdin, echoing '*' for each character typed."""
    console.print(prompt_text, end="")
    sys.stdout.flush()

    buf = []
    try:
        import msvcrt  # Windows
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                break
            if ch == "\x03":
                raise KeyboardInterrupt
            if ch == "\b":
                if buf:
                    buf.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if ch == "\x00" or ch == "\xe0":
                msvcrt.getwch()
                continue
            buf.append(ch)
            sys.stdout.write("*")
            sys.stdout.flush()
    except ImportError:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    sys.stdout.write("\r\n")
                    sys.stdout.flush()
                    break
                if ch == "\x03":
                    raise KeyboardInterrupt
                if ch in ("\x7f", "\b"):
                    if buf:
                        buf.pop()
                        sys.stdout.write("\b \b")
                        sys.stdout.flush()
                    continue
                buf.append(ch)
                sys.stdout.write("*")
                sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return "".join(buf)


def _render_providers_table():
    table = Table(
        show_header=True,
        header_style="bold yellow",
        box=SIMPLE_HEAVY,
        border_style="yellow",
        title="Available Providers",
        title_style="bold cyan",
    )
    table.add_column("#", style="bold magenta", justify="right")
    table.add_column("Provider", style="bold white")
    table.add_column("Type", style="dim")
    for i, p in enumerate(PROVIDERS, start=1):
        kind = "API key required" if p["needs_key"] else "local"
        table.add_row(str(i), p["label"], kind)
    console.print(Align.center(table))


def _fetch_ollama_models(host: str):
    url = host.rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return [m["name"] for m in data.get("models", [])]
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError):
        return None


def _setup_ollama() -> dict:
    host = Prompt.ask(
        "[bold cyan]Ollama host[/bold cyan]",
        default=OLLAMA_DEFAULT_HOST,
    )
    console.print(f"🔎 [dim]Fetching models from[/dim] [cyan]{host}[/cyan]...")
    models = _fetch_ollama_models(host)
    if not models:
        console.print(
            Panel.fit(
                "[bold red]Could not reach Ollama or no models installed.[/bold red]\n"
                "Make sure [bold]ollama serve[/bold] is running and you have pulled at least one model\n"
                "(e.g. [bold cyan]ollama pull llama3.2[/bold cyan]).",
                border_style="red",
            )
        )
        sys.exit(1)

    table = Table(
        show_header=True,
        header_style="bold yellow",
        box=SIMPLE_HEAVY,
        border_style="yellow",
        title="Available Ollama models",
        title_style="bold cyan",
    )
    table.add_column("#", style="bold magenta", justify="right")
    table.add_column("Model", style="bold white")
    for i, name in enumerate(models, start=1):
        table.add_row(str(i), name)
    console.print(Align.center(table))

    choices = [str(i) for i in range(1, len(models) + 1)]
    idx = Prompt.ask(
        "[bold cyan]Select a model[/bold cyan]",
        choices=choices,
        default="1",
        show_choices=False,
    )
    model = models[int(idx) - 1]
    return {"provider": "ollama", "host": host, "model": model}


def run_setup() -> dict:
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]✨ Welcome to lzy ✨[/bold cyan]\n"
            "[dim]No provider configured yet — let's set one up.[/dim]",
            border_style="cyan",
        )
    )
    console.print()
    _render_providers_table()
    console.print()

    choices = [str(i) for i in range(1, len(PROVIDERS) + 1)]
    idx = Prompt.ask(
        "[bold cyan]Select a provider[/bold cyan]",
        choices=choices,
        default="1",
        show_choices=False,
    )
    provider = PROVIDERS[int(idx) - 1]

    if provider["key"] == "ollama":
        cfg = _setup_ollama()
    else:
        console.print(
            f"\n🔑 [dim]Enter your[/dim] [bold cyan]{provider['label']}[/bold cyan] [dim]API key[/dim] "
            f"[dim](characters will be masked)[/dim]"
        )
        api_key = ""
        while not api_key.strip():
            api_key = masked_input("[bold yellow]›[/bold yellow] ")
            if not api_key.strip():
                console.print("[bold red]API key cannot be empty.[/bold red]")
        cfg = {"provider": provider["key"], "api_key": api_key.strip()}

    save_config(cfg)
    console.print()
    console.print(
        Panel.fit(
            f"[bold green]✓ Configuration saved[/bold green] [dim]({CONFIG_FILE})[/dim]",
            border_style="green",
        )
    )
    console.print()
    return cfg
