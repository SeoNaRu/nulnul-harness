<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="300" alt="NULNUL 로고">
</p>

<h1 align="center">NULNUL Harness</h1>

<p align="center">
  <strong>OpenAI Codex와 Anthropic Claude Code를 위한 프로젝트 인식형 AI 코딩 하네스.</strong><br>
  원하는 결과만 말하세요. NULNUL은 현재 프로젝트에 필요한 기능만 불러오고, 실제 프로젝트 검사로 결과를 검증하고, 검증된 경험을 기억하며, 근거가 있을 때만 스스로의 구성을 바꿉니다.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-3.2.0-111111" alt="버전 3.2.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> ·
  <a href="#nulnul이-하는-일">하는 일</a> ·
  <a href="#검증-근거">검증 근거</a> ·
  <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.2.0">v3.2.0 릴리스</a>
</p>

<p align="center"><strong>결과 우선 · 실제로 검증 · 필요한 것만 유지</strong></p>

---

## 왜 NULNUL인가요?

AI 코딩 에이전트 자체는 강력하지만, 그 주변의 프로젝트별 설정은 쉽게 복잡해집니다. 규칙은 중복되고, 스킬은 계속 쌓이고, 컨텍스트는 오래되고, “완료”가 실제 테스트 통과가 아니라 모델의 판단으로 끝나기도 합니다.

NULNUL은 이 주변 레이어를 **프로젝트 기준 + 검증 근거 기준**으로 관리합니다.

| NULNUL 없이 | NULNUL과 함께 |
| --- | --- |
| 세션마다 프로젝트를 다시 설명 | 검증된 프로젝트 상태에서 이어서 작업 |
| 익숙한 규칙/스킬을 한꺼번에 로드 | 현재 작업에 필요한 기능만 선택 |
| 완료 메시지를 믿음 | 저장소의 실제 테스트·빌드·검증 명령 실행 |
| AI 설정을 계속 추가 | 근거가 있을 때만 유지·개선·교체·병합·은퇴·생성 |
| 채팅에서 과거 작업을 복원 | 검증된 Experience 중 관련 항목만 다시 사용 |

현재 프로젝트 설정이 이미 가장 강하게 정당화할 수 있는 경로라면 **아무것도 추가하지 않는 것이 올바른 결과**입니다.

---

## 빠른 시작

결과물부터 보고 싶다면 **[NULNUL in Action](examples/README.ko.md)**을 확인하세요. 로컬 예약 화면·API 데모, 합성 조사 데이터 워크북 예제, 기존 프로젝트의 3.1.0 도입 기록을 모았습니다. 사례마다 증거와 한계를 구분하며, 독립적으로 검증한 고객 프로젝트 3개나 새로운 성능 벤치마크를 의미하지 않습니다.

아래 설치 명령은 새 Claude·Meta 도입 검증을 통과한 공개 `v3.2.0`을 가리킵니다. 플러그인 명령을 지원하는 Codex 또는 Claude Code를 사용하고 호스트의 신뢰·권한 확인 절차를 따르세요. 버전을 고정한 설치는 이후 릴리스를 자동으로 따라가지 않습니다.

