<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<h1 align="center">NULNUL</h1>

<p align="center">
  <strong>검증된 능력. 개인 에이전트. 통제된 진화.</strong><br>
  아이디어를 검증된 에이전트 시스템으로 바꾸는 skills-only Codex 플러그인.
</p>

<p align="center">
  <a href="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml"><img src="https://github.com/SeoNaRu/nulnul-harness/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <img src="https://img.shields.io/badge/version-1.2.1-111111" alt="version 1.2.1">
  <a href="evals/results.json"><img src="https://img.shields.io/badge/Harness_100-100%2F100-111111" alt="Harness 100: 100/100"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-111111" alt="MIT 라이선스"></a>
</p>

<p align="center">
  <a href="README.md">English</a> · <strong>한국어</strong>
</p>

## 왜 NULNUL인가

도구가 많다고 좋은 에이전트 시스템은 아닙니다. 검증되지 않은 스킬, 겹치는 역할, 불필요한 서버, 스스로 선언하는 “학습”은 비용과 실패 지점만 늘립니다.

`NULNUL`은 더 작은 경로를 택합니다.

- 변경 전에 저장소와 완료 검사를 읽습니다.
- 새로 만들기 전에 기존 능력을 찾아 검증합니다.
- 현재 작업에 필요한 스킬과 에이전트만 활성화합니다.
- 설정에서 멈추지 않고 사용자가 요청한 원래 작업을 끝냅니다.
- 채팅 기억이 아니라 저장소 근거에서 다음 세션을 재개합니다.
- 재현 가능한 피드백을 독립 Gate가 승인한 에이전트 개선으로 바꿉니다.

## 빠른 시작

```bash
git clone https://github.com/SeoNaRu/nulnul-harness.git
cd nulnul-harness
codex plugin marketplace add "$PWD"
codex plugin add nulnul-harness@nulnul-harness
```

새 Codex 세션에서 하네스가 아니라 원하는 제품을 요청하세요.

```text
금융 YouTube 크리에이터를 찾고 중복을 제거한 뒤,
검토된 결과만 Google Sheets에 안전하게 저장하는 자동화를 만들어줘.
```

하네스는 프로젝트를 검사하고, 충분한 기존 지침과 테스트를 재사용하고, 사용 가능한 능력을 검증하고, 안전하게 알 수 없는 결정만 질문한 뒤 구현과 검증까지 이어갑니다. 단순 읽기 전용 질문에는 활성화되지 않으며 충분한 프로젝트 설정을 중복 생성하지 않습니다.

## 제품 루프

```text
Discover → Verify → Assemble → Run → Checkpoint → Evolve
```

| 단계 | 남는 결과 |
| --- | --- |
| Discover | 필요한 작업과 기존 후보 |
| Verify | 출처, 호환성, 품질, 권한, 라이선스 |
| Assemble | 가장 작지만 완전한 능력·에이전트 구성 |
| Run | 사용자에게 보이는 결과와 완료 검사 |
| Checkpoint | 검증된 상태, 다음 행동, 차단 요소, 승인된 권한 |
| Evolve | 재현 가능한 피드백, 버전 비교, 독립 승격, 롤백 |

## 개인 에이전트 진화

```text
Worker feedback ──▶ Coach proposal ──▶ independent Gate
       ▲                                      │
       └──────── Navigator resumes work ◀─────┘
```

| 책임 | 하는 일 |
| --- | --- |
| Navigator | 결과, 완료 검사, 권한, 체크포인트, 재개를 관리 |
| Worker | 제한된 작업 하나를 수행하고 관찰 가능한 근거를 보고 |
| Coach | 가장 가까운 원인 계층을 진단하고 한 가지 버전 변경을 제안 |
| Gate | 후보와 승인된 버전을 비교해 승격·거부·롤백 |

