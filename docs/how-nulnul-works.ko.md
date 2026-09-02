# NULNUL은 어떻게 동작하는가

이 문서는 NULNUL을 처음 설치하는 사용자부터 capability와 harness의 진화
경계를 검토하는 기여자까지 같은 제품을 단계적으로 설명한다. 이 문서는 NULNUL
3.0.0의 실제 제품 계약을 설명하며, 공개 버전 표시는 저장소
README와 plugin manifest를 따른다.

NULNUL의 기준은 다음 한 문장이다.

> 이 프로젝트에서 가장 강하게 검증할 수 있는 결과 경로를 선택하고, 그 결과에
> 실질적으로 기여하지 않는 구성만 제거한다.

## Part 1 — 설치에서 `SKILL.md`까지

Codex에서는 다음처럼 설치한다.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code에서는 다음처럼 설치한다.

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

배포 단위는 [Codex manifest](../plugins/nulnul-harness/.codex-plugin/plugin.json)와
[Claude manifest](../plugins/nulnul-harness/.claude-plugin/plugin.json)가 가리키는
skills-only plugin이다. MCP 서버, hook, 앱, daemon은 포함하지 않는다.

핵심 실행 계약은
[SKILL.md](../plugins/nulnul-harness/skills/nulnul-harness/SKILL.md)다. 사용자는
Agent 수나 Skill 구성을 설계하지 않고 원하는 결과를 말한다. NULNUL은 저장소에
명시적인 입력·출력·제약·완료 검사가 이미 있으면 그 계약을 우선하고, 하네스
설정이나 capability 선택이 실제로 필요한 경우에만 활성화된다.

## Part 2 — 사용자 요청이 workflow로 연결되는 과정

예를 들어 사용자가 다음처럼 말할 수 있다.

```text
회원가입을 만들어줘. 기존 로그인은 깨지지 않게 해줘.
```

NULNUL은 내부 topology를 사용자에게 되묻지 않고 다음 순서로 처리한다.

```text
요청한 결과와 중요한 품질 차원 확인
→ 저장소 지침·코드·검사·권한 확인
→ 현재 capability와 검증된 상태 확인
→ 가장 강하게 정당화할 수 있는 실행·검증 경로 선택
→ 제품 작업 완료
→ 정확한 저장소 검사 실행
→ 필요할 때만 검증된 다음 상태 기록
```

이 순서의 공통 불변조건은
[baseline-kernel.md](../plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md)에
있다. 질문 규칙은
[discovery-and-questions.md](../plugins/nulnul-harness/skills/nulnul-harness/references/discovery-and-questions.md),
호스트별 파일 소유권과 생성 조건은
[project-files.md](../plugins/nulnul-harness/skills/nulnul-harness/references/project-files.md)에
있다.

Codex는 프로젝트 루트의 `AGENTS.md`만, Claude Code는 `CLAUDE.md`만 관리한다.
두 호스트는 `docs/nulnul/` 아래의 같은 durable contract와 정확히 하나의 live-state
writer를 순차적으로 공유한다. 배포·게시·인증·전역 설치·외부 쓰기·권한 확대에는
기존 승인 경계가 그대로 적용된다.

## Part 3 — Capability Discovery와 Agent Assembly

### Capability Discovery

[capability-discovery.md](../plugins/nulnul-harness/skills/nulnul-harness/references/capability-discovery.md)는
먼저 설치된 Skill, Plugin, Agent, native tool을 실제로 확인하게 한다. 설치돼 있다는
사실은 후보를 발견했다는 뜻일 뿐, 자동 선택 근거가 아니다.

판단 단위는 “유명한가?”가 아니라 다음 질문이다.

```text
이 capability가 현재 저장소의 작업·관례·실패·검사·권한 안에서
강하고 project-fit한 결과를 만드는가?
```

현재 capability가 outcome-competitive하면 재사용한다. 구체적인 기능 공백, 중요한
품질 차이, 반복 실패, 검증 약점, stale evidence가 있을 때만
[capability-registry.md](../plugins/nulnul-harness/skills/nulnul-harness/references/capability-registry.md)의
순서로 외부 후보를 제한적으로 찾는다. 외부 후보도 provenance, compatibility,
maintenance, permission, license, project check를 통과해야 한다. 최신이거나 인기
있다는 이유만으로 검색·추천·설치하지 않는다.

