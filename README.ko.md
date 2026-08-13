<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<p align="center">
  <strong>작게 시작하세요. 프로젝트가 자랄 때 하네스도 함께 자랍니다.</strong><br>
  NULNUL은 지금 필요한 개발 환경만 Codex와 Claude Code에 구성하고, 실제 작업이 다음 필요를 증명할 때만 확장합니다. 모든 변경은 검증 가능하고, 범위가 제한되며, 되돌릴 수 있습니다.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.7.0-111111" alt="version 1.7.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="확인된 동작과 안전 점수: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

> Version 1.7.0은 공개 및 release closure를 마쳤습니다. 정확한 GitHub tag가 fresh Claude Code와 personal-adaptation adoption을 통과했고, evidence commit은 main CI run `31651306556`에서 성공했습니다.
>
> **1.7 상태:** 첫 scoped adaptation은 transfer shape 두 개를 통과하고 incompatible 및 revoked case를 건너뛴 뒤 승인된 opt-in home에서 raw project memory 없이 재사용됐습니다. Fresh GitHub-marketplace Claude Code adoption도 기존 agent 두 개를 보존하고 protected write 0건과 executable check 5개 통과를 기록했습니다.
>
> **2.0 local 상태:** 서로 다른 personal adaptation family 세 개가 bounded summary selector에 연결됐습니다. Sealed 3-case 비교에서 flat lookup의 모든 결정을 유지하면서 full compatibility check를 9회에서 4회로 줄였습니다. Public 2.0.0이 아니라 미공개 local candidate입니다.

## NULNUL은 무엇인가요?

NULNUL은 Codex와 Claude Code에서 프로젝트 안에 두고 쓰는 적응형 하네스입니다. 사용자가 첫날부터 최종 에이전트 구조를 설계하게 하는 대신, AI 개발 환경과 현재 프로젝트의 요구를 계속 맞춰 줍니다.

새 프로젝트에서는 가장 작은 유용한 작업 계약으로 시작합니다. 기존 프로젝트에서는 현재 설정을 먼저 읽고 잘 작동하는 것을 보존합니다. 프로젝트가 여러 세션으로 길어지거나, 새로운 검사가 생기거나, 책임 분리·권한 경계·반복 실패가 실제로 나타나면 빠진 메커니즘만 최소한으로 추가하고 유지하기 전에 검증합니다.

원하는 결과를 말하면 NULNUL이 다음을 맡습니다.

```text
저장소를 읽는다
        ↓
이미 잘 작동하는 설정과 도구를 재사용한다
        ↓
부족한 것만 추가한다
        ↓
요청한 작업을 진행한다
        ↓
저장소의 실제 검사를 실행한다
        ↓
다음 단계에 필요한 검증된 상태를 남긴다
```

여기서 “하네스”는 coding agent가 안정적으로 일하도록 돕는 작은 프로젝트 규칙·능력·상태·검사 묶음입니다. “agent team을 만든다”는 뜻이 아닙니다. 때로는 **새 agent 0개, 새 skill 0개, 새 infrastructure 0개**가 정답입니다.

## 프로젝트와 함께 자라는 하네스

NULNUL은 미래의 복잡성을 예상해 큰 프레임워크부터 설치하지 않습니다. 사용자가 실행을 요청할 때마다 현재 프로젝트와 현재 하네스가 여전히 맞는지 비교합니다.

```text
프로젝트가 변한다
      ↓
새로운 작업·경계·재현된 실패가 생긴다
      ↓
현재 하네스로 충분한가?
    ↙                    ↘
  충분함                 부족함
그대로 유지       가장 작은 변경을 제안
                              ↓
                        독립 검증
                       ↙       ↘
                    거부    유지 / rollback
```

하네스의 성장은 프로젝트 규모나 목표 에이전트 수가 아니라 실제로 확인된 작업이 결정합니다.

