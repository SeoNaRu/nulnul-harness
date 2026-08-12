<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<p align="center">
  <strong>원하는 결과만 말하세요. NULNUL은 프로젝트에 필요한 하네스만 구성하고, 실제 작업을 끝까지 검증합니다.</strong><br>
  AI 조직도부터 설계하지 않고 Codex와 Claude Code를 믿을 수 있게 쓰고 싶은 개발자를 위한 도구입니다.<br>
  <em>검증된 능력. 개인 에이전트. 통제된 진화.</em>
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

## NULNUL은 무엇인가요?

NULNUL은 Codex와 Claude Code를 위한 skills-only plugin입니다. 사용자가 원하는 결과를 말하면 저장소를 읽고, 이미 적합한 skill·plugin·agent·프로젝트 규칙을 재사용하고, 빠진 부분만 채운 뒤 원래 작업을 계속 수행하고 실제 저장소 검사를 실행합니다.

여러 session에 걸친 작업이라면 다음 session이 chat을 처음부터 복원하지 않도록 짧고 검증된 checkpoint를 남깁니다. 재현 가능한 failure가 생기면 하나의 제한된 개선 proposal로 바꾸고, independent Gate가 accept·reject·rollback하게 할 수 있습니다.

때로는 **새 agent 0개, 새 skill 0개, 새 infrastructure 0개**가 정답입니다.

## 왜 쓰나요?

Coding agent 주변의 일이 자꾸 사용자의 일이 될 때 NULNUL이 필요합니다.

- **session마다 같은 프로젝트 설명을 반복합니다.** NULNUL은 현재 파일과 검증 결과가 아직 일치하는 제한된 repository state에서 이어갑니다.
- **저장소마다 agent 규칙과 tool이 계속 쌓입니다.** 이미 있는 구성을 먼저 조사하고 아직 덮이지 않은 job만 추가합니다.
- **agent는 “완료”라고 하지만 실제 검사를 안 돌렸습니다.** 완료는 자신감 있는 문장이 아니라 실행 가능한 저장소 command입니다.
- **어떤 agent·skill·plugin과 context 구조를 써야 하는지 직접 정해야 합니다.** NULNUL은 결과에서 출발해 repository evidence로 선택합니다.
- **그럴듯한 fix가 실패했는데 나중에 다시 등장합니다.** accept·reject·rollback된 candidate와 이유를 보존해 같은 project 안에서 약한 방향을 반복하지 않습니다.

## 잘 맞는 경우와 필요 없는 경우

**잘 맞습니다:**

- 여러 session에 걸쳐 진행하는 개발;
- state, deduplication, permission, review queue가 있는 반복 workflow;
- 여러 skill·plugin·tool·agent role 후보가 있는 저장소;
- test, validator, delivery check, rollback이 중요한 작업;
- 실제 job보다 agent 설정이 더 빠르게 커지는 프로젝트;
- 재현 가능한 failure에서 project 범위의 개선을 만들고 싶은 경우.

**아마 필요 없습니다:**

- 읽기 전용 질문이나 아주 작은 일회성 수정;
- 입력·출력·제약·실행 가능한 completion check가 이미 명확한 작업;
- background workflow engine, hosted control plane, always-on daemon이 필요한 경우;
- AI가 승인 없이 인증·공개·배포·외부 쓰기를 해야 하는 경우;
- 기반 model의 reasoning 한계를 해결하려는 경우;
- 서로 무관한 project 사이의 personal memory나 자동 학습—현재 capability가 아닙니다.

기존 project contract가 이미 작업을 충분히 덮는다면 그 작업에는 NULNUL을 쓰지 않아도 됩니다.

## 빠른 시작

Codex에 설치합니다.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

또는 Claude Code에 설치합니다.

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

새 session에서 agent 구조가 아니라 원하는 결과를 말합니다.

```text
이 저장소에 하네스를 구성하고 예약 API를 수정한 뒤,
기존 동작이 계속 통과하는지 확인해줘.
```

반복 workflow에서 시작해도 됩니다.

```text
금융 YouTube creator를 찾고 중복을 제거한 뒤,
검토된 결과만 Google Sheets로 안전하게 보내는 workflow를 만들어줘.
```

같은 skill이 두 host를 지원합니다. 현재 surface를 감지하고, 질문하기 전에 기존 설정을 조사하며, 명시적 approval boundary를 유지합니다. 무인 Claude Code 작업에서 `.claude/**`는 read-only이고, 제거 가능한 project state는 저장소 소유 지침과 `docs/nulnul/`에 둡니다.

## 실제로 하는 일

