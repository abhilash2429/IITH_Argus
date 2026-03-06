"""
Qualitative input router — save and retrieve Credit Officer observations.
POST /qualitative/{company_id}: Save qualitative notes.
GET /qualitative/{company_id}: Get latest qualitative input.
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.db_models import QualitativeInput

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/qualitative/{company_id}")
async def save_qualitative(
    company_id: str,
    notes: str = Body(...),
    factory_capacity_pct: Optional[float] = Body(default=None),
    management_assessment: Optional[str] = Body(default=None),
    submitted_by: Optional[str] = Body(default="Credit Officer"),
    db: AsyncSession = Depends(get_db),
):
    """
    Save Credit Officer qualitative notes to database.

    Args:
        company_id: UUID of the company.
        notes: Qualitative observation notes.
        factory_capacity_pct: Factory capacity from site visit.
        management_assessment: Management quality assessment.
        submitted_by: Name of the submitting officer.
        db: Database session.

    Returns:
        Dict with saved record ID.
    """
    qi = QualitativeInput(
        id=str(uuid.uuid4()),
        company_id=company_id,
        notes=notes,
        factory_capacity_pct=factory_capacity_pct,
        management_assessment=management_assessment,
        submitted_by=submitted_by,
    )
    db.add(qi)
    await db.commit()

    return {"id": qi.id, "status": "saved"}


@router.get("/qualitative/{company_id}")
async def get_qualitative(
    company_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the latest qualitative input for a company.

    Args:
        company_id: UUID of the company.
        db: Database session.

    Returns:
        Latest qualitative input record or empty dict.
    """
    result = await db.execute(
        select(QualitativeInput)
        .where(QualitativeInput.company_id == company_id)
        .order_by(QualitativeInput.created_at.desc())
        .limit(1)
    )
    qi = result.scalars().first()

    if not qi:
        return {}

    return {
        "id": str(qi.id),
        "notes": qi.notes,
        "factory_capacity_pct": qi.factory_capacity_pct,
        "management_assessment": qi.management_assessment,
        "submitted_by": qi.submitted_by,
        "created_at": str(qi.created_at),
    }