### OpenAI Codex

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref v3.2.0
codex plugin add nulnul-harness@nulnul-harness
```

### Anthropic Claude Code

```bash
claude plugin marketplace add 'https://github.com/SeoNaRu/nulnul-harness.git#v3.2.0'
claude plugin install nulnul-harness@nulnul-harness
```

처음 도입할 때는 기존 하네스가 있는 저장소에서도 다음처럼 요청하세요.

```text
기존 프로젝트 지침과 에이전트 역할을 보존하면서 이 저장소에 NULNUL을 설정해줘.
이어서 예약 API를 수정하고 기존 동작이 계속 통과하는지 확인해줘.
```

이미 NULNUL을 사용하는 프로젝트에서는 필요한 작업만 말하면 됩니다.

```text
예약 API를 수정하고 기존 동작이 계속 통과하는지 확인해줘.
```

이게 NULNUL의 기본 사용 방식입니다. 사용자가 직접 Skill을 고르거나, Session을 만들거나, Memory를 저장하거나, Agent 수를 정하거나, Evolution을 실행할 필요가 없습니다.

완전한 로컬 작업 계약이 이미 있는 요청은 Direct 경로로 처리할 수 있습니다. 플러그인을 설치했다고 모든 요청에 설정 작업이나 영구 Memory를 강제하지 않습니다.

이전 공개 버전에 고정되어 있다면 해당 호스트의 `codex plugin marketplace remove nulnul-harness` 또는 `claude plugin marketplace remove nulnul-harness --scope user`로 이전 참조를 제거한 뒤 위 설치 명령을 다시 실행하세요. 새 세션에서 프로젝트 지침과 역할을 보존하며 기존 NULNUL 설정을 업그레이드하도록 요청하세요. 패키지 갱신이 기존 프로젝트 진입 파일까지 자동으로 바꾸지는 않습니다.

기존 NULNUL 프로젝트에는 [3.0 기반 구조 업그레이드 안내](docs/upgrade-3.0.md)가 계속 적용되며, 3.2에서도 기존 체크포인트 형태는 바뀌지 않습니다. 직접 관리하는 Setup Plan이 있다면 확인한 기존 역할을 이름만 적지 말고 `이름: 분류`로 기록해야 합니다. 허용 값은 `reuse`, `kept`, `upgraded`, `merged`, `removed`이며, `kept`는 `reuse`로 정규화됩니다.

<details>
<summary>파일을 바꾸지 않고 미리 보기</summary>

```text
이 저장소를 확인하고 이 작업에 가장 강하게 정당화할 수 있는 경로를 보여줘.
무엇을 재사용하고 무엇을 제외할지, 이유와 함께 설명해줘. 파일은 수정하지 마.
```

</details>

---

<a id="nulnul이-하는-일"></a>

## NULNUL이 하는 일

### 1. 채팅이 아니라 프로젝트를 이어갑니다

NULNUL은 범위를 제한한 Session, handoff, Experience, Decision, Lesson, Open Thread 상태를 유지합니다. 다음 세션에서는 대화를 처음부터 재생하지 않고 **현재 작업과 관련된 검증된 Memory만** 복원합니다.

작업이 중간에 끊겨도 완료했다고 꾸미지 않고 복구 가능한 상태로 이어갑니다.

### 2. 작업에 맞는 Capability Pack을 만듭니다

작업을 시작하기 전에 결과 품질과 검증 가능성을 기준으로 가장 강하게 정당화되는 기능을 고릅니다. 결과가 실질적으로 동등한 경로 사이에서만 컨텍스트·조정·실행·유지보수·권한 비용이 더 낮은 구성을 선택합니다. 기능이나 에이전트 수 자체가 우선 목표는 아닙니다.

```text
작업
 ↓
프로젝트 + 관련 Memory
 ↓
Capability 선택
 ↓
Pre-Session Capability Pack
 ↓
작업 실행
```

명확한 Direct 작업에는 **capability body를 하나도 넣지 않습니다.** 필요한 작업에만 선택된 body가 들어갑니다.

### 3. 실제 프로젝트 검사로 결과를 확인합니다

NULNUL은 모델의 자신감을 완료 근거로 사용하지 않습니다.

```text
작업
 ↓
저장소 test / build / validation
 ↓
Authoritative Check receipt
 ↓
Verified Experience
```

중요한 것은 에이전트의 “잘 된 것 같습니다”가 아니라 프로젝트의 실제 검사 결과입니다.

### 4. 검증된 Experience를 기억합니다

검증된 작업 결과는 provenance와 함께 Experience로 남습니다. 다음 세션에서는 관련 Experience만 다시 사용할 수 있고, raw transcript 전체는 일반 Memory/Context에 들어가지 않습니다.

### 5. 근거가 있을 때만 진화합니다

NULNUL은 계속 자기 자신을 뜯어고치지 않습니다.

Capability lifecycle은 다음과 같이 판단할 수 있습니다.

```text
KEEP · UPGRADE · REPLACE · MERGE · RETIRE · CREATE
```

`KEEP`도 정상적인 Evolution 결과입니다. 검증된 약점이 없다면 현재 capability를 그대로 유지합니다.

외부 capability 비교, Agent topology 변경, Harness control 변경, cross-project prior도 모두 **증거가 생겼을 때만** 평가합니다.

---

## NULNUL 3.1 한눈에 보기

```text
사용자 작업
   ↓
SESSION + PROJECT CONTEXT
   ↓
관련 MEMORY
   ↓
AGENT TOPOLOGY 기회 판단
   ↓
CAPABILITY PACK
   ↓
작업
   ↓
권위 있는 검증
   ↓
EXPERIENCE
   ↓
MEMORY
   ↓
증거가 있을 때만 EVOLUTION
   ├─ Capability Natural Selection
   ├─ External Capability Competition
   ├─ Agent Evolution
   ├─ Guarded Harness Evolution
   └─ Cross-Project Generalization
