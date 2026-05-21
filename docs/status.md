# 프로젝트 진행 현황

> 본 문서는 **상태 추적용**이다. 일상적으로 업데이트한다. 정적 설계는 `docs/design/`, 결정 이력은 `docs/decisions/`(ADR), 거친 작업 메모는 `.work/`(gitignore)에 둔다.

마지막 업데이트: 2026-05-22 (M8 완료)

---

## 마일스톤

| # | 마일스톤 | 상태 | 비고 |
|---|---|---|---|
| M0 | 제안서 확정 | ✅ 완료 | `background/QAIP_proposal_report.md` |
| M1 | 데이터셋 1차 검토 | ✅ 완료 | SBC016.cha → SBCSAE 전체 확보 필요 |
| M2 | 전처리 파이프라인 설계 | ✅ 완료 | `docs/design/preprocessing_pipeline.md` |
| M3 | 프로젝트 구조 및 라이선스 정책 | ✅ 완료 | ADR-0002 참조 |
| M4 | 패키지 골격 + uv 환경 구축 | ✅ 완료 | `scripttuner/`, `pyproject.toml`, `.gitignore`, ruff/mypy/pytest |
| M5 | SBCSAE 다운로더 구현 | ✅ 완료 | `scripttuner/data_sources/sbcsae.py`, 60개 CHA 확보 |
| M6 | 모듈 ① CHA 파서 구현 + 테스트 | ✅ 완료 | `scripttuner/preprocessing/chat/parser.py` + 공통 IR |
| M7 | 모듈 ② 정규화(Cleaner) | ✅ 완료 | `scripttuner/preprocessing/chat/cleaner.py` |
| M8 | 모듈 ③ Monologue 재조립 | ✅ 완료 | `scripttuner/preprocessing/monologue.py` |
| M9 | 모듈 ④ LLM 역변환 | ⏳ 대기 | 프롬프트 설계 필요 |
| M10 | 모듈 ⑤ 통계 산출 | ⏳ 대기 | |
| M11 | SBC016.cha PoC End-to-End | ⏳ 대기 | 전 모듈 통합 검증 |
| M12 | SBCSAE 60개 확장 적용 | ⏳ 대기 | |
| — | 진단 모듈 / 변환 모델 / 백엔드 / UI | 미정 | 본 PoC 이후 |

## 결정 이력 (ADR)

- [ADR-0001](decisions/0001-jsonl-output-format.md) — 학습 데이터 출력 포맷으로 JSONL 채택
- [ADR-0002](decisions/0002-sbcsae-license-policy.md) — SBCSAE 라이선스 대응 (다운로드 스크립트 + gitignore)
- [ADR-0003](decisions/0003-pause-marker-tokenization.md) — 포즈 마커 특수 토큰화
- [ADR-0004](decisions/0004-backchannel-handling.md) — 백채널 처리 정책
- [ADR-0005](decisions/0005-style-as-dataset-metadata.md) — 스타일 레이블을 데이터셋 메타속성으로
- [ADR-0006](decisions/0006-adapter-structure-and-common-ir.md) — 어댑터 구조 + 공통 IR

## 다음 액션 (단기)

1. 모듈 ④ LLM 역변환 (`scripttuner/preprocessing/pairs.py`) — 프롬프트 설계 + LLM 호출, (구어체 → 문어체) 페어 생성

## 보류 / 추후 결정

- **Semi-formal 스타일 데이터 확보 방안** — 인터뷰/TED 등 monologue 코퍼스 후보 조사 필요
- **제어 토큰 학습 전략** — Semi-formal 데이터 확보 후
- **진단 모듈 feature set 최종화** — 본 PoC 통계 결과 보고 결정
- **LLM 역변환에 사용할 모델** — Claude / GPT / Gemini 중 비용·품질 비교
- **모델 변환 베이스 선택** — T5Gemma 2 vs Gemma 4 (제안서 후보 중)