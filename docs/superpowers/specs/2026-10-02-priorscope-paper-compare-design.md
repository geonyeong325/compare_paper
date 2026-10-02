# PriorScope 1차 MVP 설계: 논문 대 논문 차별성 비교

- 작성일: 2026-10-02
- 상태: 사용자 검토 대기
- 기반: `PriorScope 프로젝트 기획서.docx`(특허 비교용 초안)를 논문 대 논문 비교로 수정, 전남대 생성형 AI 트랙 1차 가이드(`hr-ai-service-workflow` 스타터) 구조를 따름

## 1. 목적과 범위

### 1.1 목적
투고하려는 논문(이하 "내 논문")과 기존 논문 1편을 1:1로 비교해, 내 논문의 핵심 기술 요소마다 기존 논문에 이미 있는지를 근거 위치와 함께 판정한다. 결과로 겹치는 요소, 내 논문 고유 요소(차별점), 같은 실험 조건의 정량 비교(강점), 차별성 서술 제안과 Related Work 초안을 보여준다.

### 1.2 사용자
주 사용자는 논문 초안을 쓴 공학 계열 대학원생이다. 지도교수 미팅 전이나 리뷰에서 "기존 연구와 뭐가 다른가"를 지적받았을 때 쓴다.

### 1.3 핵심 원칙
1. **허위 신규 주장 회피가 제1 원칙이다.** 근거를 특정하지 못한 대응은 "없음"이 아니라 "확인필요"로 보낸다. 검증 단계는 판정을 강등만 하고 승격하지 않는다.
2. 모든 대응 판정에는 근거 위치(섹션 번호)를 붙인다. 근거 없는 일치/유사/없음 판정은 표시하지 않고 확인필요로 내린다.
3. 숫자 계산(번호 검증, 커버리지, 등급, 수치 대소 비교)은 코드가 하고, 의미가 같은지의 판단만 LLM(Studio)이 한다.

### 1.4 1차 범위
- 입력: PDF 2개(내 논문, 기존 논문). 언어는 국문과 영문이 섞일 수 있다.
- 대응 기준축: **내 논문의 핵심 기술 요소(M1…Mn)**. 요소마다 기존 논문 요소(P1…Pn)와 대응을 판정한다.
- 강점: **정량 비교만** 한다. 같은 데이터셋과 같은 지표의 결과가 양쪽에 있을 때만 수치를 나란히 비교한다.
- 구현 도구: Upstage Studio 에이전트 3개, Python(OpenAI 호환 SDK), Streamlit, Railway 배포.

### 1.5 하지 않는 것 (1차)
- 비교할 논문 검색 (2차: ChromaDB 기반 추천)
- 정성적 강점 서술 (2차)
- 여러 논문 동시 비교 (2차)
- 표절·심사 판정, 논문 우수성 평가. 결과는 사전 점검용이다.
- 스캔본 PDF의 OCR 정확도 보장
- 로그인, 사용자별 권한

### 1.6 2차 방향 (참고)
LLM 직접 호출(LangGraph), FastAPI, ChromaDB로 관련 논문 자동 검색, Docker. 정성 강점 비교 추가. 1차의 `validator.py`와 `eval/`은 그대로 재사용한다.

## 2. 아키텍처

### 2.1 실행 흐름
```
my_paper.pdf    → [My Paper Agent]    → my_paper.json    ┐
                                                          ├→ [compare_builder.py] → Compare_Input.pdf
prior_paper.pdf → [Prior Paper Agent] → prior_paper.json ┘                              ↓
                                                                               [Compare Agent]
                                                                                        ↓
                                                                          compare_result.json (LLM 원본)
                                                                                        ↓
                                                                               [validator.py]
                                                                                        ↓
                                                                          verified_result.json → Streamlit
```
Studio 에이전트는 PDF만 입력받으므로, 두 JSON은 코드가 PDF 한 장으로 다시 조립해 Compare Agent에 넘긴다(가이드의 핵심 패턴).

### 2.2 번호 부여 규칙
- `compare_builder.py`와 `validator.py`는 같은 함수 `assign_ids(my_paper, prior_paper)`로 번호를 만든다.
- `core_techniques` 배열 순서대로 내 논문은 M1…Mn, 기존 논문은 P1…Pn을 붙인다.
- `experiment_results` 배열 순서대로 R-M1…, R-P1…을 붙인다.
- 번호는 결정적이다. 같은 JSON에서는 항상 같은 번호가 나온다.

