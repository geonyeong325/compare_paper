"""
=========================================================
HR AI Service

Business Logic

Resume
↓

Resume Agent

↓

JD

↓

JD Agent

↓

Matching PDF

↓

Matching Agent

↓

Matching Result
=========================================================
"""

from pathlib import Path
import json

from app import (
    process_document,
    build_matching_pdf,
    process_matching
)

from config import (
    RESUME_JSON,
    JD_JSON,
    MATCHING_RESULT
)

from resume_agent import analyze_resume
from jd_agent import analyze_jd


##################################################
# Resume Analysis
##################################################

def analyze_resume_document(
    resume_path: str
):
    """
    Resume 분석
    """

    process_document(

        step="Resume",

        document_name="Resume",

        input_file=resume_path,

        analyzer=analyze_resume,

        output_json=RESUME_JSON

    )


##################################################
# JD Analysis
##################################################

def analyze_jd_document(
    jd_path: str
):
    """
    Job Description 분석
    """

    process_document(

        step="Job Description",

        document_name="Job Description",

        input_file=jd_path,

        analyzer=analyze_jd,

        output_json=JD_JSON

    )


##################################################
# Matching PDF
##################################################

def build_matching_document():
    """
    Matching PDF 생성
    """

    return build_matching_pdf()


##################################################
# Matching Analysis
##################################################

def analyze_matching(
    matching_pdf
):
    """
    Matching Agent 실행
    """

    return process_matching(

        matching_pdf

    )


##################################################
# Load Result
##################################################

def load_matching_result():
    """
    matching_result.json 읽기
    """

    with open(

        MATCHING_RESULT,

        "r",

        encoding="utf-8"

    ) as file:

        return json.load(file)


##################################################
# Service
##################################################

def run_matching_service(

    resume_path: str,

    jd_path: str

):
    """
    HR AI Service

    Parameters
    ----------

    resume_path

    jd_path

    Returns
    -------

    Matching Result(dict)

    """

    print()

    print("=" * 60)

    print("HR AI Service")

    print("=" * 60)

    print()


    ##################################################
    # Resume
    ##################################################

    print("Step 1. Resume Analysis")

    analyze_resume_document(

        resume_path

    )


    ##################################################
    # JD
    ##################################################

    print()

    print("Step 2. JD Analysis")

    analyze_jd_document(

        jd_path

    )


    ##################################################
    # Matching PDF
    ##################################################

    print()

    print("Step 3. Build Matching PDF")

    matching_pdf = build_matching_document()


    ##################################################
    # Matching
    ##################################################

    print()

    print("Step 4. Matching Analysis")

    result = analyze_matching(

        matching_pdf

    )


    ##################################################
    # Result
    ##################################################

    print()

    print("Step 5. Load Result")

    if result is None:

        result = load_matching_result()


    print()

    print("=" * 60)

    print("Completed")

    print("=" * 60)

    print()

    return result