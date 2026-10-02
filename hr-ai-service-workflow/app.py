"""
Project 2. HR AI Service

app.py

전체 Workflow를 관리하는 Orchestrator
"""

from config import (

    validate_config,
    print_config,

    RESUME_FILE,
    JD_FILE,

    RESUME_JSON,
    JD_JSON,

    MATCHING_PDF,
    MATCHING_RESULT
)

from upload import upload_file

from resume_agent import (
    analyze_resume
)

from jd_agent import (
    analyze_jd
)


##################################################
# Lab 3
##################################################

from matching_builder import (
    create_matching_input
)

##################################################
# Lab 4
##################################################

from matching_agent import (
    analyze_matching
)

from file_manager import (
    save_json
)

##################################################
# Common Document Process
##################################################

def process_document(

    step,
    document_name,

    input_file,

    analyzer,

    output_json

):

    print()

    print("=" * 60)
    print(step)
    print("=" * 60)

    ##################################################
    # Upload
    ##################################################

    try:

        file_id = upload_file(
            input_file
        )

        print()

        print(f"{document_name} Upload Complete")

    except Exception as e:

        print()

        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print(e)

        return None

    ##################################################
    # Agent
    ##################################################

    try:

        result = analyzer(
            file_id
        )

        save_json(

            result,

            output_json

        )

        print()

        print(f"{document_name} JSON 저장 완료")

        print(output_json)

        return result

    except Exception as e:

        print()

        print("=" * 60)
        print("ERROR")
        print("=" * 60)
        print(e)

        return None



##################################################
# Matching Builder
##################################################

def build_matching_pdf():

    print()

    print("=" * 60)

    print("Step 3. Matching Builder")

    print("=" * 60)

    try:

        pdf_path = create_matching_input()

        print()

        print("Matching_Input.pdf 생성 완료")

        print(pdf_path)

        return pdf_path

    except Exception as e:

        print()

        print("=" * 60)

        print("ERROR")

        print("=" * 60)

        print(e)

        return None

##################################################
# Matching Analysis
##################################################

def process_matching(
    matching_pdf
):

    print()

    print("=" * 60)

    print("Step 4. Matching Analysis")

    print("=" * 60)

    try:

        ##################################################
        # Upload
        ##################################################

        file_id = upload_file(
            matching_pdf
        )

        ##################################################
        # Agent
        ##################################################

        result = analyze_matching(
            file_id
        )

        ##################################################
        # Save
        ##################################################

        save_json(

            result,

            MATCHING_RESULT

        )

        print()

        print("Matching Result 저장 완료")

        print(MATCHING_RESULT)

        return result

    except Exception as e:

        print()

        print("=" * 60)

        print("ERROR")

        print("=" * 60)

        print(e)

        return None


##################################################
# Result
##################################################

def print_result():

    print()

    print("=" * 60)

    print("Project Complete")

    print("=" * 60)

    print()

    print("Generated Files")

    print("-" * 60)

    print(RESUME_JSON)

    print(JD_JSON)

    print(MATCHING_PDF)

    print(MATCHING_RESULT)

    print("-" * 60)


##################################################
# Main
##################################################

def main():

    print()

    print("=" * 60)

    print("HR AI Service")

    print("=" * 60)

    ##################################################
    # Config
    ##################################################

    validate_config()

    print_config()

    ##################################################
    # Resume Analysis
    ##################################################

    resume = process_document(

        step="Step 1. Resume Analysis",

        document_name="Resume",

        input_file=RESUME_FILE,

        analyzer=analyze_resume,

        output_json=RESUME_JSON

    )

    if resume is None:

        return

    ##################################################
    # JD Analysis
    ##################################################

    jd = process_document(

        step="Step 2. JD Analysis",

        document_name="JD",

        input_file=JD_FILE,

        analyzer=analyze_jd,

        output_json=JD_JSON

    )

    if jd is None:

        return

    ##################################################
    # Matching Builder
    ##################################################

    matching_pdf = build_matching_pdf()

    if matching_pdf is None:

        return

    ##################################################
    # Matching Analysis
    ##################################################

    matching_result = process_matching(

        matching_pdf

    )

    if matching_result is None:

        return

    ##################################################
    # Result
    ##################################################

    print_result()

##################################################

if __name__ == "__main__":

    main()