### 2.3 파일 구조
스타터 `hr-ai-service-workflow/`는 참고용으로 그대로 두고, `llmops/priorscope/`에 복사해 수정한다.

| 파일 | 상태 | 역할 |
|---|---|---|
| `agent_client.py` | 수정(소) | Studio 호출. 상태 확인에 최대 대기 시간(기본 180초)을 추가 |
| `upload.py`, `file_manager.py` | 그대로 | Files API 업로드, JSON 입출력 |
| `config.py` | 수정 | 에이전트 ID와 CONFIG ID 6개, 경로를 `run_paths(run_dir)` 함수로 제공 |
| `my_paper_agent.py`, `prior_paper_agent.py`, `compare_agent.py` | 이름 변경 | 스타터의 resume/jd/matching 에이전트 모듈 |
| `ids.py` | 신규 | `assign_ids()` (builder와 validator가 공유) |
| `compare_builder.py` | 신규 | `matching_builder.py` 대체. 번호가 붙은 비교용 PDF 생성(ReportLab, 나눔고딕) |
| `validator.py` | 신규 | 코드 검증 층. 순수 함수로만 구성하고 LLM은 관여하지 않음 |
| `app.py` | 수정 | 1~5단계 오케스트레이션. CLI 옵션 `--from-json <run_dir>`로 비교 단계부터 재실행 |
| `service.py` | 수정 | UI용 진입점 `run_compare_service(my_path, prior_path, on_step)`. 실패하면 즉시 중단(이전 결과로 대체하지 않음) |
| `streamlit_app.py` | 신규 작성 | 결과 화면 |
| `agent_configs/*.json` | 교체 | Studio에서 내보낸 스키마 정답지 3개 |
| `tests/` | 신규 | validator, ids, builder 단위 테스트(pytest, Studio 호출 없음) |
| `eval/` | 신규 | 샘플 라벨과 `evaluate.py` |

### 2.4 실행 디렉터리
- 실행마다 `runs/<run_id>/`를 만들고 그 안에 `my_paper.json`, `prior_paper.json`, `Compare_Input.pdf`, `compare_result.json`, `verified_result.json`을 저장한다. 공개 URL에서 동시에 실행해도 결과가 섞이지 않게 하기 위해서다.
- `run_id`는 `YYYYMMDD-HHMMSS-<6자리 랜덤>` 형식이다.
- 로컬 `python app.py`는 기본 입력으로 `data/` 샘플 PDF를 쓴다.
- `runs/`는 `.gitignore`에 추가한다.

### 2.5 스타터 대비 고치는 동작
- `service.py`: 단계가 실패해도 계속 진행하고 디스크의 이전 결과를 읽어 보여주는 동작을 제거한다. 실패하면 `StepError`를 던진다.
- `agent_client.py`: 상태 확인 무한 루프에 최대 대기 시간을 추가하고, 넘기면 `TimeoutError`를 던진다.

## 3. Studio 에이전트 스키마

Studio Extract 결과는 모든 필드가 배열이다. "단일"로 적은 필드는 원소를 1개만 두고, 코드는 `[0]`으로 읽는다.

### 3.1 공통 요소 분해 규칙
두 Paper Agent의 `core_techniques` 설명에 아래 문구를 **똑같이** 넣는다.

> 원소 하나에는 기법·모듈·학습 절차를 하나만 담는다. 쉼표나 세미콜론으로 여러 개를 합치지 않는다. 형식은 `[섹션번호] 원문 표현 | 한국어 설명`이다. 원문 표현은 논문의 원래 언어를 그대로 쓴다.

### 3.2 My Paper Agent / Prior Paper Agent (Parse → Extract)

