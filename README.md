# ScriptTuner

> 구어체 특화형 영어 스크립트 변환 모델 — OPIc 등 영어 말하기 평가 대비용 비원어민 스크립트를 파인튜닝된 어댑터로 자연스러운 구어체로 변환한다.

**팀**: QAIP (임준혁, 전현준, 최인재)

자세한 프로젝트 배경은 [`background/QAIP_proposal_report.md`](background/QAIP_proposal_report.md).

## 디렉토리 구조

```
aip/
├── scripttuner/             # 메인 Python 패키지 (예정)
│   ├── preprocessing/       #   ① 파서 ② 정규화 ③ 재조립 ④ 역변환 ⑤ 통계
│   ├── data_sources/        #   데이터셋 다운로더
│   ├── diagnosis/           #   (미래) 진단 모듈
│   ├── transform/           #   (미래) 변환 모델
│   ├── api/                 #   (미래) 백엔드
│   └── cli.py               #   CLI 진입점
├── scripts/                 # 일회성 실행 스크립트
├── tests/                   # 단위 테스트
├── datasets/                # 원본 데이터 (gitignore, 다운로드 스크립트로 확보)
├── data/                    # 파이프라인 산출물 (gitignore)
├── docs/                    # 프로젝트 문서
│   ├── status.md            #   진행 현황 (자주 업데이트)
│   ├── design/              #   정적 설계 문서
│   └── decisions/           #   ADR — 결정 이력
├── background/              # 외부 자료 (제안서 등)
├── .work/                   # 개인 작업 메모 (gitignore)
└── pyproject.toml
```

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

- 원본 데이터는 git에 포함되지 않음 → 다운로드 스크립트로 확보 (구현 예정)
- 전처리 산출물은 ND 조항에 따라 공개 배포하지 않음

## 환경 셋업 (예정)

```bash
# uv 기반 환경 (계획)
uv sync
uv run python scripts/download_data.py sbcsae
uv run python -m scripttuner.cli preprocess datasets/sbcsae/SBC016.cha
```

상세 구현은 진행 중이다. [`docs/status.md`](docs/status.md) 참조.
