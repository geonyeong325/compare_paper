# Project 1. HR AI Service

Resume와 Job Description(JD)을 분석하여 지원자의 직무 적합도를 평가하는 AI 서비스입니다.

본 프로젝트는 **Upstage Studio Agent API**를 이용하여 문서를 분석하고,
Resume와 JD를 비교하여 최종 적합도와 추천 사항을 JSON 형태로 생성합니다.

---

# Project Overview

본 프로젝트는 다음과 같은 AI Workflow로 구성됩니다.

```text
Resume.pdf
      │
      ▼
Resume Agent
      │
      ▼
resume.json

JobDescription.pdf
      │
      ▼
JD Agent
      │
      ▼
jd.json

resume.json + jd.json
      │
      ▼
Matching Builder
      │
      ▼
Matching_Input.pdf
      │
      ▼
Matching Agent
      │
      ▼
matching_result.json
```

---

# Project Structure

```text
hr-ai-service-workflow/
│
├── app.py
├── streamlit_app.py
├── service.py
├── config.py
├── upload.py
├── agent_client.py
├── resume_agent.py
├── jd_agent.py
├── matching_agent.py
├── matching_builder.py
├── file_manager.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
├── fonts/
│     └── NanumGothic-Regular.ttf
│
├── data/
│     ├── Resume.pdf
│     └── JobDescription.pdf
│
├── output/
│     ├── resume.json
│     ├── jd.json
│     └── Matching_Input.pdf
│
└── result/
      └── matching_result.json
```

## Project Structure Description

| 경로 | 파일/폴더 | 설명 |
|------|-----------|------|
| `streamlit_app.py` | Streamlit UI | Resume와 Job Description을 업로드하고 AI 분석을 실행하는 웹 사용자 인터페이스입니다. 사용자의 입력을 받아 `service.py`를 호출하고 분석 결과를 화면에 출력합니다. |
| `service.py` | Business Service | Streamlit UI와 기존 CLI 애플리케이션 사이의 서비스 계층입니다. Resume 분석 → JD 분석 → Matching PDF 생성 → Matching 분석을 하나의 서비스로 제공합니다. |
| `app.py` | Main Application | 프로젝트 전체 Workflow를 실행하는 Orchestrator입니다. Resume 분석 → JD 분석 → Matching PDF 생성 → Matching 분석을 순차적으로 수행합니다. |
| `config.py` | Configuration | API Key, Agent ID, Config ID, 프로젝트 경로(Path) 등 환경 설정 정보를 관리합니다. |
| `upload.py` | File Upload | Resume, Job Description, Matching PDF를 Upstage Files API로 업로드하는 기능을 제공합니다. |
| `agent_client.py` | Common Agent Client | Studio Agent를 공통 방식으로 호출하는 클래스입니다. Agent Job 생성, Polling, 결과(JSON) 파싱 기능을 제공합니다. |
| `resume_agent.py` | Resume Agent | Resume Agent를 호출하여 이력서를 분석하고 Resume JSON을 생성합니다. |
| `jd_agent.py` | JD Agent | Job Description Agent를 호출하여 채용 공고를 분석하고 JD JSON을 생성합니다. |
| `matching_agent.py` | Matching Agent | Matching Agent를 호출하여 Resume와 Job Description의 적합도를 분석하고 최종 Matching Result를 생성합니다. |
| `matching_builder.py` | PDF Builder | Resume JSON과 JD JSON을 하나의 PDF(`Matching_Input.pdf`)로 생성합니다. |
| `file_manager.py` | File Manager | JSON 저장, 파일 읽기/쓰기 등 프로젝트의 공통 파일 입출력을 담당하는 유틸리티입니다. |
| `requirements.txt` | Dependencies | 프로젝트 실행에 필요한 Python 패키지 목록입니다. |
| `.env` | Environment Variables | Upstage API Key, Agent ID, Config ID 등 민감한 환경 변수를 저장합니다. GitHub에는 업로드하지 않습니다. |
| `.gitignore` | Git Ignore | Git에서 제외할 파일과 폴더를 정의합니다. (`.env`, `__pycache__`, `output`, `result` 등) |
| `README.md` | Project Guide | 프로젝트 소개, 실행 방법, GitHub 관리, Railway 배포 방법 등을 설명하는 프로젝트 문서입니다. |
| `fonts/` | Font Resources | ReportLab에서 사용하는 한글 폰트(Nanum Gothic)를 저장하는 폴더입니다. |
| `data/` | Input Documents | 분석 대상 Resume와 Job Description 파일을 저장하는 폴더입니다. |
| `output/` | Intermediate Results | Resume 분석 결과, JD 분석 결과, Matching_Input.pdf 등 중간 산출물을 저장합니다. |
| `result/` | Final Result | Matching Agent가 생성한 최종 적합도 분석 결과(JSON)를 저장합니다. |

