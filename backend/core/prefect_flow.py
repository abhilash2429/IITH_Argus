"""
Prefect 2.x flow wrapper for the Intelli-Credit pipeline.
"""

from __future__ import annotations

from prefect import flow, task

from backend.core.pipeline_service import IntelliCreditPipeline
from backend.database import AsyncSessionLocal


@task(name="run-intelli-credit-analysis")
async def run_analysis_task(company_id: str) -> dict:
    pipeline = IntelliCreditPipeline()
    async with AsyncSessionLocal() as db:
        return await pipeline.run_analysis(db, company_id)


@flow(name="intelli-credit-analysis-flow")
async def intelli_credit_flow(company_id: str) -> dict:
    return await run_analysis_task(company_id)

