"""
config.py

Project 2. HR AI Service

프로젝트 환경설정
"""

import os
from pathlib import Path

from dotenv import load_dotenv

##################################################
# Load Environment
##################################################

load_dotenv()

##################################################
# Upstage API
##################################################

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

##################################################
# Resume Agent
##################################################

RESUME_AGENT_ID = os.getenv("RESUME_AGENT_ID")
RESUME_CONFIG_ID = os.getenv("RESUME_CONFIG_ID")

##################################################
# JD Agent
##################################################

JD_AGENT_ID = os.getenv("JD_AGENT_ID")
JD_CONFIG_ID = os.getenv("JD_CONFIG_ID")

##################################################
# Matching Agent
##################################################

MATCHING_AGENT_ID = os.getenv("MATCHING_AGENT_ID")
MATCHING_CONFIG_ID = os.getenv("MATCHING_CONFIG_ID")

##################################################
# Project Directory
##################################################

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

OUTPUT_DIR = BASE_DIR / "output"

RESULT_DIR = BASE_DIR / "result"

##################################################
# Input Files
##################################################

RESUME_FILE = DATA_DIR / "Resume.pdf"

JD_FILE = DATA_DIR / "JobDescription.pdf"

##################################################
# Output Files
##################################################

RESUME_JSON = OUTPUT_DIR / "resume.json"

JD_JSON = OUTPUT_DIR / "jd.json"

MATCHING_PDF = OUTPUT_DIR / "Matching_Input.pdf"

MATCHING_RESULT = RESULT_DIR / "matching_result.json"


##################################################
# fonts
##################################################

FONT_NAME = "Nanum"

FONT_PATH = BASE_DIR / "fonts" / "NanumGothic-Regular.ttf"


##################################################
# Directory Initialization
##################################################

def create_directories():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

##################################################
# Configuration Validation
##################################################

def validate_config():

    required = {

        ##################################################
        # API
        ##################################################

        "UPSTAGE_API_KEY": UPSTAGE_API_KEY,

        ##################################################
        # Resume
        ##################################################

        "RESUME_AGENT_ID": RESUME_AGENT_ID,
        "RESUME_CONFIG_ID": RESUME_CONFIG_ID,

        ##################################################
        # JD
        ##################################################

        "JD_AGENT_ID": JD_AGENT_ID,
        "JD_CONFIG_ID": JD_CONFIG_ID,

        ##################################################
        # Matching
        ##################################################

        "MATCHING_AGENT_ID": MATCHING_AGENT_ID,
        "MATCHING_CONFIG_ID": MATCHING_CONFIG_ID,

    }

    missing = [

        key

        for key, value in required.items()

        if not value

    ]

    if missing:

        raise ValueError(

            "다음 환경변수가 설정되지 않았습니다.\n\n"

            + "\n".join(missing)

        )

    create_directories()

##################################################
# Project Information
##################################################

def print_config():

    print("=" * 60)
    print("Project Configuration")
    print("=" * 60)

    print(f"Project Directory : {BASE_DIR}")
    print(f"Data Directory    : {DATA_DIR}")
    print(f"Output Directory  : {OUTPUT_DIR}")
    print(f"Result Directory  : {RESULT_DIR}")

    print()

    print(f"Resume Agent      : {RESUME_AGENT_ID}")
    print(f"Resume Config     : {RESUME_CONFIG_ID}")

    print(f"JD Agent          : {JD_AGENT_ID}")
    print(f"JD Config         : {JD_CONFIG_ID}")

    print(f"Matching Agent    : {MATCHING_AGENT_ID}")
    print(f"Matching Config   : {MATCHING_CONFIG_ID}")

    print("=" * 60)