| 필드 | My | Prior | 설명 |
|---|---|---|---|
| `title` | ✔ | ✔ | 단일. 논문 제목 |
| `language` | ✔ | ✔ | 단일. `ko` 또는 `en` |
| `research_field` | ✔ | ✔ | 단일. 연구 분야 |
| `problem` | ✔ | ✔ | 해결하려는 문제 또는 기존 방법의 한계 |
| `core_techniques` | ✔ | ✔ | 3.1 규칙을 따름. 대응표의 단위 |
| `experiment_results` | ✔ | ✔ | 그 논문이 **제안한 방법의 결과만** 담음. 형식은 `데이터셋 \| 실험 설정 \| 지표 \| 수치 \| ↑ 또는 ↓ \| [표/섹션]` (3.5 참고) |
| `keywords` | ✔ | ✔ | 3~6개 |
| `contributions` | ✔ | | 저자가 주장하는 기여점. `[섹션] 내용` |
| `citation_info` | | ✔ | 단일. `저자, 학회 또는 저널, 연도` |
| `limitations` | | ✔ | 기존 논문이 스스로 밝힌 한계. `[섹션] 내용` |

두 에이전트의 공통 필드는 이름, 유형, 목록 여부를 똑같이 맞춘다.

### 3.3 Compare Agent (Parse → Classify → Extract×3)

**Classify 문서종**

| 분류 | 설명 |
|---|---|
| High Overlap | 내 논문의 핵심 요소 대부분이 기존 논문에 이미 있어서 차별성 보강이 꼭 필요한 경우 |
| Medium Overlap | 일부 요소가 겹치지만 내 논문에만 있는 구성이 있는 경우 |
| Low Overlap | 분야나 개념만 비슷하고 핵심 구성은 다른 경우 |

**Extract 스키마**: 3개 노드(`Extract_HighOverlap`, `Extract_MediumOverlap`, `Extract_LowOverlap`) 모두 동일하다.

| 필드 | 형식 / 설명 |
|---|---|
| `overlap_level` | 단일. Classify 결과 |
| `llm_score` | 단일, 숫자 0~100. 참고값으로만 씀 |
| `summary` | 단일. 두 논문의 관계 2~3문장 |
| `element_mapping` | M 요소마다 한 원소. `M2 ↔ P4,P5 \| 유사 \| M[3.1] / P[2.3] \| 설명`. 대응하는 P가 없으면 `M3 ↔ - \| 없음 \| 검토 범위 \| 설명`. 판정은 `일치`, `유사`, `없음`, `확인필요` 중 하나 |
| `result_pairs` | `R-M1 ~ R-P2 \| 동일 조건 또는 조건 다름 \| 설명`. 데이터셋과 지표가 같은 쌍만 담고, 실험 설정까지 같으면 `동일 조건`, 다르면 `조건 다름` |
| `caution_points` | 차별성을 분명히 해야 할 지점 |
| `differentiation_suggestions` | 바로 쓸 수 있는 서술 제안 3개 |
| `related_work_draft` | 단일. 내 논문 언어로 쓴 1~2문장. `citation_info`를 인용 |

**Extract 지시문에 넣을 요구사항**
- 같은 기술을 다른 용어나 다른 언어(국문/영문)로 쓴 경우도 대응으로 본다.
- 대응을 확신하지 못하면 "없음"이 아니라 "확인필요"로 적는다.
- 겹치는 요소와 고유 요소는 LLM에게 따로 묻지 않는다. 코드가 `element_mapping`에서 파생하므로, 대응표와 요약이 서로 어긋날 수 없다.

### 3.4 비교용 PDF (`Compare_Input.pdf`) 구성
1. 안내문: 번호 체계와 출력 형식 설명
2. 내 논문: 제목, 문제, `M1…Mn`(원문 | 한국어 설명), `contributions`, `R-M1…`
3. 기존 논문: 제목, 인용 정보, 문제, `P1…Pn`, `limitations`, `R-P1…`

### 3.5 추출 방법과 실험 결과 형식

**추출 방법**: 추출은 코드가 아니라 Studio 에이전트 안의 두 노드가 한다.
- **Parse 노드 (Upstage Document Parse)**: PDF를 제목·문단·표·목록 구조를 살린 텍스트(HTML)로 바꾼다. 표의 행과 열이 유지되므로 실험 결과 표를 읽을 수 있다. 스캔본은 OCR로 처리한다.
- **Extract 노드 (Information Extract)**: 필드마다 LLM이 문서를 읽고 값을 채운다. 필드의 **설명이 사실상 프롬프트**이므로, 추출 품질은 설명 문구로 정해진다. 샘플 논문으로 Studio 화면에서 실행해 보며 문구를 다듬는다.

