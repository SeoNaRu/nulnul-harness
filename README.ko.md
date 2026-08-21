<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<h1 align="center">NULNUL Harness</h1>

<p align="center">
  <strong>NULNUL은 OpenAI Codex와 Anthropic Claude Code를 위한 오픈소스 AI 개발 환경입니다.</strong><br>
  AI 설정을 바꾸기 전에 기존 <code>AGENTS.md</code> 또는 <code>CLAUDE.md</code>, 스킬·플러그인·에이전트, 프로젝트 검사를 확인합니다. 적합한 것은 유지하고 부족한 부분만 보완하며, 실제 테스트·빌드·검증 결과를 완료 기준으로 사용합니다.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-2.2.0-111111" alt="버전 2.2.0">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Release_Gate-100%2F100-111111" alt="확인된 동작과 안전 점수: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> · <a href="#파일을-바꾸지-않고-체험하기">읽기 전용 체험</a> · <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.2.0">현재 릴리스: v2.2.0</a>
</p>

<p align="center">
  기존 설정을 먼저 확인합니다 · 필요한 부분만 추가합니다 · 저장소 검사를 완료 기준으로 사용합니다
</p>

> 여기서 “하네스”는 AI 코딩 에이전트가 따르는 프로젝트 규칙, 스킬, 작업 상태, 실행 가능한 검사의 묶음입니다. NULNUL은 이 설정을 저장소 안에서 관리하며, 에이전트 팀 생성기를 뜻하지 않습니다.

## 사용 전 / NULNUL 사용 후

| 사용 전 | NULNUL 사용 후 |
| --- | --- |
| 세션마다 프로젝트를 다시 설명함 | 저장소와 현재 설정부터 읽음 |
| 비슷한 스킬과 에이전트가 계속 늘어남 | 맞는 것은 재사용하고 비어 있는 역할만 보완함 |
| 실제 검사 없이 완료 답변을 받음 | 저장소의 테스트·빌드·검증 명령을 실행함 |
| 지난 작업 상태를 채팅에서 복원함 | 필요할 때만 짧고 검증된 체크포인트를 남김 |

기존 설정으로 충분하면 **새 에이전트, 새 스킬, 새 인프라를 추가하지 않습니다.**

## 빠른 시작

OpenAI Codex에 NULNUL 플러그인을 설치합니다.

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

또는 Anthropic Claude Code에 설치합니다.

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

설치 후 새 세션에서 다음과 같이 요청합니다.

```text
이 저장소부터 확인해줘. 이미 잘 작동하는 설정은 재사용하고 빠진 것만
보완한 다음, 내가 요청한 작업을 계속하고 실제 프로젝트 검증까지 실행해줘.
```

제품 작업부터 바로 요청해도 됩니다.

```text
예약 API를 수정하고 기존 동작이 계속 통과하는지 확인해줘.
```

### 파일을 바꾸지 않고 체험하기

NULNUL이 어떤 판단을 내릴지 읽기 전용으로 확인할 수 있습니다.

```text
이 저장소를 확인하고 필요한 최소한의 하네스 변경만 제안해줘.
파일은 수정하지 마.
```

<a id="사용-목적"></a>

## NULNUL은 어떤 문제를 해결하나요?

AI 코딩 에이전트에는 플러그인, 규칙, 컨텍스트, 세션 상태, 실행 가능한 검사 같은 프로젝트별 설정이 필요합니다. 이 설정을 직접 관리하면 역할이 겹치는 에이전트와 스킬, 오래된 작업 상태, 테스트 결과가 없는 완료 답변이 남을 수 있습니다.

NULNUL은 이런 설정을 확인하고 제거할 수 있는 저장소 계약으로 관리합니다. 기존 설정을 보존하면서 필요한 부분만 보완하려는 Codex·Claude Code 프로젝트에 맞습니다.

제품 방향은 사용자가 정합니다. NULNUL은 저장소에 맞는 구현 및 검증 경로를 찾고 중요한 선택을 설명합니다.

## 대표 사용 사례 3가지

### 기존 기능을 지키며 새 기능 추가

**상황:** 이미 프로젝트 규칙, 코드, 회귀 테스트가 있는 저장소입니다.

**입력:**

