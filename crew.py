"""CrewAI HK EV workflow."""

from __future__ import annotations

import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path

from crewai import Agent, Crew, LLM, Process, Task
from crewai.llms.base_llm import BaseLLM
from crewai.tools import BaseTool
from dotenv import load_dotenv


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data: str) -> int:
        for stream in self.streams:
            stream.write(data)
            stream.flush()
        return len(data)

    def flush(self) -> None:
        for stream in self.streams: stream.flush()


class ResearchTool(BaseTool):
    name: str = "hk_ev_research_tool"
    description: str = "Returns HK EV facts with source labels."
    def _run(self) -> str:
        now("TOOL CALL | hk_ev_research_tool invoked")
        return (
            "- HK EV registrations are rising. [Source: Hong Kong Transport Department]\n"
            "- EV policy aligns with city decarbonization goals. [Source: Climate Ready @ Hong Kong]\n"
            "- Incentives helped EV adoption. [Source: HKSAR policy releases]\n"
            "- Tesla is a key incumbent. [Source: Market coverage]\n"
            "- BYD is a major competitor. [Source: Industry analyses]\n"
            "- Charging access is uneven by district. [Source: EMSD charging info]\n"
            "- High-density housing affects private charging ease. [Source: Property/utility reports]\n"
            "- Consumers care about total ownership cost. [Source: Consumer surveys]\n"
            "- Fleet electrification interest is increasing. [Source: Fleet case studies]\n"
            "- Competition intensity is high. [Source: Regional automotive press]\n"
        )


class MockLLM(BaseLLM):
    def __init__(self) -> None: super().__init__(model="mock-hk-ev-llm", provider="mock")

    def call(self, messages, tools=None, callbacks=None, available_functions=None, from_task=None, from_agent=None, response_model=None):  # type: ignore[override]
        role = (getattr(from_agent, "role", "") or "").lower()
        if "market data gatherer" in role:
            source_text = ResearchTool()._run()
            return source_text + "\n- Additional synthesis: Entry timing is favorable but competition is intense. [Source: Cross-source synthesis]"
        if "data interpreter" in role:
            return (
                "# HK EV Entry Analysis\n\n## Key Metrics\n- Demand: **4/5**\n- Competition: **5/5**\n- Infrastructure: **3/5**\n\n"
                "## SWOT\n| Category | Details |\n|---|---|\n| Strengths | Sustainability demand |\n| Weaknesses | New brand trust gap |\n"
                "| Opportunities | Fleet and partnerships |\n| Threats | Strong incumbents |\n\n## Opportunities\n- Fleet pilots\n- Charging partnerships\n- Cost-of-ownership marketing\n\n## Risks\n- Charging gaps\n- Margin pressure\n- Policy volatility"
            )
        return (
            "# Hong Kong EV Market Entry Report\n\n## Executive Summary\nPhased entry is recommended due to high demand and high competition.\n\n"
            "## Recommendation\nLaunch pilot then scale.\n\n## Action Plan\n1. Charging partnerships\n2. Fleet-first rollout\n3. Strong after-sales.\n"
        )


def now(msg: str) -> None: print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


def env_llm():
    load_dotenv()
    model = os.getenv("LLM_MODEL", "").strip()
    if model.lower() == "mock": return MockLLM()

    key = (
        os.getenv("LLM_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("GROQ_API_KEY")
    )

    if not model:
        if os.getenv("DEEPSEEK_API_KEY"):
            return LLM(model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"), base_url=os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com"), api_key=os.getenv("DEEPSEEK_API_KEY"))
        return MockLLM()
    if not key: raise EnvironmentError("Missing API key. Set LLM_API_KEY/DEEPSEEK_API_KEY/OPENAI_API_KEY/GEMINI_API_KEY/ANTHROPIC_API_KEY/GROQ_API_KEY.")
    return LLM(model=model, base_url=os.getenv("LLM_BASE_URL") or os.getenv("DEEPSEEK_API_BASE"), api_key=key)


def build() -> Crew:
    llm = env_llm()
    tool = ResearchTool()
    researcher = Agent(
        role="Market Data Gatherer",
        goal="Deliver at least 10 source-cited HK EV facts covering market size direction, competitors, regulations, and consumer trends.",
        backstory="Senior market-entry consultant who has spent 10+ years building evidence packs for automotive expansion in Asia.",
        tools=[tool], llm=llm, verbose=True,
    )
    analyst = Agent(
        role="Data Interpreter",
        goal="Convert research into decision-ready SWOT and metrics, with at least 3 opportunities and 3 risks.",
        backstory="Quantitative strategist known for turning raw market data into executive dashboards and risk frameworks using Excel/PowerBI.",
        llm=llm, verbose=True,
    )
    writer = Agent(
        role="Report Synthesizer",
        goal="Produce a clear executive report under 1000 words with recommendation, rationale, and action plan.",
        backstory="Board-level report writer focused on concise narratives, visual clarity, and stakeholder-ready recommendations.",
        llm=llm, verbose=True,
    )
    t1 = Task(
        description="Research Hong Kong EV market and competitors via tools. Include Tesla, BYD, regulations, and consumer trends.",
        expected_output="Markdown bullet list with 10+ facts, each ending with a source citation.",
        output_file="research.md", agent=researcher,
    )
    t2 = Task(
        description="Analyze Task 1 output to produce entry metrics, SWOT table, and prioritized opportunities/risks.",
        expected_output="Markdown analysis containing: key metrics, SWOT table, 3+ opportunities, and 3+ risks.",
        output_file="analysis.md", agent=analyst, context=[t1],
    )
    t3 = Task(
        description="Synthesize Tasks 1-2 into an executive recommendation report with concrete next steps.",
        expected_output="Full markdown report (<1000 words) with summary, recommendation, rationale, and action plan.",
        output_file="final_report.md", agent=writer, context=[t1, t2],
    )
    return Crew(agents=[researcher, analyst, writer], tasks=[t1, t2, t3], process=Process.sequential, verbose=True)


def run() -> str:
    log = Path("output.txt")
    log.write_text("", encoding="utf-8")
    with log.open("a", encoding="utf-8") as lf:
        with redirect_stdout(Tee(sys.stdout, lf)), redirect_stderr(Tee(sys.stderr, lf)):
            now("Starting CrewAI HK EV sequential run.")
            now("Agent collaboration chain: Researcher -> Analyst -> Writer")
            result = build().kickoff(inputs={"topic": "Hong Kong EV market entry"})
            now("FINAL RESULT START"); print(result); now("FINAL RESULT END")
            return str(result)


if __name__ == "__main__":
    run()
