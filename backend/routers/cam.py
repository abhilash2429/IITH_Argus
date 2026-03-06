"""
CAM router — retrieve and download Credit Appraisal Memo.
GET /cam/{company_id}: Returns CAM text and file paths.
GET /cam/{company_id}/download/docx: Download Word document.
GET /cam/{company_id}/download/pdf: Download PDF document.
"""

import logging

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.db_models import CamOutput

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/cam/{company_id}")
async def get_cam(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the CAM text and file paths for a company.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        Dict with cam_text, docx_path, and pdf_path.
    """
    result = await db.execute(
        select(CamOutput)
        .where(CamOutput.company_id == company_id)
        .order_by(CamOutput.created_at.desc())
        .limit(1)
    )
    cam = result.scalars().first()

    if not cam:
        return {"error": "No CAM found for this company"}

    return {
        "cam_text": cam.cam_text,
        "docx_path": cam.docx_path,
        "pdf_path": cam.pdf_path,
    }


@router.get("/cam/{company_id}/download/docx")
async def download_docx(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the CAM as a Word document.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        FileResponse with the .docx file.
    """
    result = await db.execute(
        select(CamOutput)
        .where(CamOutput.company_id == company_id)
        .order_by(CamOutput.created_at.desc())
        .limit(1)
    )
    cam = result.scalars().first()

    if not cam or not cam.docx_path:
        return {"error": "DOCX not found"}

    return FileResponse(
        cam.docx_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"CAM_{company_id}.docx",
    )


@router.get("/cam/{company_id}/download/pdf")
async def download_pdf(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Download the CAM as a PDF document.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        FileResponse with the .pdf file.
    """
    result = await db.execute(
        select(CamOutput)
        .where(CamOutput.company_id == company_id)
        .order_by(CamOutput.created_at.desc())
        .limit(1)
    )
    cam = result.scalars().first()

    if not cam or not cam.pdf_path:
        return {"error": "PDF not found"}

    return FileResponse(
        cam.pdf_path,
        media_type="application/pdf",
        filename=f"CAM_{company_id}.pdf",
    )
