# ADR-0006: 어댑터 구조 + 공통 IR

- **Status**: Accepted
- **Date**: 2026-05-22

## Context

전처리 파이프라인의 첫 두 모듈(① 파서, ② Cleaner)은 본질적으로 코퍼스/포맷별 책임이다.

| 데이터셋 | 포맷 | 마커 체계 |
|---|---|---|
| SBCSAE | CHAT (CHILDES) | `(.)`, `&=tsk`, `⌈ ⌉`, `+/.` |
| Switchboard | NXT / .swb | `[laughter]`, `<um>`, `+/+` |
| BNC Spoken | XML/SGML | `<vocal desc="laugh"/>` |
| TED | plain text | 거의 마커 없음 |

처음 설계서(`preprocessing_pipeline.md` 초안)에는 "① 파서만 코퍼스별, ②~⑤ 재사용"으로 적혀 있었으나, 다시 검토 결과 ② Cleaner도 CHA-specific 마커를 다루므로 **① + ②가 어댑터 단위로 묶이는 게 맞다**.

이후 단계(③ Monologue 재조립, ④ LLM 역변환, ⑤ 통계)는 모든 코퍼스에서 동일하게 동작 가능하다 — 단, 통일된 입출력 표현이 필요하다.

## Decision

**어댑터 구조 + 공통 IR(Intermediate Representation)**을 채택한다.

### 디렉토리 구조

```
scripttuner/preprocessing/
├── ir.py                # 공통 IR — 모든 어댑터의 출력 표준
├── chat/                # CHAT (CHILDES) 어댑터 — SBCSAE 등
│   ├── parser.py        # ① CHAT 파서
│   └── cleaner.py       # ② CHAT 정규화
├── switchboard/         # (미래) Switchboard 어댑터
├── monologue.py         # ③ 공통
├── pairs.py             # ④ 공통
└── stats.py             # ⑤ 공통
```

### 공통 IR

단일 `Utterance` dataclass. 코퍼스 무관한 최소 공통 필드만 둔다.

```python
@dataclass(frozen=True)
class Utterance:
    source: str                       # 코퍼스 식별자 (e.g. "SBCSAE")
    utterance_id: str                 # 코퍼스 내 고유 ID (e.g. "SBC016#0042")
    speaker: str                      # 화자 식별자 (필수 — monologue 재조립의 키)
    text: str                         # stage에 따라 raw or cleaned
    t_start_ms: int | None = None     # 타임스탬프 (없으면 None)
    t_end_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### 필드 정당화 (공통성 검증)

| 필드 | SBCSAE | Switchboard | BNC | TED | 결론 |
|---|---|---|---|---|---|
| `source` | ✅ | ✅ | ✅ | ✅ | 필수 |
| `utterance_id` | 파일+seq | turn id | sentence id | seq | 부여 가능 |
| `speaker` | 다자 | A/B | 다자 | 1명 (`"speaker"`) | **필수 — monologue 키** |
| `text` | ✅ | ✅ | ✅ | ✅ | 필수 |
| `t_start/end_ms` | ✅ | ✅ | 부분 | 부분 | 옵셔널 (None 허용) |
| `metadata` | line_no 등 | NXT-specific | XML attrs | TED-specific | 코퍼스별 특화 흡수 |

### 단계별 의미

`text` 필드의 의미는 파이프라인 단계에 따라 다르다:
- 파서 출력: 코퍼스 마커가 보존된 원본 텍스트 (타임스탬프 토큰만 분리됨)
- Cleaner 출력: 정규화된 텍스트 (마커가 제거/변환됨, 공통 토큰 `<pause:short>` 등 포함)

stage 분리는 파일/디렉토리(`parsed/`, `cleaned/`)로 표현하므로 한 type 안에서 텍스트 의미가 컨텍스트로 결정된다.

## Consequences

### 긍정적

- ③~⑤ 모듈이 코퍼스 무관 — 새 데이터셋 추가 시 어댑터만 작성하면 됨
- IR이 미니멀 + 옵셔널 필드 + `metadata` dict로 over-engineering 회피
- 각 어댑터는 자기 포맷의 특수성을 흡수, 다음 단계로는 깔끔한 표준만 전달
- 본 PoC(SBCSAE 단독)에서도 미래 확장 비용이 낮음

### 부정적

- 어댑터마다 자체 cleaner를 작성해야 함 — 일부 마커 처리 로직은 중복 가능성. 공통 헬퍼는 필요 시 별도로 추출.
- IR 필드 확장 시 모든 어댑터의 후방 호환 검토 필요.

## Alternatives Considered

| 안 | 채택 안 한 이유 |
|---|---|
| 평탄 단순 구조 (parser.py + cleaner.py 직접) | SBCSAE 전용으로 의역. 미래 코퍼스 추가 시 대대적 리팩토링 필요 |
| 풍부 IR (Document/Speaker/Metadata 분리) | YAGNI — 본 단계 요구 대비 과함. 필요 시 metadata dict로 흡수 가능 |
| ① 파서만 어댑터, ② Cleaner 공통 | ② 가 CHA-specific 마커를 다뤄야 하므로 자연스럽지 않음 |

## References

- [docs/design/preprocessing_pipeline.md](../design/preprocessing_pipeline.md)
- [docs/design/dataset_review.md](../design/dataset_review.md) — 데이터셋별 포맷 차이
- `scripttuner/preprocessing/ir.py` — IR 구현
- `scripttuner/preprocessing/chat/parser.py` — 첫 어댑터 구현
