from __future__ import annotations
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from api.src.domain.entities.resume_request import ResumeRequest
from api.src.domain.entities.resume_result import ResumeResult
from api.src.ports.planners.resume_polisher import ResumePolisher


class _ResumeState(TypedDict):
    resume_text: str
    job_description: str
    analysis: str
    polished: str
    improvements: list[str]


class LangGraphResumePolisher(ResumePolisher):
    def __init__(self, llm: ChatGroq) -> None:
        self._llm = llm
        self._graph = self._build_graph()

    async def polish(self, request: ResumeRequest) -> ResumeResult:
        initial_state: _ResumeState = {
            "resume_text": request.resume_text,
            "job_description": request.job_description or "",
            "analysis": "",
            "polished": "",
            "improvements": [],
        }
        result = await self._graph.ainvoke(initial_state)
        return ResumeResult(
            original=request.resume_text,
            polished=result["polished"],
            improvements=result["improvements"],
            thread_id=request.thread_id,
        )

    def _build_graph(self) -> object:
        graph: StateGraph = StateGraph(_ResumeState)
        graph.add_node("analyze_agent", self._analyze_agent)
        graph.add_node("polish_agent", self._polish_agent)
        graph.add_edge(START, "analyze_agent")
        graph.add_edge("analyze_agent", "polish_agent")
        graph.add_edge("polish_agent", END)
        return graph.compile()

    async def _analyze_agent(self, state: _ResumeState) -> dict:
        jd_context = f"\nTarget Job Description:\n{state['job_description']}" if state["job_description"] else ""
        prompt = (
            f"Analyze this resume and identify 5 specific improvements needed:{jd_context}\n\n"
            f"Resume:\n{state['resume_text']}\n\n"
            "List improvements as a Python list format: ['improvement 1', 'improvement 2', ...]"
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        improvements: list[str] = []
        try:
            import ast
            start = response.content.find("[")
            end = response.content.rfind("]") + 1
            if start >= 0 and end > start:
                improvements = ast.literal_eval(response.content[start:end])
        except Exception:
            improvements = [line.strip("- •").strip() for line in response.content.split("\n") if line.strip()]
        return {"analysis": response.content, "improvements": improvements}

    async def _polish_agent(self, state: _ResumeState) -> dict:
        jd_context = f"\nOptimize for this job:\n{state['job_description']}" if state["job_description"] else ""
        prompt = (
            f"Rewrite and polish this resume professionally.{jd_context}\n\n"
            f"Weaknesses to address:\n{state['analysis']}\n\n"
            f"Original Resume:\n{state['resume_text']}\n\n"
            "Output the complete polished resume in clean Markdown format."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"polished": response.content}
