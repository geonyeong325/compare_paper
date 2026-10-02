"""
=========================================================
HR AI Service
Streamlit MVP
=========================================================

Resume Upload
↓

JD Upload
↓

Analyze

↓

Matching Result

=========================================================
"""

import json
import os
import tempfile

import streamlit as st

from config import (
    MATCHING_RESULT
)

# Business Logic
from service import run_matching_service


##################################################
# Page
##################################################

st.set_page_config(

    page_title="HR AI Service",

    page_icon="🤖",

    layout="wide"

)


##################################################
# Sidebar
##################################################

with st.sidebar:

    st.title("HR AI Service")

    st.markdown(
        """
        ### AI Resume Matching

        Resume와

        Job Description을 분석하여

        직무 적합도를 평가합니다.
        """
    )


##################################################
# Title
##################################################

st.title("🤖 HR AI Service")

st.caption(

    "AI 기반 Resume Matching Service"

)


##################################################
# Upload
##################################################

col1, col2 = st.columns(2)

with col1:

    resume_file = st.file_uploader(

        "Resume PDF",

        type=["pdf"]

    )

with col2:

    jd_file = st.file_uploader(

        "Job Description PDF",

        type=["pdf"]

    )


##################################################
# Analyze Button
##################################################

analyze = st.button(

    "🚀 Analyze",

    type="primary",

    use_container_width=True

)


##################################################
# Execute
##################################################

if analyze:

    if resume_file is None:

        st.error("Resume를 업로드하세요.")

        st.stop()

    if jd_file is None:

        st.error("Job Description을 업로드하세요.")

        st.stop()

    ##################################################
    # Save Upload
    ##################################################

    resume_path = None
    jd_path = None

    try:

        ##################################################
        # Resume Temp File
        ##################################################

        with tempfile.NamedTemporaryFile(

                suffix=".pdf",

                delete=False

        ) as fp:

            fp.write(resume_file.read())

            resume_path = fp.name

        ##################################################
        # JD Temp File
        ##################################################

        with tempfile.NamedTemporaryFile(

                suffix=".pdf",

                delete=False

        ) as fp:

            fp.write(jd_file.read())

            jd_path = fp.name

        ##################################################
        # Execute Service
        ##################################################

        with st.spinner("AI가 문서를 분석하고 있습니다..."):

            result = run_matching_service(

                resume_path,

                jd_path

            )

            if result is None:
                st.error("Matching 실패")

                st.stop()

    finally:

        ##################################################
        # Remove Temporary Files
        ##################################################

        for file_path in [resume_path, jd_path]:

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

                print(f"Temporary File Removed : {file_path}")


    ##################################################
    # Success
    ##################################################

    st.success("분석이 완료되었습니다.")

    ##################################################
    # Score
    ##################################################

    # Overall Score
    overall_score = result["overall_score"]

    if isinstance(overall_score, list):
        overall_score = overall_score[0]

    # Matching Level
    match_level = result["match_level"]

    if isinstance(match_level, list):
        match_level = match_level[0]

    col1, col2 = st.columns(2)

    with col1:

        st.metric(

            "Overall Score",

            f"{overall_score}%"

        )

    with col2:

        st.metric(

            "Matching Level",

            match_level

        )


    ##################################################
    # Summary
    ##################################################

    st.divider()

    st.subheader("📄 Summary")

    st.write(

        result["summary"]

    )


    ##################################################
    # Skills
    ##################################################

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("✅ Matched Skills")

        for item in result["matched_skills"]:

            st.success(item)


    with col2:

        st.subheader("⚠ Missing Skills")

        for item in result["missing_skills"]:

            st.warning(item)


    ##################################################
    # Experience
    ##################################################

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("💪 Strengths")

        for item in result["strengths"]:

            st.success(item)


    with col2:

        st.subheader("📌 Weaknesses")

        for item in result["weaknesses"]:

            st.error(item)


    ##################################################
    # Recommendation
    ##################################################

    st.divider()

    st.subheader("💡 Recommendations")

    for item in result["recommendations"]:

        st.info(item)


    ##################################################
    # JSON Viewer
    ##################################################

    st.divider()

    st.subheader("JSON Result")

    st.json(result)


    ##################################################
    # Download JSON
    ##################################################

    with open(

        MATCHING_RESULT,

        "r",

        encoding="utf-8"

    ) as file:

        json_data = file.read()

    st.download_button(

        label="📥 Download JSON",

        data=json_data,

        file_name="matching_result.json",

        mime="application/json"

    )