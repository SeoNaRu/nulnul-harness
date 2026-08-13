# Launch copy

## One line

NULNUL is a free, open-source harness for Codex and Claude Code that reuses what already works in a repository, adds only what is missing, and keeps changes behind executable checks.

## r/ClaudeAI Showcase

I built NULNUL, a free MIT-licensed plugin for Claude Code and Codex.

It is for projects where the coding agent should inspect the repository, reuse the current setup, complete the requested work, and leave a verified checkpoint instead of making the user design an agent system first.

I used Claude Code in fresh public-install adoption runs to test the Claude side of the plugin. The 2.0.1 run preserved the existing Codex-owned `AGENTS.md` and two existing Claude agent profiles, created only the Claude-owned `CLAUDE.md` plus one shared repository state, and passed five executable checks.

Repository and installation: https://github.com/SeoNaRu/nulnul-harness

I am the creator. It is free to use. Feedback about a normal request, expected result, and actual result is more useful than stars; please omit private code and raw transcripts.

## Product Hunt

- Name: NULNUL
- Tagline: A minimal, evidence-gated harness for coding agents
- Description: NULNUL gives Codex and Claude Code the smallest repository-local setup needed for the current task. It reuses existing guidance and tools, runs the project's real checks, preserves one verified state across sessions, and keeps only improvements that pass an independent Gate.
- Link: https://github.com/SeoNaRu/nulnul-harness
- Pricing: Free and open source (MIT)

## Short social post

I released NULNUL 2.0.1, a free open-source harness for Codex and Claude Code.

It reads the repository first, reuses what already works, adds only what is missing, runs real checks, and leaves verified state for the next session.

2.0.1 also lets Codex and Claude Code share one project without overwriting each other's root instructions when used sequentially.

https://github.com/SeoNaRu/nulnul-harness
