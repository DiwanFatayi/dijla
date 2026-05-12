"""Certificate listing."""

from __future__ import annotations

from fastapi import APIRouter, Request

from dijla.presentation.api.schemas import CertificateOut

router = APIRouter(prefix="/api/v1/certificates", tags=["certificates"])


@router.get("", response_model=list[CertificateOut])
async def list_certificates(request: Request) -> list[CertificateOut]:
    container = request.app.state.container
    items = await container.certificates.list()
    return [CertificateOut(**c.model_dump()) for c in items]
