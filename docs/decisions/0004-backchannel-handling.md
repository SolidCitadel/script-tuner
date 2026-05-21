# ADR-0004: 백채널 처리 — Monologue 재조립 시점에 한정해 skip

- **Status**: Accepted
- **Date**: 2026-05-22

## Context

SBCSAE는 다자 대화 코퍼스로, 화자 A의 발화 중간에 화자 B의 짧은 응답(예: `Okay`, `Yeah`, `Mhm`, `I see`)이 자주 끼어든다. 이러한 **백채널**을 어떻게 처리할지 결정해야 한다.

본 프로젝트의 타겟은 OPIc 1인 2~3분 모놀로그다. 백채널을 그대로 두면 A의 monologue 학습 시퀀스가 끊긴다.

## Decision

**백채널은 데이터에서 영구 제거하지 않는다. 단, 모듈 ③ Monologue 재조립 시점에 한해 skip한다.**

- 모듈 ②까지는 모든 발화를 보존
- 모듈 ③에서 동일 화자 연속 발화를 병합할 때, 중간에 끼어든 다른 화자의 백채널을 건너뛴다
- 백채널 식별 기준: 어휘 매칭(`Okay`, `Yeah`, `Right`, `Mhm`, `I see`, `Sure` 등) + 토큰 수 임계값(≤3 정도, 추후 튜닝)

### 예시

```
A: I want a tape deck that's gonna sound about you know as good as it can
B: Okay              ← 백채널, skip
A: and I think I want a tape deck with two places for two tapes
B: Okay              ← skip
A: so I can copy
```
→ A monologue: `I want a tape deck that's gonna sound about you know as good as it can and I think I want a tape deck with two places for two tapes so I can copy`

## Consequences

### 긍정적

- OPIc 모놀로그 구조와 매칭되는 학습 시퀀스 확보
- 백채널 데이터는 보존되므로, 향후 대화형 모델·백채널 생성 등 다른 용도로 재활용 가능

### 부정적

- 백채널 식별 휴리스틱(어휘+길이)이 완벽하지 않음 — 일부 짧지만 의미 있는 응답이 잘못 skip될 수 있음
- 임계값 튜닝 필요

## References

- [docs/design/preprocessing_pipeline.md](../design/preprocessing_pipeline.md)
- [docs/design/dataset_review.md](../design/dataset_review.md) — SBCSAE 턴 구조 미스매치 항목
