from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from lzy.domain import BashCommand


class AgentBuilder:
    def __init__(self, config: dict):
        self.config = config
        self.provider = config["provider"].lower()

    def select_model(self):
        api_key = self.config.get("api_key")

        if self.provider == "openai":
            return OpenAIModel("gpt-4o", provider=OpenAIProvider(api_key=api_key))
        elif self.provider == "gemini":
            from pydantic_ai.models.gemini import GeminiModel
            from pydantic_ai.providers.google_gla import GoogleGLAProvider
            return GeminiModel(
                "gemini-1.5-flash",
                provider=GoogleGLAProvider(api_key=api_key),
            )
        elif self.provider == "anthropic":
            from pydantic_ai.models.anthropic import AnthropicModel
            from pydantic_ai.providers.anthropic import AnthropicProvider
            return AnthropicModel(
                "claude-3-5-sonnet-latest",
                provider=AnthropicProvider(api_key=api_key),
            )
        elif self.provider == "groq":
            from pydantic_ai.models.groq import GroqModel
            from pydantic_ai.providers.groq import GroqProvider
            return GroqModel(
                "llama-3.3-70b-versatile",
                provider=GroqProvider(api_key=api_key),
            )
        elif self.provider == "mistral":
            from pydantic_ai.models.mistral import MistralModel
            from pydantic_ai.providers.mistral import MistralProvider
            return MistralModel(
                "mistral-large-latest",
                provider=MistralProvider(api_key=api_key),
            )
        elif self.provider == "together":
            return OpenAIModel(
                "meta-llama/Llama-4-Scout-17B-16E-Instruct",
                provider=OpenAIProvider(
                    base_url="https://api.together.xyz/v1",
                    api_key=api_key,
                ),
            )
        elif self.provider == "nvidia":
            return OpenAIModel(
                "meta/llama-4-maverick-17b-128e-instruct",
                provider=OpenAIProvider(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=api_key,
                ),
            )
        elif self.provider == "ollama":
            host = self.config.get("host", "http://localhost:11434").rstrip("/")
            return OpenAIModel(
                self.config["model"],
                provider=OpenAIProvider(
                    base_url=f"{host}/v1",
                    api_key="ollama",
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
                "You are a helpful assistant that translates natural language commands into linux bash commands. "
                "Your response will be used in a bash script, so be careful with the syntax. "
                "Also provide a description of the command in natural language."
            ),
        )
        return agent
