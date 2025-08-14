from dataclasses import dataclass
from environs import Env

@dataclass
class BotSettings:
    token: str
    owner_ids: list[int]
    
@dataclass
class RedisSettings:
    use_redis: bool
    redis_host: str

@dataclass
class DbConfig:
    dsn: str

@dataclass
class ServiceQR:
    service_qr_url: str

@dataclass
class Config:
    bot: BotSettings
    redis: RedisSettings
    db: DbConfig
    service_qr: ServiceQR

def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    token = env("BOT_TOKEN")
    owner_ids = env.list('OWNER_IDS', subcast=int)
    dsn = env("DB_DSN")
    service_qr_url = env("SERVICE_QR_URL")
    use_redis = env.bool("USE_REDIS", False)
    redis_host = env.str("REDIS_HOST", None)
    return Config(
        bot=BotSettings(token=token, 
                        owner_ids=owner_ids,
        ),
        redis=RedisSettings(use_redis=use_redis,
                            redis_host=redis_host,
        ),
        db=DbConfig(dsn=dsn),
        service_qr=ServiceQR(service_qr_url=service_qr_url),
    )