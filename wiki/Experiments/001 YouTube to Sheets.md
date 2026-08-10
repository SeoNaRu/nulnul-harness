# 001 · YouTube → Sheets

## 목적

코인·주식 관련 YouTube 채널을 찾고, 관련성을 분류하고, 중복을 제거해 Google Sheets에 저장하는 워크플로로 `nulnul-harness`의 첫 성능 근거를 만든다.

## 현재 마일스톤

외부 API와 개인정보 없이 분류·중복 제거 품질을 반복 측정할 수 있는 고정 벤치마크를 만든다.

완료 검사:

```bash
python3 scripts/score_youtube_sheets.py \
  evals/benchmarks/youtube-sheets/fixture.json \
  evals/benchmarks/youtube-sheets/example-output.json
```

통과 조건은 precision, recall, classification accuracy가 모두 `1.0`, duplicate rate와 schema error가 모두 `0`인 것이다.

## 고정 조건

- 입력은 합성 채널 데이터다. 실제 인물이나 채널 성능을 주장하지 않는다.
- Google 인증과 외부 시트 쓰기는 별도 승인 전까지 실행하지 않는다.
- 기준 실행과 하네스 실행은 같은 모델·프롬프트·시간 제한을 사용한다.
- 설정 생성 시간과 토큰을 전체 비용에 포함한다.
- 각 조건을 최소 3회 반복한다.

## 측정값

| 지표 | 상태 |
| --- | --- |
| Precision | 채점기 준비 |
| Recall | 채점기 준비 |
| Classification accuracy | 채점기 준비 |
| Duplicate rate | 채점기 준비 |
| Task success | A/B 실행 전 |
| Token cost | A/B 실행 전 |
| Completion time | A/B 실행 전 |
| Human interventions | A/B 실행 전 |

## 실행 기록

### 2026-08-10 · 평가 계약 생성

- 합성 후보 6건과 고유 채널 정답 5건을 고정했다.
- 금융 채널 3건, 비관련 채널 2건, 중복 수집 1건을 포함했다.
- 정답 예시는 자동 채점에서 통과해야 한다.
- 성능 수치는 아직 기록하지 않는다.

### 2026-08-10 · 깨끗한 저장소 전체 흐름 실행

- `nulnul-harness`가 암묵적으로 활성화됐다.
- Google Apps Script의 YouTube 고급 서비스와 `SpreadsheetApp`을 선택하고 새 의존성이나 추가 에이전트는 만들지 않았다.
- 검색, 분류, 채널 ID 중복 제거, 검토자 결정, 학습, 수식 삽입 방지, upsert와 실행 기록을 구현했다.
- 외부 Google 호출 없이 모의 전체 실행이 통과했다.
- Google 인증, 실제 API quota 사용, 트리거 생성과 시트 쓰기는 실행하지 않았다.

### 2026-08-10 · 운영 시트 읽기 전용 관찰

- 원본 Google Sheet의 셀·탭·권한은 수정하거나 삭제하지 않았다.
- 리드, 2차 검수, 조사 기록, 연락 완료 제외의 네 단계 구조를 확인했다.
- 안정 키 중복 제거, 제외목록 우선, 직접 연락 가능 여부별 라우팅, 판정 사유 보존을 공개 예제 계약으로 채택했다.
- 원본에는 개인 연락처와 메시징 정보가 있으므로 어떤 실제 행도 저장소에 복사하지 않았다.
- 공개 예제는 합성 이름과 `.invalid` 예약 도메인만 사용하며 회귀 테스트로 이를 강제한다.

## 다음 실행

동일한 입력으로 하네스 없음/있음 각각 3회 결과를 만들고 자동 채점한다. 이후 실제 YouTube 검색과 Google Sheets 쓰기는 읽기·인증·비용·외부 쓰기 경계를 별도로 승인받아 연결한다.
