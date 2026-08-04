# Project Harness

Project Harness는 사용자가 하네스를 배우지 않아도 새 프로젝트를 바로 시작하게 해주는 Codex 플러그인입니다.

평소처럼 만들고 싶은 것을 요청하면 에이전트가 먼저 저장소를 읽고, 코드에서 알 수 없는 목표·완료 조건·제약만 짧게 확인합니다. 그런 다음 프로젝트에 필요한 규칙, 스킬, 에이전트 구성과 검증 절차를 로컬에 만들고 원래 요청을 계속 수행합니다. 이후 작업에서는 실제 결과, 반복 실패, 테스트와 사용자 수정을 근거로 그 구성을 개선합니다.

## 제품 구조

```text
.agents/plugins/marketplace.json
plugins/project-harness/
├── .codex-plugin/plugin.json
└── skills/project-harness/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── references/
    └── assets/
tests/test_product_plugin.py
```

`plugins/project-harness/`만 사용자에게 설치되는 제품입니다. MCP, 외부 서비스, 전역 설정은 포함하지 않습니다.

## 사용 경험

### 로컬 설치

저장소를 받은 뒤 다음 명령을 한 번 실행합니다.

```bash
codex plugin marketplace add /absolute/path/to/project-harness-repository
codex plugin add project-harness@project-harness
```

그다음 새 Codex 세션을 시작합니다. 별도 초기화 명령은 없습니다.

설치 후 특별한 명령을 외울 필요 없이 다음처럼 요청합니다.

```text
이 프로젝트에 로그인 기능을 만들어줘.
```

프로젝트 설정이 없으면 Project Harness가 준비 작업을 처리하고 같은 흐름에서 로그인 기능 구현을 계속합니다. 이미 충분한 설정이 있으면 새 구성을 만들지 않고 기존 규칙을 사용합니다.

제거할 때는 다음을 실행합니다.

```bash
codex plugin remove project-harness@project-harness
codex plugin marketplace remove project-harness
```

## 개발 검증

```bash
python3 -m unittest discover -s tests -p 'test_product_plugin.py' -v
```

현재 제출용 5개 긍정·3개 부정 시나리오는 `evals/`에 있으며 모두 통과해야 릴리스할 수 있습니다. 공개 배포 자료는 `submission/`에 정리합니다.