| 필드 | Extract 설명(요지) | 주로 읽는 곳 |
|---|---|---|
| `title` | 논문 제목 하나 | 첫 페이지 상단 |
| `language` | 본문 언어. `ko` 또는 `en` | 본문 |
| `research_field` | 연구 분야 한 구절 | 초록, 키워드 |
| `problem` | 해결하려는 문제나 기존 방법의 한계. 문제 하나당 원소 하나 | 초록, 서론 |
| `core_techniques` | 3.1 공통 분해 규칙 | 방법론 섹션 소제목과 본문 |
| `experiment_results` | 아래 형식. 제안 방법의 결과만 | 실험 섹션의 표 |
| `keywords` | 키워드 3~6개 | 키워드 란, 초록 |
| `contributions` | 저자가 명시한 기여("our contributions are…") | 서론 끝부분 |
| `citation_info` | 저자, 학회 또는 저널, 연도 | 첫 페이지 헤더·푸터 |
| `limitations` | 저자가 스스로 밝힌 한계 | 결론, Limitations 섹션 |

LLM 추출이라 정확도가 100%는 아니다. 코드의 형식 검사(4장)와 평가 샘플(7.3)로 보완한다.

**`experiment_results` 형식 (6칸)**: 실험 결과 한 건을 구분자 `|`로 이은 문자열 하나로 받는다. 필드별 배열로 따로 받으면 원소 하나만 빠져도 짝이 어긋나기 때문이다.
```
데이터셋 | 실험 설정 | 지표 | 수치 | 방향 | 위치
ImageNet-1k | ViT-B/16, 300ep | Top-1 Acc (%) | 83.1 | ↑ | Table 2
```

| 칸 | 규칙 |
|---|---|
| 데이터셋 | 논문에 적힌 이름 그대로 |
| 실험 설정 | 수치를 얻은 조건(모델 크기, 백본, 학습량, 추가 데이터, 평가 방식 등). 없으면 `-` |
| 지표 | 단위 포함 |
| 수치 | 표에 적힌 숫자. ± 표준편차는 있어도 됨 |
| 방향 | 높을수록 좋으면 `↑`, 낮을수록 좋으면 `↓`. 논문 표시가 없으면 지표 성격으로 정함(정확도 ↑, 오류율·지연 시간 ↓) |
| 위치 | 근거 표 또는 섹션 |

- 제안한 방법의 결과만 담고 베이스라인 수치는 넣지 않는다.
- (데이터셋, 실험 설정, 지표) 조합 하나당 한 줄이다.
- 실험 설정을 두는 이유: 데이터셋과 지표가 같아도 조건이 다르면(예: BERT-base vs BERT-large) 공정한 비교가 아니다. Compare Agent가 실험 설정을 보고 `조건 다름`으로 표시하면 코드는 대소 비교를 하지 않는다.

## 4. 코드 검증 층 (`validator.py`)

입력은 `my_paper.json`, `prior_paper.json`, `compare_result.json`이고 출력은 `verified_result.json`이다. 모든 함수는 순수 함수다.

### 4.1 입력 점검
`core_techniques`가 비어 있는 쪽이 있으면 `InputError("내 논문|기존 논문이 논문으로 인식되지 않았습니다")`를 던진다. 두 파일의 SHA-256이 같으면 분석 전에 중단한다(`service.py`에서 처리).

### 4.2 `element_mapping` 파싱과 판정 강등

| 상황 | 처리 |
|---|---|
| 형식이 깨진 줄 | 버리고 `dropped`에 "형식 오류"로 기록 |
| 존재하지 않는 M 번호 | 그 줄을 제거하고 `dropped`에 기록 |
| 존재하지 않는 P 번호 | 그 P만 제거. 남은 P가 없는데 판정이 일치/유사면 확인필요 |
| 대응 줄이 없는 M | 확인필요 (사유: "대응 판정 누락") |
| 같은 M에 서로 다른 판정 | 확인필요 (사유: "판정 충돌") |
| 일치/유사인데 M[섹션] 또는 P[섹션] 근거가 없음 | 확인필요 |
| 인용한 섹션이 실제 요소의 섹션 태그와 다름 | 확인필요 |
| 없음인데 검토 범위가 비어 있음 | 확인필요 |
| 판정 값이 4종 밖 | 확인필요 |

강등된 항목에는 `downgraded_reason`을 남긴다.