```text
Spring 예약 API가 겹치는 예약을 거부하도록 수정해줘.
현재 설정부터 확인하고, 이미 있는 것은 재사용하고,
완료 전에 기존 회귀 검사를 실행해줘.
```

**확인하고 남기는 것:** 현재 지침과 사용 가능한 기능을 먼저 확인하고, 필요한 코드만 바꾼 뒤 저장소의 기존 완료 검사를 실행한 결과를 남깁니다.

### 여러 세션에 걸친 작업 이어가기

**상황:** 대화 전체를 다시 읽지 않고도 장기 작업을 안전하게 이어가야 합니다.

**입력:**

```text
다음 세션에서 대화 내용을 처음부터 복원하지 않고도 이 프로젝트를 이어가게 해줘.
짧고 검증된 체크포인트를 사용하고, 검사한 파일이 바뀌면 빠른 재개를 막아줘.
```

**확인하고 남기는 것:** 범위를 제한한 체크포인트 하나, 정확한 완료 명령, 그 명령이 검사하는 파일과 연결된 최신성 확인 정보를 남깁니다.

### 복잡해진 AI 설정 정리

**상황:** `AGENTS.md`, `CLAUDE.md`, skills, plugins, agents의 역할이 서로 겹칩니다.

**입력:**

```text
현재 에이전트, 스킬, 플러그인, 프로젝트 규칙을 확인해줘.
실제 역할이 있는 것은 유지하거나 재사용하고, 중복을 구분한 뒤,
현재 작업에서 부족한 점이 확인되지 않으면 아무것도 추가하지 마.
```

**확인하고 남기는 것:** 기존 역할마다 유지·업그레이드·병합·제거 중 하나를 판단하고, 같은 역할을 하는 새 구성을 옆에 만들지 않습니다.

<details>
<summary>새 프로젝트, 반복 워크플로, 반복 실패, 개인 재사용 프롬프트</summary>

**새 프로젝트**

```text
로컬 우선 지출 관리 앱을 만들고 싶어.
가장 작은 개발 하네스를 구성하고, 필요한 권한 경계를 설명한 뒤,
첫 번째로 실제 동작하는 기능과 실행 가능한 검사 하나까지 만들어줘.
```

**반복 워크플로**

```text
금융 유튜브 크리에이터를 찾고 중복을 제거한 뒤,
불확실한 결과는 검토 대상으로 보내고 Google Sheets 쓰기는
승인 뒤에만 실행하는 작업 흐름을 만들어줘.
```

**반복되는 실패**

```text
이 실패가 두 번 이상 반복됐어. 재현하고, 이전에 거부된 방향을 확인한 뒤,
범위를 제한한 개선 절차를 한 번 실행해줘. 결정론적 근거에서 더 나은
후보가 없으면 현재 하네스를 그대로 유지해줘.
```

**다른 프로젝트에서 검증된 방법 재사용**

```text
이 프로젝트에서 다른 곳에도 쓸 만한 방법이 나오면 메커니즘만 일반화하고,
대표 전이 검사와 적용하면 안 되는 경우의 건너뛰기 검사를 실행한 뒤
개인 진화 홈에 쓰기 전에 물어봐. 새 프로젝트에서는 호환성 검사를
통과한 뒤에만 적용해줘.
```
</details>

<a id="동작-방식"></a>

## NULNUL은 어떻게 동작하나요?

```text
저장소와 실행 환경을 확인한다
        ↓
잘 작동하는 규칙과 기능을 재사용한다
        ↓
담당이 비어 있는 일이나 검증 경계만 보완한다
        ↓
사용자가 요청한 원래 작업을 계속한다
        ↓
저장소의 정확한 완료 검사를 실행한다
        ↓
다음 세션에 꼭 필요한 검증된 상태만 남긴다
```

실제로 플러그인은 다음 순서로 움직입니다.

