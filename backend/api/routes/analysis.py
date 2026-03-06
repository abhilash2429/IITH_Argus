"""
Analysis pipeline trigger, status stream, and results endpoints.
"""

from __future__ import annotations

import asyncio
import json
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import RequestContext, get_request_context
from backend.core.pipeline_service import IntelliCreditPipeline
from backend.core.state_store import get_latest_run
from backend.database import AsyncSessionLocal, get_db
from backend.schemas.common import build_response

router = APIRouter(prefix="/api/v1", tags=["analysis"])

_pipeline = IntelliCreditPipeline()
_active_tasks: Dict[str, asyncio.Task] = {}


async def _run_pipeline(company_id: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            await _pipeline.run_analysis(db, company_id)
    finally:
        _active_tasks.pop(company_id, None)


@router.post("/companies/{company_id}/analyze")
async def trigger_analysis(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
):
    task = _active_tasks.get(company_id)
    if task and not task.done():
        return build_response(
            {"company_id": company_id, "status": "processing", "message": "Analysis already running"},
            status="processing",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )

    _active_tasks[company_id] = asyncio.create_task(_run_pipeline(company_id))
    run = await get_latest_run(db, company_id)
    return build_response(
        {
            "company_id": company_id,
            "status": "processing",
            "run_id": str(run.id) if run else None,
            "message": "Analysis triggered",
        },
        status="processing",
        request_id=ctx.request_id,
        started_at=ctx.started_at,
    )


@router.get("/companies/{company_id}/status")
async def stream_status(company_id: str):
    async def event_stream():
        sent = 0
        while True:
            async with AsyncSessionLocal() as db:
                run = await get_latest_run(db, company_id)
            if run:
                logs = run.audit_log or []
                for line in logs[sent:]:
                    sent += 1
                    payload = {
                        "type": "log",
                        "message": line.get("message"),
                        "step": line.get("step"),
                        "timestamp": line.get("timestamp"),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

                state = {
                    "type": "status",
                    "status": run.status,
                    "step": run.current_step,
                    "progress_pct": run.progress_pct,
                }
                yield f"data: {json.dumps(state)}\n\n"
                if run.status in {"completed", "error"}:
                    yield f"data: {json.dumps({'type': 'complete' if run.status == 'completed' else 'error'})}\n\n"
                    break
            elif company_id in _active_tasks:
                yield f"data: {json.dumps({'type': 'status', 'status': 'processing', 'step': 'INITIALIZING', 'progress_pct': 0})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'message': 'No analysis run found'})}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/companies/{company_id}/results")
async def get_results(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
):
    run = await get_latest_run(db, company_id)
    if not run:
        return build_response(
            {
                "company_id": company_id,
                "status": "processing",
                "current_step": "AWAITING_ANALYSIS",
                "progress_pct": 0,
                "message": "Documents uploaded. Waiting for analysis run to start.",
            },
            status="processing",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )
    if run.status == "error":
        return build_response(
            {
                "company_id": company_id,
                "status": "error",
                "current_step": run.current_step,
                "progress_pct": run.progress_pct,
                "error_message": run.error_message or "Analysis failed",
            },
            status="error",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )
    if run.status != "completed":
        return build_response(
            {
                "company_id": company_id,
                "status": run.status,
                "current_step": run.current_step,
                "progress_pct": run.progress_pct,
            },
            status="processing",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )
    return build_response(
        run.result_payload or {},
        request_id=ctx.request_id,
        started_at=ctx.started_at,
    )


@router.get("/companies/{company_id}/explain")
async def get_explanation(
    company_id: str,
    db: AsyncSession = Depends(get_db),
    ctx: RequestContext = Depends(get_request_context),
):
    run = await get_latest_run(db, company_id)
    if not run:
        return build_response(
            {
                "company_id": company_id,
                "status": "processing",
                "message": "Analysis not started yet",
                "decision_narrative": "",
                "top_positive_factors": [],
                "top_negative_factors": [],
                "shap_waterfall_data": {},
                "confidence_in_decision": 0.0,
            },
            status="processing",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )
    if run.status != "completed" or not run.result_payload:
        return build_response(
            {
                "company_id": company_id,
                "status": "processing",
                "message": "Explainability is being generated",
                "decision_narrative": "",
                "top_positive_factors": [],
                "top_negative_factors": [],
                "shap_waterfall_data": {},
                "confidence_in_decision": 0.0,
            },
            status="processing",
            request_id=ctx.request_id,
            started_at=ctx.started_at,
        )
    return build_response(
        run.result_payload.get("explanation", {}),
        request_id=ctx.request_id,
        started_at=ctx.started_at,
    )