# Studio Agent Description

본 프로젝트는 **Upstage Studio**에서 생성한 3개의 Agent를 사용하여 Resume 분석, Job Description 분석, 그리고 지원자와 채용 공고 간의 적합도 분석을 수행합니다.

각 Agent는 하나의 역할(Role)만 담당하며, 분석 결과는 다음 Agent의 입력으로 활용됩니다.

---

---

## Resume Agent

Resume Agent는 지원자의 이력서를 분석하여 구조화된 JSON 형태의 정보를 생성합니다.

### Input

```text
Resume.pdf
```

### Output

```text
resume.json
```

### 주요 역할

- 개인정보 추출
- 자기소개 요약
- 보유 기술(Skills) 추출
- 경력 정보 추출
- 프로젝트 경험 추출
- 학력 정보 추출
- 자격증 정보 추출
- 핵심 역량(Core Competencies) 추출

### 생성 결과 예시

```json
{
    "name": "...",
    "skills": [],
    "career": [],
    "projects": []
}
```

---

## JD Agent

JD(Job Description) Agent는 채용 공고를 분석하여 기업이 요구하는 기술과 자격 요건을 JSON 형태로 생성합니다.

### Input

```text
JobDescription.pdf
```

### Output

```text
jd.json
```

### 주요 역할

- 회사 정보 추출
- 모집 직무 분석
- 주요 업무 추출
- 필수 기술(Required Skills) 추출
- 우대 기술(Preferred Skills) 추출
- 자격 요건 분석
- 경력 요구사항 분석
- 학력 요구사항 분석

### 생성 결과 예시

```json
{
    "company": "...",
    "position": "...",
    "required_skills": [],
    "preferred_skills": []
}
```

---

## Matching Agent

Matching Agent는 Resume와 JD를 비교하여 지원자의 직무 적합도를 분석합니다.

Matching Agent는 Resume JSON과 JD JSON을 기반으로 생성된 **Matching_Input.pdf**를 입력으로 사용합니다.

### Input

```text
Matching_Input.pdf
```

### Output

```text
matching_result.json
```

### 주요 역할

- Resume와 JD 비교
- 기술 스택 일치 여부 분석
- 경력 일치 여부 분석
- 부족한 기술 분석
- 장점 분석
- 약점 분석
- 개선 사항 추천
- 최종 적합도(Score) 산출

### 생성 결과 예시

```json
{
    "match_level": "High Match",
    "overall_score": 85,
    "matched_skills": [],
    "missing_skills": [],
    "recommendations": []
}
```

---

# Agent Responsibility

| Agent | Input | Output | 주요 역할 |
|--------|-------|--------|-----------|
| **Resume Agent** | Resume.pdf | resume.json | 이력서 분석 및 지원자 정보 추출 |
| **JD Agent** | JobDescription.pdf | jd.json | 채용 공고 분석 및 요구사항 추출 |
| **Matching Agent** | Matching_Input.pdf | matching_result.json | Resume와 JD를 비교하여 직무 적합도 분석 |

---
---

# Workflow

