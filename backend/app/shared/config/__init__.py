from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PizzaFlow AI"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:5173"]

    database_url: str
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    menu_file_path: str
    base_file_path: str
    topping_file_path: str

    admin_username: str
    admin_password: str
    secret_key: str


settings = Settings()
