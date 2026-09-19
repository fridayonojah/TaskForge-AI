"""ARQ background task definitions."""
from __future__ import annotations
import json
import os
from datetime import datetime

import redis.asyncio as aioredis
from langchain_groq import ChatGroq
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg
import certifi

from api.src.adapters.planners.langgraph_travel_planner import LangGraphTravelPlanner
from api.src.adapters.planners.langgraph_industry_researcher import LangGraphIndustryResearcher
from api.src.adapters.tools.aviationstack_flight_tool import AviationStackFlightTool
from api.src.adapters.tools.tavily_hotel_tool import TavilyHotelTool
from api.src.adapters.tools.tavily_web_search_tool import TavilyWebSearchTool
from api.src.domain.entities.travel_request import TravelRequest
from api.src.domain.entities.research_request import ResearchRequest
from api.src.domain.value_objects.thread_id import ThreadId


async def plan_trip_task(ctx: dict, job_id: str, query: str, thread_id_value: str) -> None:
    redis: aioredis.Redis = ctx["redis"]
    key = f"job:{job_id}"

    async def _update(status: str, result: dict | None = None, error: str | None = None) -> None:
        raw = await redis.get(key)
        if raw:
            data = json.loads(raw)
            data["status"] = status
            if result:
                data["result"] = result
                data["completed_at"] = datetime.utcnow().isoformat()
            if error:
                data["error"] = error
                data["completed_at"] = datetime.utcnow().isoformat()
            await redis.set(key, json.dumps(data), ex=3600)

    await _update("processing")
    try:
        db_url = os.environ["DATABASE_URL"]
        if "sslmode" not in db_url:
            db_url += "?sslmode=require"
        os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        conn = psycopg.connect(db_url)
        checkpointer = PostgresSaver(conn)
        checkpointer.setup()
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.environ["GROQ_API_KEY"])
        flight_tool = AviationStackFlightTool(
            api_key=os.environ["AVIATIONSTACK_API_KEY"],
            default_origin=os.environ.get("DEFAULT_ORIGIN_IATA", "DAC"),
        )
        hotel_tool = TavilyHotelTool(api_key=os.environ["TAVILY_API_KEY"])
        planner = LangGraphTravelPlanner(
            flight_tool=flight_tool, hotel_tool=hotel_tool, llm=llm, checkpointer=checkpointer
        )
        request = TravelRequest(query=query, thread_id=ThreadId.from_optional(thread_id_value))
        import asyncio
        plan = await asyncio.to_thread(planner.plan, request)
        await _update("completed", result={
            "success": True,
            "thread_id": plan.thread_id.value,
            "answer": plan.answer,
            "flight_results": plan.flight_results,
            "hotel_results": plan.hotel_results,
            "itinerary": plan.itinerary,
            "llm_calls": plan.llm_calls,
        })
    except Exception as exc:
        await _update("failed", error=str(exc))


async def research_industry_task(ctx: dict, job_id: str, industry: str, thread_id_value: str) -> None:
    redis: aioredis.Redis = ctx["redis"]
    key = f"job:{job_id}"

    async def _update(status: str, result: dict | None = None, error: str | None = None) -> None:
        raw = await redis.get(key)
        if raw:
            data = json.loads(raw)
            data["status"] = status
            if result:
                data["result"] = result
                data["completed_at"] = datetime.utcnow().isoformat()
            if error:
                data["error"] = error
                data["completed_at"] = datetime.utcnow().isoformat()
            await redis.set(key, json.dumps(data), ex=3600)

    await _update("processing")
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.environ["GROQ_API_KEY"])
        search_tool = TavilyWebSearchTool(api_key=os.environ["TAVILY_API_KEY"])
        researcher = LangGraphIndustryResearcher(llm=llm, search_tool=search_tool)
        request = ResearchRequest(industry=industry, thread_id=ThreadId.from_optional(thread_id_value))
        result = await researcher.research(request)
        await _update("completed", result={
            "success": True,
            "industry": result.industry,
            "summary": result.summary,
            "trends": result.trends,
            "key_players": result.key_players,
            "thread_id": result.thread_id.value,
        })
    except Exception as exc:
        await _update("failed", error=str(exc))
