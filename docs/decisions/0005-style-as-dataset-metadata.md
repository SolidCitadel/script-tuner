# ADR-0005: 스타일 레이블을 데이터셋 메타속성으로 부여

- **Status**: Accepted
- **Date**: 2026-05-22

## Context

제안서는 Casual / Semi-formal spoken 두 가지 발화 스타일을 제어 토큰 기반 조건부 생성으로 다룬다. 이를 위해 학습 데이터의 스타일 레이블을 어떻게 부여할지 결정해야 한다.

후보:

- (a) 청크별 분류기(머신러닝 또는 LLM)로 자동 레이블링
- (b) 데이터셋 단위로 일괄 메타속성 부여

SBCSAE 안에서 청크별로 Casual vs Semi-formal을 구분할 신호는 약하다 (전체적으로 일상 대화 톤). 청크별 분류기를 도입하면 노이즈가 큰 레이블이 학습 데이터에 들어갈 위험이 있다.

## Decision

**스타일은 데이터셋 단위 메타속성으로 일괄 부여한다.**

- SBCSAE → `style: "casual"`
- (향후) 인터뷰/TED/팟캐스트 등 monologue 코퍼스 → `style: "semi_formal"`
- 청크별 분류기 모듈은 두지 않는다

## Consequences

### 긍정적

- 단순·일관·재현 가능
- 데이터셋 추가 시 메타속성 한 줄로 분류 끝
- 노이즈 큰 자동 레이블링 회피
- 본 PoC는 Casual 단일 스타일로 진행, Semi-formal 데이터 확보 후 추가 가능
- 제어 토큰 슬롯(`<style:casual>` / `<style:semi_formal>`)을 미리 설계해 두면 향후 학습에 바로 적용 가능

### 부정적

- 한 데이터셋 안에 두 스타일이 섞여 있어도 구분 불가 — 데이터셋 선정 시 스타일 일관성을 신중히 검토해야 함
- Semi-formal spoken 데이터를 SBCSAE에서 추출할 수 없음 → 별도 코퍼스 확보 필요

## References

- [docs/design/preprocessing_pipeline.md](../design/preprocessing_pipeline.md)
- [docs/design/dataset_review.md](../design/dataset_review.md)
- [background/QAIP_proposal_report.md](../../background/QAIP_proposal_report.md) — 제안서의 발화 스타일 조건부 생성 섹션