### 4.3 커버리지와 등급 (범위 규칙)
- n은 M 요소 개수다.
- 최소 커버리지 = (일치 + 유사 × 0.5) ÷ n × 100. 확인필요를 전부 "없음"으로 가정한 값이다.
- 최대 커버리지 = (일치 + 확인필요 + 유사 × 0.5) ÷ n × 100. 확인필요를 전부 "일치"로 가정한 값이다.
- 등급 구간은 70 이상 High, 30 이상 70 미만 Medium, 30 미만 Low다.
- 최소와 최대가 같은 구간이면 그 등급으로 **확정**한다(`level_status = "확정"`). 다르면 `level_status = "보류"`이고, 등급은 범위로 표시한다(예: `Low~Medium`).
- 교차 검증: 등급이 확정됐을 때만 Classify의 `overlap_level`과 비교해 `일치` 또는 `확인필요`로 표시한다. 보류면 `참고`로 표시하고 Classify 등급은 참고값으로만 쓴다.

### 4.4 파생 목록
- `overlapping`: 판정이 일치 또는 유사인 M
- `novel`: 검증을 통과한 "없음" M
- `uncertain`: 확인필요 M과 그 사유

### 4.5 정량 비교 (`result_pairs`)
1. R-M, R-P 번호가 실제로 있는지 확인한다. 없으면 `dropped`에 기록한다.
2. 6칸으로 쪼갠다. 칸 수가 다르면 `dropped`에 "형식 오류"로 기록한다.
3. 수치를 파싱한다. `%`, `±` 이하, 쉼표, 공백을 제거하고 float로 읽는다.
4. 다음 경우에는 `outcome = "비교 불가"`로 두고 사유를 남긴다.
   - Compare Agent가 `조건 다름`으로 표시함
   - 수치를 숫자로 읽을 수 없음
   - 한쪽 방향(↑/↓)이 없음
   - 양쪽 방향이 다름
   - 두 값의 비가 50배 이상 (단위가 다를 가능성)
5. 그 밖의 경우 방향에 따라 `우세`, `열세`, `동일`을 판정하고 두 가지 차이를 남긴다.
   - 절대 차이 `diff = my − prior` (지표 단위 그대로)
   - 상대 차이 `rel_diff = (my − prior) ÷ |prior| × 100` (%, 소수점 첫째 자리). `prior`가 0이면 `null`
6. 화면 표시는 `+1.3 (상대 +1.6%)`처럼 절대 차이를 앞에, 상대 차이를 괄호에 둔다. 정확도처럼 %인 지표는 절대 차이에 `%p`를 붙여 상대 차이(%)와 헷갈리지 않게 한다.

| 내 논문 | 기존 논문 | 판정 |
|---|---|---|
| `ImageNet-1k \| ViT-B/16 \| Top-1 Acc (%) \| 83.1 \| ↑ \| Table 2` | `ImageNet-1K \| ViT-B/16 \| Top-1 정확도 \| 81.8 \| ↑ \| 표 3` (동일 조건) | 우세, +1.3%p (상대 +1.6%) |
| `COCO \| R-50 \| Latency (ms) \| 2.0 \| ↓ \| Table 4` | `COCO \| R-50 \| Latency (ms) \| 4.0 \| ↓ \| Table 5` (동일 조건) | 우세, −2.0 ms (상대 −50.0%) |
| `… \| Acc \| 0.831 \| ↑` | `… \| Acc (%) \| 81.8 \| ↑` | 비교 불가 (비 약 98배, 단위 의심) |
| `GLUE \| BERT-base \| 평균 \| 84.0 \| ↑` | `GLUE \| BERT-large \| 평균 \| 86.0 \| ↑` (조건 다름) | 비교 불가 (조건 다름) |

통계적 유의성 검정, 여러 지표를 합친 종합 점수, 표준편차를 고려한 판정은 하지 않는다. 화면에는 "수치상 우세/열세"로만 표시한다.

