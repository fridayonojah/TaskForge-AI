from __future__ import annotations
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from api.src.domain.entities.sheet_request import SheetRequest
from api.src.domain.entities.sheet_result import SheetResult
from api.src.ports.planners.sheet_builder import SheetBuilder


class _SheetState(TypedDict):
    topic: str
    requirements: str
    schema_design: str
    csv_content: str
    summary: str


class LangGraphSheetBuilder(SheetBuilder):
    def __init__(self, llm: ChatGroq) -> None:
        self._llm = llm
        self._graph = self._build_graph()

    async def build(self, request: SheetRequest) -> SheetResult:
        initial_state: _SheetState = {
            "topic": request.topic,
            "requirements": request.requirements,
            "schema_design": "",
            "csv_content": "",
            "summary": "",
        }
        result = await self._graph.ainvoke(initial_state)
        return SheetResult(
            topic=request.topic,
            csv_content=result["csv_content"],
            summary=result["summary"],
            thread_id=request.thread_id,
        )

    def _build_graph(self) -> object:
        graph: StateGraph = StateGraph(_SheetState)
        graph.add_node("schema_agent", self._schema_agent)
        graph.add_node("generate_agent", self._generate_agent)
        graph.add_edge(START, "schema_agent")
        graph.add_edge("schema_agent", "generate_agent")
        graph.add_edge("generate_agent", END)
        return graph.compile()

    async def _schema_agent(self, state: _SheetState) -> dict:
        prompt = (
            f"Design a spreadsheet schema for: {state['topic']}\n"
            f"Requirements: {state['requirements']}\n\n"
            "Define: column names, data types, and purpose. Be specific and practical."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"schema_design": response.content}

    async def _generate_agent(self, state: _SheetState) -> dict:
        prompt = (
            f"Generate a complete CSV spreadsheet for: {state['topic']}\n"
            f"Schema design:\n{state['schema_design']}\n\n"
            "Output: First a CSV block (```csv ... ```) with a header row and 10-15 realistic sample rows. "
            "Then a brief summary paragraph explaining the sheet structure."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content
        csv_content = content
        summary = ""
        if "```csv" in content:
            start = content.find("```csv") + 6
            end = content.find("```", start)
            csv_content = content[start:end].strip()
            summary = content[end + 3:].strip()
        return {"csv_content": csv_content, "summary": summary or f"Spreadsheet for {state['topic']}"}
