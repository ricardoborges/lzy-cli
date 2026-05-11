import argparse
import json
import subprocess

from rich.box import SIMPLE_HEAVY
from rich.console import Console
from rich.table import Table

from lzy.agent_builder import AgentBuilder
from lzy.config import load_config, run_setup

console = Console()


def print_bash_table(command: str, description: str):
    table = Table(
        show_header=True,
        header_style="bold yellow",
        box=SIMPLE_HEAVY,
        border_style="yellow",
    )
    table.add_column("Command", style="bold white")
    table.add_column("Description", style="bold white")
    table.add_row(command, description)
    console.print(table)


def handle_command(prompt: str, config: dict):
    agent = AgentBuilder(config).build_agent()
    label = config.get("model") or config["provider"]
    console.print(f"[{label}] 🔎 [bold cyan]Wait...[/bold cyan]")

    response = agent.run_sync(prompt)
    result = json.loads(response.output.model_dump_json())

    print_bash_table(result["command"], result["description"])

    confirm = input("\n👉 Run (y), Abort (n) or Edit(e)?").strip().lower()
    if confirm == "e":
        bash_cmd = f'read -e -p "🔧 Edit or [enter] to execute => " -i "{result["command"]}" cmd; eval "$cmd"'
        subprocess.run(["bash", "-c", bash_cmd])
    elif confirm == "y":
        print("🚀...\n")
        subprocess.run(result["command"], shell=True)
    else:
        console.print("❌ [bold red]Aborted.[/bold red]")


def main():
    parser = argparse.ArgumentParser(
        description="Translate natural language commands into Linux bash commands."
    )
    parser.add_argument(
        "command",
        nargs="*",
        help="The natural language command to translate into a bash command.",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Re-run the interactive provider setup.",
    )
    args = parser.parse_args()

    config = load_config()
    if args.setup or not config:
        config = run_setup()

    if not args.command:
        console.print("[dim]Usage:[/dim] [bold]lzy[/bold] <natural language command>")
        return

    prompt = " ".join(args.command)
    handle_command(prompt, config)


if __name__ == "__main__":
    main()
