# CHANGELOG: Antigravity AI (Netherlands)

All notable changes to this project will be documented in this file.

## [2026-04-13] - Big Cleanup & Automation Restoration

### Major Reorganization
- **Project Structure:** Moved all root scripts to `/scripts/automation` and `/scripts/wordpress`.
- **Logs:** Centralized all logs into the `/logs` directory.

### Bug Fixes
- **Telegram Bot (@my_ai_ark_agent_bot):** Fixed `MemoryManager` AttributeError and console `UnicodeEncodeError`. Bot is now online.
- **Dr. Priya Voiceover:** Implemented `clean_script_for_tts` to filter emojis and non-spoken metadata from script generation.
- **Pillow Error:** Installed missing `Pillow` (PIL) library.

### New Skills
- **Multimodal Analysis:** Added `/multimodal` for product photo analysis.
- **RAG Testing:** Added `/test-ai` for retrieval accuracy and source attribution.

## [2026-04-01] - Stability & Pipeline Fixes

### Bug Fixes - 2026-04-01

- **FFmpeg Error 183:** Resolved a persistent file conflict error in `src/skills/video_skill.py` by adding explicit file flushes, OS syncs, and pre-emptive deletion of intermediate files.
- **Port 8080 Conflict:** Identified redundant bot processes as the cause of "Address already in use" errors and provided cleanup procedures.
- **Concurrent Rendering:** Improved session isolation during video generation to allow for thread-safe production by passing fragments as direct objects rather than using a global file.

## [2026-03-29] - Phase 9: Canva Integration

### New Features - 2026-03-29

- **Canva Agent:** Full integration with Canva REST API using OAuth 2.0 PKCE.
- **Canva Commands:** Added `/canva auth`, `/canva instagram`, `/canva reels`, and `/canva export` to the Telegram bot.
- **Automated Video Delivery:** Canva MP4 exports are now automatically sent to users via Telegram.
- **SSL Implementation:** Configured `arkmediaflow.com` for secure OAuth callbacks.

## [2026-03-24] - Phase 7 & 8: Intelligence & Memory

### New Features - 2026-03-24

- **Intelligent Funnel Logic:** Implemented dynamic prompt injection based on lead stage (Awareness, Interest, Consideration, Intent).
- **SQLite Memory Manager:** Replaced JSON storage with a thread-safe SQLite backend for cross-agent memory persistence.
- **User Profiling:** Automated tracking of user interactions to build persona-aware marketing strategies.

## [2026-03-20] - Phase 5 & 6: Multi-Agent Expansion

### New Features - 2026-03-20

- **Specialized Agents:** Launched Sales, Research, Email, and LinkedIn agents within the `src/` modular architecture.
- **Orchestrator V2:** Improved routing logic between agents with automatic fallback to legacy systems.

## [2026-03-15] - Phase 1-4: Foundation

### New Features - 2026-03-15

- **Core Architecture:** Set up the `src/` directory with `BaseAgent`, `Settings`, and `Logging`.
- **AI Connectivity:** Established high-speed connections to OpenAI (GPT-4o-mini) and Anthropic (Claude).
- **Telegram Bridge:** Connected the AI orchestrator to the Telegram bot UI.
