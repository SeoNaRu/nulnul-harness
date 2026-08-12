<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<p align="center">
  <strong>검증된 능력. 개인 에이전트. 통제된 진화.</strong><br>
  Codex와 Claude Code를 위한 연구 주도 메타 하네스입니다. 최신 에이전트 연구를 반증 가능한 로컬 실험으로 바꾸고, 근거와 독립 Gate를 통과한 mechanism만 남깁니다.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.5.0-111111" alt="version 1.5.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="Release Gate: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

## NULNUL이 하는 일

원하는 결과를 설명하면 됩니다. NULNUL은 저장소를 검사하고, 이미 잘 작동하는 것을 재사용하고, 빠진 하네스만 만들고, 실제 작업을 완료·검증한 뒤, 재현 가능한 실패를 Gate가 있는 개선으로 바꿉니다.

논문을 기능 목록으로 옮기는 파이프라인은 아닙니다. 연구에서 질문, 가능한 mechanism, 더 강한 baseline, 잘못된 평가를 찾는 방법을 가져옵니다. 이를 제한된 실험으로 바꾸고, 실패하거나 근거가 부족한 아이디어는 제품에 넣지 않습니다.

## 빠른 시작

Codex:

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code:

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

새 세션에서 에이전트 구조가 아니라 원하는 결과를 말하세요.

```text
금융 YouTube 크리에이터를 찾고 중복을 제거한 뒤,
검토된 결과만 Google Sheets에 안전하게 쓰는 하네스 만들어줘.
```

두 환경 모두 같은 skill을 사용합니다. 호스트를 감지하고, 질문하기 전에 기존 구성을 검사하며, 저장소 소유 경로에만 씁니다. 무인 Claude Code 세션에서 `.claude/**`는 읽기 전용이고, `CLAUDE.md`와 `docs/nulnul/`이 제거 가능한 프로젝트 상태를 담습니다.

### 업데이트

Codex의 현재 plugin CLI에는 별도 plugin-update 명령이 없으므로 Git marketplace를 갱신한 뒤 재설치합니다.

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code는 marketplace와 plugin을 업데이트한 뒤 재시작합니다.

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

로컬 clone에서 marketplace를 추가했다면 먼저 그 clone을 pull하세요. 업데이트 후 새 에이전트 세션을 시작합니다. 프로젝트 지침과 `docs/nulnul/` 상태는 보존됩니다.

## 왜 NULNUL인가

도구가 많다고 좋은 에이전트 시스템은 아닙니다. NULNUL은 더 작은 경로를 택합니다.

- **만들기 전에 재사용합니다.** 로컬 대체물을 만들기 전에 설치된·공식·큐레이션·신뢰할 만한 공개 능력을 검사합니다.
- **저장소 현실을 따릅니다.** 변경 전에 실제 계약, 코드, 상태, 실행 가능한 완료 검사를 읽습니다.
- **검증된 상태만 재개합니다.** `verified` 표기만으로 부족합니다. 제한된 저장소 파일과 여전히 일치하는 runner-owned receipt가 있어야 빠르게 재개합니다.
- **권한 경계를 지킵니다.** 인증, 외부 쓰기, 배포, 공개, 전역 등록은 계속 명시적 승인이 필요합니다.
- **독립적으로 승격합니다.** Coach는 task 또는 meta-level 변경을 제안할 수 있지만 자기 candidate를 승인하지 못합니다.
- **쉽게 제거됩니다.** 안정적인 근거는 저장소에 두고, 실제 job이 없는 서비스·daemon·생성 역할을 피합니다.
- **근거가 infrastructure를 결정합니다.** memory, benchmark, lock, agent, hook, MCP는 측정된 workflow가 필요성을 드러낼 때만 추가합니다.

항상 적용되는 [Baseline Kernel](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md)은 일곱 가지뿐입니다. 저장소 현실, 원래 목표, 실행 가능한 검사 하나, 변경 전 상태, 검사된 capability 결정, 권한 경계, rollback이 있는 독립 Gate 진화입니다.

## 연구 주도 진화

NULNUL은 논문을 feature checklist로 다루지 않습니다. 최신 agent/harness 연구가 던지는 질문을 읽고, NULNUL 안에서 재현 가능한 가설로 바꾸고, 관련 Gate를 통과한 mechanism만 받아들입니다.

