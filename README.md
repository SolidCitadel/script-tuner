# ScriptTuner

> 구어체 특화형 영어 스크립트 변환 모델 — OPIc 등 영어 말하기 평가 대비용 비원어민 스크립트를 파인튜닝된 어댑터로 자연스러운 구어체로 변환한다.

**팀**: QAIP (임준혁, 전현준, 최인재)

자세한 프로젝트 배경은 [`background/QAIP_proposal_report.md`](background/QAIP_proposal_report.md).

## 디렉토리 구조

```
aip/
├── scripttuner/                    # 메인 Python 패키지
│   ├── cli.py                      #   CLI 진입점 (subcommands)
│   ├── preprocessing/
│   │   ├── ir.py                   #   공통 IR (Utterance, Monologue)
│   │   ├── monologue.py            #   ③ Monologue 재조립
│   │   └── chat/                   #   CHAT (CHILDES) 어댑터
│   │       ├── parser.py           #     ① 파서
│   │       └── cleaner.py          #     ② 정규화
│   └── data_sources/
│       └── sbcsae.py               #   SBCSAE 다운로더
├── tests/                          # 단위 테스트
├── datasets/                       # 원본 데이터 (gitignore, 다운로드 스크립트로 확보)
├── data/                           # 파이프라인 산출물 (gitignore)
├── docs/                           # 프로젝트 문서
│   ├── status.md                   #   진행 현황 (자주 업데이트)
│   ├── design/                     #   정적 설계 문서
│   └── decisions/                  #   ADR — 결정 이력
├── background/                     # 외부 자료 (제안서 등)
├── .work/                          # 개인 작업 메모 (gitignore)
└── pyproject.toml
```

**아직 미생성 (계획)**: ④ LLM 역변환(`pairs.py`), ⑤ 통계(`stats.py`), 진단 모듈(`diagnosis/`), 변환 모델(`transform/`), 백엔드(`api/`). 진행도는 [`docs/status.md`](docs/status.md) 참조.

## 빠른 진입점

| 알고 싶은 것 | 보세요 |
|---|---|
| 지금 어디까지 진행됐는지 | [`docs/status.md`](docs/status.md) |
| 전처리 파이프라인 설계 | [`docs/design/preprocessing_pipeline.md`](docs/design/preprocessing_pipeline.md) |
| 데이터셋 분석 | [`docs/design/dataset_review.md`](docs/design/dataset_review.md) |
| "왜 이렇게 결정했는가" | [`docs/decisions/`](docs/decisions/) — ADR 목록 |
| 프로젝트 제안서 원본 | [`background/QAIP_proposal_report.md`](background/QAIP_proposal_report.md) |

## 데이터 라이선스

본 프로젝트가 사용하는 1차 데이터셋은 **SBCSAE (Santa Barbara Corpus of Spoken American English)**, CC BY-ND 3.0 US 라이선스이다. 정책은 [ADR-0002](docs/decisions/0002-sbcsae-license-policy.md) 참조.

- 원본 데이터는 git에 포함되지 않음 → `scripts/download_data.py`로 확보
- 전처리 산출물은 ND 조항에 따라 공개 배포하지 않음

## 환경 셋업

전제: Python 3.11+, [uv](https://docs.astral.sh/uv/) 설치 필요.

```bash
# 1) 의존성 설치 (.venv 생성)
uv sync

# 2) SBCSAE 데이터셋 다운로드 (60개 .cha → datasets/sbcsae/)
uv run scripttuner download sbcsae

# 3) 테스트 / 린트 / 타입체크
uv run pytest
uv run ruff check .
uv run mypy scripttuner tests scripts
```