| 프로젝트에서 생긴 신호 | 정당화되는 최소 하네스 변화 |
| --- | --- |
| 명확한 검사 하나가 있는 작은 저장소 | 기존 지침과 검사를 재사용하고 역할을 추가하지 않습니다. |
| 작업이 여러 세션으로 길어짐 | 전체 대화를 저장하는 대신 짧은 verified checkpoint 하나를 둡니다. |
| 독립된 책임 주체가 필요함 | 그 경계만 분리하고 주변에 에이전트 팀을 만들지 않습니다. |
| 반복 워크플로에 상태나 외부 쓰기가 생김 | 필요한 위치에만 식별자, 중복 제거, 검토 상태, 권한 통제를 추가합니다. |
| 실패가 재현 가능해짐 | 인과관계가 명확한 개선 후보 하나를 등록하고 기존 방식과 비교해 Gate 통과 시에만 유지합니다. |
| 역할이나 메커니즘의 실제 일이 사라짐 | 병합하거나 제거합니다. 하네스의 성장은 누적만을 뜻하지 않습니다. |

공개된 1.7.0은 opt-in personal 경로를 추가했습니다. 미공개 2.0 candidate는 그 위에서 privacy-safe activation summary를 사용해 어떤 verified adaptation을 full compatibility check할 가치가 있는지 고릅니다. 과거 성공 횟수만으로 적용하지 않으며 unresolved conflict는 자동 선택을 중단시킵니다.

## 실제 운영 문제

AI로 개발하다 보면 프로젝트 옆에 또 하나의 프로젝트가 생깁니다. AI coding 환경 자체를 관리하는 일입니다.

- 세션마다 같은 프로젝트 설명을 다시 합니다.
- 좋다는 plugin·agent·rule을 계속 추가하다 보니 설정이 코드보다 이해하기 어려워집니다.
- 만들고 싶은 것보다 context와 token 관리부터 공부하게 됩니다.
- agent는 완료했다고 했지만 실제 test는 실행되지 않았습니다.
- 실패했던 방법이 다음 세션에서 조용히 다시 등장합니다.
- 저장소마다 하네스를 처음부터 다시 구성합니다.
- 프로젝트보다 AI 도구를 고르는 데 더 오래 걸립니다.

NULNUL은 이 일을 inspectable repository contract로 옮깁니다. 질문하기 전에 조사하고, 만들기 전에 재사용하고, 오래 남길 상태는 작게 유지하며, 자신감 있는 답변이 아니라 실행 가능한 검사를 완료 기준으로 삼습니다.

## 통제된 진화: 제안은 승인이 아닙니다

NULNUL은 프로젝트 하네스를 바꿀 수 있지만 자기 변경을 스스로 승인할 수는 없습니다.

```text
재현 가능한 실패
        ↓
     개선 후보
        ↓
 기존 방식과 후보 비교
        ↓
  Independent Gate
     ↙        ↘
   거부        승격
                 ↓
           실제 실행 관찰
              ↙       ↘
            유지     rollback
```

변경을 제안하는 과정과 credit을 부여하는 과정을 분리합니다. Coach는 causal hypothesis, prediction, falsification condition을 제시할 수 있지만 그 자체는 근거가 아닙니다. Gate가 completion check, validator, permission/privacy guardrail, cost, candidate identity, rollback 가능성에 대한 deterministic measurement를 소유합니다.

Bounded evolution에서는 탐색을 시작하기 전에 후보 수, generation 수, 평가 budget, permission, 종료 조건을 고정합니다. 더 나은 후보가 없다면 **`NO_PROMOTION`이 올바른 결과**입니다.

Personal reuse에서는 project 승인만으로도 부족합니다. 일반화된 후보가 representative transfer check와 별도 Personal Gate를 통과해야 하며, 새 프로젝트는 다시 compatibility를 검사해 적용·범위 축소·건너뛰기 중 하나를 선택합니다. 이는 사용자가 시작한 제한된 개선 절차입니다. 지속적인 자동 학습, 무인 반복 실행, open-ended self-improvement가 아닙니다.

## 잘 맞는 경우와 필요 없는 경우

**잘 맞습니다:**