네 책임은 항상 네 개의 실행 에이전트를 뜻하지 않습니다. 단순 작업에서는 역할을 합칠 수 있지만 승격 제안자와 Gate는 반드시 분리합니다. Coach도 피드백으로 개선될 수 있지만 자신의 후보를 승인할 수 없습니다.

다중 세션 작업은 `docs/nulnul/evolution.json`에 제한된 상태만 저장합니다. 포함된 표준 라이브러리 검사기는 대상 또는 제안 작성자의 자기 승인, 모순된 기록, 빈 근거, 잘못된 버전 이동, 민감 키 저장, 사전 승인 없는 권한 확대를 거부합니다.

## 실전에서 굳힌 규칙

실제 반복 워크플로를 하루 종일 무인 루프로 돌리며 얻은 규칙입니다. 각 항목은 기존 참조 문서가 막지 못해 실제로 사고를 낸 실패를 대체합니다.

| 규칙 | 막는 실패 |
| --- | --- |
| 상태 파일 하나당 쓰기 프로세스 하나: 배타 락, 프로세스 그룹 단위 정지, 병렬 수집기는 각자 샤드 | 여러 루프가 각자 메모리의 전체 상태를 통째로 다시 쓰면 나중에 쓴 쪽이 나머지를 덮습니다. 원자적 rename은 찢어진 파일만 막고 덮어쓰기는 막지 못합니다 |
| `verified`·`failed`와 구분되는 `unknown` 상태 | 건너뛴 검사나 시간 초과를 통과로 기록하거나, 실패로 굳혀 멀쩡한 레코드를 지우는 일 |
| 결과가 0건인 사이클에서도 커서 기록 | 다음 구간을 마지막 실행 기록에서 계산하므로, 기록이 없으면 커서가 얼어붙어 같은 구간만 반복해 긁습니다 |
| 승격마다 한 사이클의 현장 지표 관찰과 자동 롤백 임계 | 실행 중에만 드러나는 회귀(조회 방식, 부하, 실행 순서, 길어진 입력)는 동결 표본을 그대로 통과합니다 |
| 목표 지표는 함수 하나로 정의하고 모든 카운터가 그것을 import | 카운터마다 정의가 갈라지고, 프록시 지표로 목표를 채운 루프가 납품되지 않은 일을 두고 종료합니다 |
| 모든 유효성 검사는 대조군으로 검증 | 존재하지 않는 대상이 실제 대상과 똑같이 응답하는, 아무것도 검사하지 않는 검사 |
| 각 단계는 자기 시작·종료를 스스로 기록 | 기록 없는 시간이 옆 단계에 붙어 엉뚱한 병목을 지목합니다 |
| 기각·롤백된 후보를 diff와 사유째로 보존하고 다음 제안 전에 조회 | Coach가 이미 Gate에서 기각된 후보를 다시 제안하는 일 |
| 게이트 판정 로그와 오탐 비율 리포트 | 오탐이 쌓이면 사람이 반사적으로 승인하게 되고, 그 순간 게이트는 아무것도 지키지 못합니다 |
| 첫날 설정에 문서 부채 감지기 포함 | 코드에만 남은 수정은 다음 세션에서 보이지 않습니다 |
| 첫날 설정이 최소 동결 벤치마크, 납품 단위 함수, 문서 부채 훅, 상태 파일 락을 함께 산출 | 콜드 스타트에서는 Gate가 돌릴 대상이 없어 진화 자체가 시작되지 않습니다 |

## 주장보다 근거

| 검사 | 현재 결과 |
| --- | --- |
| 저장소 자동 검사 | 31개 통과 |
| Harness 100 행동·안전 게이트 | 100/100 |
| 긍정 격리 시나리오 | 6개 통과 |
| 부정 안전 시나리오 | 3개 통과 |
| 독립 포워드 평가 | 검증기 결함 3개 발견, 수정 후 회귀 검사로 보존 |
| 오프라인 워크북 A/B(각 3회) | 모두 정답, Navigator v3는 1.2.0 대비 중앙 시간 -25.76%, 출력 토큰 -22.76% |

