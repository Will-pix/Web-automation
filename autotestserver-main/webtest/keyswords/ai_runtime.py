import os

from platformconfig.service.runtime_store import load_settings


def get_runtime_ai_settings():
    """读取运行时 AI 配置，优先 runtime_settings.json，fallback 环境变量"""
    settings = load_settings().get("ai", {})
    api_base = (settings.get("api_base") or "https://ark.cn-beijing.volces.com/api/v3").rstrip("/")
    api_key = settings.get("api_key") or os.environ.get("OPENAI_API_KEY", "")
    model_name = settings.get("model_name") or os.environ.get("AI_MODEL_NAME", "doubao-pro-4k")
    request_path = settings.get("request_path") or "/chat/completions"
    if not request_path.startswith("/"):
        request_path = f"/{request_path}"
    return {
        "api_base": api_base,
        "api_key": api_key,
        "model_name": model_name,
        "request_path": request_path,
        # 视觉模型：用于截图坐标识别（doubao-1-5-ui-tars 系列）
        "vision_model": settings.get("vision_model_name") or "doubao-1-5-ui-tars-250428",
        # 文本模型：用于语义分析/分解（doubao-seed 系列）
        "text_model": settings.get("text_model_name") or "doubao-seed-1-6-250615",
    }


def apply_runtime_api_key():
    config = get_runtime_ai_settings()
    os.environ["OPENAI_API_KEY"] = config["api_key"]
    return config


def build_headers(config):
    return {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
    }

