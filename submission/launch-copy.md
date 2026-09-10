# Launch copy

Historical 3.0.0 launch copy. The following claims remain historical; current 3.2.0 package and exact-public adoption evidence are in [release notes](release-notes.md).

## One line

NULNUL is a free, open-source harness for Codex and Claude Code that selects task-fit capabilities for the outcome, verifies the work, and removes what does not materially help.

## r/ClaudeAI Showcase

I built NULNUL, a free MIT-licensed plugin for Claude Code and Codex.

It is for projects where the coding agent should inspect the repository, reuse the current setup, complete the requested work, and leave a verified checkpoint instead of making the user design an agent system first.

I used Claude Code in fresh public-install adoption runs to test host ownership. NULNUL 3.0 adds automatic Session continuity, pre-session Capability Packs, authoritative checks, durable Experience and Memory, and evidence-gated evolution while keeping the package skills-only.

Repository and installation: https://github.com/SeoNaRu/nulnul-harness

I am the creator. It is free to use. Feedback about a normal request, expected result, and actual result is more useful than stars; please omit private code and raw transcripts.

## Product Hunt

- Name: NULNUL
- Tagline: An outcome-first, evidence-gated harness for coding agents
- Description: NULNUL gives Codex and Claude Code a task-fit repository-local capability path. It reuses outcome-competitive guidance and tools, adds capability when it materially improves the result, runs the project's real checks, and removes non-contributing setup.
- Link: https://github.com/SeoNaRu/nulnul-harness
- Pricing: Free and open source (MIT)

## GeekNews Show GN

### Title

Show GN: NULNUL - Codex와 Claude Code용 결과 우선·검증형 프로젝트 하네스

### Body

코딩 에이전트를 쓰다 보면 실제 작업보다 에이전트 구성, 반복 설명, 세션 상태 관리가 별도 프로젝트처럼 커지는 문제가 있었습니다. NULNUL은 사용자가 에이전트 팀을 먼저 설계하지 않아도 저장소를 읽고, 결과를 실질적으로 개선하는 작업 맞춤형 기능을 선택하고, 기여하지 않는 설정은 제거하도록 만든 MIT 라이선스 플러그인입니다.

서버나 계정, 텔레메트리 없이 하나의 skills-only 패키지로 동작합니다. 요청한 작업을 계속 수행하고 저장소의 실제 검사를 실행하며, 여러 세션이 필요한 경우에는 검증된 체크포인트만 남깁니다. 외부 게시, 배포, 자격 증명 사용, 전역 설치는 사용자 승인 없이 하지 않습니다.

3.0.0에서는 자동 Session 연속성, 작업 전 Capability Pack, 권위 있는 check receipt, durable Experience와 Memory, 증거 기반 evolution을 추가했습니다. Codex와 Claude Code를 순차적으로 사용할 때의 루트 지침 소유권은 계속 분리하며 동시 변경이나 자동 충돌 병합은 지원한다고 주장하지 않습니다.

3.0.0 패키지는 결정론적 테스트 431개와 Release Gate 제품 점수 100/100을 통과했습니다. 이 수치는 공개된 검사 범위의 결과이며 범용 품질 점수는 아닙니다.

설치와 소스: https://github.com/SeoNaRu/nulnul-harness

사용 중 불편했던 평범한 요청, 기대한 결과, 실제 결과를 알려주시면 가장 도움이 됩니다. 비공개 코드나 원문 대화는 올리지 말아 주세요.

## Show HN

### Title

Show HN: NULNUL – an outcome-first, evidence-gated harness for Codex and Claude Code

### Body

I built NULNUL because configuring coding agents was becoming a second project: repeated repository explanations, growing agent rosters, stale session state, and completion claims without the repository's real checks.

NULNUL is a free MIT-licensed, skills-only plugin. It reads the repository first, reuses outcome-competitive guidance and capabilities, adds capability when it materially improves the result, verifies the requested task, and removes non-contributing setup. It has no server, account, analytics, or telemetry.

Version 3.0.0 adds automatic Session continuity, pre-session Capability Packs, authoritative checks, durable Experience and Memory, and evidence-gated capability, Agent, and bounded Harness evolution. Root instruction ownership remains separate when Codex and Claude Code are used sequentially; concurrent mutation and automatic conflict merging remain out of scope.

The package passes 431 deterministic tests and a 100/100 Release Gate product score. Those numbers cover the shipped fixtures and safety controls; they are not a general quality score.

Source and install instructions: https://github.com/SeoNaRu/nulnul-harness

I would especially value reports containing the normal request, expected result, and actual result. Please do not share private code or raw transcripts.

## 60-second demo

1. Show an existing repository with `AGENTS.md`, two Claude agent profiles, and a runnable test.
2. Install NULNUL from the public GitHub marketplace.
3. Ask: `Fix this bug. Reuse what already works and verify the result.`
4. Show the plugin inventorying the repository instead of generating a new agent team.
5. Show the changed product file, the real test passing, and the concise verified checkpoint.
6. Open the same repository in Claude Code and show that `AGENTS.md` remains byte-identical while Claude owns `CLAUDE.md`.
7. End on the two install commands and the GitHub issue link; do not ask for stars.

## Launch order

1. Publish the 60-second demo with the Korean short post.
2. Post the factual long version to GeekNews Show GN.
3. Post the Claude-specific adoption story to r/ClaudeAI without cross-posting the same copy elsewhere.
4. Post Show HN after replying to early feedback and fixing any reproducible onboarding friction.
5. Submit to curated awesome lists only after their age or community-usage requirements are met.

## Korean short social post

NULNUL 3.0.0을 공개했습니다. Codex와 Claude Code가 저장소를 먼저 읽고, 관련 Memory와 Capability만 제한적으로 불러오며, 실제 검사를 통과한 Experience에서만 배우도록 돕는 무료 오픈소스 플러그인입니다.

여러 세션에는 검증된 상태만 남기고, 두 호스트를 순차적으로 써도 서로의 루트 지침을 덮어쓰지 않습니다.

https://github.com/SeoNaRu/nulnul-harness

## Short social post

I released NULNUL 3.0.0, a free open-source harness for Codex and Claude Code.

It reads the repository first, selects task-fit capabilities for the outcome, runs real checks, removes non-contributing setup, and leaves verified state for the next session.

3.0.0 adds automatic Session continuity, bounded Capability Packs, authoritative checks, durable Experience and Memory, and evidence-gated evolution without adding a service or telemetry.

https://github.com/SeoNaRu/nulnul-harness