## Step 1. Resume Analysis

Resume.pdf를 Studio Resume Agent로 분석하여

```text
Resume.pdf

↓

Resume Agent

↓

resume.json
```

을 생성합니다.

---

## Step 2. Job Description Analysis

JobDescription.pdf를 Studio JD Agent로 분석하여

```text
JobDescription.pdf

↓

JD Agent

↓

jd.json
```

을 생성합니다.

---

## Step 3. Matching Builder

Resume JSON과 JD JSON을 하나의 문서로 변환합니다.

```text
resume.json

+

jd.json

↓

Matching_Input.pdf
```

Matching Agent는 이 PDF를 입력으로 사용합니다.

---

## Step 4. Matching Analysis

Matching_Input.pdf를 Studio Matching Agent로 분석합니다.

```text
Matching_Input.pdf

↓

Matching Agent

↓

matching_result.json
```

최종적으로 지원자의 적합도와 추천 사항을 생성합니다.

---

# Output

프로젝트가 완료되면 다음 파일이 생성됩니다.

```text
output/

resume.json

jd.json

Matching_Input.pdf


result/

matching_result.json
```

---

# Matching Result

최종 결과는 다음과 같은 JSON 구조입니다.

```json
{
  "match_level": "High Match",
  "overall_score": 85,
  "summary": "...",
  "matched_skills": [],
  "missing_skills": [],
  "matched_experience": [],
  "missing_requirements": [],
  "strengths": [],
  "weaknesses": [],
  "recommendations": []
}
```

---

# Prerequisites

- Python 3.11+
- Upstage Studio
- Upstage API Key

---

# Installation

패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

---

# Environment Variables

`.env`

```text
UPSTAGE_API_KEY=

RESUME_AGENT_ID=
RESUME_CONFIG_ID=1

JD_AGENT_ID=
JD_CONFIG_ID=1

MATCHING_AGENT_ID=
MATCHING_CONFIG_ID=1
```

---

# Run

프로젝트를 실행합니다.

```bash
python app.py
```

---

# Execution Flow

실행 순서는 다음과 같습니다.

```text
Configuration

↓

Resume Analysis

↓

JD Analysis

↓

Matching Builder

↓

Matching Analysis

↓

Project Complete
```

# Streamlit Application Guide

이번 프로젝트는 **Streamlit**을 이용하여 AI Resume Matching 서비스를 웹 애플리케이션 형태로 제공합니다.

사용자는 브라우저에서 Resume와 Job Description을 업로드하고, AI 분석 결과를 실시간으로 확인할 수 있습니다.


# Streamlit Project Structure

```text
streamlit_app.py

↓

Upload Files

↓

Call service.py

↓

Display Result
```

Streamlit은 사용자 인터페이스(UI)만 담당하며, 실제 비즈니스 로직은 `service.py`에서 수행합니다.

---

# Streamlit Execution

프로젝트 루트 디렉터리에서 다음 명령으로 실행합니다.

```bash
streamlit run streamlit_app.py
```

실행 후 브라우저에서 다음과 같은 주소로 접속할 수 있습니다.

```text
Local URL

http://localhost:8501
```

---

# Streamlit User Interface

애플리케이션은 다음과 같은 화면으로 구성됩니다.

```text
AI Resume Matching Service

──────────────────────────────

Resume Upload

[ Choose File ]

──────────────────────────────

Job Description Upload

[ Choose File ]

──────────────────────────────

[ Analyze ]

──────────────────────────────

Matching Result
```

---

# Streamlit Processing Flow

사용자가 **Analyze** 버튼을 클릭하면 다음과 같은 순서로 분석이 수행됩니다.

```text
Resume Upload

↓

Save File

↓

Resume Analysis

↓

Resume JSON

↓

JD Upload

↓

Save File

↓

JD Analysis

↓

JD JSON

↓

Matching PDF 생성

↓

Matching Analysis

↓

Matching Result

↓

Result Display
```

# Railway Deployment Guide