공개된 [YouTube → Google Sheets 예시](examples/youtube-sheets)는 agent diagram이 아니라 일반적인 요청에서 시작합니다. NULNUL은 다음을 맡습니다.

1. 저장소와 설치된 capability를 조사합니다.
2. 적합한 discovery와 spreadsheet 동작을 재사용합니다.
3. 빠진 classification, deduplication, review flow만 추가합니다.
4. Google 인증과 Sheet write는 명시적 승인 뒤에 둡니다.
5. offline completion check를 실행합니다.
6. 작업이 지속된다면 다음 session을 위한 verified state를 남깁니다.

fixture는 synthetic이며 실제 identity나 contact data를 저장하지 않습니다. [Offline benchmark](evals/benchmarks/youtube-sheets)는 classification, channel-ID deduplication, exclusion precedence, reviewer feedback, formula escaping, safe upsert, run metric을 확인합니다. 하나의 task 예시이지 범용 성능 주장이 아닙니다.

## 동작 방식

```text
Inspect → Reuse → Fill the gaps → Do the work → Verify → Resume / Improve
```

NULNUL에는 여섯 가지 취향이 있습니다.

- **Reuse before creation.** local substitute를 만들기 전에 설치된 것, official, curated, reputable capability를 찾습니다.
- **Smallest useful system.** direct 또는 single-agent 실행이 기본이며, 새 role에는 실제 independent job이 필요합니다.
- **Repository truth over chat memory.** 이전 session의 설명보다 contract, file, state, executable check를 믿습니다.
- **Verification over confidence.** agent의 완료 선언보다 통과한 command와 제한된 evidence를 믿습니다.
- **Evidence before infrastructure.** memory, benchmark, lock, agent, hook, MCP, service는 측정된 job이 있을 때만 추가합니다.
- **Improvement without self-approval.** Coach는 변경을 제안할 수 있지만 author와 target은 independent Gate가 될 수 없습니다.

항상 적용되는 [Baseline Kernel](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md)은 의도적으로 작습니다. repository truth, 원래 outcome, 실행 가능한 check 하나, before state, 조사된 capability 결정, permission boundary, rollback을 가진 gated improvement가 전부입니다.

Navigator, Worker, Coach, Gate는 네 명의 필수 agent가 아니라 responsibility boundary입니다. 단순 작업은 role을 합칩니다. 독립 검증 자체가 실제 job일 때만 분리를 강제합니다.

### 다른 하네스와 무엇이 다른가요?

- **Agent-team generator가 아닙니다.** role을 추가하지 않는 것이 더 좋은 결과일 수 있습니다.
- **Prompt bundle이 아닙니다.** repository state와 executable check를 사용합니다.
- **Memory product가 아닙니다.** raw conversation이나 private workload를 저장하지 않습니다.
- **Hosted orchestration platform이 아닙니다.** server, daemon, hook, app, MCP service가 필요 없습니다.
- **Autonomous deployment system이 아닙니다.** credential, 외부 쓰기, 공개, 배포, 전역 등록은 approval boundary로 남습니다.

## 저장소에 남는 것

아무것도 남지 않을 수 있습니다. 완전한 기존 설정은 그대로 재사용합니다. 지속 가능한 지원이 실제로 부족할 때만 다음과 같은 footprint가 생깁니다.

```text
your-project/
├── AGENTS.md or CLAUDE.md     # 필요할 때 병합되는 host-loaded guidance
├── docs/nulnul/
│   ├── project.md             # stable goal, check, decisions, permissions, rollback
│   ├── checkpoint.json        # 짧은 일반 multi-session state
│   └── evolution.json         # governed history; 필요하면 checkpoint를 대체
├── .agents/skills/<name>/     # 적합한 기존 capability가 없을 때만
└── docs/nulnul/workflows/<name>.md
                                # 필요한 경우의 unattended workflow
```

Continuity writer는 하나입니다. 일반 작업은 `checkpoint.json`, governed evolution은 `evolution.json`을 사용하며 둘을 함께 쓰지 않습니다. Legacy state는 `unknown`으로 시작하고 fast resume 전에 exact check를 다시 실행합니다. 생성된 state와 local skill은 product code를 건드리지 않고 제거할 수 있습니다.

## NULNUL은 어떻게 검증하나요?

논문 링크는 신뢰 모델이 아닙니다. 신뢰 모델은 실행 가능한 evidence입니다.

```text
behavior check → negative controls → candidate comparison → independent Gate
                                                        ↓
                                              live cycle / rollback

transfer claim만 → sealed unseen check → scoped decision
```

