---
name: obsidian-agent-memory
description: Read, update, and verify a local Markdown/Obsidian knowledge base across multiple AI agents (Claude Code, Codex, Kimi Code, DeepSeek Harness) using deterministic fragment retrieval and link checking. Use when resuming cross-session project context, recording decisions or source excerpts, or checking vault link integrity.
---

# Obsidian Agent Memory Workflow

Use this skill when working with a structured local Markdown/Obsidian knowledge base (`Topics/` + `Sources/`). Always treat `rules/Rules.md` and `rules/Harness.md` as the governing ruleset.

## 1. Progressive Read Order (Minimize Context Bloat)

Never read an entire long note upfront unless it is short (< 80 lines). Follow this sequence:

1. **List notes**: `python3 tools/kb.py --kb <vault> notes [--area AREA]`
2. **Inspect structure**: `python3 tools/kb.py --kb <vault> outline "<note>"`
3. **Read targeted section or source**:
   - `python3 tools/kb.py --kb <vault> section "<note>" "<heading>"`
   - `python3 tools/kb.py --kb <vault> src <source_id>`
4. **Read exact line range if needed**: `python3 tools/kb.py --kb <vault> lines "<note>" <start> <end>`
5. **Keyword search**: `python3 tools/kb.py --kb <vault> find "<keyword>" [--sources]`

## 2. Four-Category Content Separation

When updating a topic note, keep these four categories strictly separate:

1. **User explicit expression**: Quote or paraphrase faithfully; keep hesitations, conditions, and negations intact. Silence is not acceptance.
2. **External source evidence**: Store verifiable excerpts in `Sources/` under `## <source_id>` (get the next ID via `kb.py next-id <prefix>`), and link to `#<source_id>` from the topic note.
3. **Confirmed decisions**: Record only decisions the user explicitly approved, along with the reason and date.
4. **AI suggestions (unverified / pending)**: Mark clearly as pending or unaccepted; never promote a suggestion into a decision without explicit confirmation.

Do not duplicate full source code, dependencies, or chat transcripts into the vault; link to repository paths and verified commit SHAs instead.

## 3. Write & Verification Loop

1. **Re-read before writing** to avoid overwriting concurrent edits from another agent.
2. **Merge into existing sections** rather than appending dated sections at the bottom; keep only a brief update log at the end.
3. **Run deterministic check after every write**:
   ```sh
   python3 tools/kb.py --kb <vault> check
   ```
   Confirm `问题 0 条` (exit code `0`) before reporting that the update is saved. If any link or anchor fails, fix it immediately.
