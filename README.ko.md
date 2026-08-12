<p align="center">
  <img src="plugins/nulnul-harness/assets/nulnul-logo-green.svg" width="320" alt="NULNUL 로고">
</p>

<p align="center">
  <strong>검증된 능력. 개인 에이전트. 통제된 진화.</strong><br>
  초보자도 결과만 말하면 프로젝트에 맞는 에이전트 팀·능력·진화형 메타 하네스를 구성하는 Codex·Claude Code 플러그인입니다.
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

## 왜 NULNUL인가

도구가 많다고 좋은 에이전트 시스템은 아닙니다. 검증되지 않은 스킬, 겹치는 역할, 불필요한 서버, 스스로 선언하는 “학습”은 비용과 실패 지점만 늘립니다.

`NULNUL`은 더 작은 경로를 택합니다.

- 변경 전에 저장소와 완료 검사를 읽습니다.
- 새로 만들기 전에 기존 능력을 찾아 검증합니다.
- 현재 작업에 필요한 스킬과 에이전트만 활성화합니다.
- 설정에서 멈추지 않고 사용자가 요청한 원래 작업을 끝냅니다.
- 채팅 기억이 아니라 저장소 근거에서 다음 세션을 재개합니다.
- 재현 가능한 피드백을 독립 Gate가 승인한 에이전트 개선으로 바꿉니다.
- 사용자가 더 좋은 방법을 대신 찾아와야 했다면 Coach의 탐색·개선 절차 자체를 고칩니다.

사용자는 AI 구조가 아니라 원하는 결과만 말합니다. 기존 프로젝트에서는 저장소를 먼저 읽고 현재 설정을 제자리에서 업그레이드합니다. 빈 프로젝트에서는 무엇을 만들지 묻고 가장 작은 팀을 고릅니다. 맞는 스킬과 플러그인이 이미 설치돼 있으면 바로 재사용하고, 새 설치는 쉬운 말로 설명한 뒤 승인이 필요한 항목만 한 번 묻고, 겹치는 도구는 생략합니다.

## 항상 켜지는 기본선

모든 세팅에는 일곱 가지 **Baseline Kernel**이 적용됩니다. 저장소의 실제 상태, 원래 사용자 목표, 실행 가능한 완료 검사 하나, 변경 전 상태, 검사한 능력과 결정, 권한 경계, 독립 Gate와 롤백이 있는 진화입니다. 연속 작업이 필요하면 안정적인 세팅 근거는 `docs/nulnul/project.md`에 두고, 짧은 체크포인트에는 현재 목표·검사·제한된 검증 파일·명시적인 `verified`/`failed`/`unknown` 상태·마지막 근거·다음 행동·권한 경계·차단 요소만 담습니다. 빠른 재개에는 runner가 기록한 receipt의 fingerprint가 현재 파일과 일치해야 하며 stale `verified` 표시는 충분하지 않습니다.

무거운 인프라는 여전히 근거가 생길 때만 추가합니다. 다중 세션에는 영속 메모리, 결과 비교에는 성능 추적, 반복적인 사람의 판단에 추세가 필요하면 대시보드, 독립 작업에는 추가 에이전트, 위험한 변경에는 다단계 검증, 공유 상태에는 락, 기존 능력으로 못 푸는 도구·서비스 경계에는 승인된 MCP, 적합한 기존 후보가 없을 때만 프로젝트 로컬 스킬을 추가합니다. 자세한 계약은 [`references/baseline-kernel.md`](plugins/nulnul-harness/skills/nulnul-harness/references/baseline-kernel.md)에 있습니다.

## 하네스 엔지니어링에서 메타 하네스로