Harness 100은 범용 성능 벤치마크가 아니라 릴리스 게이트입니다. 새 프로젝트 암묵적 활성화, 모호한 빈 저장소, 충분한 설정 재사용, 기존 능력 우선 자동화, 권한 경계, 근거 기반 진화, 읽기 전용 비활성화, 비밀 저장 거부, 미승인 전역 등록 거부를 검사합니다.

공개 검증을 재현할 수 있습니다.

```bash
python3 scripts/harness_100.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

입력과 판정은 [`evals/cases.json`](evals/cases.json)과 [`evals/results.json`](evals/results.json)에 공개돼 있습니다.

## 대표 워크플로: YouTube → Google Sheets

공개 예제는 운영 중인 신원이나 연락처를 복사하지 않고 금융 크리에이터 조사 흐름을 모델링합니다. 채널 탐색, 분류, 채널 ID 기반 중복 제거, 제외 우선순위, 검토자 피드백, 스프레드시트 수식 삽입 방지, 안전한 upsert, 실행 지표를 다룹니다.

- 합성 공개 예제: [`examples/youtube-sheets`](examples/youtube-sheets)
- 오프라인 품질 채점기와 A/B 근거: [`evals/benchmarks/youtube-sheets`](evals/benchmarks/youtube-sheets)

명시적 승인 없이 실제 Google 인증이나 Sheet 쓰기를 실행하지 않습니다. 첫 격리 3×3 비교에서 완전한 계약의 오버헤드를 발견했고, Navigator v3는 불필요한 활성화를 건너뛰면서 정답과 더 낮은 중앙값을 재현했습니다. 특정 작업의 예비 근거이며 범용 성능 주장으로 일반화하지 않습니다.

## 신뢰 모델

- **Installed ≠ verified.** 설치 여부는 발견 근거이지 검증 증명이 아닙니다.
- **Popularity ≠ fitness.** 인기도는 출처·권한·라이선스·작업 적합성 실패를 덮지 못합니다.
- **Least privilege.** 인증, 외부 쓰기, 배포, 공개, 전역 등록은 승인 경계로 남습니다.
- **No secret persistence.** 자격 증명, 대화 전문, 개인 데이터를 프로젝트 기억으로 만들지 않습니다.
- **Independent promotion.** 에이전트는 자신의 업그레이드를 승인하지 못합니다.
- **Verified resume.** 체크포인트를 사용하기 전에 저장소 현실과 다시 비교합니다.
- **Removable setup.** 생성된 프로젝트 상태는 제품 코드를 손상하지 않고 제거할 수 있습니다.

## 배포 범위

```text
plugins/nulnul-harness/                 # 유일한 배포 제품 경계
├── .codex-plugin/plugin.json
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # 실행 계약
    ├── agents/openai.yaml              # Codex UI 메타데이터
    ├── references/                     # 탐색·조립·안전·진화 규칙
    ├── assets/                         # 제거 가능한 프로젝트 템플릿
    └── scripts/                        # 결정론적 상태 검사기
```

플러그인은 skills-only입니다. MCP 서버, 훅, 앱, 인증, 텔레메트리, 호스팅 서비스, 백그라운드 프로세스를 포함하지 않습니다. 진화는 일반 에이전트 작업 중에 일어나며 무감독 데몬이 아닙니다. Gate 독립성은 선언된 상태를 검증하며 실행자 신원을 암호학적으로 증명하지는 않습니다.

## 제거

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

## 개발

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/harness_100.py
```

제품 결정과 실험 기록은 [`CHANGELOG.md`](CHANGELOG.md)에 요약되어 있습니다. [`SUPPORT.md`](SUPPORT.md)와 [MIT 라이선스](LICENSE)도 확인하세요.

MIT © [SeoNaRu](https://github.com/SeoNaRu)