네 가지 사례가 그럴듯한 설명과 측정된 동작의 차이를 보여줍니다.

- **Stale verified checkpoint.** repository mutation 뒤에도 3/3 interrupted run이 fast resume됐습니다. runner-owned freshness receipt가 재현된 unsafe outcome을 0/3으로 줄였습니다.
- **그럴듯한 instruction도 reject.** Navigator wording/order candidate 두 개는 말로는 타당했지만 verification을 계속 놓치거나 read와 cost를 늘려 promotion되지 않았습니다.
- **Scoped transfer, 과장 없는 판정.** checkpoint freshness는 unseen local Perl/TAP project shape 하나에서 살아남았지만 판정은 **Narrower Scope**였습니다. Harness-wide generalization은 확립되지 않았습니다.
- **Field failure를 invariant로 전환.** 하루 동안 실행한 workflow에서 concurrent writer가 decision 12,000개를 잃었고 empty-cycle cursor가 같은 120개를 반복 탐색했습니다. 이 failure는 single-writer와 cursor-persistence 규칙이 됐지만 범용 benchmark는 아닙니다.

| Evidence | 현재 결과 | 무엇을 말해 주나요? |
| --- | --- | --- |
| 저장소 test | **108개 통과 (108/108)** | deterministic product, state, privacy, rollback, negative-control contract가 유지됩니다. |
| Release Gate | 12개 behavior/safety case에서 **100/100** | 공개 fixture와 exact-version Claude adoption evidence가 통과합니다. 범용 benchmark는 아닙니다. |
| Checkpoint defect | unsafe fast resume **3/3 → 0/3** | 재현된 correctness defect 하나를 freshness mechanism이 닫았습니다. |
| Unseen transfer | **Narrower Scope** | mechanism 하나가 Perl/TAP shape 하나로 전이됐지만 전체 harness 일반화는 미입증입니다. |
| Bounded evolution candidate | frozen replay 하나가 evaluation 1회로 기록된 winner를 선택; retry는 0/2 | archive-aware bounded selection이 해당 failure family에서는 동작합니다. live candidate generation과 public v1.6.0 evidence는 아직 필요합니다. |

공개 검사를 직접 실행할 수 있습니다.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

근거 기록도 공개돼 있습니다. [Behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [generalization exposure](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), [Perl/TAP result](evals/generalization/results.json)을 확인할 수 있습니다. 버전별 상세 내용은 [`CHANGELOG.md`](CHANGELOG.md)의 역할입니다.

## NULNUL을 만든 이유

Coding agent를 쓰다 보면 model보다 주변 설정이 더 귀찮아지는 순간이 있습니다. 프로젝트마다 어떤 skill을 쓸지, agent를 하나 더 만들어야 하는지, 어떤 규칙을 context에 둘지, 다음 session을 어떻게 이어갈지, 무엇이 실제 완료를 증명할지 다시 결정하게 됩니다.

사용자가 결과를 요청하기 전에 AI 조직도부터 설계해야 한다는 점이 이상하다고 생각했습니다. 나는 원하는 outcome만 말하고, 반복되는 설정과 검증은 harness가 흡수하길 바랐습니다. 필요 없는 agent와 infrastructure를 계속 만드는 대신 만들지 않는 것이 기본인 시스템을 원했습니다.

Session이 바뀌어도 막연한 chat memory가 아니라 검증된 repository state에서 이어져야 합니다. 실패한 방법은 사라지지 않고 다음에는 같은 실수를 덜 하게 할 만큼의 evidence를 남겨야 합니다. 그래서 NULNUL을 시작했습니다.

## 뿌리와 영향

NULNUL은 [GeekNews Weekly 353](https://news.hada.io/weekly/202615)이 던진 harness engineering 문제에서 출발했습니다. Agent capability가 많아질수록 왜 사용자가 매번 주변 시스템을 직접 조립해야 하는가라는 질문입니다.

이후 editable task/meta boundary, generator/verifier separation, champion/challenger evaluation, eval-gated delivery의 영향을 받았습니다. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents))는 editable task/meta 질문의 중요한 참고였습니다. NULNUL은 HyperAgents를 재현하거나 open-ended self-improvement를 주장하지 않습니다.

<details>
<summary>측정된 evolution 작업에 영향을 준 기술 연구</summary>

1.4 observability 작업은 [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850)의 영향을 받았습니다. 1.5 evaluation boundary는 [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227)을 참고했습니다. 제한된 1.6 candidate는 [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621)에서 필요한 아이디어만 골라 사용했습니다.

논문은 질문, candidate mechanism, 더 강한 falsification 방법을 제공합니다. local evidence 없이 feature가 되지는 않습니다. 정확한 contract는 [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) reference에 있습니다.
</details>