- 작게 시작하지만 기능, 검사, 워크플로가 점차 늘어날 프로젝트
- 미리 만든 에이전트 팀 대신 최소 AI 작업 계약으로 시작하고 싶은 새 프로젝트
- 기존 규칙과 도구를 버리지 않고 현재 자리에서 보완하고 싶은 프로젝트
- 여러 세션에 걸쳐 검증된 저장소 상태에서 작업을 이어가야 하는 개발
- 프로젝트 성장에 따라 테스트, 권한, 독립 검토, rollback이 중요해지는 작업
- 반복 워크플로나 재현된 실패를 측정 가능한 프로젝트 범위 개선으로 바꾸고 싶은 경우
- 실제 작업에 따라 구조를 추가할 뿐 아니라 병합하거나 제거하고 싶은 프로젝트

**아마 필요 없습니다:**

- 읽기 전용 질문이나 아주 작은 일회성 수정
- 명확하고 안정적인 contract와 실행 가능한 completion check가 필요한 일을 이미 모두 덮는 단순 작업
- always-on workflow engine이나 hosted orchestration service가 필요한 경우
- AI가 승인 없이 인증·배포·공개·외부 쓰기를 해야 하는 경우
- 기반 model의 reasoning 성능을 높여 주는 도구를 찾는 경우
- raw personal memory, automatic global rule, 승인 없는 cross-project learning—1.7 release는 user-selected local home에 scoped verified adaptation만 저장합니다.

저장소가 작업에 필요한 것을 이미 모두 갖췄다면 NULNUL을 쓰지 않아도 됩니다.

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

새 세션에서 가장 짧게 시작해 보세요.

```text
이 프로젝트에 하네스를 세팅해줘. 이미 잘 작동하는 것은 재사용하고 부족한 것만 추가해줘.
```

원래 작업부터 바로 요청해도 됩니다.

```text
예약 API를 수정하고 기존 동작이 계속 통과하는지 확인해줘.
```

어떤 agent가 필요한지, workflow를 어떻게 나눌지 먼저 설계할 필요가 없습니다.

## 운영 use case

아래 prompt는 공개 evaluation case와 같은 contract를 실제 프로젝트에 적용합니다.

### 기존 backend 프로젝트

```text
Spring 예약 API가 겹치는 예약을 거부하도록 수정해줘.
현재 프로젝트 설정을 먼저 조사하고, 이미 있는 것은 재사용하고,
완료 전에 기존 regression check를 실행해줘.
```

### 새 프로젝트

```text
local-first 지출 관리 앱을 만들고 싶어.
가장 작은 개발 하네스를 구성하고, 필요한 permission boundary를 설명한 뒤,
첫 번째 동작 가능한 기능과 실행 가능한 검사 하나까지 만들어줘.
```

### 여러 세션에 걸친 개발

```text
다음 세션이 chat을 처음부터 복원하지 않아도 이 프로젝트를 이어가게 해줘.
짧고 검증된 checkpoint를 사용하고, 검사한 파일이 바뀌면 fast resume을 막아줘.
```

### 반복 workflow

```text
금융 YouTube creator를 찾고 중복을 제거한 뒤,
불확실한 결과는 review로 보내고 Google Sheets write는 승인 뒤에 두는 workflow를 만들어줘.
```

### 복잡해진 기존 AI 설정

```text
현재 agent, skill, plugin, 프로젝트 rule을 조사해줘.
실제 job이 있는 것은 유지하거나 재사용하고, 중복을 구분하고,
현재 작업이 gap을 증명하지 않으면 아무것도 추가하지 마.
```

### 반복되는 실패

```text
이 실패가 두 번 이상 반복됐어. 재현하고, 이전에 reject된 방향을 확인하고,
bounded improvement episode를 한 번 실행해줘. Deterministic evidence로 이기는
후보가 없으면 현재 하네스를 그대로 유지해줘.
```

### 다른 프로젝트에서 검증된 방법 재사용 (1.7)

```text
이 프로젝트에서 다른 곳에도 쓸 만한 방법이 나오면 mechanism만 일반화하고,
representative transfer와 negative-skip check를 실행한 뒤 personal evolution home에
쓰기 전에 물어봐. 새 프로젝트에서는 compatibility check 뒤에만 적용해줘.
```

## NULNUL이 실제로 하는 일

하네스가 없다면 사용자가 capability를 고르고, 프로젝트 rule을 쓰고, context를 관리하고, completion check를 설계하고, 세션 상태와 실패한 개선 방법까지 기억해야 할 수 있습니다.