```text
Research → Question → Reproduce → Candidate → Independent Gate → Live cycle
                                                                    │
                                                        Keep / Reject / Roll back
```

| 단계 | 연구 질문 | NULNUL 실험 | 근거와 판정 |
| --- | --- | --- | --- |
| 시작 | task agent를 개선하는 절차 자체도 수정 가능하게 만들 수 있는가? | 수정 가능한 task/meta 경계, Coach 제안, 독립 Gate, run 간 상태 축적 | HyperAgents 재현을 주장하지 않는, 통제된 [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md) |
| 1.4 Observable Evolution | 무엇을 왜 바꿨고, 그 변경 때문에 결과가 달라졌는지 관찰할 수 있는가? | 제한된 Experience Digest, 안정적인 stage/owner 분리, prediction과 falsification | 넓은 test count `[1, 1, 2]`가 Navigator `0` 대 Gate `1`을 숨겼습니다. path resolution을 반증하고 final-action ordering을 지지했으며 instruction candidate 두 개를 reject했고, stale-checkpoint 위험을 3/3에서 0/3으로 줄였습니다. |
| 1.5 Generalization Gate | evolution이 단순 search를 이기고 candidate에 영향을 주지 않은 case에서도 살아남는가? | machine-readable exposure state, 사전 등록, one-shot holdout, champion/retry/best-of-3 control | 잘못된 Ruby fixture는 실패 후 validation이 됐습니다. 새 Perl/TAP shape는 stale state 3/3 차단과 검증 후 resume 3/3을 보였고 champion retry/best-of-3는 계속 unsafe했습니다. 판정: **Narrower Scope** |
| 다음 | 지금 바꿀 가치가 있는 병목은 무엇인가? | 구현 전에 새로운 dogfooding 또는 evolution evidence 요구 | **근거 대기 중. 다음 milestone과 Research Watch 항목은 확정되지 않았습니다.** |

위 1.4와 1.5는 연구 evidence milestone 이름입니다. 둘을 포함한 현재 공개 plugin version은 **1.5.0**입니다.

### 논문 → 제품

> **논문을 읽었다고 기능이 되지는 않습니다.** 논문은 질문을 드러내고, mechanism을 제안하고, 더 강한 baseline을 정의하거나 평가 결함을 보여줄 수 있습니다. 로컬에서 재현되고, 필요할 때 독립적으로 승인되고, live cycle까지 통과해야 NULNUL에 들어옵니다. Reject도 지침으로 둔갑시키지 않고 evidence로 남깁니다.

1.4는 observability 연구 질문의 영향을 받았지만 구체적인 발견은 NULNUL의 로컬 결과입니다. completion-count attribution이 실패했고, path 가설은 틀렸으며, 실제로 측정된 결함은 checkpoint freshness였습니다. 1.5 역시 논문의 transfer 주장을 가져다 쓰지 않고 자체 one-shot evidence가 확립한 범위만 보고합니다.

## 연구 계보

### 설계 기반

