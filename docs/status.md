# 프로젝트 진행 현황

> 본 문서는 **상태 추적용**이다. 일상적으로 업데이트한다. 정적 설계는 `docs/design/`, 결정 이력은 `docs/decisions/`(ADR), 거친 작업 메모는 `.work/`(gitignore)에 둔다.

마지막 업데이트: 2026-05-24

---

## 마일스톤

**M0~M13: PoC 전처리 파이프라인 + SBCSAE 60파일 배치 완료** ✅
`scripttuner run sbcsae --all` 한 명령으로 60파일 end-to-end. 산출: `data/pairs/SBCSAE/_all.jsonl` (1,757 pairs / 131 speakers) + `data/stats/SBCSAE/_aggregate.json`. 자세한 진행 이력은 `git log` 및 아래 ADR 목록 참조.

| # | 마일스톤 | 상태 | 비고 |
|---|---|---|---|
| — | 진단 모듈 / 변환 모델 / 백엔드 / UI | 미정 | 본 PoC 이후 — 모델 베이스 선택, 학습 파이프라인 |

## 결정 이력 (ADR)

- [ADR-0001](decisions/0001-jsonl-output-format.md) — 학습 데이터 출력 포맷으로 JSONL 채택
- [ADR-0002](decisions/0002-sbcsae-license-policy.md) — SBCSAE 라이선스 대응 (다운로드 스크립트 + gitignore)
- [ADR-0003](decisions/0003-pause-marker-tokenization.md) — 포즈 마커 특수 토큰화
- [ADR-0004](decisions/0004-backchannel-handling.md) — 백채널 처리 정책
- [ADR-0005](decisions/0005-style-as-dataset-metadata.md) — 스타일 레이블을 데이터셋 메타속성으로
- [ADR-0006](decisions/0006-adapter-structure-and-common-ir.md) — 어댑터 구조 + 공통 IR
- [ADR-0007](decisions/0007-llm-client-provider-agnostic-and-caching.md) — LLM 클라이언트 provider-agnostic + 디스크 캐싱
- [ADR-0008](decisions/0008-pause-token-strip-on-llm-input.md) — LLM 입력 전 pause 토큰 strip (spoken 보존)

## 다음 액션 (단기)

1. 팀에 `_all.jsonl` + `_aggregate.json` 공유 → 학습 방법 검토 피드백 수렴.
2. 본격 학습/모델 단계로 전환 — 변환 모델 베이스 선택, 진단 모듈, 학습 파이프라인.

## 보류 / 추후 결정

- **Semi-formal 스타일 데이터 확보 방안** — 인터뷰/TED 등 monologue 코퍼스 후보 조사 필요
- **제어 토큰 학습 전략** — Semi-formal 데이터 확보 후
- **진단 모듈 feature set 최종화** — M11 통계 결과 보고 결정
- **모델 변환 베이스 선택** — T5Gemma 2 vs Gemma 4 (제안서 후보 중)
- **few-shot 도입 시점** — 현재 zero-shot 결과 양호. 후속 코퍼스 추가/품질 이슈 시 재검토
- **정량 품질 메트릭** — 본격 학습 단계 진입 시 BLEU/embedding similarity 등 도입 결정