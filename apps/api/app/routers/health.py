from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.config import Settings, get_settings
from app.models.responses import ApiSuccessEnvelope, success_envelope
from app.models.system import HealthData, VersionData

router = APIRouter(tags=["system"])


@router.get("/health", response_model=ApiSuccessEnvelope)
def health(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ApiSuccessEnvelope:
    return success_envelope(
        request,
        HealthData(status="ok", service=settings.service_slug).model_dump(),
    )


@router.get("/version", response_model=ApiSuccessEnvelope)
def version(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> ApiSuccessEnvelope:
    return success_envelope(
        request,
        VersionData(
            service=settings.service_slug,
            version=settings.app_version,
            api_version=settings.api_version,
        ).model_dump(),
    )