### 4.6 `verified_result.json` 구조
```json
{
  "level": "Low | Medium | High | Low~Medium | Medium~High | Low~High",
  "level_status": "확정 | 보류",
  "coverage_min": 10.0,
  "coverage_max": 40.0,
  "classify_level": "Low Overlap",
  "cross_check": "일치 | 확인필요 | 참고",
  "counts": {"일치": 1, "유사": 0, "없음": 6, "확인필요": 3},
  "mappings": [{"m_id": "M1", "m_text": "...", "p_ids": ["P3"], "p_texts": ["..."],
                "verdict": "일치", "evidence": "M[3.1] / P[2.3]", "note": "...",
                "downgraded_reason": null}],
  "overlapping": ["M1"],
  "novel": ["M2"],
  "uncertain": [{"m_id": "M4", "reason": "근거 섹션 불일치"}],
  "result_comparisons": [{"r_m": "R-M1", "r_p": "R-P2", "dataset": "...",
                          "my_setting": "...", "prior_setting": "...", "condition": "동일 조건",
                          "metric": "...", "my_value": 83.1, "prior_value": 81.8, "direction": "↑",
                          "outcome": "우세", "diff": 1.3, "rel_diff": 1.6, "reason": null}],
  "report": {"summary": "...", "caution_points": [], "differentiation_suggestions": [],
             "related_work_draft": "..."},
  "dropped": [{"raw": "...", "reason": "..."}]
}
```

## 5. 화면 (`streamlit_app.py`)

한 페이지이며 위에서 아래로 다음 순서를 따른다.

1. **입력**: 업로드 칸 2개("투고할 내 논문 PDF", "비교할 기존 논문 PDF"), [비교 시작] 버튼, 샘플 PDF 다운로드 링크. 파일이 빠지면 어느 쪽인지 안내한다.
2. **진행 상태**: `st.status`로 1~5단계를 표시한다. 실패하면 몇 단계에서 왜 실패했는지 보여주고 멈춘다.
3. **결과 배지**: 등급(확정 또는 보류와 범위), 커버리지(확정이면 값, 보류면 범위), 교차 검증, 판정 개수
4. **요소 대응표**: M마다 내 요소, 대응 P 요소, 판정(색 구분), 근거 위치, 강등 사유
5. **차별점 / 겹침 (2열)**: 내 논문 고유 요소, 기존 논문과 겹치는 요소
6. **정량 비교 표**: 데이터셋, 실험 설정(내/기존), 지표, 내 수치, 기존 수치, 결과, 차이(절대·상대), 사유. 비교할 쌍이 없으면 "직접 비교 가능한 실험이 없습니다"를 표시한다.
7. **차별성 리포트**: 요약, 주의 지점, 서술 제안 3개
8. **Related Work 초안**: `st.code`로 보여줘서 복사 버튼이 붙는다.
9. **확인 필요 목록**: 접지 않고 별도 섹션으로 둔다. 보류면 "이 항목을 확인하면 등급이 확정됩니다"를 안내한다.
10. **다운로드와 고지**: `verified_result.json`, `compare_result.json` 다운로드. 하단에 "사전 점검용이며 심사·표절 판정을 대체하지 않습니다."를 표시한다.

## 6. 오류 처리

| 상황 | 처리 |
|---|---|
| 업로드 실패, Job 생성 실패, `status=failed` | `StepError(step, message)`. 화면에 단계와 메시지를 표시하고 중단 |
| 최대 대기 시간 초과 | `TimeoutError`를 `StepError`로 감싸서 표시 |
| `output_text`가 없거나 JSON이 아님 | `StepError` |
| 스키마 필드 누락 | 빈 배열로 처리하고 `dropped`에 기록 |
| 입력 점검 실패 (4.1) | `InputError`. 어느 파일인지 안내 |
| 같은 파일 두 번 업로드 | 분석 전에 안내하고 중단 |
| 논문이 아닌데 그럴듯한 요소가 추출되는 문서 | 막지 못한다. README에 한계로 명시 |

자동 재시도는 하지 않는다. 사용자가 버튼을 다시 누른다.

## 7. 테스트와 평가

### 7.1 단위 테스트 (pytest, Studio 호출 없음)
- `ids.py`: 번호 부여가 결정적인지
- `validator.py`: 4.2 강등 규칙을 하나씩, 4.3 범위 규칙(확정 Low / 보류 Low~Medium / 확정 High 예시), 교차 검증, 4.5 정량 비교의 모든 분기
- `compare_builder.py`: 번호가 붙은 PDF가 생성되는지(텍스트 추출로 M1, P1 존재 확인)
- 손으로 만든 JSON 픽스처를 `tests/fixtures/`에 둔다.

