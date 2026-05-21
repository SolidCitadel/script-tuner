# ADR-0001: 학습 데이터 출력 포맷으로 JSONL 채택

- **Status**: Accepted
- **Date**: 2026-05-22

## Context

전처리 파이프라인의 각 모듈 산출물 및 최종 학습 페어를 어떤 포맷으로 저장할지 결정해야 한다. 후보는 JSONL, Parquet, Arrow, CSV/TSV 등이다.

데이터 규모는 SBCSAE 60개 풀 처리 시 수천~수만 페어 수준. PoC 단계에서는 변환 품질을 사람이 직접 검수해야 한다.

## Decision

**JSONL(JSON Lines)을 모든 모듈의 영구 저장 포맷으로 채택한다.**

- 모듈별 중간 산출물을 분리해서 JSONL로 저장
- 통계(`stats`)는 단일 JSON 파일
- 학습 시 HuggingFace `datasets`로 직접 로드하거나 필요 시 parquet으로 변환

## Consequences

### 긍정적

- 사람이 직접 들여다보기 쉬움 (PoC 검수 친화)
- 라인 단위 append/스트리밍 가능
- HuggingFace `datasets`, `trl`, `peft` 등 파인튜닝 도구 표준 입력
- 모듈 한 곳 재실행 시 앞 단계 캐시 재활용 가능

### 부정적

- 압축률 낮음 — 데이터 규모가 수십만 이상으로 커지면 parquet 재검토 필요
- 컬럼 단위 쿼리 비효율 — 본 단계 사용 패턴(전체 로드 후 처리)엔 무관

## References

- [docs/design/preprocessing_pipeline.md](../design/preprocessing_pipeline.md)
