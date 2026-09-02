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
  <img src="https://img.shields.io/badge/version-3.0.0-111111" alt="버전 3.0.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

<p align="center">
  <a href="#빠른-시작">빠른 시작</a> ·
  <a href="#nulnul이-하는-일">하는 일</a> ·
  <a href="#검증-근거">검증 근거</a> ·
  <a href="https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0">v3.0.0 릴리스</a>
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

### OpenAI Codex

```bash
codex plugin marketplace add SeoNaRu/nulnul-harness --ref main
codex plugin add nulnul-harness@nulnul-harness
```

### Anthropic Claude Code

```bash
claude plugin marketplace add SeoNaRu/nulnul-harness
claude plugin install nulnul-harness@nulnul-harness
```

설치한 다음 그냥 작업을 말하면 됩니다.

```text
예약 API를 수정하고 기존 동작이 계속 통과하는지 확인해줘.
```

이게 NULNUL의 기본 사용 방식입니다. 사용자가 직접 Skill을 고르거나, Session을 만들거나, Memory를 저장하거나, Agent 수를 정하거나, Evolution을 실행할 필요가 없습니다.

기존 NULNUL 프로젝트를 업그레이드한다면 먼저 [NULNUL 3.0 업그레이드 안내](docs/upgrade-3.0.md)를 확인하세요.

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

작업을 시작하기 전에 현재 프로젝트와 Memory를 보고 필요한 기능만 고릅니다.

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

## NULNUL 3.0 한눈에 보기

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
| Agent 팀 생성기 | 역할 여러 개 생성 | 한 실행 경로에서 시작하고 실제 가치가 있을 때만 topology 추가 |
| Prompt / Rule bundle | 준비된 지침 로드 | 현재 저장소를 먼저 보고 작업에 맞는 capability만 선택 |
| Memory layer | 대화/컨텍스트 보존 | raw chat 대신 범위를 제한한 검증된 프로젝트 Memory 유지 |
| Hosted orchestrator | 원격 서비스에서 workflow 실행 | repository-local, 별도 서버/daemon 불필요 |
| Capability marketplace | 더 많은 capability 탐색/설치 | 검증된 프로젝트 필요가 있을 때만 후보 비교 |
| NULNUL | — | 작업 완료 → 검증 → Experience → 필요할 때만 진화 |

---

## 불필요하게 변하지 않는 Evolution

NULNUL 3.0은 “자가개선”을 하나의 자유로운 자기수정으로 취급하지 않습니다.

### Capability Natural Selection

프로젝트 capability는 유지, 업그레이드, 교체, 병합, 은퇴하거나 검증된 공백이 있을 때 새로 생성될 수 있습니다.

### External Capability Competition

외부 후보는 **신뢰하지 않은 상태**로 quarantine한 뒤 평가합니다. 존재한다는 이유만으로 일반 Pack 선택에 들어오지 않습니다.

현재 3.0의 외부 source 지원은 의도적으로 bounded되어 있으며, “인터넷에서 최고의 Skill을 자동으로 찾는다”는 주장은 하지 않습니다.

### Agent Evolution

Agent topology는 **누가 어떤 실행 책임을 가지는지**를 다룹니다. 기본은 Agent 하나입니다. 여러 Agent를 쓰는 구조는 coordination cost를 상쇄할 실제 검증 가치가 있어야 합니다.

### Guarded Harness Evolution

NULNUL은 Guarded Kernel과 진화 가능한 control policy를 분리합니다. 증거가 있으면 제한된 control tuning/replacement를 제안할 수 있지만, 후보가 자기 증거·승격 결과·provenance·authority·rollback 규칙을 바꿀 수는 없습니다.

### Cross-Project Generalization

프로젝트끼리 raw Memory를 공유하지 않습니다. provenance와 적용 조건을 가진 privacy-safe abstract prior만 전달하며, target project truth가 항상 우선입니다. target validation을 통과해야 target project의 실제 지식으로 사용할 수 있습니다.

---

<a id="검증-근거"></a>

## 검증 근거

NULNUL의 공개 주장은 내부 아키텍처보다 의도적으로 좁게 잡습니다.

| 근거 | 결과 | 무엇을 보여주나 |
| --- | --- | --- |
| [Repository test suite](tests/) | **431/431 PASS** | Foundation, Pack, verification, Memory, lifecycle, privacy, rollback, evolution, migration, release contract |
| [Release Gate](scripts/release_gate.py) | **100/100 PASS** | 동결된 3.0.0 제품의 release integrity |
| [NULNUL 3.0.0 release](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0) | **Stable release published** | 공개 `v3.0.0` 태그와 릴리스 |
| `nulnul-harness-3.0.0.zip` | **53 files · 220,223 bytes** | 재현 가능한 release archive |
| Release archive SHA-256 | `99fd14bef3432f1542270cbdd8640f0a185d319cafcf054505b37260bc9335c1` | 동결된 artifact identity |

동결된 live Direct pair 하나에서는 명확한 Direct 작업에 capability body 0개를 유지하면서 프로젝트가 선호한 `<=120%` input 목표 안에 들어왔습니다. 이 수치는 해당 증거 범위에만 해당하며 보편적 성능 보장은 아닙니다.

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

과거 실패 증거는 남겨두되 현재 제품 상태처럼 보이지 않도록 분리했습니다.

</details>

---

## 안전성과 개인정보

NULNUL 3.0은 중요한 경계를 명시적으로 유지합니다.

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

정확한 migration/ownership 규칙은 [NULNUL 3.0 업그레이드 안내](docs/upgrade-3.0.md)에 있습니다.

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

NULNUL 3.0은 현재 증거보다 더 큰 주장을 하지 않습니다.

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
<summary>3.0 핵심 레이어</summary>

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

- 현재 stable release: [NULNUL 3.0.0](https://github.com/SeoNaRu/nulnul-harness/releases/tag/v3.0.0)
- 업그레이드: [docs/upgrade-3.0.md](docs/upgrade-3.0.md)
- 변경 내역: [CHANGELOG.md](CHANGELOG.md)
- 보안: [SECURITY.md](SECURITY.md)
- 개인정보: [PRIVACY.md](PRIVACY.md)

---

## License

MIT — [LICENSE](LICENSE).
