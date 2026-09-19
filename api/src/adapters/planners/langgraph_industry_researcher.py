from __future__ import annotations
from typing_extensions import TypedDict

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

from api.src.domain.entities.research_request import ResearchRequest
from api.src.domain.entities.research_result import ResearchResult
from api.src.ports.planners.industry_researcher import IndustryResearcher
from api.src.adapters.tools.tavily_web_search_tool import TavilyWebSearchTool


class _ResearchState(TypedDict):
    industry: str
    raw_search: str
    analysis: str
    trends: str
    key_players: str
    summary: str


class LangGraphIndustryResearcher(IndustryResearcher):
    def __init__(self, llm: ChatGroq, search_tool: TavilyWebSearchTool) -> None:
        self._llm = llm
        self._search = search_tool
        self._graph = self._build_graph()

    async def research(self, request: ResearchRequest) -> ResearchResult:
        initial_state: _ResearchState = {
            "industry": request.industry,
            "raw_search": "",
            "analysis": "",
            "trends": "",
            "key_players": "",
            "summary": "",
        }
        result = await self._graph.ainvoke(initial_state)
        return ResearchResult(
            industry=request.industry,
            summary=result["summary"],
            trends=result["trends"],
            key_players=result["key_players"],
            thread_id=request.thread_id,
        )

    def _build_graph(self) -> object:
        graph: StateGraph = StateGraph(_ResearchState)
        graph.add_node("search_agent", self._search_agent)
        graph.add_node("analyze_agent", self._analyze_agent)
        graph.add_node("report_agent", self._report_agent)
        graph.add_edge(START, "search_agent")
        graph.add_edge("search_agent", "analyze_agent")
        graph.add_edge("analyze_agent", "report_agent")
        graph.add_edge("report_agent", END)
        return graph.compile()

    async def _search_agent(self, state: _ResearchState) -> dict:
        import asyncio
        results = await asyncio.to_thread(
            self._search.search,
            f"{state['industry']} industry overview trends 2024 2025",
        )
        return {"raw_search": self._search.format_results(results)}

    async def _analyze_agent(self, state: _ResearchState) -> dict:
        prompt = (
            f"Analyze the {state['industry']} industry based on these search results:\n\n"
            f"{state['raw_search']}\n\n"
            "Identify:\n1. Top 3 current trends\n2. Top 5 key players/companies\n3. Market challenges\n"
            "Format clearly with headers."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        content = response.content
        trends = ""
        key_players = ""
        if "trend" in content.lower():
            lines = content.split("\n")
            in_trends = False
            in_players = False
            trend_lines = []
            player_lines = []
            for line in lines:
                if "trend" in line.lower():
                    in_trends = True
                    in_players = False
                elif "player" in line.lower() or "compan" in line.lower():
                    in_players = True
                    in_trends = False
                elif in_trends:
                    trend_lines.append(line)
                elif in_players:
                    player_lines.append(line)
            trends = "\n".join(trend_lines).strip()
            key_players = "\n".join(player_lines).strip()
        return {"analysis": content, "trends": trends or content, "key_players": key_players or content}

    async def _report_agent(self, state: _ResearchState) -> dict:
        prompt = (
            f"Write a comprehensive 2-page industry report on the {state['industry']} industry.\n\n"
            f"Research data:\n{state['analysis']}\n\n"
            "Include sections: Executive Summary, Market Overview, Key Trends, Major Players, "
            "Opportunities & Challenges, Outlook. Use Markdown formatting."
        )
        response = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return {"summary": response.content}
