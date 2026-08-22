"""Test Async Agent Jobs polling lifecycle (processing -> success)."""
from __future__ import annotations

import asyncio
import pytest
from app.models.agent_schemas import AgentAnalysisRequest
from app.services.agent_job_service import create_agent_job, get_agent_job, list_agent_jobs


@pytest.mark.asyncio
async def test_agent_job_lifecycle():
    req = AgentAnalysisRequest(
        query="tumbler",
        window="30d",
        data_source="MARKET_SIGNALS",
        deep=False,
        live_scrape=False,
        limit=5,
    )

    # 1. Create Job
    job = await create_agent_job(req)
    assert job.job_id.startswith("job_")
    assert job.status in ("processing", "success")

    # 2. Poll until completed or timeout (up to 30s)
    for _ in range(60):
        current_job = get_agent_job(job.job_id)
        assert current_job is not None
        if current_job.status == "success":
            assert current_job.result is not None
            assert len(current_job.result.top_keywords) > 0
            assert current_job.progress_pct == 100
            break
        await asyncio.sleep(0.5)
    else:
        pytest.fail("Job did not finish in time")

    # 3. List jobs
    all_jobs = list_agent_jobs()
    assert any(j.job_id == job.job_id for j in all_jobs)
