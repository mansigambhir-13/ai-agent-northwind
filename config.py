import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class Config:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    database_path: str = os.getenv("DATABASE_PATH", "northwind.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    model_name: str = os.getenv("MODEL_NAME", "gpt-4")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))

    def validate(self) -> bool:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return True

config = Config()