```

**겉은 단순하게, 내부는 확인 가능하게.** 평범한 작업에서는 필요하지 않은 유지보수·진화 시스템을 불러오지 않습니다.

---

## 실제 사용 예시

사용자:

```text
import API에 validation을 추가하고 기존 error contract는 유지해줘.
```

NULNUL은 필요하다면 다음과 같이 처리합니다.

1. 현재 프로젝트 계약과 검사를 확인합니다.
2. 관련 Memory만 복원합니다.
3. 프로젝트 API validation capability를 선택합니다.
4. 작업 전에 해당 capability를 준비합니다.
5. 코드를 수정합니다.
6. 저장소의 권위 있는 validation 명령을 실행합니다.
7. 검증된 Experience를 저장합니다.
8. 이후 정말 관련 있을 때만 해당 Experience를 다시 사용합니다.

사용자는 여전히 하나만 요청했습니다. **원하는 제품 결과**입니다.

---

## 다른 AI 코딩 도구와 무엇이 다른가요?

NULNUL은 Agent 팀 생성기, 거대한 프롬프트 묶음, Hosted orchestrator가 아닙니다.

| 도구 유형 | 흔한 기본값 | NULNUL 기본값 |
| --- | --- | --- |
| Agent 팀 생성기 | 역할 여러 개 생성 | 직접 실행이 결과 면에서 경쟁력 있으면 재사용하고, 실질적인 결과 가치가 있을 때 제한된 역할 추가 |
| Prompt / Rule bundle | 준비된 지침 로드 | 현재 저장소를 먼저 보고 작업에 맞는 capability만 선택 |
| Memory layer | 대화/컨텍스트 보존 | raw chat 대신 범위를 제한한 검증된 프로젝트 Memory 유지 |
| Hosted orchestrator | 원격 서비스에서 workflow 실행 | repository-local, 별도 서버/daemon 불필요 |
| Capability marketplace | 더 많은 capability 탐색/설치 | 검증된 프로젝트 필요가 있을 때만 후보 비교 |
| NULNUL | — | 작업 완료 → 검증 → Experience → 필요할 때만 진화 |

---

## 불필요하게 변하지 않는 Evolution

NULNUL 3.1은 “자가개선”을 하나의 자유로운 자기수정으로 취급하지 않습니다.

### Capability Natural Selection

프로젝트 capability는 유지, 업그레이드, 교체, 병합, 은퇴하거나 검증된 공백이 있을 때 새로 생성될 수 있습니다.

### External Capability Competition

외부 후보는 **신뢰하지 않은 상태**로 quarantine한 뒤 평가합니다. 존재한다는 이유만으로 일반 Pack 선택에 들어오지 않습니다.

3.1의 오프라인 준비 도우미는 검토하고 리비전을 고정한 공개 Skill 파일을 기존 로컬 디렉터리 기반 격리 경로에 맞게 준비합니다. 후보를 다운로드·설치하거나 자동으로 채택하지 않으며, “인터넷에서 최고의 Skill을 자동으로 찾는다”는 주장도 하지 않습니다.

### Agent Evolution

Agent topology는 **누가 어떤 실행 책임을 가지는지**를 다룹니다. 직접 실행이나 단일 에이전트가 결과 면에서 경쟁력이 있으면 우선합니다. 추가하는 역할은 전문성·컨텍스트 분리·병렬 작업·독립 검증을 실질적으로 개선해야 하며, 최종 종합 책임자는 한 명으로 유지합니다.

### Guarded Harness Evolution

NULNUL은 Guarded Kernel과 진화 가능한 control policy를 분리합니다. 증거가 있으면 제한된 control tuning/replacement를 제안할 수 있지만, 후보가 자기 증거·승격 결과·provenance·authority·rollback 규칙을 바꿀 수는 없습니다.

### Cross-Project Generalization

교차 프로젝트 재사용은 선택 사항이며, 사용자가 선택하고 승인한 기존 로컬 개인 적응 저장소(Personal Home)가 필요합니다. 프로젝트끼리 raw Memory를 복사하지 않습니다. 출처와 적용 조건을 갖추고 개인정보를 제거한 추상적 사전 지식만 후보가 될 수 있으며, 대상 프로젝트의 사실이 항상 우선하고 호환성과 대상 검증이 필요합니다. 공개 Meta 도입 근거는 동결된 선택기와 제한된 사례를 검증한 것이지, 보편적인 전이나 모든 Generalization 경로의 실사용을 증명한 것은 아닙니다.

---

<a id="검증-근거"></a>

**3.2.0:** 작업에 맞춘 진입 지침, 실행 가능한 호스트 재개 명령, 설치 파일 전체 비교, 검증된 설정 영수증 재사용, 체크포인트 검증 보강, 제한된 Trace 관측을 포함합니다.

| 현재 릴리스 근거 | 확인한 결과 |
| --- | --- |
| [저장소·실제 프로젝트 검사](evals/release-3.2.0-validation.json) | 저장소 검사 **481/481 통과**. 설명만 바꾼 설정 두 건에서 완료 검사를 추가 실행하지 않았고, 검토한 Trace 수정도 원본 프로젝트에서 통과했습니다. |
| [공개 Claude 도입](evals/benchmarks/claude-adopt/release-3.2.0-r1.json) | 첫 새 세션에서 **검사 5/5 통과**. 기존 역할 두 개와 비활성 Codex 진입 파일을 보존하고 상태 기록자를 하나로 유지했습니다. 보호 경로 쓰기는 0건입니다. |
| [공개 Meta 도입](evals/meta-evolution/release-3.2.0-meta-r1.json) | 같은 적응을 flat 검사 3회, Meta 검사 1회로 선택했습니다. 비해당·충돌·마이그레이션·재개·롤백이 통과했고, 추가 모델 호출이나 폐기한 holdout 재사용은 없습니다. |
| [공개 Release Gate](scripts/public_release_gate.py) | **100/100, `release_ready=true`**. [후보 CI](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34445729753)와 [태그 CI](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34445849457)가 통과했습니다. |

공개 ZIP은 제품 커밋 `59d366f7df3a6f0633317d563786caa6893ec109`의 **65개 파일, 255,448바이트**입니다. 내려받은 ZIP·릴리스 소스·Claude 설치 파일이 일치합니다. SHA-256: `95611e2f603c31f05d3be35b62aafa541b2ce86e93e2c27dfb050cf92f872bcb`.
제한된 검증이며 보편적 라우팅 보장이나 모델 간 성능 우위·전체 실행 비용 절감을 뜻하지 않습니다. 이전 비통과와 동결된 3.1.0 근거는 그대로 보존합니다.

스킬 진입 문서는 기존 계약으로 충분한 일반 작업을 먼저 처리하고, 설치·연속 작업·전문 워크플로·진화 절차를 필요할 때 연결하도록 정리했습니다. 설명은 244자, 진입 문서는 약 1,026단어이며 문서 크기를 뜻할 뿐 실행 성능 개선 수치는 아닙니다. 필수 권한·검사 책임과 검증된 체크포인트의 읽기·검사 범위는 유지했습니다. 이번 사용자 요청에 따른 문서 정리는 아래 종료된 실험과 별개입니다.

현재 로컬 유지보수에서는 세부 개발 규칙을 [조건부 개발 계약](docs/development-contract.md)으로 옮겨 기본 개발 지침도 615단어로 정리했습니다. 체크포인트 재검사 시작 전에 과거 검증을 무효화하고, 잘못된 필드를 거부하며, 상태 조회에서 본문 로드의 식별자·순서를 확인합니다. Git 이력이 없을 때의 문서 검사는 한 번만 순회합니다. [재현과 검증 기록](docs/runtime-maintenance.md)에 범위를 정리했으며, 기존 공개 채택 결과가 이 변경을 인증하지는 않습니다.

후속 [설치 사본·실제 사용 검증](docs/live-use-validation.md)에서는 오래된 로컬 캐시를 갱신하고, 실제 영수증 버전 검사 결함을 수정한 뒤 새 Codex 세션에서 중단된 검사를 복구했습니다. 각 세션은 완료 검사를 한 번 실행해 12개 검사를 모두 통과했습니다. 두 세션 모두 체크포인트 검증 전 파일 목록 조회가 남았고, 효과가 없던 문서 순서 변경은 복원했으므로 빠른 재개 규칙 준수나 비교 속도 개선은 주장하지 않습니다.

[세 가지 후속 업그레이드](docs/live-use-validation.md#follow-up-all-three-requested-upgrades)에서는 실행 가능한 호스트 진입 명령과 설치 파일 전체 비교를 추가했습니다. 새 문서·버그 수정 세션 두 건은 탐색 전에 체크포인트를 검증하고 완료 검사를 한 번 실행했으며, 중단된 검사도 복구했습니다. 로컬 전용 도입은 목록 조회 조건을 보완한 뒤 기존 코드와 역할을 보존했습니다. 전체 로컬 검사 476개가 통과했습니다. 별도 스킬 로드와 도입 후 추가 검사는 한계로 남기며 비교 속도 개선이나 공개 릴리스 완료는 주장하지 않습니다.

[지침 라우팅 평가](docs/instruction-routing.md)는 모델 8회 시도 후 NO_PROMOTION으로 종료했습니다. 첫 평가기는 무효 처리했고, 수정 평가기에서도 후보의 미확인 실행 기록 때문에 합격 근거가 부족했습니다. 이번 제품·지침 변경은 복원했으며, 검증된 로컬 평가기 수정과 기각 근거만 남겼습니다. 아래 동결된 3.1.0 근거는 그대로 유지합니다.

## 3.1에서 추가된 기능

공개된 **3.1.0** 기준 버전은 아래 검증을 통과했습니다. 3.0 상태 형식, 빠른 재개, 기존 수용 권한, skills-only 경계를 유지하면서 여섯 가지 작업 실행 기능을 추가했습니다.

1. [경계면 QA](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): 실제 생산자와 소비자를 함께 확인하고, 단계별 통합 검사와 재현 가능한 부정 대조군을 유지합니다.
2. [업무별 절차](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-recipes.md): 웹/API 변경, 데이터 마이그레이션·동기화, 근거 기반 조사를 다룹니다.
3. [실행 패턴](plugins/nulnul-harness/skills/nulnul-harness/references/workflow-delivery.md): 기존 역할과 인계를 사용하는 조건부 패턴 6개이며 필수 팀이나 고정 모델을 강제하지 않습니다.
4. [부분 재실행](plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py): 영향을 받는 의존 관계를 재실행하고 현재 계약·입출력 지문이 일치하는 검증 결과만 재사용합니다.
5. [스킬 수용 사례](plugins/nulnul-harness/skills/nulnul-harness/references/skill-acceptance.md): 실제 사용·유사하지만 제외할 요청·후속 요청을 권위 있는 검사 참조와 함께 기록합니다.
6. [오프라인 후보 준비](plugins/nulnul-harness/skills/nulnul-harness/references/external-candidate-preparation.md): 검토한 고정 리비전의 스킬을 다운로드·설치·채택 승인 없이 기존 격리·경쟁 경로에 준비합니다.

필요한 참조만 읽습니다. 계획 영수증과 개발 점수는 보조 자료이며 Foundation 증거, 승격 권한, 비공개 최종 평가, 실사용 품질 향상의 증명이 아닙니다. 새로운 상태 마이그레이션은 필요하지 않습니다.

공개 도입에서 확인한 세 공백을 수정했습니다: [설치된 플러그인의 초기 설정](evals/benchmarks/claude-adopt/release-3.1.0-failure.json), [최초 설정의 설치 목록·문서 완료 조건](evals/benchmarks/claude-adopt/release-3.1.0-r2-failure.json), [역할별 명시적 분류](evals/benchmarks/claude-adopt/release-3.1.0-r3-failure.json)입니다. 설정 영수증은 프로젝트·호스트·실행 패키지 지문에 묶이며, 트랜잭션은 누락·중복·모호하거나 알 수 없는 역할 분류를 거부합니다. 별도 스킬 복사본·추가 상태 writer·보호 경로 쓰기·체크포인트 마이그레이션은 필요하지 않습니다. 검증 기준을 완화하지 않고 [새 프로젝트의 네 번째 공개 실행이 통과했습니다](evals/benchmarks/claude-adopt/release-3.1.0-r4.json). 앞선 실패와 프리릴리스 패키지는 보존하며, 이 실행들은 릴리스 회귀 검증이지 비공개 최종 평가나 보편적인 품질 향상 benchmark가 아닙니다.

```bash
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/workflow_delivery.py demo
```

## 검증 근거

아래 결과는 **2026-09-08에 공개한 동결된 3.1.0 릴리스**의 검증 근거이며, 이후의 모든 작업 폴더 변경을 검증한 것은 아닙니다. 검사 수는 깨끗한 배포 트리를 기준으로 합니다. 새 실행 도우미는 결정론적으로 검증했지만 실사용 품질 우위를 주장하지 않습니다.

| 근거 | 결과 | 무엇을 보여주나 |
| --- | --- | --- |
| [Repository test suite](tests/) | **446개 통과 (446개 검사)** | 깨끗한 릴리스 기준으로 실행 도우미·후보 준비·두 호스트의 설치 플러그인 초기 설정·역할별 분류와 음성 대조군을 검증했습니다. 임의로 변경한 로컬 작업 폴더까지 통과를 보장하지는 않습니다. |
| [Release Gate](scripts/release_gate.py) | **100/100 PASS** | 정확한 버전의 공개 도입 증거를 포함해 `release_ready=true`. |
| [공개 Claude 도입](evals/benchmarks/claude-adopt/release-3.1.0-r4.json) | **PASS, 5/5 검사** | 설치 목록 확인·역할 분류·검증된 체크포인트·원래 작업 완료·문서 최신성, 기존 프로필과 비활성 Codex 진입점 보존, 보호 경로 쓰기 0건. |
| [공개 Meta 도입](evals/meta-evolution/release-3.1.0-meta-r4.json) | **PASS** | 같은 적용 대상을 flat 검사 3회 대신 Meta 검사 1회로 선택. 해당 없음·충돌·마이그레이션·롤백 대조군 통과. 동결된 선택기와 이번 새 도입 사례에 한정합니다. |
| [NULNUL 3.1.0 릴리스](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0) | **공개 패키지 검증 완료** | 제품 동결 커밋 `a9fd59e8c5852e8808f6698262e90d389f39f42a`; [태그 CI 통과](https://github.com/SeoNaRu/nulnul-harness/actions/runs/34212367385). |
| `nulnul-harness-3.1.0.zip` | **60개 파일, 237,942바이트** | 재현 가능한 패키지이며 공개 다운로드와 실제 설치 파일이 일치합니다. |
| Release archive SHA-256 | `7716a8ddfeb43632b4ad836c29deb1fd2981a84d423d2f2705fb88becad9e49d` | 동결된 패키지 식별자. |

이전에 동결한 live Direct pair 하나에서는 명확한 Direct 작업에 capability body 0개를 유지하면서 프로젝트가 선호한 `<=120%` input 목표 안에 들어왔습니다. 이는 과거의 제한된 측정 근거이며, 새로운 3.1 실사용 benchmark나 보편적인 성능 보장이 아닙니다.

### 증거를 구분합니다

- **Live proven:** 핵심 Session/Pack/Check/Experience/Memory continuity와 Skill `KEEP` 경로.
- **구현 + deterministic validation:** non-KEEP capability lifecycle, Agent Evolution, Harness Evolution, Generalization 같은 더 넓은 lifecycle mechanics.
- **주장하지 않음:** 전역 최적 capability, multi-Agent의 보편적 우월성, 무제한 재귀 self-evolution, 모든 프로젝트에 통하는 best practice.

<details>
<summary>과거 v2.2 / v2.3 연구 결과</summary>

과거 Project-Fit 실험은 exact v2.2.1보다 우위를 증명하지 못했고 `v2.3 NOT READY`를 명시적으로 기록했습니다. 그 실패가 3.0의 bounded Direct 경로, Pre-Session Capability Pack, deterministic verification receipt, Experience/Memory, evidence-gated evolution, runtime-exclusive activation 폐기로 이어졌습니다.

자세한 기록:

- [Post-2.2.1 proof decision](docs/roadmap/post-2.2.1-proof-decision.md)
- [Baseline findings](docs/roadmap/post-2.2.1-baseline-findings.md)
- [Meta HyperAgents](https://ai.meta.com/research/publications/hyperagents/)
- [GeekNews Weekly 2026-15](https://news.hada.io/weekly/202615)

과거 실패 증거는 남겨두되 현재 제품 상태처럼 보이지 않도록 분리했습니다.

</details>

---

## 안전성과 개인정보

NULNUL 3.1은 중요한 경계를 명시적으로 유지합니다.

- **Repository-local:** NULNUL용 서버나 daemon이 필요하지 않습니다.
- **Raw evidence는 local-only:** raw transcript/runtime event는 일반 durable Memory가 아닙니다.
- **프로젝트 Memory 격리:** cross-project transfer는 source Memory 복사가 아니라 abstract prior를 사용합니다.
- **외부 후보 quarantine:** discovery가 authority를 부여하거나 신뢰하지 않은 설치 동작을 실행하지 않습니다.
- **Capability context ≠ authority:** Skill을 불러왔다고 구조적 프로젝트/Harness 쓰기 권한을 얻지 않습니다.
- **권위 있는 검증:** 모델이 쓴 성공 문장이 deterministic check receipt를 대신하지 않습니다.
- **Transactional mutation:** lifecycle 변경은 검증·provenance·rollback을 거칩니다.
- **Host trust는 사용자/host 소유:** NULNUL이 몰래 trust를 가져가지 않습니다.

전체 경계는 [SECURITY.md](SECURITY.md), [PRIVACY.md](PRIVACY.md)를 확인하세요.

---

## 프로젝트에 어떤 파일을 추가할 수 있나요?

NULNUL은 이미 존재하는 프로젝트를 우선 재사용합니다. Durable state도 실제 역할이 있을 때만 추가합니다.

대표적인 managed surface:

- 활성 host를 위한 `AGENTS.md` 또는 `CLAUDE.md` managed guidance
- 안정적인 프로젝트 사실과 check를 위한 `docs/nulnul/project.md`
- `docs/nulnul/` 아래의 bounded checkpoint / Session / Experience / Memory state
- 현재 capability ecosystem이 작업을 커버하지 못할 때만 project-local Skill

활성 호스트의 진입점만 수정합니다. Codex는 `AGENTS.md`, Claude Code는 `CLAUDE.md`를 소유합니다. 다른 호스트를 순차적으로 도입해도 비활성 진입점은 보존하고, 같은 공유 계약과 하나의 상태 writer를 재사용합니다. 두 호스트가 공유 상태를 동시에 수정하는 것은 지원하지 않습니다.

기반 구조의 마이그레이션과 소유권 규칙은 [3.0 업그레이드 안내](docs/upgrade-3.0.md)에 계속 적용됩니다.

---

## 내부를 확인하고 싶다면

일반 사용은 작게 유지하면서 내부 판단은 확인할 수 있게 설계했습니다.

고급 사용자는 다음을 확인할 수 있습니다.

- 왜 이 capability가 선택됐는가?
- 어떤 프로젝트 Check가 실행됐는가?
- 어떤 verified Experience가 저장됐는가?
- 다음 Session에서 어떤 Memory가 복원됐는가?
- 왜 Evolution이 변경 대신 `KEEP`을 선택했는가?
- 어떤 capability / Agent / Harness 버전이 결과를 만들었는가?

Durable record는 provenance로 연결되며, 일반 inspection을 위해 raw transcript 전체를 읽을 필요가 없습니다.

---

## 현재 한계

NULNUL 3.1은 기록된 증거보다 더 큰 주장을 하지 않습니다.

- Skill `KEEP` lifecycle은 live evidence가 있지만 자연 발생한 live Skill `UPGRADE`는 아직 공개 증거에서 관찰되지 않았습니다.
- External Capability Competition은 bounded source/quarantine mechanics가 구현되어 있지만 인터넷 전체에서 최고의 capability를 찾는다고 주장하지 않습니다.
- Agent Evolution mechanics는 구현되어 있지만 multi-Agent가 Single-Agent보다 항상 낫다고 주장하지 않습니다.
- Harness Evolution은 first-order guarded evolution이며 무제한 recursive self-evolution은 지원하지 않습니다.
- Cross-Project Generalization은 privacy-gated되어 있지만 보편적 transferability를 주장하지 않습니다.
- Codex와 Claude Code는 host-independent core record를 공유해도 실제 기능 깊이는 다를 수 있습니다.

이 한계들은 숨겨진 TODO가 아니라 현재 제품의 명시적인 경계입니다.

---

## 아키텍처 자세히 보기

<details>
<summary>핵심 레이어</summary>

```text
Project Model
Session / Task
Context Assembly
Capability Selection
Pre-Session Capability Pack
Agent Topology
Verification
Observability
Experience
Memory
Provenance
Natural Selection
External Competition
Agent Evolution
Guarded Harness Evolution
Cross-Project Generalization
```

Stateful layer에는 identity와 provenance가 명시적으로 연결됩니다. 일반 작업은 maintenance stack 전체를 로드하지 않습니다.

</details>

<details>
<summary>Evolution lifecycle</summary>

```text
Verified Experience
        ↓
