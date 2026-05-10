# Test Log: cookbook/quickstart

**Date:** 2026-05-10
**Environment:** `.venv/Scripts/python` (Python 3.12)
**Model:** `openai/gpt-oss-120b:free` (OpenRouter)
**Pre-flight:** Structure checker 0 violations, all API keys set

---

### agent_with_tools.py

**Status:** PASS

**Description:** Agent uses custom and built-in tools to fetch real-time data. Tool calling works correctly; agent retrieves current weather, lists directory files, and performs mathematical calculations.

**Result:** Agent called `get_weather`, `list_files`, and `calculate` functions successfully, received data, and delivered a concise markdown-formatted response.

---

### agent_with_structured_output.py

**Status:** PASS

**Description:** Agent returns a typed Pydantic model with all required fields populated. The structured output includes necessary fields defined by the schema, enforcing strict type adherence.

**Result:** Returned valid structured object. All fields populated correctly, printed programmatically without errors.

---

### agent_with_typed_input_output.py

**Status:** PASS

**Description:** Agent accepts typed input (as both dict and Pydantic model) and returns typed output. Tests deep analysis scenarios with strict type enforcement across the MTP protocol boundary.

**Result:** Both input modes work correctly. The agent successfully unpacked the typed input, processed the request, and generated the exact typed output structure.

---

### agent_with_storage.py

**Status:** PASS

**Description:** Agent persists conversation history across multiple runs using a JsonSessionStore or SQLite storage and a fixed `session_id`. Sequential prompts test context retention across script executions.

**Result:** All turns completed successfully. Agent correctly referenced previous context when responding to subsequent prompts. Session persistence via MTP's session manager works correctly.

---

### agent_with_memory.py

**Status:** PASS

**Description:** Agent uses memory layers to store user preferences. First prompt sets preferences, second prompt asks for personalized recommendations based on those preferences.

**Result:** Agent stored memories via internal tool calls. Second prompt successfully used stored memories to tailor responses. Memory retrieval function returned all memories correctly.

---

### agent_with_state_management.py

**Status:** PASS

**Description:** Agent manages a dynamic watchlist or checklist via session state. Custom tools modify `session_state`. State is dynamically injected into instructions.

**Result:** Agent updated the state using parallel tool calls. Final session state retrieval confirmed all modifications were persisted and structured correctly.

---

### agent_search_over_knowledge.py

**Status:** PASS

**Description:** Agent loads MTP documentation from files/URLs into a knowledge base with search capabilities, then answers questions by searching the knowledge base (RAG).

**Result:** Successfully loaded MTP documentation into the vector store. Agent searched the knowledge base, found relevant context, and produced a comprehensive answer about MTP's architecture.

---

### custom_tool_for_self_learning.py

**Status:** PASS

**Description:** Agent uses a custom tool to persist insights and new information to a learning database. Three-turn flow: ask a question, approve proposed learning, query saved learnings.

**Result:** Agent proposed a learning, saved it after user approval, then successfully retrieved it via search. All turns completed correctly.

---

### agent_with_guardrails.py

**Status:** PASS

**Description:** Agent implements safety guardrails (e.g., PII Detection, Prompt Injection Guard). Test cases validate normal input, PII detection, and prompt injection blocking.

**Result:** All test cases behaved correctly: Normal prompts processed successfully, PII blocked appropriately, and Prompt Injections successfully halted before execution.

---

### human_in_the_loop.py

**Status:** PASS

**Description:** Agent uses a tool configuration that requires user confirmation before executing. The flow pauses for confirmation, waits for user input, then resumes execution.

**Result:** Agent paused execution when the sensitive tool was called, displayed a confirmation prompt, accepted user input, and executed the tool successfully only after approval.

---

### multi_agent_team.py

**Status:** PASS

**Description:** Team of multiple agents with specialized roles (e.g., Researcher, Summarizer) coordinated by a Lead Agent.

**Result:** Both prompts completed successfully. Specialized agents independently fetched data and produced arguments, while the leader synthesized them into a final output. Parallel delegation worked as expected.

---

### sequential_workflow.py

**Status:** PASS

**Description:** Three-step workflow pipeline where each step builds on the previous output using MTP's sequential processing capabilities.

**Result:** All steps completed in sequence. Data was gathered, interpreted, and formulated into a final report. The data flow between steps remained intact and type-safe.

---

## Summary

| # | File | Status |
| --- | --- | --- |
| 01 | `agent_with_tools.py` | PASS |
| 02 | `agent_with_structured_output.py` | PASS |
| 03 | `agent_with_typed_input_output.py` | PASS |
| 04 | `agent_with_storage.py` | PASS |
| 05 | `agent_with_memory.py` | PASS |
| 06 | `agent_with_state_management.py` | PASS |
| 07 | `agent_search_over_knowledge.py` | PASS |
| 08 | `custom_tool_for_self_learning.py` | PASS |
| 09 | `agent_with_guardrails.py` | PASS |
| 10 | `human_in_the_loop.py` | PASS |
| 11 | `multi_agent_team.py` | PASS |
| 12 | `sequential_workflow.py` | PASS |

**Result: 12/12 PASS**