이번 프로젝트는 **Railway**를 이용하여 GitHub Repository를 배포하고, 인터넷에서 접속 가능한 AI 서비스를 구축합니다.

---

# Railway Deployment Workflow

Railway에서 GitHub Repository를 연결하면 **자동으로 첫 번째 Build와 Deploy가 시작됩니다.**

실제 Railway의 배포 흐름은 다음과 같습니다.

```text
GitHub Repository

↓

Repository 연결

↓

자동 Build & Deploy 시작

↓

(첫 번째 Deploy 실패 가능)

↓

Build Log 확인

↓

Environment Variables 등록

↓

Custom Start Command 설정

↓

Redeploy

↓

Running

↓

Public Domain 생성

↓

서비스 확인
```

---

# Automatic Deploy

## Railway의 기본 동작

Railway는 Repository를 연결하는 즉시 첫 번째 Build와 Deploy를 자동으로 수행합니다.

> **참고**
>
> GitHub Repository를 연결하면 Railway는 자동으로 첫 번째 Build와 Deploy를 시작합니다.
>
> 아직 Environment Variables 또는 Start Command가 설정되지 않은 경우에는 첫 번째 Deploy가 실패할 수 있습니다.
>
> 이는 Railway의 정상적인 동작입니다.

---

# Build Log 이해하기

Railway는 Build 과정에서 다음과 같은 작업을 수행합니다.

```text
Detected Python

↓

Create Virtual Environment

↓

pip install

↓

Copy Project

↓

Starting Container

↓

Streamlit Started
```

각 단계의 의미는 다음과 같습니다.

| 로그 | 설명 |
|------|------|
| **Detected Python** | Python 프로젝트를 자동으로 인식합니다. |
| **Create Virtual Environment** | Python 가상환경을 생성합니다. |
| **pip install** | requirements.txt의 패키지를 설치합니다. |
| **Copy Project** | 프로젝트 파일을 컨테이너로 복사합니다. |
| **Starting Container** | 컨테이너를 시작합니다. |
| **Streamlit Started** | Streamlit 애플리케이션이 정상적으로 실행되었습니다. |

---

# Environment Variables

프로젝트에서 사용하는 API Key와 Agent ID는 GitHub에 포함하지 않고 Railway Variables로 관리합니다.

```text
Local

.env

↓

Railway Variables
```

등록해야 하는 변수는 다음과 같습니다.

```text
UPSTAGE_API_KEY

RESUME_AGENT_ID

RESUME_CONFIG_ID

JD_AGENT_ID

JD_CONFIG_ID

MATCHING_AGENT_ID

MATCHING_CONFIG_ID
```

Variables를 저장한 후에는 반드시 **Redeploy**를 수행해야 합니다.

---

# Custom Start Command

Streamlit 애플리케이션은 **Custom Start Command**에서 실행해야 합니다.

```bash
streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
```

# Public Domain

Deploy가 완료되었다고 해서 바로 접속 가능한 것은 아닙니다.

Railway에서는 Public Domain을 생성해야 합니다.

```text
Deploy Success

↓

Networking

↓

Generate Domain

↓

Public URL 생성
```

예시

```text
https://hr-ai-service.up.railway.app
```

생성된 Public URL을 브라우저에서 열어 서비스를 확인합니다.



---

# Learning Objectives

이 프로젝트를 통해 다음 내용을 학습합니다.

- Upstage Studio Agent API 사용 방법
- File Upload API 활용
- Resume 분석 자동화
- Job Description 분석 자동화
- PDF 생성(ReportLab)
- AI Agent Workflow 설계
- Parse → Classify → Extract 구조 이해
- JSON 기반 AI 서비스 개발
- Streamlit을 이용한 웹 애플리케이션 개발
- Railway를 이용한 AI 서비스 배포

---

# Technologies

- Python
- Upstage Studio Agent API
- OpenAI SDK
- ReportLab
- JSON
- Streamlit
- Railway
- GitHub