### Agent Assembly

[agent-assembly.md](../plugins/nulnul-harness/skills/nulnul-harness/references/agent-assembly.md)는
Agent 수에 목표를 두지 않는다. 직접 실행이 결과 경쟁력이 있으면 0개나 1개일 수
있다. 전문성, 독립 검증, context isolation, 실제 병렬 작업이 결과를 실질적으로
개선하면 더 많은 bounded role을 사용할 수 있다.

모든 역할에는 distinct job, activation condition, bounded input와 capability,
completion check, handoff, merge/removal condition이 필요하다. 기존 역할은 제자리에서
`KEEP`, `UPGRADE`, `MERGE`, `RETIRE`하고 같은 역할을 옆에 다시 만들지 않는다.

## Part 4 — Checkpoint와 Continuity

여러 세션이 필요한 프로젝트는 대화 원문 대신 검증된 프로젝트 상태로 이어간다.
초기 모양은
[checkpoint.template.json](../plugins/nulnul-harness/skills/nulnul-harness/assets/checkpoint.template.json)에
있다.

관련 실행 파일은 다음과 같다.

- [validate_checkpoint.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_checkpoint.py): checkpoint schema와 상태를 검사한다.
- [run_checkpoint_check.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/run_checkpoint_check.py): checkpoint에 기록된 정확한 완료 명령을 실행하고 verification receipt를 쓴다.
- [migrate_legacy_checkpoint.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/migrate_legacy_checkpoint.py): 이전 durable contract를 한 live-state writer로 안전하게 옮긴다.
- [sync_host_entry.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/sync_host_entry.py): 활성 호스트의 루트 entry만 동기화한다.

`verified` checkpoint이며 task, named files, permission이 그대로일 때만 bounded fast
resume을 허용한다. 파일·작업·권한이 달라졌거나 receipt가 invalid, failed, unknown이면
fail closed하고 full workflow로 돌아간다. Ordinary resume은 closed evolution history를
전부 읽지 않는다.

## Part 5 — Skill과 Agent의 Evolution

[evolution.md](../plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md)는
Skill과 Agent를 static file이 아니라 비교 가능한 project-local hypothesis로 다룬다.
반복 실패나 사용자 교정이 생겼다고 바로 영구 지침을 늘리지는 않는다.

```text
경험
→ bounded feedback와 재현
→ 현재 capability가 놓친 이유
→ 한 개의 후보
→ champion과 같은 검사로 비교
→ 독립 Gate
→ provisional live confirmation 또는 rollback
```

Skill의 새 버전은 외부 대체재가 없어도 만들 수 있다. 단, “문서가 길어졌다”가
아니라 재현된 project failure가 줄고 regression이 없어야 한다. Agent도 같은
방식으로 전문화, 병합, Skill로 대체, 또는 retire될 수 있다. 독립 Gate와 rollback은
기존 evolution contract를 재사용하며 새 Gate나 lifecycle engine을 만들지 않는다.

활성 상태의 기본 모양은
[evolution-state.template.json](../plugins/nulnul-harness/skills/nulnul-harness/assets/evolution-state.template.json),
검증과 compact archive는
[validate_evolution_state.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/validate_evolution_state.py)와
[compact_evolution_state.py](../plugins/nulnul-harness/skills/nulnul-harness/scripts/compact_evolution_state.py)에
있다.

## Part 6 — KEEP / UPGRADE / REPLACE / MERGE / RETIRE / CREATE

이 여섯 단어는 새 state enum이 아니라 기존 discovery·assembly·evolution 계약에서
사용하는 판단 언어다.

| 판단 | 적용 조건 |
| --- | --- |
| `KEEP` | 현재 capability가 여전히 strong하고 project-fit하다. |
| `UPGRADE` | 재현된 project evidence가 같은 capability의 bounded 새 버전을 정당화한다. |
| `REPLACE` | 후보가 materially better하고 기존 unique value를 승계했거나 불필요함을 검증했다. |
| `MERGE` | overlap을 합친 survivor가 outcome을 유지·개선하고 routing, context 또는 ownership도 낫게 한다. |
| `RETIRE` | 대체재에 패배했거나 job이 사라졌고, duplicate·unsafe·unmaintained이거나 removal check에서 영향이 없다. |
| `CREATE` | 반복 가능한 실제 job이 남아 있고 현재·외부 후보 모두 outcome-competitive하지 않다. |

