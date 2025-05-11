from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv
from rich.table import Table
from rich.console import Console
import sys
import subprocess
import json
import argparse
import os  # Import necessário para acessar variáveis de ambiente


from rich.box import SIMPLE_HEAVY

load_dotenv()
console = Console()

class BashCommand(BaseModel):
    command: str
    description: str



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

def handle_command(prompt: str):
    agent = Agent(
        'google-gla:gemini-1.5-flash', 
        output_type=BashCommand,
        system_prompt=(
            'You are a helpful assistant that translates natural language commands into linux bash commands. '
            'Your response will be used in a bash script, so be careful with the syntax. '
            'Also provide a description of the command in natural language.'
        )
    )    
    console.print("🔎 [bold cyan]Wait...[/bold cyan]")
    
    response = agent.run_sync(prompt)
    result = json.loads(response.output.model_dump_json())

    print_bash_table(result["command"], result["description"])

    confirm = input("\n👉 Run (y), Abort (n) or Edit(e)?").strip().lower()
    if confirm == 'e':
        bash_cmd = f'read -e -p "🔧 Edit or [enter] to execute => " -i "{result["command"]}" cmd; eval "$cmd"'
        subprocess.run(["bash", "-c", bash_cmd])
    elif confirm == 'y':
        print("🚀...\n")
        subprocess.run(result['command'], shell=True)
    else:
        console.print("❌ [bold red]Aborted.[/bold red]")

def main():
    cli_provider = os.getenv("CLI_PROVIDER")
    if not cli_provider:
        console.print("❌ [bold red]Error:[/bold red] The environment variable [bold cyan]CLI_PROVIDER[/bold cyan] is not set.")
        console.print("Available options: [bold yellow]Gemini, Together, Openai, NVidia[/bold yellow].")
        sys.exit(1)

    # Verifica se a variável de ambiente correspondente à API key do provider está definida
    cli_api_key = None
    if cli_provider.lower() == "gemini":
        cli_api_key = os.getenv("GEMINI_API_KEY")
        if not cli_api_key:
            console.print("❌ [bold red]Error:[/bold red] The environment variable [bold cyan]GEMINI_API_KEY[/bold cyan] is not set.")
    elif cli_provider.lower() == "together":
        cli_api_key = os.getenv("TOGETHER_API_KEY")
        if not cli_api_key:
            console.print("❌ [bold red]Error:[/bold red] The environment variable [bold cyan]TOGETHER_API_KEY[/bold cyan] is not set.")
    elif cli_provider.lower() == "openai":
        cli_api_key = os.getenv("OPENAI_API_KEY")
        if not cli_api_key:
            console.print("❌ [bold red]Error:[/bold red] The environment variable [bold cyan]OPENAI_API_KEY[/bold cyan] is not set.")
    elif cli_provider.lower() == "nvidia":
        cli_api_key = os.getenv("NVIDIA_API_KEY")
        if not cli_api_key:
            console.print("❌ [bold red]Error:[/bold red] The environment variable [bold cyan]NVIDIA_API_KEY[/bold cyan] is not set.")
    else:
        console.print(f"❌ [bold red]Error:[/bold red] Unknown provider [bold cyan]{cli_provider}[/bold cyan].")
        console.print("Available options: [bold yellow]Gemini, Together, Openai, NVidia[/bold yellow].")
        sys.exit(1)

    if not cli_api_key:
        sys.exit(1)

    if not cli_provider or not cli_api_key:
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="Translate natural language commands into Linux bash commands."
    )
    parser.add_argument(
        "command",
        nargs="+",
        help="The natural language command to translate into a bash command."
    )
    args = parser.parse_args()

    prompt = " ".join(args.command)
    handle_command(prompt)

if __name__ == "__main__":
    main()