프로젝트의 출발 맥락은 [GeekNews Weekly 353: “스킬이 넘쳐나는 시대, 나만의 하네스를 구축하라”](https://news.hada.io/weekly/202615)였습니다. 새 이름을 붙이는 대신 다음의 확립된 개념도 사용합니다.

| 기반 | NULNUL이 가져온 것 | 주장하지 않는 것 |
| --- | --- | --- |
| Meta/UBC [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([논문](https://arxiv.org/abs/2603.19461), [코드](https://github.com/facebookresearch/Hyperagents)) | task/meta side가 하나의 수정 가능한 program에 있고 meta side가 자기 improvement procedure도 바꿀 수 있음 | 완전한 재현, open-ended evolution, autonomous self-modification |
| Actor/critic와 generator/verifier 분리 ([Sutton & Barto](http://incompleteideas.net/book/the-book.html)) | Coach가 제안하고 독립 Gate가 검증 | 두 runtime identity가 독립이라는 암호학적 증명 |
| Champion/challenger와 canary release | accepted version을 유지하고 제한된 candidate를 비교하며 live cycle을 관찰하고 실행 가능한 임계로 rollback | 관리형 model registry나 hosted rollout system |
| Eval-gated CI | 행동·안전 근거가 release를 차단 | 공개 fixture 밖의 범용 성능이나 안전 |

### NULNUL에서 검증한 mechanism

| Primary research question | NULNUL에서 구현하고 측정한 것 |
| --- | --- |
| [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850): component·experience·decision observability, prediction → evaluation | 제한된 Experience Digest, owner/stage attribution, 반증 가능한 candidate, reject 보존, checkpoint-freshness 결함 발견. [진화 규칙](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md)과 [activation evidence](evals/benchmarks/activation/results.json)를 확인하세요. |
| [Rethinking the Evaluation of Harness Evolution for Agents](https://arxiv.org/abs/2607.12227): matched feedback/inference budget, test-time search baseline, held-out evaluation, limited generalization | DEV/VALIDATION/HOLDOUT exposure state, retry와 best-of-3 control, one-shot holdout retire, 범위가 좁은 판정. [Generalization Gate](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md), [manifest](evals/generalization/manifest.json), [result](evals/generalization/results.json)를 확인하세요. |

왼쪽은 논문의 연구 질문과 보고된 mechanism이고, 오른쪽은 이 저장소가 실제 구현·측정한 것입니다. 둘을 같은 주장으로 취급하지 않습니다.

### Research Watch — 미구현, 확정 roadmap 아님

| 연구 | 지켜보는 질문 | 상태 |
| --- | --- | --- |
| [Self-Evolving Agent Harnesses via Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683) | sealed credit assignment와 pathology 기반 candidate archive가 overfitting 없이 순차적인 one-off proposal보다 나은가? | Watching — candidate population, quality-diversity archive, autonomous evolution loop를 구현하지 않았습니다. |
| [EvolveNet: Collaborative Harness Evolution for Agent Self-Improvement](https://arxiv.org/abs/2608.04968) | raw workload를 공유하지 않고 scope-typed verified adaptation을 격리된 project 사이에 전이할 수 있는가? | Watching — cross-project adaptation 공유나 aggregation을 구현하지 않았습니다. |

Research Watch는 release 계획이 아닙니다. NULNUL 자체 evidence가 병목을 보여주고, 그 아이디어로 검증할 수 있을 때만 다음 방향을 정합니다.

## 제품 루프

```text
Discover → Verify → Assemble → Run → Checkpoint → Task 또는 improvement process 진화
```

| 단계 | 남는 결과 |
| --- | --- |
| Discover | 필요한 job, 저장소 현실, 기존 candidate |
| Verify | 출처, 호환성, 품질, 권한, 유지보수, license |
| Assemble | 빠진 job을 모두 덮는 가장 작은 capability와 책임 집합 |
| Run | 사용자가 요청한 실제 결과와 정확한 완료 검사 |
| Checkpoint | 현재 검증 상태, 제한된 파일, 다음 행동, blocker, 권한 |
| Evolve | 하나의 causal change, 독립 판정, live observation, rollback |

성숙한 저장소에서는 기존 coherent setup을 재사용하고 하네스 파일을 하나도 쓰지 않는 경로가 일반적입니다. Setup은 task completion이 아닙니다. 원래 작업을 계속 수행하고 저장소 자체 검사로 검증합니다.

### 책임 경계

| 책임 | 일 |
| --- | --- |
| Navigator | 결과, 완료 검사, 권한, checkpoint, resume 소유 |
| Worker | 제한된 job 하나를 완료하고 관찰 가능한 evidence 보고 |
| Coach | 재현 가능한 feedback을 진단하고 task/meta-level 변경 하나 제안 |
| Gate | candidate와 accepted version을 비교한 뒤 promote, reject, rollback |

네 명의 live agent를 반드시 만드는 구조가 아니라 논리적 경계입니다. 단순한 작업은 합칠 수 있지만 promotion 작성자와 Gate는 분리합니다. 제한된 상태는 `docs/nulnul/evolution.json`에 있고, validator는 self-approval, 모순된 기록, 누락된 evidence, 민감한 key, 잘못된 version 전이, 승인 없는 권한 확대를 거부합니다.

## 저장소에 남는 것

```text
your-project/
├── AGENTS.md or CLAUDE.md     # 기존 내용과 병합한 host-loaded guidance
├── docs/nulnul/
│   ├── project.md             # 안정적인 목표, 검사, capability, 권한, rollback
│   ├── checkpoint.json        # 일반 multi-session용 concise state
│   └── evolution.json         # governed evolution history가 필요할 때 checkpoint 대체
├── .agents/skills/<name>/     # 기존 skill이 workflow를 덮지 못할 때만
└── docs/nulnul/workflows/<name>.md
                                # 무인 Claude Code용 재사용 workflow
```

일반 multi-session 작업은 `checkpoint.json`을 사용하고, governed agent history가 필요하면 `evolution.json`으로 대체합니다. state writer를 두 개 만들지 않습니다. legacy state는 `unknown`으로 시작하고 빠른 재개 전에 기록된 명령을 실행해야 합니다. 생성된 `docs/nulnul/`과 local skill을 지우면 product code를 건드리지 않고 제거됩니다. host-owned agent definition은 이 footprint에 들어가지 않습니다.

## 사용 사례

새 세션에서 한 문장이면 됩니다.

```text
채용 공고를 지켜보다가 중복을 빼고 검토 큐 하나로 모으는 하네스 만들어줘.
경쟁사 가격을 매주 snapshot하고 변경만 보고하는 하네스 만들어줘.
새 논문과 release note를 모아 weekly digest 하나로 만드는 하네스 만들어줘.
raw log를 memory로 저장하지 않고 반복 CI failure를 묶는 하네스 만들어줘.
```

반복 데이터 workflow는 실제 job이 있을 때 stable identity, deduplication, exclusion precedence, `unknown` verification, cursor persistence, idempotent write, 단일 state writer를 상속합니다.

## 실전에서 굳힌 규칙

관찰된 실패 대부분은 model reasoning이 아니라 operational invariant였습니다. 하루 동안 실행한 무인 creator workflow에서 concurrent writer가 결정 12,000개를 잃었고, empty-cycle cursor 버그는 같은 120개를 반복 검사하다가 수정 후 한 번에 새 기록 1,265개를 찾았습니다. 건너뛴 검사가 `ok`가 됐고, `MX` 대신 `A`를 본 검사가 정상 mailbox 15개를 막았으며, 넓은 text filter는 유효 record 20개를 버렸고, 세 가지 “completed” 정의가 delivery 전 작업을 멈췄습니다. 한 workflow를 하루 관찰한 field evidence이지 범용 benchmark가 아닙니다.

| 규칙 | 막는 실패 |
| --- | --- |
| state file 하나당 writer 하나: exclusive lock, 멈춘 process group, parallel collector당 shard 하나 | concurrent loop가 memory에서 전체 state를 다시 써서 update를 잃는 문제. atomic rename은 torn file만 막습니다. |
| `verified`, `failed` 옆에 별도 `unknown` state | skip·timeout 검사를 pass로 기록하거나 영구 failure로 굳히는 문제 |
| cycle이 아무것도 찾지 못해도 cursor 기록 | 다음 범위가 멈춰 과거 작업을 영원히 다시 읽는 문제 |
| promotion 후 한 번의 live cycle과 실행 가능한 rollback threshold | frozen sample이 드러내지 못하는 runtime-only regression |
| goal metric을 정의하는 함수 하나, 모든 counter가 이를 import | proxy metric이 미완료 작업을 complete로 선언할 때까지 정의가 갈라지는 문제 |
| 모든 validity check를 negative control로 증명 | 없는 target과 실제 target에 같은 답을 하는 검사 |
| stage마다 start와 end 직접 기록 | 기록되지 않은 시간이 이웃 stage에 붙어 잘못된 병목을 지목하는 문제 |
| reject·rollback proposal과 이유를 검색 가능하게 보존 | Coach가 이미 reject된 candidate를 다시 제안하는 문제 |
| Gate decision과 false-positive evidence 보존 | 반복되는 오탐이 Gate 무시를 학습시키는 문제 |
| source와 durable guidance가 함께 진화할 때 문서 부채 검사 | code-only fix가 다음 session의 운영 규칙에서 사라지는 문제 |
| benchmark, lock, role, hook을 검사한 job에서 선택 | 단순한 project의 speculative scaffolding 또는 실제 job에 필요한 mechanism 누락 |

## 주장보다 근거

### 행동

| 검사 | 현재 결과 |
| --- | --- |
| 저장소 테스트 | **94개 통과** |
| Release Gate | 12개 weighted behavior/safety case에서 **100/100**; isolated scenario는 positive 9개, negative 3개 |
| release-blocking regression | setup, bounded workflow, activation, fast-resume cost/read scope, Claude adoption, learning loop, observable evolution, scoped generalization evidence를 검증 |
| activation과 fast resume | positive/negative project shape 10개, 기본 3회 실행; accepted candidate는 counterbalanced 4/4에서 bounded, 비교 가능한 pair 3개에서 input −18.4% |
| 공개 Claude adoption | GitHub marketplace 설치 **1.5.0**, `.claude/**` write call 0, agent hash 변화 0, verified checkpoint, machine-recorded check 5개 |

### 진화

| 검사 | 현재 결과 |
| --- | --- |
| Experience observability | 제한된 digest 3개가 Navigator completion check `0`과 Gate `1`을 분리했습니다. prompt, response, transcript, command list, machine path는 저장하지 않았습니다. |
| Causal candidate | path resolution 반증, final-action ordering 지지, 그럴듯한 문구만으로 Navigator instruction candidate 두 개를 승격하지 않고 reject |
| Checkpoint freshness | runner-owned bounded receipt 전에는 unverified mutated repository state가 **3/3** fast-resumable, 이후 **0/3**. Gate 후 task behavior/read scope/verified resume는 **3/3** 통과 |
| release adoption 학습 | sanitized v1.5.0 nonpass 세 건을 보존했고, Navigator v16은 reject, v17은 branch-first installed-roster inventory의 fresh run 통과 후 accept |

### 일반화

| 검사 | 현재 결과 |
| --- | --- |
| Exposure accounting | 기존 Release, activation, setup, workflow, meta-evolution, Claude adoption, deterministic fixture 전체를 이미 노출된 DEV 또는 VALIDATION evidence로 기록 |
| 첫 holdout 실패 | 잘못된 Ruby fixture는 completion check에 실패했고, 보존 후 validation이 됐으며, 이 실패로 mandatory fixture preflight 추가 |
| 새 transfer estimate | 당시 unseen이던 Perl/TAP case가 stale resume **3/3** 차단, verified resume **3/3** 복구. 한 번 사용한 뒤 현재 retire됨 |
| Search baseline | single champion, champion retry 3회, best-of-3가 모두 unsafe. deterministic arm은 trial당 같은 subprocess 6회를 사용했으며 inference-budget 승리는 주장하지 않음 |
| 판정 | **Narrower Scope. Checkpoint freshness는 unseen local Perl/TAP CLI shape 하나로 전이됐습니다. Harness-wide generalization은 확립되지 않았습니다.** |

Release Gate는 범용 benchmark가 아닙니다. Generalization Gate는 personal/core mechanism promotion, transfer claim, public generalization claim에만 붙는 별도 adjunct입니다. 일반 project-local change에는 holdout 비용을 부과하지 않습니다. development에서 본 case는 HOLDOUT으로 이름을 바꿀 수 없고, 이미 쓴 holdout은 두 번째 unseen claim의 근거가 될 수 없습니다.

공개 검사를 재현할 수 있습니다.

```bash
python3 scripts/release_gate.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

원본 evidence도 공개돼 있습니다. [behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance comparisons](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [exposure manifest](evals/generalization/manifest.json), [failed Ruby result](evals/generalization/results-ruby-failed.json), [Perl/TAP result](evals/generalization/results.json)을 확인할 수 있습니다. 자세한 version archaeology는 [`CHANGELOG.md`](CHANGELOG.md)에 남아 있습니다.

## 대표 워크플로: YouTube → Google Sheets

공개 예시는 실제 identity나 contact data를 복사하지 않고 creator research를 모델링합니다. discovery, classification, channel-ID deduplication, exclusion precedence, reviewer feedback, spreadsheet formula escaping, safe upsert, run metric을 다룹니다.

- synthetic example: [`examples/youtube-sheets`](examples/youtube-sheets)
- offline scorer와 A/B evidence: [`evals/benchmarks/youtube-sheets`](evals/benchmarks/youtube-sheets)

명시적 승인 없이 Google 인증이나 Sheet write를 수행하지 않습니다. 이 performance evidence는 task-specific preliminary result이며 범용 claim이 아닙니다.

## 신뢰 모델

- **Installed ≠ verified.** 사용 가능하다는 사실은 discovery evidence이지 proof가 아닙니다.
- **Popularity ≠ fitness.** 인기도는 provenance, permission, maintenance, license, task fit 실패를 덮지 못합니다.
- **Least privilege.** 인증, 외부 쓰기, 배포, 공개, 전역 등록은 approval boundary로 남습니다.
- **No secret persistence.** credential, raw conversation, transcript, private project data를 evolution memory로 만들지 않습니다.
- **Independent promotion.** agent는 자기 upgrade를 승인하지 못합니다.
- **Evaluation exposure is state.** development case를 unseen으로 다시 부를 수 없고, 사용한 holdout은 retire합니다.
- **Verified resume.** checkpoint를 사용하기 전에 제한된 repository reality와 다시 비교합니다.
- **Host-owned configuration stays host-owned.** 무인 session은 `.claude/**`를 검사하지만 다시 쓰지 않습니다.
- **Removable setup.** 생성된 state는 product code를 손상하지 않고 제거할 수 있습니다.

## 배포 범위

```text
plugins/nulnul-harness/                 # 유일한 배포 product boundary
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # 실행 contract
    ├── agents/openai.yaml              # Codex UI metadata
    ├── references/                     # discovery, assembly, safety, evolution
    ├── assets/                         # 제거 가능한 project template
    └── scripts/                        # validator, check runner, rollback, doc debt
```

plugin은 계속 skills-only입니다. MCP server, hook, app, authentication, remote telemetry, hosted service, dashboard, daemon, background process가 없습니다. local evidence는 sanitized aggregate만 보존합니다. evolution은 일반적인 user-triggered work 중에 일어나며 unsupervised process가 아닙니다. Gate independence는 선언된 state를 검증하며 runtime identity를 암호학적으로 증명하지 않습니다.

## 자주 묻는 질문

<details>
<summary>NULNUL은 계속 혼자 학습하나요?</summary>

아닙니다. 일반 작업 중 재현 가능한 failure를 bounded candidate 하나로 바꿉니다. promotion에는 evidence와 independent Gate가 필요하고, 이후 live cycle이 executable rollback을 작동시킬 수 있습니다. autonomous population이나 daemon은 없습니다.
</details>

<details>
<summary>Release Gate는 범용 성능 benchmark인가요?</summary>

아닙니다. 공개된 behavior, safety, task-specific cost evidence를 Gate합니다. Generalization Gate가 transfer claim을 별도로 제한하며, 현재 harness-wide claim은 명시적으로 확립되지 않았습니다.
</details>

<details>
<summary>왜 agent가 적고 MCP server도 없나요?</summary>

role과 infrastructure도 비용입니다. 구체적인 independent job, 아직 덮이지 않은 tool boundary, coordination 필요, verification boundary가 있을 때만 추가합니다. 현재 product는 skills-only plugin 이상의 구성 요소가 필요하지 않습니다.
</details>

<details>
<summary>왜 agent가 자기 improvement를 accept하지 못하나요?</summary>

candidate를 만드는 일과 검사하는 일은 다릅니다. validator는 author나 target의 self-approval을 거부하고, promotion에는 reproduced evidence와 live-cycle rollback threshold가 필요합니다.
</details>

## 제거

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

```bash
claude plugin uninstall nulnul-harness@nulnul-harness
claude plugin marketplace remove nulnul-harness
```

생성된 project state는 별도입니다. checkpoint나 evolution history가 더 필요하지 않을 때만 제거하세요.

## 개발

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

[`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), [MIT 라이선스](LICENSE)를 확인하세요.

MIT © [SeoNaRu](https://github.com/SeoNaRu)
