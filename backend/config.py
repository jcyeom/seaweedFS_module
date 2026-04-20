"""config.json 읽기/쓰기."""

from pathlib import Path

from .models import AppConfig, AppConfigUpdate

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


def load_config() -> AppConfig:
    if CONFIG_PATH.exists():
        return AppConfig.model_validate_json(CONFIG_PATH.read_text("utf-8"))
    cfg = AppConfig()
    save_config(cfg)
    return cfg


def save_config(cfg: AppConfig) -> None:
    CONFIG_PATH.write_text(cfg.model_dump_json(indent=2), "utf-8")


def update_config(update: AppConfigUpdate) -> AppConfig:
    cfg = load_config()
    data = cfg.model_dump()
    for k, v in update.model_dump(exclude_none=True).items():
        data[k] = v
    cfg = AppConfig(**data)
    save_config(cfg)
    return cfg
