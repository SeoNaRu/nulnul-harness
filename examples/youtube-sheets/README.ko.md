# 조사 자료를 검수용 워크북으로 정리하기

[English](README.md) | [한국어](README.ko.md) | [전체 사례](../README.ko.md)

**상태: 2026-09-09 기대 출력 비교와 관련 테스트 5개 통과.** 모든 행은 합성 데이터이며 URL은 예약 도메인 `.invalid`, 연락처는 `example.invalid`를 사용합니다. 실제 4단계 크리에이터 조사 업무의 형태를 재현하지만 원본 행, 신원, 채널 URL, 연락처, 비공개 메모를 공개하지 않습니다. [로컬 검증 기록](../validation-2026-09-09.json)을 참고하세요.

## 요청과 결과물

> 이 합성 조사 결과를 검수용 워크북으로 정리해 주세요. 같은 채널을 합치고, 이미 연락한 채널을 제외하고, 주어진 품질 규칙을 적용한 뒤 직접 연락 가능한 대상과 재검수가 필요한 대상을 나누세요. 감사 기록도 남겨 주세요.

[input.json](input.json)과 [expected.json](expected.json)을 비교할 수 있습니다. 새로운 측정이 아닌 기존 기대 출력은 다음과 같습니다.

| 단계 | 공개된 기대 결과 |
| --- | --- |
| 발견 | 입력 10행을 채널 기록 9개로 통합 |
| 연락 가능 | `leads` 2행 |
| 재검수 | `needs_second_review` 3행 |
| 감사 | 거절된 채널 4개를 포함해 고유 채널 9개 모두 `research_log`에 유지 |
| 제외 목록 | 이전에 연락한 채널 식별자 1개 |

중복 발견한 암호화폐 채널에는 두 발견 경로와 더 나은 연락 경로가 남습니다. 채널 링크만 있는 경우, 간접 경로, 연락처 누락은 서로 다른 재검수 이유를 가집니다. 관련 없는 행의 수식 형태 이름은 감사 출력에서 이스케이프됩니다.

## 실행과 완료 검사

저장소 루트에서 실행합니다.

```bash
python3 scripts/build_youtube_sheets_example.py \
  examples/youtube-sheets/input.json
```

생성된 JSON은 공개된 기대 구조와 같아야 합니다. 다음 명령은 파싱한 값을 비교하며 기대 답안을 덮어쓰지 않습니다.

```bash
python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

actual = json.loads(subprocess.check_output([
    sys.executable, 'scripts/build_youtube_sheets_example.py',
    'examples/youtube-sheets/input.json',
], text=True))
expected = json.loads(Path('examples/youtube-sheets/expected.json').read_text(encoding='utf-8'))
if actual != expected:
    raise SystemExit('FAIL: output differs from the published expected workbook')
print('PASS: output matches the published expected workbook')
PY
```

## 기능 선택과 거절 조건

기존 [생성기](../../scripts/build_youtube_sheets_example.py), 입력, 기대 출력을 재사용합니다. 새 조사 에이전트, Google 연결 도구, 스크래핑 서비스, 스프레드시트 쓰기 도구를 추가하지 않았습니다. 이 공개 입력만으로 원래 실제 에이전트가 어떤 설치 기능을 선택했는지 알 수는 없습니다.

이미 연락한 채널, 장기 미활동 채널, 기준보다 작은 채널, 관련 없는 채널은 연락 대상으로 들어가면 안 됩니다. 채널 링크만 있는 경로를 직접 연락처로 취급하거나 중복 발견을 별도 연락 대상으로 만들면 안 됩니다. 현재 공개 입력에는 이 거절 조건들이 포함되어 있지만, 가능한 모든 정책 임곗값을 시험하지는 않습니다.

## 증거와 한계

이 예제는 3.1.0 저장소에 이미 있었습니다. 제품 아카이브에는 플러그인만 포함되며 예제 입력은 들어 있지 않습니다. 위의 기대 출력 비교와 `python3 -m unittest discover -s tests -p 'test_youtube_sheets_example.py' -v`가 2026-09-09에 통과했으며 테스트는 5개입니다. 로컬 결정론적 재실행이지 새로운 실제 조사 세션은 아닙니다. 이 사례의 실행 시간, 토큰 비용, 금전 비용, 독립적으로 측정한 하네스 우위는 `unknown`입니다.

결과물은 워크북 구조의 JSON이며 XLSX 파일이나 실제 Google 스프레드시트가 아닙니다. 실제 유튜브 수집 범위, 연락처 정확도, 연락 성공률, 금융 판단을 입증하지 않습니다. 금융 주제 채널은 합성 업무 데이터이지 추천이 아닙니다. 외부에서 가져오거나 업로드하거나 연락을 보내지 않습니다.