Evidence review
        ↓
약점 없음? ─────────────→ KEEP
        ↓
정당화된 변경
        ↓
Frozen Challenger
        ↓
Champion vs Challenger
        ↓
Verification + holdout + rollback gate
        ↓
승격 또는 거절
```

모델은 의미적인 변경안을 제안할 수 있지만 identity, digest, evidence validation, promotion state, provenance, rollback은 deterministic runtime이 소유합니다.

</details>

---

## 릴리스와 업그레이드

- 현재 패키지: [NULNUL 3.2.0](submission/release-notes.md). 정확한 버전의 공개 Claude·Meta 도입 검증을 통과했습니다.
- 검증된 기준 버전: [NULNUL 3.1.0](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.1.0)
- 업그레이드: [docs/upgrade-3.0.md](docs/upgrade-3.0.md), 3.1에서도 기존 체크포인트 형태 유지
- 변경 내역: [CHANGELOG.md](CHANGELOG.md)
- 보안: [SECURITY.md](SECURITY.md)
- 개인정보: [PRIVACY.md](PRIVACY.md)

---

## License

MIT — [LICENSE](LICENSE).


## NULNUL + Trace: 결과를 설명할 수 있는 실행 근거

로컬 실행 검증을 통과한 연동 후보이며, 공개된 v3.1.0의 고정 릴리스 근거에 포함되지 않습니다.
NULNUL은 기존 런타임 기록에 민감정보를 제외한 버전 명시형 근거를 추가하여
[NULNUL Trace](https://github.com/SeoNaRu/nulnul-trace)에 전달합니다.
차별점은 로그의 양이 아니라 **능력 선택 -> 실제 본문 로드 -> 작업 -> 공식 검증 -> 작업 결과**를
소스 다이제스트와 함께 연결한다는 점입니다.

Trace는 프로젝트 설정과 실제 사용을 구분하고, 영수증·파일·검증 명령의 유효성을 확인하며,
검증된 결과와 근거 부족, 제한된 비용 신호를 표시합니다. 별도 모델 호출, 원문 대화 전송,
하네스 상태 수정, 비교 없는 개선율 주장은 하지 않습니다. 토큰 절감과 새 세션 재개 성공은
아직 미측정입니다. [근거 계약](plugins/nulnul-harness/skills/nulnul-harness/references/trace-evidence.md)을 참고하세요.

### Trace에서 하네스가 하는 일 보기

1. 업데이트된 Harness 생산자 코드로 새 Foundation 작업을 실행합니다. 설정만 하거나 이전 세션을 여는 것으로 실행 근거가 생기지 않으며, 기존 설치 플러그인이 자동으로 갱신되지는 않습니다.
2. 대응하는 Trace API·웹·수집기를 실행합니다. DB를 업데이트할 때는 기존 `pnpm db:push` 명령으로 추가 테이블을 적용합니다.
3. 세션 티켓에서 **하네스가 한 일**를 펼치고 **이번 세션** 또는 **이 프로젝트**를 선택합니다. 능력 선택·본문 로드·영수증 연결 결과는 구분해서 표시합니다.

### 로컬 검증 결과 (2026-09-09)

- Trace 테스트 **71/71 통과**(도메인 48/48, 수집기 23/23). API·웹 빌드도 통과했습니다.
- 결정적 연동 검증에서 공식 런타임 이벤트 12개, 작업 1개, 영수증 연결 통과 1건이 수집기·API·브라우저까지 전달됐습니다. 세션·프로젝트 범위, 영수증 출처, 모바일 너비 390px 표시를 확인했습니다.
- API 음성 대조군 통과: 재전송 중복 방지, 잘못된 프로젝트·세션, 민감정보 필드 거부, 인증 누락, 다른 기기의 세션·프로젝트 접근 차단.
- Harness 작업 공간은 **447/448 통과**입니다. 남은 제품 경계 실패는 기존 `docs/research` 디렉터리이며, 통과를 만들기 위해 삭제하거나 검사에서 제외하지 않았습니다.
- 별도 공개 기준 복사본은 448개 테스트 중 실패 5개·오류 6개로 전체 통과하지 못했습니다. 고정 근거의 소스 식별 불일치 등이 포함되며, 깨끗한 릴리스 검증으로 취급하지 않습니다.
- 문서 부채 검사는 통과했습니다. Release Gate는 변경된 생산자 코드에 맞는 공개 Claude·교차 프로젝트 Meta 채택 근거가 없어 여전히 `release_ready: false`입니다.
- 합성 데이터와 임시 DB 스키마로 진행한 검증이며 실제 사용자·모델 실험이 아닙니다. 임시 서버·스키마는 제거했고 기존 세션은 건드리지 않았습니다. 추가 모델 호출 **0회**. 전역 플러그인 갱신·푸시·릴리스는 하지 않았습니다.

### 요청 중심 연동 갱신 (2026-09-09)

Trace 첫 화면을 사용자 요청별 결과·검증·다음 행동으로 바꿨습니다. **하네스가 한 일**은 연결됨·기록 없음·이전 형식·세션 미연결을 구분하며, `nulnul-trace doctor`로 로컬 원인을 확인합니다. 이번에 명시적으로 요청한 연동 작업을 위해 로컬 Codex 설치 플러그인도 갱신했습니다.

이 코딩 세션의 실제 작업에서 `trace-core-purity`를 선택하고 본문을 로드한 뒤 Foundation 검사 통과 영수증이 실행 중인 수집기·API·브라우저에 도착했습니다. 앞서 중단된 시작 기록은 부분 관측으로 남겼습니다. 실제 개발 실행 한 건이며 통제된 모델 비교나 절감 효과의 근거는 아닙니다.

소스 상태 확인은 Git 추적 파일과 무시되지 않은 미추적 파일을 사용하며, 무시 규칙에 걸려도 추적 중인 파일은 유지합니다. 의존성·빌드 폴더 때문에 시작 단계가 전체 작업 트리를 훑던 문제를 해결했습니다. 로컬 Trace에서 다이제스트 계산만 약 2.1초였으며 전체 실행 성능 측정은 아닙니다. 회귀 검사 2개를 추가했습니다. 다시 패키징한 뒤 Harness 전체 검사는 **449/450 통과**이며 기존 `docs/research` 제품 경계 실패만 남았습니다. 공개 릴리스의 고정 근거는 변경하지 않았습니다.

## 3.2의 작동 상태 확인

Trace를 열지 않고도 NULNUL이 무엇을 하는지 확인할 수 있습니다. 읽기 전용 상태 명령은
개발 소스·명시적으로 검사한 설치 사본·호스트 세션 연결·작업 상태·능력 선택과 기록된 이유·
변경 내용·검증 근거를 구분합니다.

~~~bash
python3 plugins/nulnul-harness/skills/nulnul-harness/scripts/harness_status.py --root . --lang ko
~~~

호스트가 실제 세션 키를 제공합니다. 연결 미확인은 미작동 판정이 아니며, 과거 기록 조회는
현재 실행의 증거가 아닙니다. 플러그인이 설치·활성화되어 있어도 이미 열린 스레드가 최신
스킬 본문을 읽었다고 단정하지 않습니다. 검사 종료 기록과 검증된 과거 영수증도 구분합니다.
알림·추가 모델 호출·전역 설치·두 번째 상태 기록기를 추가하지 않습니다.

기존 연구자료는 삭제하지 않고 제품 밖에 보존합니다. 패키징은 배포 플러그인 안의 과거
실험실 경로와 심볼릭 링크를 거부하며, 아카이브 타임스탬프·권한 정규화는 유지합니다.

로컬 근거 검사와 공개 허용 판정은 다른 명령입니다.

~~~bash
python3 scripts/release_gate.py
python3 scripts/public_release_gate.py
~~~

두 번째 명령은 `release_ready`가 정확히 true가 아니면 실패합니다. main과 main 대상 PR에는
엄격한 판정을, non-main 후보에는 로컬 근거 검사를 적용합니다. 변경된 후보를 인증된 것처럼
보이게 하려고 고정된 판정기나 과거 채택 근거의 해시를 덮어쓰지 않습니다.

업데이트한 후보는 전체 저장소 검사 481개를 통과했습니다. 실제 Trace 프로젝트에서는 따옴표로 감싼 검증 경로 인식을 수정했고, 검토한 두 파일을 반영한 원본 작업 폴더의 완료 검사도 통과했습니다. 새 세션의 설명 변경 도입에서는 두 번의 설정 처리 모두 기존 영수증을 재사용해 완료 검사를 추가 실행하지 않았고, 최초 중복 실행 실패 기록도 보존했습니다. 정확한 공개 3.2.0 Claude·Meta 도입도 통과했으며, 릴리스 근거는 이 로컬 관찰과 구분합니다. 비교 우위를 주장하지 않습니다.