## 2.0까지의 로드맵

현재 공개 plugin은 **1.5.0**입니다. Roadmap은 사용자 가치의 방향이지 자동 release 약속이 아닙니다.

| 단계 | 상태 | 사용자 가치 |
| --- | --- | --- |
| 1.4 Observable Evolution | 완료 | harness가 어디서 실패했는지 보고, evidence와 그럴듯한 설명을 구분합니다. |
| 1.5 Generalization Gate | 완료 | 익숙한 fixture에 맞춘 fix와 실제로 전이되는 fix를 구분합니다. |
| 1.6 Bounded Autonomous Evolution | 현재 local candidate | 고정 budget 안에서 작은 candidate space를 탐색하고, 승자를 지지할 evidence가 없으면 promotion 없이 멈춥니다. live generation과 public v1.6.0 evidence는 아직 필요합니다. |
| 1.7 Personal Evolution | 다음, 시작하지 않음 | project에서 검증된 adaptation이 fresh transfer evidence로 personal harness knowledge 승격 자격을 얻습니다. |
| 2.0 Cross-project / Meta Evolution | 장기 목표 | raw workload를 공유하지 않고 project 사이의 scoped lesson을 합치며 improvement procedure 자체를 발전시킵니다. |

## 신뢰 경계와 한계

- 설치됐거나 인기 있다는 사실만으로 verified가 되지 않습니다. provenance, compatibility, maintenance, permission, license, task fit을 확인합니다.
- 인증, 외부 쓰기, 배포, 공개, destructive action, paid resource, 전역 등록에는 명시적 승인이 필요합니다.
- credential, raw conversation, transcript, 전체 command history, machine path, private project data는 evolution memory가 되지 않습니다.
- 무인 session은 host-owned `.claude/**` configuration을 검사할 수 있지만 다시 쓰지 않습니다.
- fast resume 전에 checkpoint를 제한된 repository reality와 다시 비교합니다.
- Independent Gate ownership은 선언된 state에서 검증하며 두 runtime identity의 암호학적 분리를 증명하지 않습니다.

이 근거는 NULNUL이 모든 project를 개선하거나, 모든 agent error를 막거나, model reasoning 한계를 없애거나, 여러 repository에서 일반화되거나, hosted-service reliability를 제공한다는 뜻이 **아닙니다**. 현재 unseen result는 mechanism 하나와 project shape 하나만 다룹니다. 1.6 evidence는 retrospective frozen replay 하나이지 live open-ended autonomy가 아닙니다.

## 자주 묻는 질문

<details>
<summary>NULNUL은 항상 agent나 file을 추가하나요?</summary>

아닙니다. 저장소가 이미 job을 덮는지 먼저 확인합니다. 현재 설정을 재사용하고 아무것도 만들지 않는 것도 성공입니다.
</details>

<details>
<summary>NULNUL은 계속 혼자 학습하나요?</summary>

아닙니다. Improvement는 user-triggered, bounded, evidence-gated, reversible합니다. daemon, candidate population, recursive Coach, unattended infinite loop가 없습니다.
</details>

<details>
<summary>Release Gate는 NULNUL이 어디서나 더 좋다는 증거인가요?</summary>

아닙니다. 공개 behavior와 safety fixture를 보호합니다. Generalization Gate가 transfer claim을 별도로 제한하며 harness-wide generalization은 확립되지 않았습니다.
</details>

<details>
<summary>왜 skills-only plugin인가요?</summary>

현재 관찰된 workflow에는 server, hook, app, MCP service가 필요하지 않습니다. 이런 component는 검증된 job보다 permission과 maintenance cost를 먼저 늘립니다.
</details>

## 업데이트, 제거, 개발

Codex의 현재 plugin CLI에는 별도 plugin-update command가 없으므로 Git marketplace를 갱신한 뒤 재설치합니다.

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

Local clone에서 marketplace를 추가했다면 먼저 그 clone을 pull하세요. 업데이트 후 새 agent session을 시작합니다. Project-local guidance와 `docs/nulnul/` state는 보존됩니다.

Plugin을 제거합니다.

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

```bash
claude plugin uninstall nulnul-harness@nulnul-harness
claude plugin marketplace remove nulnul-harness
```

생성된 project state는 별도입니다. checkpoint나 evolution history가 더 필요하지 않을 때만 제거하세요.

Local development와 검증:

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

[`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), [MIT 라이선스](LICENSE)를 확인하세요.

MIT © [SeoNaRu](https://github.com/SeoNaRu)
