"""
Company registration and document upload endpoints.
"""

from __future__ import annotations

import os
import uuid
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import RequestContext, get_request_context
from backend.config import settings
from backend.database import get_db
from backend.models.db_models import Company, Document
from backend.schemas.common import build_response
from backend.schemas.credit import CompanyCreateInput

router = APIRouter(prefix="/api/v1", tags=["upload"])


@router.post("/companies")
async def create_company(
    payload: CompanyCreateInput,
    db: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
):
    company = Company(
        id=uuid.uuid4(),
        name=payload.name,
        cin=payload.cin,
        sector=payload.sector,
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)

    return build_response(
        {
            "company_id": str(company.id),
            "name": company.name,
            "sector": company.sector,
            "loan_amount_requested": payload.loan_amount_requested,
            "loan_tenor_months": payload.loan_tenor_months,
            "loan_purpose": payload.loan_purpose,
            "status": "created",
        },
        request_id=ctx.request_id,
        started_at=ctx.started_at,
    )


@router.post("/companies/{company_id}/documents")
async def upload_documents(
    company_id: str,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
):
    try:
        company_uuid = uuid.UUID(company_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid company_id") from exc

    size_limit_bytes = settings.max_file_size_mb * 1024 * 1024
    upload_dir = os.path.join(settings.upload_dir, company_id)
    os.makedirs(upload_dir, exist_ok=True)

    saved = []
    for upload in files:
        content_type = (upload.content_type or "").lower()
        file_ext = os.path.splitext(upload.filename or "document")[1].lower()
        if content_type not in settings.allowed_mime_types and file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=415,
                detail=(
                    f"Unsupported file type: MIME={content_type}, extension={file_ext}. "
                    f"Allowed MIME: {settings.allowed_mime_types}; allowed extensions: {settings.allowed_extensions}"
                ),
            )

        raw = await upload.read()
        if len(raw) > size_limit_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"{upload.filename} exceeds max size of {settings.max_file_size_mb}MB",
            )

        safe_name = f"{uuid.uuid4().hex}{file_ext.lower()}"
        file_path = os.path.join(upload_dir, safe_name)

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(raw)

        db_doc = Document(
            id=uuid.uuid4(),
            company_id=company_uuid,
            file_path=file_path,
            doc_type="UNKNOWN",
            extraction_method=None,
        )
        db.add(db_doc)
        saved.append(
            {
                "document_id": str(db_doc.id),
                "filename": upload.filename,
                "stored_path": file_path,
                "content_type": content_type,
                "size_bytes": len(raw),
            }
        )

    await db.commit()
    return build_response(
        {
            "company_id": company_id,
            "uploaded_count": len(saved),
            "documents": saved,
        },
        request_id=ctx.request_id,
        started_at=ctx.started_at,
    )