NULNUL을 사용하면 사용자는 결과를 요청할 수 있습니다. Plugin은 다음 순서로 움직입니다.

1. Codex 또는 Claude Code surface를 감지하고 질문하기 전에 저장소를 읽습니다.
2. 기존 설정을 inventory하고 local substitute를 만들기 전에 검증된 capability를 찾습니다.
3. roster를 다시 만들지 않고 현재 구성을 유지·업그레이드·병합하거나 중복을 제거합니다.
4. 덮이지 않은 작업이나 독립 검증 경계만 추가합니다.
5. 원래 작업을 계속합니다. 설정만 끝낸 것은 완료가 아닙니다.
6. 정확한 저장소 command를 실행하고 제한되고 정제된 근거를 남깁니다.
7. 오래 진행되는 프로젝트라면 다음 세션을 위한 verified state를 남깁니다.
8. 재현 가능한 nonpass 결과를 제한된 개선 후보로 바꿉니다.
9. 명시적으로 opt-in한 경우 Personal Gate를 통과한 adaptation을 찾고 새 프로젝트와의 compatibility를 확인한 뒤, source project를 복사하지 않고 적용하거나 건너뜁니다.
10. 서로 다른 verified family가 세 개 이상이면 bounded summary로 relevant adaptation을 shortlist한 뒤에만 full compatibility check를 엽니다.

Navigator, Worker, Coach, Gate는 네 명의 필수 agent가 아니라 responsibility boundary입니다. 단순한 작업에서는 역할을 합칩니다. 독립 검증처럼 별도 job이 있을 때만 역할을 분리합니다.

프로젝트가 변하면 같은 조사를 다시 합니다. 새로운 일이 생기면 새 경계가 필요할 수 있고, 중복된 책임이 사라지면 병합하거나 제거할 수 있습니다. NULNUL은 에이전트와 파일을 한 방향으로 누적하는 대신 하네스 구조를 현재 프로젝트에 맞게 조정합니다.

## Engineering model

NULNUL은 의도적으로 skills-only입니다. Server, daemon, hosted control plane, background self-improvement process를 추가하지 않습니다. 신뢰성은 작은 repository-native contract 집합에서 나옵니다.

| Contract | Enforcement |
| --- | --- |
| Repository truth | 구성 전에 host surface, 기존 guidance, capability, agent, test, permission을 조사합니다. |
| Adaptive topology | 독립된 프로젝트 작업과 그 검사가 정당화할 때만 role과 mechanism을 추가·병합·제거합니다. |
| Verified continuity | Schema-v3 checkpoint는 exact completion command, bounded verification files, runner-owned freshness receipt를 사용합니다. 변경된 상태는 verified fast resume를 주장할 수 없습니다. |
| Governed evolution | Schema-v4 episode는 승격 전에 pathology, candidate/generation/evaluation budget, permission delta, archive identity, deterministic credit owner, stop reason을 고정합니다. |
| Evaluation exposure | DEV, VALIDATION, HOLDOUT, first exposure, retirement, mechanism identity가 machine-readable합니다. 사용한 holdout을 unseen으로 다시 부를 수 없습니다. |
| Personal adaptation | User-selected local registry에는 generalized mechanism, activation condition, contraindication, transfer summary, provenance, permission, revocation state만 저장합니다. Home 누락, conflict, private data, stale status, false activation은 fail-closed입니다. |
| Cross-project selection | Typed privacy-safe summary에 activation boundary, failed transfer, status, permission, evidence-backed relation을 보존합니다. 근거 없는 관계는 `UNKNOWN`으로 두고 raw project workload는 집계하지 않습니다. |
| Release integrity | Exact plugin provenance/version, protected write, agent hash, validator, negative control, archive/source parity, documentation debt가 fail-closed로 동작합니다. |
| Evidence hygiene | 저장 artifact에는 prompt, response, raw transcript, credential, private project data, 전체 command, machine path가 들어가지 않습니다. |

이는 architecture 명칭이 아니라 실행 가능한 contract입니다. Validator와 negative control도 저장소에 함께 제공됩니다.

## 주변 도구와 무엇이 다른가요?

다음 category는 함께 사용할 수 있습니다. 차이는 어떤 도구가 다른 모든 도구를 대체한다는 주장이 아니라 기본 job의 차이입니다.