1. Codex인지 Claude Code인지 확인하고 해당 `AGENTS.md` 또는 `CLAUDE.md`, 프로젝트 메타데이터, 테스트, 실행 기록을 읽습니다.
2. 빠진 것을 판단하기 전에 기존 스킬·플러그인·에이전트·도구를 목록으로 확인합니다.
3. 프로젝트 전용 대체 기능을 만들기 전에 설치된 기능과 공식·큐레이션된·신뢰할 만한 공개 기능을 찾습니다.
4. 기존 역할을 다시 만들지 않고 유지·업그레이드·병합하거나 제거합니다.
5. 직접 실행이나 단일 에이전트를 우선하고, 독립된 일이나 검증 경계가 있을 때만 역할을 나눕니다.
6. 사용자가 원래 요청한 작업을 계속합니다. 설정만 끝낸 것은 완료가 아닙니다.
7. 저장소의 정확한 완료 명령을 실행하고 민감 정보를 뺀 최소 근거만 남깁니다.
8. 여러 세션이 필요한 작업에는 짧고 검증된 상태를 남깁니다.
9. 재현된 실패는 곧바로 규칙으로 굳히지 않고 범위를 제한한 개선안으로 만듭니다.
10. 사용자가 명시적으로 동의한 경우에만 원본 프로젝트를 복사하지 않고 검증된 개인 적응 방식의 호환성을 확인합니다.

Navigator, Worker, Coach, Gate는 네 명의 필수 에이전트가 아니라 책임의 구분입니다. 일반 작업에서는 한데 합칩니다. 변화를 측정해 승인해야 할 때만 개선안을 내는 쪽과 독립 Gate를 분리합니다.

<a id="다른-도구-유형과의-비교"></a>

## 다른 AI 개발 도구와 무엇이 다른가요?

아래 도구는 서로 함께 쓸 수 있습니다. 무엇이 더 우월한지가 아니라 기본적으로 맡는 일이 다릅니다.

| 범주 | 보통 시작하는 방식 | NULNUL의 차이 |
| --- | --- | --- |
| 에이전트 팀 생성기 | 여러 에이전트로 역할 구성을 만듦 | 독립된 일이 확인될 때만 역할을 추가하고, 기존 역할은 현재 자리에서 보완함 |
| 프롬프트·규칙 묶음 | 준비된 지침을 불러옴 | 저장소의 현재 규칙과 실행 가능한 검사에서 시작함 |
| 메모리 계층 | 대화나 컨텍스트를 보존함 | 원본 대화 대신 짧고 검증된 프로젝트 상태를 남김 |
| 호스팅 오케스트레이터 | 서비스에서 장기 작업을 실행함 | 저장소 안에서 스킬만으로 동작하며 서버나 데몬을 요구하지 않음 |
| 저장소 템플릿 | 같은 초기 구조를 적용함 | 기존 저장소에 맞춰 조정하며 아무것도 추가하지 않을 수도 있음 |
| NULNUL | 저장소 확인, 실제 작업, 검증, 개선 | 먼저 재사용하고, 실제로 부족하다고 확인된 부분만 채우며, 독립 검증을 통과한 변화만 유지함 |

<a id="저장소에-추가될-수-있는-파일"></a>

## 저장소에 어떤 파일을 추가하나요?

기존 설정으로 충분하면 파일을 추가하지 않습니다. 오래 유지할 지원이 부족할 때는 다음 파일을 추가할 수 있습니다.

```text
your-project/
├── AGENTS.md or CLAUDE.md     # 필요할 때만 기존 내용과 합치는 활성 호스트 지침
├── docs/nulnul/
│   ├── project.md             # 안정된 목표, 검사, 결정, 권한
│   ├── checkpoint.json        # 짧고 검증된 다중 세션 상태
│   ├── evolution.json         # 필요할 때만 쓰는 현재 개선 상태
│   └── evolution.archive.json # 일반 재개 컨텍스트 밖의 종료된 근거
├── .agents/skills/<name>/     # Codex: 적합한 기존 기능이 없을 때만
└── docs/nulnul/workflows/<name>.md
                                # Claude Code: 반복 필요성이 입증됐을 때만
```

Codex는 `AGENTS.md`만, Claude Code는 `CLAUDE.md`만 관리합니다. 두 환경을 순서대로 쓸 때는 같은 `docs/nulnul/` 계약과 현재 상태 기록자 하나를 공유합니다. 두 환경이 동시에 같은 상태를 바꾸는 동작은 보장하지 않습니다.

일반 작업을 이어갈 때는 `checkpoint.json`을, 통제된 개선이 필요할 때는 `evolution.json`을 씁니다. 두 파일이 동시에 현재 상태를 기록하지 않습니다. 생성된 설정은 제품 코드를 건드리지 않고 제거할 수 있습니다.

