# Hong Kong EV Market Entry Crew

## Business Problem Addressed
This project models a company decision process for entering the Hong Kong electric vehicle (EV) market, where sustainability pressure is increasing but market competition is already intense. The core problem is reducing uncertainty before committing investment: management needs structured evidence about market size and demand, the competitive landscape (especially Tesla and BYD), regulations, and customer behavior, then a clear recommendation balancing growth potential against execution risk. The crew converts fragmented market inputs into a practical go/no-go style report that supports strategy discussions.

## How the 3 Agents Work Together
The workflow is sequential in `crew.py` using a three-agent setup: first, the **Researcher** (Market Data Gatherer) uses the research tool to produce a source-cited fact base on HK EV market direction, competitors, regulations, and consumer behavior; second, the **Analyst** (Data Interpreter) uses that evidence to produce decision metrics, a SWOT table, and prioritized opportunities/risks; third, the **Writer** (Report Synthesizer) turns both prior outputs into an executive recommendation report with concrete actions. This handoff structure makes collaboration explicit and traceable because Task 2 depends on Task 1, and Task 3 depends on Tasks 1 and 2.

## Agent Outputs and Coherence
- **Researcher output (`research.md`):** A 10+ bullet fact list with sources on market trends, competitors, regulations, and consumer behavior. This is the evidence base for all later reasoning.
- **Analyst output (`analysis.md`):** A markdown analysis with key metrics, SWOT table, opportunities, and risks, generated from `research.md`. This translates raw facts into decision-ready insight.
- **Writer output (`final_report.md`):** A concise executive recommendation report under 1000 words, synthesized from both `research.md` and `analysis.md`. This ensures recommendations are traceable back to evidence and structured analysis.
- **Execution trace (`output.txt`):** Full run log showing task order, agent actions, tool call(s), and final result, which demonstrates the sequential collaboration chain end-to-end.

## Challenges Encountered and Solutions
- **Challenge:** Different execution environments and API/provider restrictions could block live model runs.
  **Solution:** Added provider-agnostic LLM environment loading with a deterministic `mock` mode fallback so the CrewAI flow can still execute reliably for grading.
- **Challenge:** Rubric requires visible collaboration and tool usage in the execution output.
  **Solution:** Added explicit tool-call logging and sequential task dependencies so `output.txt` clearly shows researcher -> analyst -> writer collaboration.
- **Challenge:** Outputs needed strict format compliance for each task.
  **Solution:** Defined concrete expected output formats and dedicated files: `research.md`, `analysis.md`, and `final_report.md`.

## One Thing I Would Change With More Time
I would add live data connectors (e.g., web/API feeds and policy sources) and confidence scoring per insight so leadership can distinguish high-certainty findings from assumptions before committing capital.

## Run Instructions
1. Create and activate Python 3.11 virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Run: `python crew.py`.
4. Check generated files: `output.txt`, `research.md`, `analysis.md`, `final_report.md`.

## API Key Setup (DeepSeek)

API Key setup:

```bash
export DEEPSEEK_API_KEY=your_key_here
export DEEPSEEK_MODEL=deepseek-chat
export DEEPSEEK_API_BASE=https://api.deepseek.com
python crew.py
```