| Category | 보통 하는 일 | NULNUL의 기본 선택 |
| --- | --- | --- |
| Agent-team generator | 여러 agent를 조합한다 | 독립된 job이 없다면 role을 만들지 않는다. |
| Prompt 또는 rule bundle | 준비된 지침을 불러온다 | 현재 repository state와 executable check에서 시작한다. |
| Memory layer | 대화나 context를 보존한다 | raw conversation 대신 짧고 검증된 repository state를 선호한다. |
| Hosted orchestrator | service에서 장기 workflow를 실행한다 | project-local, skills-only로 유지하며 server나 daemon을 요구하지 않는다. |
| NULNUL | 프로젝트에 맞춘 하네스, 실제 작업, 검증, gated improvement | 작게 시작하고, 확인된 작업에만 적응하며, 측정된 개선만 승격한다. |

## 저장소에 남는 것

아무것도 남지 않을 수 있습니다. 완전한 기존 설정은 그대로 재사용합니다. 지속 가능한 지원이 실제로 부족할 때만 다음과 같은 footprint가 생길 수 있습니다.

```text
your-project/
├── AGENTS.md or CLAUDE.md     # 필요할 때만 병합되는 host guidance
├── docs/nulnul/
│   ├── project.md             # stable goal, check, decision, permission
│   ├── checkpoint.json        # 짧고 검증된 multi-session state
│   └── evolution.json         # 필요한 경우의 governed improvement history
├── .agents/skills/<name>/     # 적합한 기존 capability가 없을 때만
└── docs/nulnul/workflows/<name>.md
                                # 필요성이 입증된 reusable workflow
```

일반 continuity는 `checkpoint.json`, governed evolution은 `evolution.json`을 사용하며 둘을 동시에 live writer로 두지 않습니다. 생성된 설정은 product code를 바꾸지 않고 제거할 수 있습니다.

## NULNUL은 어떻게 검증하나요?

논문 citation은 배경일 뿐 신뢰 모델이 아닙니다. 신뢰 모델은 실행 가능한 근거입니다.

```text
behavior check → negative controls → 후보 비교 → Independent Gate
                                                  ↓
                                        live cycle / rollback

transfer claim만 → sealed unseen check → scoped decision
```

강한 근거 중 상당수는 실패에서 나왔습니다.

- **Stale checkpoint defect.** 검증되지 않은 repository mutation이 interrupted run 3/3에서 fast resume됐습니다. Runner-owned freshness receipt가 unsafe result를 0/3으로 줄였습니다.
- **그럴듯한 후보 거부.** Navigator instruction 후보는 말로는 타당했지만 verification을 계속 놓치거나 read와 cost를 늘려 승격되지 않았습니다.
- **잘못된 holdout 보존.** 첫 one-shot Ruby fixture 오류를 validation으로 강등하고 다시 unseen이라고 부르지 않았으며, 새 case로 교체했습니다.
- **범위를 좁힌 일반화.** Checkpoint freshness는 unseen local Perl/TAP 프로젝트 shape 하나에서 살아남았습니다. 판정은 “harness가 generalize한다”가 아니라 **Narrower Scope**였습니다.
- **Live bounded evolution.** Unchanged champion 검사는 두 번 모두 stale public-positioning surface 7개를 찾았습니다. 새로 생성된 one-generation 후보는 0개에 도달하고 independent Gate를 통과한 뒤 `SUCCESS`로 종료했습니다. 이 근거는 해당 activation-metadata failure family에만 유효합니다.
- **Personal transfer candidate.** Accepted checkpoint-freshness mechanism은 fresh Node와 Make project shape를 통과하고 one-shot shape를 건너뛴 뒤 fresh data-CLI Project D에서 발견·검증됐습니다. Gate 판정 `PERSONAL_PROMOTION`은 명시된 durable-checkpoint 조건에만 유효하며 일반 personal-memory system을 증명하지 않습니다.
- **Cross-project Meta Evolution.** Transactional local migration과 machine-linked nonpass verdict가 같은 Personal Gate lifecycle을 통과해 독립 family 세 개가 됐습니다. Frozen one-generation selector는 fresh Project X, no-match, conflict에서 flat lookup과 같은 결정을 내리면서 full compatibility check를 9회에서 4회로 줄였습니다. Independent Meta Gate가 승격했고 이후 live cycle도 rollback trigger 0건으로 통과했습니다.
- **Field failure를 rule로 전환.** 한 workflow에서 concurrent writer가 decision 12,000개를 잃었고 empty-cycle cursor가 같은 120개를 반복 탐색했습니다. 이 incident는 single-writer와 cursor-persistence rule이 됐지만 범용 benchmark는 아닙니다.

