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
