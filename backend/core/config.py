from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Variables para Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    
    # Aquí puedes añadir las otras variables (Twilio, Telegram) después
    # twilio_account_sid: str | None = None
    # etc...

    class Config:
        # Esta línea le dice a Pydantic que lea las variables del archivo .env
        env_file = ".env" 

# Creamos una instancia global que será usada en toda la aplicación
settings = Settings()