| Evidence | 현재 결과 | 의미 |
| --- | --- | --- |
| 저장소 test | **161개 통과 (161/161)** | deterministic product, state, privacy, rollback, transfer, cross-project, Meta Gate, negative-control contract가 유지됩니다. |
| 확인된 behavior/safety 점수 | 12개 case에서 **100/100** | 공개 fixture가 통과합니다. 범용 품질 점수가 아닙니다. |
| 최종 1.7.0 Release Gate | **통과** | Exact-tag Claude Code와 personal-adaptation adoption 통과 후 main CI run `31651306556`도 green이 됐습니다. |
| Checkpoint defect | unsafe fast resume **3/3 → 0/3** | 재현된 correctness defect 하나를 닫았습니다. |
| Unseen transfer | **Narrower Scope** | mechanism 하나가 project shape 하나로 전이됐으며 harness-wide generalization은 미입증입니다. |
| Bounded evolution | champion/retry **위반 7개**, 새 후보 **0개**, stop `SUCCESS` | 좁은 failure family 하나에서 live generation과 bounded stopping이 한 번 동작했습니다. |
| Personal transfer candidate | **적용 2, 건너뜀 1, fresh Project D 통과** | Raw project data 없이 adaptation 하나를 transfer, compatibility check, reuse, dedup, revoke할 수 있습니다. 더 넓은 personal evolution은 미입증입니다. |
| 2.0 local Meta Gate | **3 family, full check 9 → 4, 결정 3/3 정답** | Bounded summary evidence가 sealed episode 하나에서 selection work를 줄였습니다. Token, runtime, universal, cross-user 개선은 미입증입니다. |
| 1.7 release 상태 | **공개 및 검증 완료** | 정확한 public 1.7.0 tag가 local override 없는 fresh adoption을 통과했고 evidence의 main CI도 성공했습니다. 더 넓은 personal evolution은 미입증입니다. |

개선 후보가 반드시 이겨야 하는 것은 아닙니다. 거부, `NO_PROMOTION`, narrower scope, rollback은 모두 정상 결과입니다.

저장소 검사를 직접 재현할 수 있습니다.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

공개된 버전이라면 두 번째 command가 `release_ready: true`를 보고해야 합니다. Version 1.7.0은 exact public-tag evidence로 이를 통과했고, 같은 evidence의 main CI도 성공했습니다. 현재 미공개 2.0 development 상태에서는 `local_candidate_ready: true`를 보고하되 exact-version publication과 adoption 전까지 `release_ready: false`를 유지합니다.

근거 기록도 공개돼 있습니다. [Behavior cases](evals/cases.json), [behavior results](evals/results.json), [performance evidence](evals/benchmarks/performance.json), [activation evidence](evals/benchmarks/activation/results.json), [generalization exposure](evals/generalization/manifest.json), [failed Ruby evidence](evals/generalization/results-ruby-failed.json), [Perl/TAP evidence](evals/generalization/results.json), [live 1.6 preregistration](evals/autonomous/live-1.6-preregistration.json), 1.7 [personal transfer preregistration](evals/personal-evolution/preregistration.json)과 [results](evals/personal-evolution/results.json), 2.0 [meta preregistration](evals/meta-evolution/preregistration.json), [typed evidence](evals/meta-evolution/cross-project-evidence.json), [Meta Gate result](evals/meta-evolution/results.json)을 확인할 수 있습니다. 버전별 history는 [`CHANGELOG.md`](CHANGELOG.md)의 역할입니다.

## NULNUL을 만든 이유

