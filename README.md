# nulnul harness

> 신경 꺼.

아이디어만 말하세요. nulnul harness가 프로젝트를 읽고, 이미 잘 만들어진 스킬과 플러그인을 먼저 찾아 검증하고, 필요한 에이전트만 맞춘 뒤 실제 결과까지 만듭니다. 자동화를 돌리면서 쌓인 실패·품질 지표·사용자 수정을 비교해 더 나아진 구성만 남깁니다.

만드는 것보다 가져오는 편이 나으면 가져옵니다. 에이전트를 늘리는 것보다 하나가 나으면 하나만 씁니다. 설정을 늘리는 것이 아니라 사용자가 신경 쓸 과정을 없애는 제품입니다.

## 작동 방식

```text
아이디어
  → 프로젝트와 완료 조건 파악
  → 필요한 능력 분해
  → 설치됨·공식·큐레이션·공개 스킬 검색
  → 출처·호환성·유지보수·품질·권한·라이선스 검증
  → 최소 스킬과 에이전트 조합
  → 원래 작업 실행
  → 실제 결과 측정
  → 나아진 변경만 채택하거나 되돌리기
```

예를 들어 “코인·주식 관련 유튜버를 찾아 시트에 저장하는 자동화”라고 요청하면 검색, 관련성 판별, 중복 제거, 시트 저장, 반복 실행과 검증에 필요한 능력을 나눕니다. Google Sheets처럼 검증된 기존 연동이 있으면 재사용하고, 적절한 후보가 없는 좁은 부분만 프로젝트 전용으로 만듭니다.

다운로드, 전역 설치, 인증, 외부 쓰기, 배포와 공개는 무엇을 왜 사용하는지 밝히고 사용자의 승인을 받습니다.

## 제품 구조

```text
.agents/plugins/marketplace.json
plugins/nulnul-harness/
├── .codex-plugin/plugin.json
└── skills/nulnul-harness/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── assets/
tests/test_product_plugin.py
```

`plugins/nulnul-harness/`만 사용자에게 설치되는 제품입니다. 자체 MCP, 외부 서비스, 인증, 텔레메트리와 전역 설정은 포함하지 않습니다. 필요한 외부 기능은 사용자가 선택한 기존 플러그인이나 도구를 승인된 범위에서 사용합니다.

## 사용 경험

### 로컬 설치

저장소를 받은 뒤 다음 명령을 한 번 실행합니다.

```bash
codex plugin marketplace add /absolute/path/to/nulnul-harness-repository
codex plugin add nulnul-harness@nulnul-harness
```

그다음 새 Codex 세션을 시작합니다. 별도 초기화 명령은 없습니다.

설치 후 특별한 명령을 외울 필요 없이 다음처럼 요청합니다.

```text
이 프로젝트에 로그인 기능을 만들어줘.
```

설정이 없거나 자동화에 새 능력이 필요하면 nulnul harness가 검색과 준비를 처리하고 같은 흐름에서 원래 작업을 계속합니다. 이미 충분한 구성이 있으면 아무것도 덧붙이지 않습니다.

제거할 때는 다음을 실행합니다.

```bash
codex plugin remove nulnul-harness@nulnul-harness
codex plugin marketplace remove nulnul-harness
```

## 개발 검증

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
```

제출용 긍정·부정 시나리오는 `evals/`에 있으며 모두 통과해야 릴리스할 수 있습니다. 공개 배포 자료는 `submission/`에 정리합니다.