### 7.2 통합 확인
샘플 쌍으로 `python app.py`를 실행해 1~5단계가 오류 없이 끝나는지, 결과 파일 5개가 생성되는지 확인한다.

### 7.3 평가 (`eval/`)

**샘플 5쌍** (구체적 논문은 팀에서 선정)

| 샘플 | 구성 | 기대 결과 |
|---|---|---|
| S1 | 같은 연구의 학회판 ↔ 저널 확장판 | High |
| S2 | 후속 논문 ↔ 원 논문 (예: RoBERTa ↔ BERT) | Medium |
| S3 | 분야가 다른 논문 쌍 | Low |
| S4 | 국문 논문 ↔ 같은 기술의 영문 논문 | 언어가 섞여도 대응 유지 |
| S5 | 논문이 아닌 문서 | 판정 없이 입력 확인 안내 |

**정답 고정 방식**
- M 번호는 추출 결과에 따라 달라지므로, 각 샘플의 `my_paper.json`과 `prior_paper.json`을 한 번 생성해 `eval/samples/S*/`에 고정한다.
- 팀원 2명이 고정본의 M 요소별 정답 판정을 `eval/samples/S*/labels.json`에 라벨링한다. 의견이 갈린 요소는 정답을 "확인필요"로 둔다.
- `labels.json` 형식: `{"expected_level": "High", "mappings": {"M1": "일치", "M2": "없음"}}`. S5는 `{"expected_error": "InputError"}`.

**`eval/evaluate.py`**
- `--mode compare`: 고정 JSON에서 비교 단계(`app.py --from-json`)를 실행하고 정답과 비교한다. 요소 단위 지표를 계산한다.
- `--mode full --repeat 3`: 원본 PDF로 전체 파이프라인을 3회 실행해 등급 일관성과 처리 시간을 측정한다.
- 결과는 `eval/report.json`과 콘솔 표로 출력한다.

**지표**

| 지표 | 정의 | 목표 |
|---|---|---|
| 허위 신규 주장률 (주 지표) | 정답이 일치/유사인 M 중 "없음"으로 판정된 비율 | 10% 이하 |
| 요소 대응 정확도 | 판정이 정답과 같은 M 비율. 유사와 일치는 구분 | 80% 이상 |
| 등급 일치율 | 확정 등급이 기대 등급과 같은 비율. 보류는 별도 집계 | 80% 이상 |
| 근거 인용 유효율 | 표시된 판정 중 인용 번호와 섹션이 실제로 있는 비율 | 100% |
| 정량 비교 정확도 | 비교된 쌍 중 대소 판정이 수동 계산과 같은 비율 | 100% |
| 등급 일관성 | 3회 실행 등급이 모두 같은 샘플 비율 | 100% |
| 처리 시간 | 1건 전체 파이프라인 소요 시간 | 측정만 함 |

## 8. 배포
- GitHub 저장소와 Railway를 연결한다.
- 환경변수: `UPSTAGE_API_KEY`, 에이전트 ID와 CONFIG ID 6개, `PORT`
- 시작 명령: `streamlit run streamlit_app.py --server.port=$PORT --server.headless=true`
- `.env`, `runs/`는 `.gitignore`에 넣는다.

## 9. 리스크

| 리스크 | 영향 | 대응 |
|---|---|---|
| 요소 분해가 실행마다 다름 | 커버리지가 흔들림 | 3.1 공통 규칙, 평가 시 추출 결과 고정, 등급 일관성 측정 |
| 국문/영문 용어 차이 | 대응 누락 | 한국어 정규화 설명 필드, S4로 확인, 불확실하면 확인필요 |
| Extract 3개 스키마 불일치 | 화면 코드 KeyError | 스키마 하나를 복사해 쓰고 `agent_configs/`로 대조. validator는 누락 필드를 빈 배열로 처리 |
| LLM이 "신규"를 단정 | 허위 신규 주장 | 근거 없는 판정 강등, 범위 규칙으로 등급 보류 |
| 긴 논문으로 Studio 처리 지연 | 실행 시간 초과 | 최대 대기 시간 오류 표시, 처리 시간 측정 |
| Extract가 여러 요소를 한 문자열로 합침 | M 개수 왜곡 | 3.1 규칙 명시, 평가에서 확인 |