Coding agent로 프로젝트를 시작할 때 만들고 싶은 것보다 AI 환경을 먼저 공부하게 되는 경우가 있었습니다. 어떤 skill을 써야 하는지, agent가 몇 개나 필요한지, 어떤 rule을 context에 넣을지, token을 낭비하는 건 아닌지, 다음 세션을 어떻게 이어갈지, 무엇이 실제 완료를 증명하는지부터 정해야 했습니다.

좋다고 추천되는 도구를 모두 추가한다고 설정이 더 좋아지지는 않았습니다. 초보자가 결과를 요청하기 전에 AI 조직도부터 설계해야 한다는 점도 이상했습니다.

새 프로젝트에는 처음부터 작은 작업 환경을 잡아 주고, 기존 프로젝트에는 무엇이 있는지 먼저 읽은 뒤 부족한 것만 더하고 싶었습니다. 프로젝트가 달라지면 사용자가 AI 설정 전체를 다시 설계하지 않아도 하네스가 필요한 구조를 추가하고, 겹치면 합치고, 쓸모가 없어지면 제거할 수 있어야 한다고 생각했습니다. 사용 중 더 나은 방법을 발견해도 실제로 더 낫다는 근거가 있을 때만 남기고 싶었습니다.

사용자가 하네스를 계속 관리하기보다 만들고 싶은 프로젝트에 더 집중할 수 있는 환경을 만들고 싶어서 NULNUL을 시작했습니다.

## 뿌리와 영향

