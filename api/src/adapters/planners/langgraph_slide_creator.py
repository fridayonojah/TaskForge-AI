from __future__ import annotations
import operator
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from domain.entities.slide_request import SlideRequest
from domain.entities.slide_deck import SlideDeck
from ports.planners.slide_creator import SlideCreator


class _SlideState(TypedDict):
    topic: str
    num_slides: int
    outline: str
    slides_markdown: str


class LangGraphSlideCreator(SlideCreator):
    def __init__(self, llm: ChatGroq) -> None:
        self._llm = llm
        self._graph = self._build_graph()

    async def create(self, request: SlideRequest) -> SlideDeck:
        initial_state: _SlideState = {
            "topic": request.topic,
            "num_slides": request.num_slides,
            "outline": "",
            "slides_markdown": "",
        }
        result = await self._graph.ainvoke(initial_state)
        return SlideDeck(
            topic=request.topic,
            slides_markdown=result["slides_markdown"],
            thread_id=request.thread_id,
        )

    def _build_graph(self) -> object:
        graph: StateGraph = StateGraph(_SlideState)
        graph.add_node("outline_agent", self._outline_agent)
        graph.add_node("content_agent", self._content_agent)
        graph.add_edge(START, "outline_agent")
        graph.add_edge("outline_agent", "content_agent")
        graph.add_edge("content_agent", END)
        return graph.compile()

    async def _outline_agent(self, state: _SlideState) -> dict:
        prompt = (
            f"Create a structured outline for a {state['num_slides']}-slide presentation on: {state['topic']}\n"
            "List each slide title and 3 bullet points. Be concise and professional."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"outline": response.content}

    async def _content_agent(self, state: _SlideState) -> dict:
        prompt = (
            f"Convert this outline into a complete slide deck in Markdown format for: {state['topic']}\n\n"
            f"Outline:\n{state['outline']}\n\n"
            "Format: Use ## for slide titles, bullet points for content. "
            "Include a title slide and conclusion slide. Make it professional and engaging."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"slides_markdown": response.content}