외부 후보가 이기면 약한 기존 capability를 active context에 영구 누적하지 않는다.
반대로 유명한 외부 후보가 project-specific check에서 지면 현재 local survivor를
유지한다. 0 additions는 현재 set이 이미 strongest justified path일 때의 결과이지
독립 목표가 아니다.

## Part 7 — Harness routing 자체의 Evolution

Capability가 충분히 좋은데 선택·활성화·조합·권한·handoff가 잘못되어 반복 실패할
수 있다. 이 경우 좋은 Skill을 불필요하게 다시 쓰지 않고 routing procedure 하나를
후보로 만든다. 반대로 Skill 자체가 project job을 놓쳤다면 routing 변경으로 결함을
숨기지 않는다.

[meta-evolution.md](../plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md)는
이 두 층을 구분한다.

```text
Layer 1: project capabilities가 진화
Layer 2: NULNUL이 capability를 선택하고 조합하는 방법이 진화
```

두 층 모두 동일한 evidence 경계를 따른다. 한 번에 재현된 feedback family 하나,
bounded candidate 하나, 공정한 champion comparison, 독립 Gate, live confirmation과
rollback이 필요하다. Personal 및 cross-project 전이는 별도 opt-in·privacy·compatibility
경계를 통과해야 하며 일반 project-local 변화와 섞지 않는다.

## Part 8 — NULNUL 3.0 Foundation과 Generalization

3.0의 일반 작업 경로는 다음처럼 구성된다.

```text
Task → Session/Context → Pre-Session Capability Pack → Work
     → Authoritative Check → Experience → Memory
```

Clear Direct 작업은 capability body와 evolution review를 받지 않는다. Material-fit
작업만 exact current capability body를 작업 시작 전에 받으며, 완료 뒤 deterministic
check receipt가 Experience의 검증 근거가 된다.

Natural Selection은 verified Experience가 실제 lifecycle need를 만들었을 때만
KEEP·UPGRADE·REPLACE·MERGE·RETIRE·CREATE를 평가한다. 외부 후보는 quarantine과
project check 경쟁을 통과하기 전까지 active capability가 아니다. Agent Evolution은
capability 자체가 아니라 실행 책임 topology를 관리하고, Harness Evolution은
provenance·authority·rollback 같은 guarded Kernel 밖의 bounded control만 다룬다.

Cross-project Generalization은 프로젝트 Memory를 합치지 않는다. Privacy-safe abstract
candidate만 독립 프로젝트 또는 target validation 뒤 bounded prior가 될 수 있고,
target-project truth를 덮어쓰지 않는다.

## 사용자가 보는 결과

기본 출력은 내부 구조가 아니라 다음 세 줄이다.

```text
RESULT
VERIFY
RESUME
```

더 알고 싶을 때만 `USED`, `UPGRADED`, `REPLACED`, `MERGED`, `RETIRED`, `CREATED`,
`SKIPPED`, `WHY`, `EVIDENCE`, `EVOLUTION`, `ROLLBACK`을 펼친다. 모든 항목은 실제
파일·검사·bounded decision evidence와 연결돼야 하며 raw chain-of-thought, private
transcript, secret은 노출하지 않는다.

## 현재 증거의 한계

[Product North Star](product-north-star.md)와
[outcome-first eval](../evals/outcome-first/cases.json)은 위 결정 계약의 구조를
결정론적으로 검사한다. 이것만으로 실제 coding agent가 더 좋은 결과를 낸다고
주장하지 않는다. Post-2.2.1 실제 작업 benchmark에서는 Vanilla, exact v2.2.1,
당시 Project-Fit 후보가 모두 25개 중 21개 strict pass로 동률이었던 결과는 역사적
proof 경계로 남아 있다. 이후 3.0 Foundation은 별도의 live Pack→Check→Experience→
Memory→Evolution proof와 결정론적 lifecycle 회귀 검사를 통과했다. 이것은 기록한
제품 경계의 근거이며 보편적 coding 품질, live Harness 자기개선, multi-Agent 우위,
또는 전 세계 capability 최적성을 뜻하지 않는다.
