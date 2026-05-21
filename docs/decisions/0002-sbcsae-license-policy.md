# ADR-0002: SBCSAE 라이선스 대응 — 다운로드 스크립트 + gitignore

- **Status**: Accepted
- **Date**: 2026-05-22

## Context

SBCSAE는 **CC BY-ND 3.0 US** 라이선스로 배포된다.

- **BY (Attribution)**: 인용 의무 — 출처/저작자 명시 필수
- **ND (No Derivative Works)**: 파생물 공개 배포 금지 — 원본을 수정한 버전을 배포할 수 없음
- 원본 그대로의 재배포는 가능

본 프로젝트는 SBCSAE 원본을 정규화·monologue 재조립·LLM 역변환 등 다단계로 가공하므로, 산출물은 ND 조항의 "파생물"에 해당할 가능성이 높다. 또한 git에 원본 데이터를 직접 commit할지 여부도 결정해야 한다.

## Decision

1. **원본 데이터(`datasets/`)는 git에 commit하지 않는다.** 다운로드 스크립트(`scripttuner/data_sources/sbcsae.py`)로 확보한다.
2. **전처리 산출물(`data/`)은 gitignore한다.** 재생성 가능하며, ND 조항 위반 회피를 위해 공개 배포하지 않는다.
3. **다운로더 모듈은 라이선스/Citation 정보를 docstring 및 README에 명시한다.**
4. 다운로더는 공식 출처(TalkBank/OpenSLR)에서 받아오고, 무결성 체크(checksum)를 수행한다.

## Consequences

### 긍정적

- 라이선스 위반 위험 회피
- 출처 추적 가능 (TalkBank가 업데이트해도 재다운로드로 반영)
- 학생 프로젝트의 코드 저장소에 대용량 데이터 미포함 → 클론 부담 ↓
- 다른 코퍼스(Switchboard 등) 추가 시 동일 패턴(`data_sources/<corpus>.py`) 재사용 가능

### 부정적

- 협업자 환경 셋업 시 다운로드 단계 추가 필요 — README에 명시 필요
- 다운로드 URL이 사라지면 데이터 확보 불가 → 무결성 체크 및 대체 URL 관리 필요

## References

- [OpenSLR SBCSAE](http://www.openslr.org/155/)
- [TalkBank CABank English SBCSAE](https://talkbank.org/ca/access/SBCSAE.html)
- [UCSB SBCSAE](https://www.linguistics.ucsb.edu/research/santa-barbara-corpus-spoken-american-english)
- [docs/design/dataset_review.md](../design/dataset_review.md)
