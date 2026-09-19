from __future__ import annotations
import asyncio
import operator
from typing import Annotated

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from typing_extensions import TypedDict

from api.src.domain.entities.travel_request import TravelRequest
from api.src.domain.entities.travel_plan import TravelPlan
from api.src.ports.planners.travel_planner import TravelPlanner
from api.src.ports.tools.flight_search_tool import FlightSearchTool
from api.src.ports.tools.hotel_search_tool import HotelSearchTool


class _TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


class LangGraphTravelPlanner(TravelPlanner):
    def __init__(
        self,
        flight_tool: FlightSearchTool,
        hotel_tool: HotelSearchTool,
        llm: ChatGroq,
        checkpointer: PostgresSaver,
    ) -> None:
        self._flight_tool = flight_tool
        self._hotel_tool = hotel_tool
        self._llm = llm
        self._graph = self._build_graph(checkpointer)

    async def plan(self, request: TravelRequest) -> TravelPlan:
        config = {"configurable": {"thread_id": request.thread_id.value}}
        initial_state: _TravelState = {
            "messages": [HumanMessage(content=request.query)],
            "user_query": request.query,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        }
        result = await asyncio.to_thread(self._graph.invoke, initial_state, config)
        last_message = result.get("messages", [])
        answer = last_message[-1].content if last_message else ""
        return TravelPlan(
            thread_id=request.thread_id,
            answer=answer,
            flight_results=result.get("flight_results", ""),
            hotel_results=result.get("hotel_results", ""),
            itinerary=result.get("itinerary", ""),
            llm_calls=result.get("llm_calls", 0),
        )

    def _build_graph(self, checkpointer: PostgresSaver) -> object:
        graph: StateGraph = StateGraph(_TravelState)
        graph.add_node("flight_agent", self._flight_agent)
        graph.add_node("hotel_agent", self._hotel_agent)
        graph.add_node("itinerary_agent", self._itinerary_agent)
        graph.add_node("final_agent", self._final_agent)
        graph.add_edge(START, "flight_agent")
        graph.add_edge("flight_agent", "hotel_agent")
        graph.add_edge("hotel_agent", "itinerary_agent")
        graph.add_edge("itinerary_agent", "final_agent")
        graph.add_edge("final_agent", END)
        return graph.compile(checkpointer=checkpointer)

    def _flight_agent(self, state: _TravelState) -> dict:
        return {"flight_results": self._flight_tool.search(state["user_query"])}

    def _hotel_agent(self, state: _TravelState) -> dict:
        return {"hotel_results": self._hotel_tool.search(state["user_query"])}

    def _itinerary_agent(self, state: _TravelState) -> dict:
        prompt = (
            f"Create a detailed day-by-day travel itinerary for: {state['user_query']}\n\n"
            f"Available flights:\n{state['flight_results']}\n\n"
            f"Available hotels:\n{state['hotel_results']}"
        )
        response = self._llm.invoke([HumanMessage(content=prompt)])
        return {"itinerary": response.content, "llm_calls": state["llm_calls"] + 1}

    def _final_agent(self, state: _TravelState) -> dict:
        prompt = (
            "You are TaskForge AI. Provide a comprehensive travel plan with these 6 sections:\n"
            "1. Trip Overview\n2. Flight Options\n3. Accommodation\n"
            "4. Day-by-Day Itinerary\n5. Budget Estimate\n6. Travel Tips\n\n"
            f"Query: {state['user_query']}\n"
            f"Flights:\n{state['flight_results']}\n\n"
            f"Hotels:\n{state['hotel_results']}\n\n"
            f"Itinerary:\n{state['itinerary']}"
        )
        response = self._llm.invoke([HumanMessage(content=prompt)])
        return {
            "messages": [AIMessage(content=response.content)],
            "llm_calls": state["llm_calls"] + 1,
        }
