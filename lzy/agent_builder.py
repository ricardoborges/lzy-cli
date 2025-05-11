from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from lzy.domain import BashCommand
import os
from dotenv import load_dotenv

load_dotenv()

class AgentBuilder:
    def __init__(self, provider: str):
        self.provider = provider.lower()

    def select_model(self):
        if self.provider == "openai":
            return "openai:gpt-4o"        
        elif self.provider == "gemini":
            return "google-gla:gemini-1.5-flash"
        elif self.provider == "anthropic":
            return "anthropic:claude-3-5-sonnet-latest"
        elif self.provider == "groq":
            return "groq:llama-3.3-70b-versatile"
        elif self.provider == "mistral":
            return "mistral:mistral-large-latest"
        elif self.provider == "together":
            return OpenAIModel(
                'meta-llama/Llama-4-Scout-17B-16E-Instruct',
                provider=OpenAIProvider(
                    base_url='https://api.together.xyz/v1',
                    api_key=os.getenv('TOGETHER_API_KEY'),
                ),
            )
        elif self.provider == "nvidia":
            return OpenAIModel(
                'meta/llama-4-maverick-17b-128e-instruct',
                provider=OpenAIProvider(
                    base_url='https://integrate.api.nvidia.com/v1',
                    api_key=os.getenv('NVIDIA_API_KEY'),
                ),
            )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def build_agent(self):
        model = self.select_model()
        agent = Agent(
            model,
            output_type=BashCommand,
            system_prompt=(
                'You are a helpful assistant that translates natural language commands into linux bash commands. '
                'Your response will be used in a bash script, so be careful with the syntax. '
                'Also provide a description of the command in natural language.'
            )
        )
        return agent