종료된 개선 이력은 다이제스트로 연결한 인접 아카이브에 보존합니다. 결정론적 코드가 무결성과 전체 관계를 확인하고, 일반 재개에서는 현재 상태만 읽으며 거절 이력은 필요할 때만 조회합니다.

상태 파일마다 기록 주체를 하나만 둡니다. 검증 상태는 `verified`, `failed`, `unknown`을 구분하고, 유효성 검사는 반드시 실패해야 하는 부정 대조군과 함께 확인합니다.

<a id="검증과-신뢰-방식"></a>

## AI 작업을 어떻게 검증하나요?

NULNUL은 모델의 자신감을 증거로 취급하지 않습니다. 저장소의 실제 검사를 실행하고 범위를 제한한 근거를 남깁니다. 더 넓은 주장을 할 때는 부정 대조군, 미리 고정한 후보, 독립 Gate, 롤백 경로까지 사용합니다.

```text
저장소 검사 → 부정 대조군 → 후보 비교 → 독립 Gate
                                         ↓
                                실제 작업 주기 또는 롤백

전이 주장에만 적용 → 봉인된 미사용 검사 → 범위를 제한한 판정
```

### 현재 공개 근거

| 근거 | 현재 결과 | 확인된 범위 |
| --- | --- | --- |
| [저장소 전체 검사](tests/) | **234개 통과 (234/234)** | 제품, 상태, 실행 환경 전환, 개인정보 보호, 롤백, 전이, Meta Gate, 문서 부채, 정확한 후보, 동작 경계, 부정 대조군의 결정론적 계약이 통과함 |
| [확인된 동작과 안전](evals/results.json) | 사례 12개에서 **100/100** | 공개 픽스처가 통과함. 어디서나 더 좋다는 범용 품질 점수가 아님 |
| [공개 2.2.0 정확한 버전 채택](evals/personal-evolution/public-adoption.json) | **Claude 검사 5/5, 보호 대상 쓰기 0건** | 공개 버전을 새로 설치한 환경에서 기존 에이전트 프로필 두 개와 사용하지 않은 Codex 루트 지침을 보존함 |
| [공개 버전 Project M](evals/meta-evolution/public-adoption.json) | 전체 호환성 검사 **3 → 1** | 트랜잭션 마이그레이션 적용 판단을 그대로 유지하며 일치 항목 없음·충돌·개인정보·권한·마이그레이션·롤백 대조군을 통과함 |
| [릴리스 산출물](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v2.2.0) | **바이트 단위 일치, SHA-256 `779bd3d43178925fe53eafa348484d8bf6d0cb1e79fc00a31615b754b71124d0`** | 내려받은 v2.2.0 아카이브와 고정한 로컬 산출물이 정확히 같음 |

