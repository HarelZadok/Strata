from fastapi import APIRouter
from strata_core.config import settings

router = APIRouter()

@router.get("/config")
def get_config():
    return {
        "llm_provider_mode": settings.llm_provider_mode,
        "llm_base_url": settings.llm_base_url,
        "llm_model": settings.llm_model,
    }

@router.get("/config/models")
async def get_models():
    from strata_core.llm_provider import LLMClient
    client = LLMClient()
    models = await client.get_available_models()
    return {"models": models, "active": settings.llm_model}