NULNUL의 출발점은 [GeekNews Weekly 353: “스킬이 쏟아지는 시대, 내 하네스는 내가 만든다”](https://news.hada.io/weekly/202615)입니다. 연구적 근간은 Meta·UBC의 [HyperAgents](https://ai.meta.com/research/publications/hyperagents/)([논문](https://arxiv.org/abs/2603.19461), [코드](https://github.com/facebookresearch/Hyperagents))입니다. 태스크 에이전트와 메타 에이전트를 하나의 편집 가능한 프로그램에 두고, 메타 에이전트가 이후 개선을 만드는 절차 자체도 개선한다는 구조입니다.

NULNUL은 사용자가 하네스를 직접 설계하지 않아도 되도록 이 아이디어를 제거 가능한 프로젝트 시스템으로 옮깁니다.

| 편집 가능한 측 | NULNUL 책임 |
| --- | --- |
| 태스크 측 | Navigator와 Worker가 선택된 스킬·플러그인으로 프로젝트를 완수 |
| 메타 측 | Coach가 더 나은 능력과 방법을 찾고 태스크 측 또는 자신의 탐색·개선 규칙을 수정 |
| 독립 경계 | Gate가 후보를 비교하고 자기 승인·권한 확대를 막으며 다음 실제 실행을 관찰 |

이는 일반 프로젝트 작업 중 일어나는 통제된 자기 개선입니다. HyperAgents의 개방형 연구 시스템을 그대로 재현했다는 주장은 아닙니다. 초기 조건과 정확한 메타 진화 계약은 [`references/meta-evolution.md`](plugins/nulnul-harness/skills/nulnul-harness/references/meta-evolution.md)에 있습니다.

## 어떻게 만들었나

**출발점.** 에이전트 설정은 대개 모델이 틀리기 전에 먼저 무너집니다. 원인은 추론 실패가 아니라, 두 번째 프로세스가 상태 파일을 덮어쓰거나, 실행조차 안 된 검사가 통과로 기록되거나, 같은 이름의 카운터가 세 군데서 다른 뜻으로 세지는 쪽입니다. 그래서 이 프로젝트는 **스킬만 있는 플러그인**으로 남았습니다. 서버도, 데몬도, 백그라운드 프로세스도 없습니다. 에이전트가 읽는 실행 계약과, 끝나면 지워도 되는 템플릿뿐입니다.

**진행 방식.** 1.x는 설정 문제를 풀었습니다. 저장소를 먼저 읽고, 새로 만들기 전에 기존 능력을 검증하고, 가장 작은 구성을 조립하고, 실행하고, 체크포인트를 남기고, 진화합니다. 이 뼈대는 검증을 통과했기 때문에 다시 쓰지 않았습니다.

**부하 시험.** 그다음 실제 반복 워크플로(크리에이터 리드 수집·검토)를 하루 종일 무인 루프로 돌렸습니다. 참조 문서가 막지 못한 방식으로 열한 번 깨졌고, 그중 추론 실패는 하나도 없었습니다.

- 무인 루프 3개가 각자 메모리의 전체 상태를 통째로 다시 써서 **판정 12,000건 소실**
- 수집기가 신규 0건이면 실행 기록을 안 남겼는데, 다음 검색 구간을 마지막 실행 기록에서 계산했습니다. 커서가 얼어붙어 하루 종일 같은 120개만 조회. 고친 뒤 **한 번에 1,265건 발견**
- 링크 검증기가 검사를 건너뛰었는데 집계가 `ok`로 적어서, **한 번도 검증 안 된 행이 검증됨으로 납품**
- 메일 도메인을 `MX`가 아니라 `A` 레코드로 검사해 **멀쩡한 메일 15건**을 죽음으로 굳힘
- 업종 필터가 긴 소개글의 면책 문구에 걸려 **정상 리드 20건 오탐**
- "완료 건수"를 세 군데서 세 정의로 세다가, 루프가 목표 달성으로 오판하고 납품되지 않은 상태에서 즉시 종료

각 실패는 그 숫자와 함께 규칙이 되어, 에이전트가 실제로 읽는 참조 문서에 들어갔습니다. [실전에서 굳힌 규칙](#실전에서-굳힌-규칙) 참고.

**그날이 설계에서 바꾼 것.** 측정된 개선은 전부 **이미 있던 판정 함수를 고친 데서** 나왔습니다. 새 에이전트의 기여분은 0이었습니다. 그래서 지금은 에이전트를 더하기 전에 네 가지 작업을 확인합니다. 반복 판정에는 동결 벤치마크, 목표 건수를 세는 반복 작업에는 납품 함수 하나, 코드와 지침이 함께 변하면 문서 부채 훅, 공유 상태를 동시에 쓰면 쓰기자 하나와 락이 필요할 수 있습니다. 실제 작업이 있는 기전만 만들고 나머지는 이후 실행 근거가 생길 때 Meta Coach가 추가합니다. 한 프로젝트의 하루치이므로 벤치마크가 아니라 현장 근거로 읽어야 합니다.

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

두 환경 모두 같은 스킬을 씁니다. 하네스는 호스트를 감지하고 저장소가 소유한 설정 경로에만 씁니다. 무인 Claude Code 세션에서는 `.claude/**`를 검사만 하고 수정하지 않으며, `CLAUDE.md`, `docs/nulnul/`, 검증된 체크포인트가 세션 연속성과 재사용 워크플로를 담당합니다.

새 세션에서 원하는 결과를 말하세요. "하네스 만들어줘"면 충분합니다. 에이전트도, 역할도, 설정 절차도 직접 적지 않습니다.

```text
금융 YouTube 크리에이터를 찾고 중복을 제거한 뒤,
검토된 결과만 Google Sheets에 안전하게 저장하는 하네스 만들어줘.
```

하네스는 프로젝트를 검사하고, 충분한 기존 지침과 테스트를 재사용하고, 사용 가능한 능력을 검증하고, 안전하게 알 수 없는 결정만 질문한 뒤 구현과 검증까지 이어갑니다. "하네스"라는 말 없이 원하는 제품만 설명해도 동일하게 동작합니다. 단순 읽기 전용 질문에는 활성화되지 않으며 충분한 프로젝트 설정을 중복 생성하지 않습니다.

## 업데이트

Codex는 Git 마켓플레이스를 갱신한 뒤 다시 설치합니다. 현재 Codex 플러그인 CLI에는 별도 플러그인 업데이트 명령이 없습니다.

```bash
codex plugin marketplace upgrade nulnul-harness
codex plugin remove nulnul-harness@nulnul-harness
codex plugin add nulnul-harness@nulnul-harness
```

Claude Code는 마켓플레이스와 플러그인을 갱신한 뒤 재시작합니다.

```bash
claude plugin marketplace update nulnul-harness
claude plugin update nulnul-harness@nulnul-harness
```

처음에 로컬 복제본을 마켓플레이스로 추가했다면 그 폴더에서 먼저 `git pull origin main`을 실행하고 같은 재설치·업데이트 명령을 사용합니다. 어느 환경이든 새 에이전트 세션을 시작해야 합니다. 프로젝트에 만들어진 `AGENTS.md`, `CLAUDE.md`, `docs/nulnul/` 상태는 보존됩니다.

## 제품 루프

```text
Discover → Verify → Assemble → Run → Checkpoint → 태스크 또는 개선 절차를 Evolve
```

| 단계 | 남는 결과 |
| --- | --- |
| Discover | 필요한 작업과 기존 후보 |
| Verify | 출처, 호환성, 품질, 권한, 라이선스 |
| Assemble | 가장 작지만 완전한 능력·에이전트 구성 |
| Run | 사용자에게 보이는 결과와 완료 검사 |
| Checkpoint | 검증된 상태, 다음 행동, 차단 요소, 승인된 권한 |
| Evolve | 태스크 또는 메타 절차 변경, 전이 검사, 실제 실행 관찰, 롤백 |

한 번의 실행 전체:

```text
당신의 요청
     │
     ▼
저장소 검사 ──▶ 충분한 설정과 완료 검사가 이미 있나? ──있음──▶ 재사용, 설정 건너뜀
     │ 없음                                                            │
     ▼                                                                 │
필요한 작업 정리 ──▶ 설치된·기존 능력 탐색                             │
     │                        │                                        │
     │                        └─ 적합 후보 없음 ──▶ 후보 하나 검증 ──▶ 빠진 것만 생성
     ▼                                                                 │
가장 작은 구성 조립 ◀──────────────────────────────────────────────────┘
     │
     ▼
실제 작업 수행 ──▶ 저장소의 실제 검사로 검증
     │                     │
     │                     └─ 실패 ──▶ 피드백 ──▶ Coach 제안 ──▶ 독립 Gate ──▶ 승격 또는 롤백
     ▼
검증된 상태를 체크포인트 ──▶ 다음 세션은 채팅 기억이 아니라 여기서 재개
```

성숙한 저장소에서는 `있음` 분기가 기본값이고, 이 경로는 파일을 하나도 만들지 않습니다.

## 저장소에 남는 것

```text
your-project/
├── AGENTS.md 또는 CLAUDE.md   # 호스트가 읽는 저장소 지침, 기존 내용과 병합
├── docs/nulnul/
│   ├── project.md             # 목표, 완료 검사, 능력, 권한 경계, 롤백
│   ├── checkpoint.json        # 일반 다중 세션 작업의 짧은 재개 상태
│   └── evolution.json         # 에이전트 진화 이력이 필요할 때 checkpoint.json을 대체
├── .agents/skills/<name>/      # Codex: 반복 작업을 맡을 기존 스킬이 없을 때만
└── docs/nulnul/workflows/<name>.md
                                # 무인 Claude Code: CLAUDE.md가 참조하는 재사용 워크플로
```

이게 전부입니다. 일반 다중 세션 작업에는 `checkpoint.json`을 쓰고, 에이전트별 피드백과 승격 이력이 필요하면 두 번째 상태 작성자를 만들지 않고 `evolution.json`으로 대체합니다. 기존 지속형 세팅을 업그레이드할 때는 계약과 권한 제약을 보존하고 체크포인트를 `unknown`으로 시작해 기록된 검사를 다시 통과해야 합니다. 프로젝트 로컬 스킬은 기존 후보를 전부 확인하고 기각했을 때만 생기며, 빠른 경로 실행은 아무것도 쓰지 않습니다. 생성된 `docs/nulnul/`과 프로젝트 로컬 스킬 디렉터리를 지우면 제품 코드는 그대로 두고 하네스만 사라집니다. 호스트 소유 에이전트 정의는 이 설치 범위에 포함되지 않습니다.

목표는 생성 파일을 늘리는 게 아니라 줄이는 것입니다. 에이전트 정의 수십 개를 뽑아내는 설정은 문제를 푼 게 아니라 옮긴 것입니다.

## 사용 사례

새 세션에서 한 문장이면 됩니다. 전부 반복 데이터 워크플로라, 중복 제거·제외 우선순위·`unknown` 상태·커서 유지·단일 쓰기자 락을 따로 요청하지 않아도 상속합니다.

```text
금융 YouTube 크리에이터를 찾고 중복을 제거한 뒤 검토된 결과만 Google Sheets에 저장하는 하네스 만들어줘.
채용 공고를 계속 지켜보다가 중복을 빼고 검토 가능한 큐 하나로 모으는 하네스 만들어줘.
경쟁사 가격 페이지를 매주 스냅샷 찍고 바뀐 것만 보고하는 하네스 만들어줘.
내 분야의 새 논문과 릴리스 노트를 모아 주간 다이제스트 하나로 만드는 하네스 만들어줘.
문의 인박스를 분류하고 애매한 건은 검토 큐로 보내는 하네스 만들어줘.
제품 리뷰를 모아 반복되는 이슈를 태깅하고 요약 시트를 유지하는 하네스 만들어줘.
문서의 모든 링크를 검증하고, 확인 못 한 상태까지 구분해서 죽은 링크를 보고하는 하네스 만들어줘.
CI 실패를 모아 여러 실행에서 반복되는 것만 묶어주는 하네스 만들어줘.
```

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
| Coach | 메타 에이전트로서 더 나은 방법을 찾고 한 가지 태스크·메타 변경을 제안 |
| Gate | 후보와 승인된 버전을 비교해 승격·거부·롤백 |

네 책임은 항상 네 개의 실행 에이전트를 뜻하지 않습니다. 단순 작업에서는 역할을 합칠 수 있지만 승격 제안자와 Gate는 반드시 분리합니다. Coach는 자신의 탐색·개선 절차도 개선할 수 있지만 자신의 후보를 승인할 수 없습니다.

다중 세션 작업은 `docs/nulnul/evolution.json`에 제한된 상태만 저장합니다. 포함된 표준 라이브러리 검사기는 대상 또는 제안 작성자의 자기 승인, 모순된 기록, 빈 근거, 잘못된 버전 이동, 민감 키 저장, 사전 승인 없는 권한 확대를 거부합니다.

1.4 Observable Evolution 후보는 기존 활성화 실행기에 제한된 Experience Digest를 추가합니다. 안정적으로 구분되는 `activation`·`resume`·`verification` 단계, 논리적 owner, 경과 시간, 도구·읽기·검증기·테스트·완료 검사 집계, 제한된 signal, 검증 상태만 남깁니다. prompt, response, transcript, command 목록, 머신 경로는 저장하지 않습니다. 1.4.1은 path resolution을 반증하고 final-action ordering을 지지했으며 Navigator instruction 후보 두 개를 reject했습니다. 마지막 1.4.2 interruption 실험은 실제 defect를 찾았습니다. 세 mutated state 모두 independent Gate 전 fast resume가 가능했습니다. schema-v3 checkpoint는 이제 runner가 기록한 제한된 파일 fingerprint를 요구하며, Navigator 문구를 바꾸지 않고 unverified mutated-state acceptance를 3/3에서 0/3으로 줄였습니다.

1.5 Generalization Gate는 이미 노출된 DEV/VALIDATION case와 candidate가 고정된 뒤 한 번만 쓰는 HOLDOUT 근거를 분리합니다. 첫 Ruby holdout은 fixture 자체가 잘못되어 실패했고 영구히 validation으로 강등했으며, 이 실패로 mandatory fixture preflight를 추가했습니다. 고정된 Navigator v15 snapshot에 없던 새 Perl/TAP CLI case는 stale-state 3/3 차단과 post-check resume 3/3을 보였고, champion 3회 retry와 best-of-3는 계속 unsafe했습니다. 판정은 의도적으로 **Narrower Scope**입니다. checkpoint freshness는 이 unseen shape로 전이됐지만 harness 전체의 일반화는 확립되지 않았습니다. 릴리스 adoption은 제한된 `claude plugin list --json` inventory를 Adopt and upgrade의 첫 행동으로 요구하며, sanitized 1.5.0 nonpass 세 건이 이 규칙을 branch 경계로 이동시켰습니다.

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
| 코드와 지속 지침이 함께 변할 때 문서 부채 감지기 포함 | 코드에만 남은 수정은 다음 세션에서 보이지 않습니다 |
| 검사한 작업에 따라 벤치마크·납품 함수·문서 훅·상태 락 선택 | 단순 프로젝트의 추측성 비계 또는 반복 작업에 실제 필요한 기전 누락 |

## 기존 개념과의 관계

여기 있는 부품 중 새로운 것은 없습니다. 구조를 쪼개면 각각은 이미 이름이 있는 개념이고, 아래 대응은 확인 결과 정확합니다.

| NULNUL의 부품 | 기존 이름 | 여기서는 어디에 있나 |
| --- | --- | --- |
| 편집 가능한 태스크·메타 측 | [HyperAgents](https://ai.meta.com/research/publications/hyperagents/) — 메타 에이전트가 태스크 에이전트와 자신의 수정 절차를 변경 | `references/meta-evolution.md`, 안전 경계로 독립 Gate 추가 |
| Coach/Gate 분리 | actor-critic([Sutton & Barto](http://incompleteideas.net/book/the-book.html)), generator-verifier gap — 만드는 일과 채점하는 일은 다른 일이고 채점이 더 쉽습니다 | `references/personal-evolution.md` |
| 자동 승격·롤백 | champion/challenger, 모델 레지스트리 승격 게이트([MLflow](https://mlflow.org/docs/latest/model-registry.html)), [카나리 배포](https://martinfowler.com/bliki/CanaryRelease.html) | 승격 조건 8번 — 한 사이클 현장 관찰, 지표 하락 시 자동 되돌림 |
| 회귀 테스트로 게이팅 | eval-gated CI([promptfoo](https://www.promptfoo.dev/), [Braintrust](https://www.braintrust.dev/), [LangSmith](https://docs.smith.langchain.com/)) | [`evals/cases.json`](evals/cases.json), `scripts/release_gate.py`, 저장소 테스트 |
| 지표 기준 프롬프트 최적화 | [DSPy](https://arxiv.org/abs/2310.03714) — 메트릭에 대고 프롬프트를 컴파일 | 모든 카운터가 import하는 목표 지표 함수, Coach가 명시하는 주요 지표 |
| 실패에서 배워 재시도 | [Reflexion](https://arxiv.org/abs/2303.11366), [Self-Refine](https://arxiv.org/abs/2303.17651) | 피드백 → 제안 루프 |
| 에이전트가 스킬을 쌓아감 | [Voyager](https://arxiv.org/abs/2305.16291)의 skill library | `.agents/skills/<name>/` — 기존 후보를 확인하고 기각한 뒤에만 생성 |
| 밖에서 스킬·도구 가져오기 | [MCP](https://modelcontextprotocol.io/) 레지스트리, 플러그인 마켓플레이스 | `references/capability-discovery.md` |

의도적으로 다르게 둔 지점은 두 개입니다.

- **시스템은 자신을 개선하지만, 자신을 승인하지는 못합니다.** Reflexion 계열은 같은 에이전트가 자기 재시도를 비평하고 받아들입니다. 여기서는 Coach가 자신의 개선 절차를 수정할 수 있지만 승격에는 독립 Gate와 한 사이클의 실제 관찰이 필요하고, 제안 작성자나 대상이 승인한 상태 파일은 검증기가 거부합니다.
- **관리형 런타임은 선택 사항입니다.** [Claude Managed Agents](https://news.hada.io/topic?id=28326)는 호스팅된 세션·샌드박스·ID·추적을 제공하지만 HyperAgents는 아닙니다. NULNUL은 그 서비스를 요구하거나 프로젝트를 한 모델 제공자에 묶지 않습니다.
- **루프가 실제로 깨지는 지점은 운영이라, 규칙도 운영 쪽입니다.** 락, 커서, `unknown` 상태 분리는 에이전트 추론 주제가 아닙니다. 그래서 에이전트만 다루는 설계가 계속 데이터를 잃습니다.

기여라고 할 만한 건 포장입니다. 실행할 서비스 없이, 새 저장소에 그대로 옮겨지고, 지우면 흔적이 남지 않는 계약 하나로 위 전부를 옮깁니다.

## 주장보다 근거

| 검사 | 현재 결과 |
| --- | --- |
| 저장소 자동 검사 | 94개 통과 |
| Release Gate | 행동·안전 100/100, 기록된 세팅·워크플로·빠른 재개·제한된 일반화 Gate도 통과 |
| 긍정 격리 시나리오 | 9개 통과 |
| 부정 안전 시나리오 | 3개 통과 |
| 코덱스 2회 메타 진화 | Coach v1 → v2, 관련 방법 누락 0/2, fixture 검사 8/8, 불필요한 인프라 생략 |
| 독립 포워드 평가 | 검증기 결함 3개 발견, 수정 후 회귀 검사로 보존 |
| 오프라인 워크북 A/B(각 3회) | 모두 정답, Navigator v3는 1.2.0 대비 중앙 시간 -25.76%, 출력 토큰 -22.76% |
| 신규 Codex 세팅 A/B | 행동 정확, 채택된 1.3.0은 1.2.1 대비 입력 +2.31%, 출력 -5.42%, 추론 -9.80%; 최초 +50.89% 안은 기각 |
| 신규 Codex 재개 A/B | 3/3 실행 모두 행동 정확, 짧은 체크포인트가 1.3.0 대비 중앙 입력 38.52%, 출력 30.72%, 추론 56.33% 절감; 약한 세 안은 기각 |
| 후속 전이 실행 | 별도 slugger 프로젝트에서 행동과 검사 하나만 정확히 바꾸고 3/3 검사와 양쪽 하네스 검사를 통과했으며 표시된 전체 계약은 읽지 않음 |
| 활성화·빠른 재개 실행기 | 긍정·부정 프로젝트 형태 10개, 기본 3회 반복; 교차 순서 후보는 4/4회 읽기 경계를 지켰고 비교 가능한 3쌍에서 paired 입력 -18.4% |
| Observable Evolution | 6개 진단 run이 path resolution을 반증하고 final-action ordering을 지지했으며, 잘못된 event order·stage·raw transcript 대조군은 실패하고 ordering-only 후보는 기각 |
| Generalization Gate | 노출 benchmark inventory 기록, 실패한 Ruby case는 validation으로 강등, 새 Perl/TAP case는 3/3 통과하고 champion retry/best-of-3는 unsafe; 판정은 Narrower Scope |
| 무인 Claude Code 도입 | GitHub marketplace 설치본 1.3.5가 두 에이전트 프로필 해시를 보존하고 `.claude/**` 쓰기 호출 0건, 실행 가능한 완료 명령이 든 검증 체크포인트, 기계 기록 검사 5개 통과 |
| 학습 루프·업그레이드 대조군 | schema v1 체크포인트는 읽기 전용, 판정 목록 누락은 Product·Release Gate 실패, 마이그레이션 쓰기 실패 주입 시 앞선 파일 전부 복원 |
| 실행형 롤백 대조군 | 임계값 위반 시 Coach v1 활성 버전 상태 복구, 정상 지표에서는 파일을 쓰지 않음 |

Release Gate은 범용 성능 벤치마크는 아닙니다. 가중 행동·안전 케이스 12개가 모두 통과하며 기록된 세팅·워크플로·빠른 재개 성능이 회귀해도 릴리스가 실패합니다. Generalization Gate는 personal/core 승격이나 전이 주장에만 붙는 별도 Gate이며, 일반 project-local 변경에는 holdout 비용을 부과하지 않습니다. 성능 근거는 버전과 무관한 champion/candidate 형식이고, 빠른 재개는 실행 순서를 교차한 paired 상대 토큰 예산으로 검사합니다. 활성화 실행기는 정밀도·재현율·단계 시간·논리적 owner와 도구/읽기/검증/테스트/완료 검사 집계를 내되 원본 대화나 command 목록은 보존하지 않습니다.

공개 검증을 재현할 수 있습니다.

```bash
python3 scripts/release_gate.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

입력과 판정은 [`evals/cases.json`](evals/cases.json), [`evals/results.json`](evals/results.json), [`성능 비교`](evals/benchmarks/performance.json), [`신규 Codex 세팅 기준선`](evals/benchmarks/setup-baseline/results.json), [`일반화 노출 inventory`](evals/generalization/manifest.json)와 [one-shot 결과](evals/generalization/results.json)에 공개돼 있습니다.

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
- **Evaluation exposure는 state입니다.** development에서 본 case를 unseen으로 다시 부를 수 없고, 사용한 holdout은 retire합니다.
- **Verified resume.** 체크포인트를 사용하기 전에 저장소 현실과 다시 비교합니다.
- **호스트 소유 설정은 호스트가 관리합니다.** 무인 세션은 `.claude/**`를 검사하지만 자기 에이전트·스킬·설정·훅을 다시 쓰지 않습니다.
- **Removable setup.** 생성된 프로젝트 상태는 제품 코드를 손상하지 않고 제거할 수 있습니다.

## 배포 범위

```text
plugins/nulnul-harness/                 # 유일한 배포 제품 경계
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json          # Claude Code 매니페스트
├── assets/nulnul-harness.svg
└── skills/nulnul-harness/
    ├── SKILL.md                        # 실행 계약
    ├── agents/openai.yaml              # Codex UI 메타데이터
    ├── references/                     # 탐색·조립·안전·진화 규칙
    ├── assets/                         # 제거 가능한 프로젝트 템플릿
    └── scripts/                        # 상태 검사기와 문서 부채 감지기
```

플러그인은 skills-only입니다. MCP 서버, 훅, 앱, 인증, 원격 텔레메트리, 호스팅 서비스, 백그라운드 프로세스를 포함하지 않습니다. 로컬 릴리스 벤치마크는 정제된 집계만 보존합니다. 진화는 일반 에이전트 작업 중에 일어나며 무감독 데몬이 아닙니다. Gate 독립성은 선언된 상태를 검증하며 실행자 신원을 암호학적으로 증명하지는 않습니다.

## 자주 묻는 질문

<details>
<summary>Release Gate은 성능 벤치마크인가요?</summary>

범용 벤치마크는 아닙니다. 행동·안전을 검사한 뒤 공개된 특정 작업의 세팅·워크플로·빠른 재개 성능 예산도 강제합니다. 측정 범위는 기록된 fixture에 한정하며 [주장보다 근거](#주장보다-근거)에 그대로 표기합니다.
</details>

<details>
<summary>왜 에이전트를 이렇게 적게 만드나요?</summary>

측정이 그쪽을 가리켜서입니다. 하루 무인 운영에서 측정된 개선은 전부 이미 있던 판정 함수를 고친 데서 나왔고, 새 에이전트의 기여분은 0이면서 조정 비용만 늘렸습니다. 역할은 구체적인 독립 작업, 컨텍스트 경계, 병렬 분기, 독립 검증이 필요할 때만 추가합니다.
</details>

<details>
<summary>에이전트가 자기 개선을 스스로 승인하지 못하는 이유는?</summary>

답을 만드는 일과 검사하는 일은 다른 일이고, 정직하게 유지하기 쉬운 쪽은 검사입니다. 승격에는 독립 Gate, 재현된 실패, 통과한 회귀 검사, 자동 롤백 임계가 걸린 한 사이클의 현장 관찰이 필요합니다. 제안 작성자나 대상 에이전트가 자기 승격에 서명한 상태 파일은 검증기가 거부하므로, 설득력 있는 에이전트가 있어도 규칙이 살아남습니다.
</details>

<details>
<summary>MCP 서버나 훅, 백그라운드 프로세스가 없는 이유는?</summary>

계속 떠 있어야 하는 게 없기 때문입니다. 상시 실행되는 구성 요소는 운영·보안·제거 대상이 됩니다. 실제로 필요한 작업이 생기면 능력 탐색이 MCP 서버나 플러그인을 채택할 수 있습니다. 다만 명시적 승인을 거치고, 권한 경계와 제거 조건을 함께 기록합니다.
</details>

<details>
<summary>제거하면 뭐가 남나요?</summary>

제품 코드와 직접 쓴 지침만 남습니다. 생성된 프로젝트 상태는 `docs/nulnul/`과 `.agents/`에 있고, 플러그인은 사용자가 쓴 지침을 덮어쓰지 않고 병합합니다.
</details>

<details>
<summary>에이전트 팀을 생성해 주는 하네스와는 뭐가 다른가요?</summary>

목적이 다릅니다. 팀 생성형은 도메인 설명에서 인력이 배치된 조직을 뽑아냅니다. 이쪽은 이미 있는 저장소에서 출발해, 작업을 덮는 것은 재사용하고, 완료 검사를 통과하는 가장 작은 구성만 생성합니다. 아무것도 안 만드는 경우도 많습니다. 그리고 무인 루프가 데이터를 지킬지 결정하는 운영 규칙(락, 커서, 미검증 상태, 롤백 임계)을 함께 들고 다닙니다.
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

## 개발

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/release_gate.py
```

제품 결정과 실험 기록은 [`CHANGELOG.md`](CHANGELOG.md)에 요약되어 있습니다. [`SUPPORT.md`](SUPPORT.md)와 [MIT 라이선스](LICENSE)도 확인하세요.

MIT © [SeoNaRu](https://github.com/SeoNaRu)