v2.2.0 근거에는 `local_candidate_ready: true`와 `release_ready: true`가 기록돼 있습니다. [기본 브랜치 CI 실행 32348453221](https://github.com/SeoNaRu/nulnul-harness/actions/runs/32348453221)도 전체 검사와 Release Gate를 통과했습니다.

<details>
<summary>현재 계약을 뒷받침하는 측정 결과</summary>

| 근거 | 결과 | 주장하지 않는 범위 |
| --- | --- | --- |
| 최종 1.7.0 Release Gate | 정확한 태그의 Claude Code·개인 적응 채택과 기본 브랜치 CI `31651306556` 통과 | 이후 모든 환경 |
| 오래된 체크포인트 결함 | 위험한 빠른 재개 **3/3 → 0/3** | 재현된 정확성 결함 하나 |
| 미사용 사례 전이 | **Narrower Scope** | 메커니즘 하나가 새 Perl/TAP 프로젝트 형태 하나에 전이됨. 하네스 전체의 일반화는 아님 |
| 실제 환경의 제한된 개선 | 기존 방식과 재시도에서 **위반 7개**, 한 번 생성한 후보에서 **0개**, `SUCCESS`로 종료 | 활성화 메타데이터 실패 계열 하나 |
| 개인 적응 방식 | **적용 2, 건너뜀 1, 새 Project D 통과** | 체크포인트 최신성 메커니즘 하나. 일반 개인 메모리 시스템은 아님 |
| 프로젝트 간 Meta Gate | **3개 계열, 전체 검사 9 → 4, 판단 3/3 정답** | 봉인된 선택 실행 하나. 토큰·실행 시간·범용성·사용자 간 개선은 아님 |
| 재개 컨텍스트 축소 | 현재 진화 픽스처 **87.48% 축소** | 공개 픽스처 하나. 전체 근거는 무결성을 확인한 아카이브에 남음 |
| 문서 부채 A/B | 순서를 교차한 네 차례에서 중앙값 **17.73645초 → 0.2308초(−98.70%)** | Git으로 추적되는 릴리스 저장소에서 같은 결과를 유지한 측정 |
</details>

거절되거나 실패한 후보도 근거에 남깁니다.

- 그럴듯했던 Navigator 후보가 검증을 놓치거나 비용을 늘려 거부됐습니다.
- 오류가 난 첫 Ruby 홀드아웃은 미사용 사례라고 다시 부르지 않고 폐기 이력으로 보존했습니다.
- 2.2 동의·연속성 후보는 사전에 정한 엄격한 Gate가 `NO_PROMOTION`을 반환해 제거했습니다.
- 2.0 이후 기능 권한, 사용자 의도, 결정 산출물, 저장소 영수증 후보는 `NO_ADVANTAGE` 또는 `NO_PROMOTION` 기록으로 남아 있습니다.
- 여러 기록기가 동시에 써서 결정 12,000개가 사라진 사건과 빈 주기 뒤 같은 항목 120개를 다시 탐색한 사건은 단일 기록자·커서 유지 규칙이 됐지만 범용 벤치마크로 주장하지 않습니다.

릴리스 수준 검사를 직접 실행할 수 있습니다.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

## 통제된 개선(Controlled Evolution)

하네스 변경안은 독립 Gate가 관리하는 검사를 통과해야 유지할 수 있습니다.

```text
재현된 실패
    ↓
범위를 제한한 후보
    ↓
현재 방식과 후보 비교
    ↓
독립 Gate
  ↙       ↘
거부       잠정 적용
              ↓
        실제 작업 주기 1회
          ↙         ↘
        확정         롤백
```

후보를 만들기 전에 실패 설명, 후보·생성 횟수, 평가·모델 예산, 권한 경계, 거절 이력 조회, 공정한 재시도 기준, 종료 조건을 고정합니다. Coach는 개선안을 내고, 결정론적 검사와 독립 Gate가 성과를 판정합니다. 후보가 결과를 개선하지 못하면 `NO_PROMOTION`으로 판정합니다.

평가 사례의 노출 이력도 상태로 관리합니다. DEV는 개발에 활용할 수 있고, VALIDATION은 후보 선택에 쓸 수 있으며, 봉인된 HOLDOUT은 전이 범위를 한 번 확인하는 데만 씁니다. 최초 노출과 폐기 여부를 기계가 읽을 수 있게 남기므로, 이미 사용한 사례를 “미사용”이라고 다시 부를 수 없습니다.

Gate를 통과했다고 확정 버전을 곧바로 바꾸지 않습니다. 후보는 **잠정(provisional)** 상태로 두고 마지막 확정 버전을 유지합니다. 다음 실제 작업 주기 하나가 문제없이 끝나면 확정하고, 실행 가능한 기준을 넘으면 롤백을 기록합니다. 제공되는 실행기는 임의의 롤백 명령을 실행하거나 제품 파일을 마음대로 고치지 않습니다.

### 개인 적응

개인 재사용은 사용자가 선택해야만 동작하며, 프로젝트 기억을 복사하는 기능이 아닙니다. 사용자가 지정한 기존 로컬 홈, 대표 전이 검사와 건너뛰기 검사, 독립 Personal Gate가 필요합니다. 새 프로젝트에서는 호환성을 다시 확인합니다. 권한 누락, 비공개 데이터, 중복 식별자, 충돌, 오래되거나 폐기된 상태, 잘못된 활성화가 발견되면 자동 적용하지 않습니다. 원본 프로젝트 기억은 다른 저장소로 복사하지 않습니다.

### 프로젝트 간 선택과 Meta Evolution

프로젝트 간 선택은 서로 독립적인 메커니즘 세 계열이 Personal Gate 절차를 통과한 뒤에만 시작합니다. 승인된 로컬 경계 안에서 개인정보를 뺀 형식화된 요약만 모으고, 실패한 전이와 근거 없는 관계도 그대로 남깁니다. 새 사례에 노출하기 전에 선택 후보를 고정하고, 전체 조회·단순 기준과 비교합니다. Meta Gate가 승격, 거부, 범위 축소, 차이 없음, 충돌, 권한 차단, 롤백을 결정합니다.

이는 사용자가 시작하는 제한된 개선입니다. 지속적인 자동 학습, 무인 반복 실행, 벡터 데이터베이스, 호스팅 진화 서비스, 사용자 간 학습이 아닙니다.

<a id="잘-맞는-경우"></a>

## 어떤 프로젝트에 맞나요?

**이런 프로젝트에 잘 맞습니다.**

- 현재 규칙, skills, plugins, agents, 검사를 보존해야 하는 기존 프로젝트
- 미리 만든 에이전트 팀이 아니라 가장 작은 AI 작업 계약으로 시작하려는 새 프로젝트
- 여러 세션에 걸쳐 검증된 저장소 상태에서 이어가야 하는 개발
- 테스트, 권한, 독립 검토, 롤백이 중요한 작업
- 반복 워크플로나 재현된 실패를 측정 가능한 프로젝트 범위 개선으로 바꾸려는 경우
- 낡은 구조를 계속 쌓지 않고 병합하거나 제거하고 싶은 설정

**아마 필요 없거나 맞지 않습니다.**

- 읽기 전용 질문이나 아주 작은 일회성 수정
- 명확한 로컬 작업 계약과 실행 가능한 완료 검사가 이미 충분한 작업
- 상시 실행 워크플로 엔진이나 호스팅 오케스트레이션 서비스가 필요한 경우
- 승인 없이 인증·배포·공개·외부 쓰기를 해야 하는 시스템
- 기반 모델의 추론 능력을 높이는 도구를 찾는 경우
- 가공하지 않은 개인 기억, 자동 전역 규칙, 승인 없는 프로젝트 간 학습이 필요한 경우

저장소가 작업에 필요한 조건을 이미 모두 갖췄다면 NULNUL을 쓰지 않아도 됩니다.

## 신뢰 경계와 확인된 한계

- 인증, 외부 쓰기, 배포, 공개, 파괴적 작업, 유료 자원 사용, 전역 등록에는 명시적인 승인이 필요합니다.
- 인증 정보, 원본 대화, 전체 명령 이력, 컴퓨터 경로, 비공개 프로젝트 데이터는 개선 이력으로 저장하지 않습니다.
- Personal Evolution에는 사용자가 직접 선택한 기존 로컬 디렉터리가 필요합니다. 실제 비공개 로컬 홈 하나가 검증을 통과했지만 그 경로는 공개 근거에 남기지 않았습니다.
- 무인 Claude Code 세션은 실행 환경이 소유한 `.claude/**` 설정을 확인할 수 있지만 다시 쓰지 않습니다.
- 빠른 재개 전에 체크포인트와 검사 범위에 해당하는 저장소 상태 지문을 비교합니다.
- 압축한 아카이브는 무결성을 확인하는 로컬 근거이며 일반 재개 컨텍스트에는 불러오지 않습니다.
- 독립 Gate의 책임 주체는 선언된 상태에서 확인하며 서로 다른 실행 주체를 암호학적으로 증명하지 않습니다.
- NULNUL은 기반 모델의 추론 한계를 없애거나 모든 에이전트 오류를 막지 않습니다.
- 미사용 사례 전이 하나와 실제 환경의 제한된 개선 실행 하나는 범용적이거나 하네스 전체에 적용되는 일반화를 증명하지 않습니다.
- 2.0 근거는 메커니즘 세 계열, 봉인된 선택 사례 세 개, 확인된 `COMPLEMENTS` 관계 하나, 실제 작업 주기 하나에만 해당합니다. 다른 관계는 `UNKNOWN`입니다. 임의의 프로젝트 교훈, 토큰·실행 시간 개선, 사용자 간 학습은 입증하지 못했습니다.
- 데몬, 재귀적으로 실행되는 Coach, 후보 집단, 호스팅 제어 계층, 무인 무한 반복은 없습니다.

<a id="현재-릴리스"></a>

## 현재 NULNUL 릴리스

현재 공개 버전은 2026년 8월 20일에 공개한 **v2.2.0**입니다.

- 스키마 v4의 잠정→확정 절차는 실제 작업 주기 하나가 문제없이 끝날 때까지 기존 확정 버전을 유지하고, 문제가 생기면 롤백을 기록합니다.
- 문서 부채 검사는 현재 실행 환경과 작업 트리 변경을 반영합니다.
- 릴리스 근거는 버전 문자열뿐 아니라 후보 산출물의 정확한 바이트와 연결됩니다.
- 주석이 붙은 릴리스 태그는 커밋 `14806e44bdc5bd2dbc3f2e52cea3b3799442d461`을 가리킵니다.
- 공개된 정확한 버전을 새로 설치한 Claude Code와 Meta Evolution 채택 검증은 보호 대상 쓰기, 권한 확대, 비공개 근거, 폐기한 홀드아웃 재사용 없이 통과했습니다.
- 동의·연속성 동작 후보는 **포함하지 않았습니다.** 엄격한 Gate가 `NO_PROMOTION`을 반환했기 때문에 Navigator는 v20을 유지하며 새로운 동의 처리나 일반 제품 작업 라우팅을 검증했다고 주장하지 않습니다.

전체 변경 이력은 [`CHANGELOG.md`](CHANGELOG.md)에서 확인할 수 있습니다.

<details>
<summary>이전 진화 단계</summary>

| 단계 | 상태 | 사용자에게 달라진 점 |
| --- | --- | --- |
| 1.4 Observable Evolution | 완료 | 그럴듯한 설명을 믿는 대신 하네스가 실패한 이유를 확인함 |
| 1.5 Generalization Gate | 완료 | 해결책이 다른 환경으로 옮겨가는지, 익숙한 사례에만 맞는지 구분함 |
| 1.6 Bounded Autonomous Evolution | 완료 | 고정한 예산 안에서 작은 후보 공간만 확인하고 근거가 약하면 바꾸지 않고 멈춤 |
| 1.7 Personal Evolution | 완료 | 프로젝트에서 검증한 메커니즘을 전이 근거, Personal Gate, 새 프로젝트 호환성 검사 뒤에만 재사용함 |
| 2.0 Cross-project / Meta Evolution | 공개 및 검증 완료 | 검증된 세 계열을 제한된 선택기에 연결해 같은 판단을 유지하며 전체 검사를 9회에서 4회로 줄임 |
| 2.0.1 실행 환경 소유권 | 공개 및 검증 완료 | Codex와 Claude Code를 순서대로 쓸 때 하나의 상태를 공유하되 각자 자신의 루트 진입 파일만 관리함. 동시 변경은 보장하지 않음 |
| 2.1 제한된 이력 | 공개 및 검증 완료 | 종료된 개선 근거를 일반 재개 컨텍스트 밖으로 옮기고도 전체 관계를 결정론적으로 복구함 |
| 2.1.1 문서 부채 | 공개 및 검증 완료 | 순서를 교차한 네 차례에서 같은 결과를 유지하며 검사 시간 중앙값을 98.70% 줄임 |
</details>

<a id="공개된-기술-자료와-평가-결과"></a>

## NULNUL 평가 결과와 기술 자료

제품 기본 기록:

- [동작 사례](evals/cases.json)와 [동작 결과](evals/results.json)
- [성능 근거](evals/benchmarks/performance.json), [활성화 근거](evals/benchmarks/activation/results.json), [문서 부채 A/B](evals/benchmarks/doc-debt/results.json)
- 거부된 [컨텍스트 라우팅 A/B](evals/benchmarks/context-routing/results.json)
- Generalization Gate [노출 목록](evals/generalization/manifest.json), [실패한 Ruby 근거](evals/generalization/results-ruby-failed.json), [Perl/TAP 결과](evals/generalization/results.json)

진화 기록:

- [1.6 실제 실행 사전 등록](evals/autonomous/live-1.6-preregistration.json)
- 1.7 [개인 전이 사전 등록](evals/personal-evolution/preregistration.json), [결과](evals/personal-evolution/results.json), [공개 채택 근거](evals/personal-evolution/public-adoption.json)
- 2.0 [Meta 사전 등록](evals/meta-evolution/preregistration.json), [형식화된 근거](evals/meta-evolution/cross-project-evidence.json), [Meta Gate 결과](evals/meta-evolution/results.json), [공개 버전 채택 근거](evals/meta-evolution/public-adoption.json)
- 2.0 이후 [기능 권한 `NO_ADVANTAGE`](evals/capability-authority/results.json), [의도·더 나은 경로 `NO_PROMOTION`](evals/intent-better-path/results.json), [결정 산출물 `NO_PROMOTION`](evals/decision-boundaries/results.json), [저장소 영수증 `NO_PROMOTION`](evals/repository-receipts/results.json)
- 2.2 동작 경계 [사전 등록](evals/behavior-boundaries/preregistration.json), [사례](evals/behavior-boundaries/cases.json), [정제된 거절 결과](evals/behavior-boundaries/results.json), 평가에서 제외한 [잘못된 첫 실행](evals/behavior-boundaries/invalid-evaluator-episode-1.json)

마지막 묶음은 공개 기능의 근거가 아니라 거절 기록입니다.

## 업데이트, 제거, 개발, 기여

Codex를 업데이트합니다.

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code를 업데이트한 뒤 다시 시작합니다.

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

마켓플레이스가 로컬 복제본을 가리킨다면 먼저 그 복제본을 갱신하세요. 그다음 새 에이전트 세션을 시작합니다. 프로젝트 지침과 `docs/nulnul/` 상태는 플러그인과 별개로 유지됩니다.

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

플러그인을 지워도 프로젝트 상태는 자동으로 지워지지 않습니다. 체크포인트나 개선 이력이 더 이상 필요 없을 때만 제거하세요.

로컬 변경을 검증합니다.

```bash
python3 scripts/pack_plugin.py
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/check_doc_debt.py . --host codex
```

릴리스 근거를 바꿨다면 전체 `test_*.py` 검사와 `python3 scripts/release_gate.py`도 실행합니다.

버그나 설정 불일치는 [GitHub 이슈](https://github.com/SeoNaRu/nulnul-harness/issues/new?template=bug_report.yml)에 남겨 주세요. 요청한 내용, 기대한 결과, 실제 결과만 적고 비공개 코드, 인증 정보, 원본 대화는 포함하지 마세요.

[`SUPPORT.md`](SUPPORT.md), [`PRIVACY.md`](PRIVACY.md), [`TERMS.md`](TERMS.md), [MIT 라이선스](LICENSE)도 확인할 수 있습니다.

## 연구 배경

NULNUL은 [GeekNews Weekly 353](https://news.hada.io/weekly/202615)에서 다룬 하네스 엔지니어링 문제에서 출발했습니다. 코딩 에이전트의 기능이 늘면서 사용자가 프로젝트마다 주변 시스템을 반복해서 구성하는 문제입니다.

편집 가능한 작업·메타 경계, 독립 검증, 기존 방식과 후보 방식의 비교, 평가를 통과해야 공개하는 절차가 설계에 영향을 줬습니다. [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) ([논문](https://arxiv.org/abs/2603.19461), [코드](https://github.com/facebookresearch/Hyperagents))는 작업과 메타 영역을 함께 개선하는 방식을 고민하는 데 중요한 참고 자료였습니다. NULNUL은 HyperAgents를 재현하거나 끝없는 자기 개선을 주장하지 않습니다.

<details>
<summary>측정된 개선 작업에 영향을 준 기술 자료</summary>

Observable Evolution은 [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850), Generalization Gate는 [Rethinking the Evaluation of Harness Evolution](https://arxiv.org/abs/2607.12227)의 영향을 받았습니다. 범위를 제한한 1.6 실행에는 [Gated Semantic Quality-Diversity](https://arxiv.org/abs/2607.13683), [Hierarchical Self-Improvement](https://arxiv.org/abs/2608.08466), [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621)의 아이디어 중 필요한 것만 사용했습니다.

연구는 더 나은 질문과 반증 방법을 줍니다. 저장소 안의 근거가 없으면 제품 기능으로 취급하지 않습니다. 정확한 계약은 [진화](plugins/nulnul-harness/skills/nulnul-harness/references/evolution.md), [메타 진화](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md), [개인 적응](plugins/nulnul-harness/skills/nulnul-harness/references/personal-evolution.md), [일반화](plugins/nulnul-harness/skills/nulnul-harness/references/generalization.md) 문서에 있습니다.
</details>

MIT © [SeoNaRu](https://github.com/SeoNaRu)