NULNUL은 [GeekNews Weekly 353](https://news.hada.io/weekly/202615)이 던진 harness-engineering 문제에서 출발했습니다. Coding-agent capability가 많아질수록 왜 사용자가 매번 주변 시스템을 직접 조립해야 하는가라는 질문입니다.

설계에는 editable task/meta boundary, independent verification, champion/challenger comparison, eval-gated delivery가 영향을 줬습니다. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([paper](https://arxiv.org/abs/2603.19461), [code](https://github.com/facebookresearch/Hyperagents))는 editable task/meta 질문의 중요한 참고였습니다. NULNUL은 HyperAgents를 재현하거나 open-ended self-improvement를 주장하지 않습니다.

<details>
<summary>측정된 evolution 작업의 기술 참고 자료</summary>

Observable Evolution은 [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850), Generalization Gate는 [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227)의 영향을 받았습니다. 제한된 1.6 episode에는 [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621)의 아이디어 중 필요한 것만 사용했습니다.

논문은 질문과 더 강한 falsification 방법을 제공합니다. Local evidence 없이 product capability가 되지는 않습니다. 정확한 contract는 [evolution](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [meta-evolution](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), [generalization](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) reference에 있습니다.
</details>

## 2.0까지의 로드맵

Roadmap은 사용자 가치의 방향이지 자동 release 약속이 아닙니다.

| 단계 | 상태 | 사용자에게 좋아지는 점 |
| --- | --- | --- |
| 1.4 Observable Evolution | 완료 | 그럴듯한 설명을 믿는 대신 하네스가 왜 실패했는지 볼 수 있습니다. |
| 1.5 Generalization Gate | 완료 | 해결책이 전이되는지 익숙한 evaluation case에만 맞는지 구분합니다. |
| 1.6 Bounded Autonomous Evolution | 완료 | 고정 budget 안에서 작은 후보 공간을 탐색하고 근거가 약하면 아무것도 바꾸지 않은 채 멈춥니다. |
| 1.7 Personal Evolution | 완료 | 프로젝트에서 검증된 개선을 transfer evidence, Personal Gate, 새 프로젝트 compatibility check 뒤에만 재사용합니다. Exact public adoption과 main CI가 통과했습니다. |
| 2.0 Cross-project / Meta Evolution | Local functional candidate, 미공개 | Verified family 세 개를 bounded selector에 연결했습니다. Sealed Meta Gate에서 동일 결정을 유지하며 full check를 9회에서 4회로 줄였고 live cycle도 통과했습니다. Public exact-version release/adoption은 별도 작업입니다. |

## 신뢰 경계와 한계

- 인증, 외부 쓰기, 배포, 공개, destructive operation, paid resource, 전역 등록에는 명시적 승인이 필요합니다.
- Credential, raw conversation, transcript, 전체 command history, machine path, private project data는 evolution memory가 되지 않습니다.
- Personal Evolution은 사용자가 명시적으로 선택한 기존 local directory를 요구합니다. 실제 private local home 하나가 설정되어 validator를 통과했으며, machine path는 public evidence에 남기지 않습니다.
- 무인 Claude Code 세션은 host-owned `.claude/**` configuration을 검사할 수 있지만 다시 쓰지 않습니다.
- Fast resume 전에 checkpoint를 제한된 repository reality와 비교합니다.
- Independent Gate ownership은 선언된 state에서 검증하며 서로 다른 runtime identity를 암호학적으로 증명하지 않습니다.
- NULNUL은 기반 model의 reasoning 한계를 없애거나 모든 agent error를 막지 않습니다.
- unseen transfer 하나와 live bounded episode 하나는 universal 또는 harness-wide generalization을 증명하지 않습니다.
- 2.0 local evidence는 mechanism family 세 개, sealed selector case 세 개, 확인된 `COMPLEMENTS` relation 하나, live cycle 하나에만 해당합니다. 다른 관계는 `UNKNOWN`이며 arbitrary project lesson, token/runtime 개선, cross-user learning은 미입증입니다.
- Daemon, recursive Coach, candidate population, hosted evolution service, unattended infinite loop가 없습니다.

## 자주 묻는 질문

<details>
<summary>NULNUL은 항상 agent나 file을 추가하나요?</summary>

아닙니다. 저장소가 이미 job을 덮는지 먼저 확인합니다. 현재 설정을 재사용하고 아무것도 만들지 않는 것도 성공입니다.
</details>

<details>
<summary>NULNUL은 계속 혼자 학습하나요?</summary>

아닙니다. Improvement는 user-triggered, bounded, evidence-gated, reversible합니다. 이기는 후보가 없으면 현재 champion을 유지합니다.
</details>

<details>
<summary>저장소가 커지면 하네스도 자동으로 커지나요?</summary>

크기만 보고 커지지 않으며 백그라운드에서 자동 실행되지도 않습니다. 사용자가 작업을 요청했을 때 현재 저장소를 조사하고, 새로운 작업·경계·재현된 실패가 있을 때만 하네스를 바꿉니다. 변화는 메커니즘 하나를 추가하는 것일 수도, 중복을 합치는 것일 수도, 낡은 역할을 제거하는 것일 수도, 아무것도 바꾸지 않는 것일 수도 있습니다.
</details>

<details>
<summary>기존 AI 설정이 있어도 사용할 수 있나요?</summary>

네. 무엇을 추가하기 전에 현재 설정을 조사하고 분류합니다. 기존 roster를 무조건 교체하는 것이 아니라 재사용하거나 in-place로 개선하도록 설계됐습니다.
</details>

<details>
<summary>100/100은 NULNUL이 어디서나 더 좋다는 뜻인가요?</summary>

아닙니다. 확인된 behavior와 safety fixture만 다룹니다. Generalization Gate가 transfer claim을 별도로 제한하며, accepted mechanism 하나가 unseen project shape 하나에 전이됐을 뿐 harness-wide generalization은 아닙니다.
</details>

## 업데이트, 제거, 개발

Codex는 Git marketplace를 갱신한 뒤 plugin을 다시 설치합니다.

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

Local clone에서 marketplace를 추가했다면 먼저 해당 clone을 pull하세요. 업데이트 후 새 agent 세션을 시작합니다. Project-local guidance와 `docs/nulnul/` state는 보존됩니다.

Codex에서 제거합니다.

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

Claude Code에서 제거합니다.

```bash
claude plugin uninstall nulnul-harness@nulnul-harness
claude plugin marketplace remove nulnul-harness
```

생성된 project state는 plugin과 별개입니다. Checkpoint나 evolution history가 더 이상 필요 없을 때만 제거하세요.

Local development와 검증:

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

[`CHANGELOG.md`](CHANGELOG.md), [`SUPPORT.md`](SUPPORT.md), [`PRIVACY.md`](PRIVACY.md), [`TERMS.md`](TERMS.md), [MIT license](LICENSE)를 확인할 수 있습니다.

MIT © [SeoNaRu](https://github.com/SeoNaRu)
