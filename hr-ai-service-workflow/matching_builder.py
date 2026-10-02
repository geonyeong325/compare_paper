"""
matching_builder.py

Resume Agent와 JD Agent의 결과(JSON)를 이용하여
Matching_Input.pdf를 생성한다.
"""

import json

from reportlab.pdfbase import pdfmetrics

from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib.enums import TA_CENTER

from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)

from reportlab.lib.units import cm

from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from config import (
    RESUME_JSON,
    JD_JSON,
    MATCHING_PDF,

    FONT_NAME,
    FONT_PATH
)

##################################################
# JSON Load
##################################################

def load_json(path):
    """
    JSON 파일 읽기
    """

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


##################################################
# Style
##################################################

pdfmetrics.registerFont(

    TTFont(

        FONT_NAME,

        str(FONT_PATH)

    )

)



styles = getSampleStyleSheet()


TITLE_STYLE = ParagraphStyle(

    "Title",

    parent=styles["Heading1"],

    fontName=FONT_NAME,

    fontSize=22,

    leading=30,

    alignment=TA_CENTER,

    spaceAfter=20

)


HEADING_STYLE = ParagraphStyle(

    "Heading",

    parent=styles["Heading2"],

    fontName=FONT_NAME,

    fontSize=14,

    leading=20,

    spaceBefore=12,

    spaceAfter=8

)


BODY_STYLE = ParagraphStyle(

    "Body",

    parent=styles["BodyText"],

    fontName=FONT_NAME,

    fontSize=10,

    leading=16,

    spaceAfter=4

)


##################################################
# PDF Document
##################################################

def create_document():
    """
    PDF Document 생성
    """

    return SimpleDocTemplate(

        str(MATCHING_PDF),

        pagesize=A4,

        leftMargin=2 * cm,

        rightMargin=2 * cm,

        topMargin=2 * cm,

        bottomMargin=2 * cm

    )

##################################################
# Story
##################################################

def create_story():
    """
    PDF Story 생성
    """

    return []



##################################################
# Title
##################################################

def add_title(
    story,
    title
):
    """
    Title 추가
    """

    story.append(

        Paragraph(

            title,

            TITLE_STYLE

        )

    )

    story.append(

        Spacer(
            1,
            0.5 * cm
        )

    )

##################################################
# Heading
##################################################

def add_heading(
    story,
    heading
):
    """
    Heading 추가
    """

    story.append(

        Paragraph(

            heading,

            HEADING_STYLE

        )

    )


##################################################
# Text
##################################################

def add_text(
    story,
    text
):
    """
    일반 Text 추가

    Studio Extract 노드는 값을 리스트로 반환하므로
    리스트이면 ", "로 이어 붙여 한 줄로 만든다.
    """

    if isinstance(
        text,
        list
    ):

        text = ", ".join(
            str(item) for item in text
        )

    if not text:

        text = "-"

    story.append(

        Paragraph(

            str(text),

            BODY_STYLE

        )

    )

##################################################
# List
##################################################

def add_list(
    story,
    items
):
    """
    목록 추가
    """

    if not items:

        add_text(
            story,
            "-"
        )

        return

    if isinstance(
        items,
        str
    ):

        items = [items]

    for item in items:

        story.append(

            Paragraph(

                f"• {item}",

                BODY_STYLE

            )

        )


##################################################
# Flat List → Item List
##################################################

def group_items(
    data,
    **fields
):
    """
    Resume Agent의 Extract 결과는
    company, career_position, career_period 처럼
    항목별로 나뉜 리스트(평면 구조)로 온다.

    같은 순서(index)의 값을 하나의 dict로 묶어
    [{company, position, period, description}, ...] 형태로 만든다.

    fields : 출력 키 = Resume JSON 키
    """

    columns = {}

    for key, source in fields.items():

        value = data.get(source, [])

        if isinstance(value, str):

            value = [value]

        columns[key] = value or []

    count = max(
        (len(v) for v in columns.values()),
        default=0
    )

    items = []

    for index in range(count):

        item = {}

        for key, values in columns.items():

            item[key] = values[index] if index < len(values) else ""

        items.append(item)

    return items


##################################################
# Resume
##################################################

def add_resume(
    story,
    resume
):
    """
    Resume Section
    """

    add_title(
        story,
        "Resume"
    )

    add_heading(
        story,
        "Name"
    )

    add_text(
        story,
        resume.get("name")
    )

    add_heading(
        story,
        "Position"
    )

    add_text(
        story,
        resume.get("position")
    )

    add_heading(
        story,
        "Email"
    )

    add_text(
        story,
        resume.get("email")
    )

    add_heading(
        story,
        "Phone"
    )

    add_text(
        story,
        resume.get("phone")
    )

    add_heading(
        story,
        "Location"
    )

    add_text(
        story,
        resume.get("location")
    )

    add_heading(
        story,
        "Summary"
    )

    add_text(
        story,
        resume.get("summary")
    )

    add_heading(
        story,
        "Skills"
    )

    add_list(
        story,
        resume.get("skills", [])
    )

    add_heading(
        story,
        "Career"
    )

    add_career(
        story,
        group_items(
            resume,
            company="company",
            position="career_position",
            period="career_period",
            description="career_description"
        )
    )

    add_heading(
        story,
        "Projects"
    )

    add_projects(
        story,
        group_items(
            resume,
            name="project_name",
            period="project_period",
            description="project_description",
            skills="project_skills"
        )
    )

    add_heading(
        story,
        "Education"
    )

    add_education(
        story,
        group_items(
            resume,
            school="school",
            major="major",
            period="education_period"
        )
    )

    add_heading(
        story,
        "Certifications"
    )

    add_list(
        story,
        resume.get("certifications", [])
    )

    add_heading(
        story,
        "Core Competencies"
    )

    add_list(
        story,
        resume.get("core_competencies", [])
    )


##################################################
# Career
##################################################

def add_career(
    story,
    careers
):
    """
    Career 추가
    """

    if not careers:

        add_text(
            story,
            "-"
        )

        return

    for career in careers:

        add_text(
            story,
            f"Company : {career.get('company','')}"
        )

        add_text(
            story,
            f"Position : {career.get('position','')}"
        )

        add_text(
            story,
            f"Period : {career.get('period','')}"
        )

        add_text(
            story,
            career.get(
                "description",
                ""
            )
        )

        story.append(
            Spacer(
                1,
                0.3 * cm
            )
        )

##################################################
# Projects
##################################################

def add_projects(
    story,
    projects
):
    """
    Project 추가
    """

    if not projects:

        add_text(
            story,
            "-"
        )

        return

    for project in projects:

        add_text(
            story,
            f"Project : {project.get('name','')}"
        )

        add_text(
            story,
            f"Period : {project.get('period','')}"
        )

        add_text(
            story,
            project.get(
                "description",
                ""
            )
        )

        add_heading(
            story,
            "Skills"
        )

        add_list(
            story,
            project.get(
                "skills",
                []
            )
        )

        story.append(
            Spacer(
                1,
                0.3 * cm
            )
        )

##################################################
# Education
##################################################

def add_education(
    story,
    educations
):
    """
    Education 추가
    """

    if not educations:

        add_text(
            story,
            "-"
        )

        return

    for edu in educations:

        add_text(
            story,
            f"School : {edu.get('school','')}"
        )

        add_text(
            story,
            f"Major : {edu.get('major','')}"
        )

        add_text(
            story,
            f"Period : {edu.get('period','')}"
        )

        story.append(
            Spacer(
                1,
                0.3 * cm
            )
        )

##################################################
# Job Description
##################################################

def add_job_description(
    story,
    jd
):
    """
    Job Description Section
    """

    add_title(
        story,
        "Job Description"
    )

    add_heading(
        story,
        "Company"
    )

    add_text(
        story,
        jd.get("company_name")
    )

    add_heading(
        story,
        "Position"
    )

    add_text(
        story,
        jd.get("position")
    )

    add_heading(
        story,
        "Responsibilities"
    )

    add_list(
        story,
        jd.get("responsibilities", [])
    )

    add_heading(
        story,
        "Required Skills"
    )

    add_list(
        story,
        jd.get("required_skills", [])
    )

    add_heading(
        story,
        "Preferred Skills"
    )

    add_list(
        story,
        jd.get("preferred_skills", [])
    )

    add_heading(
        story,
        "Qualifications"
    )

    add_list(
        story,
        jd.get("qualifications", [])
    )

    add_heading(
        story,
        "Preferred Qualifications"
    )

    add_list(
        story,
        jd.get("preferred_qualifications", [])
    )

    add_heading(
        story,
        "Experience Required"
    )

    add_text(
        story,
        jd.get("experience_required")
    )

    add_heading(
        story,
        "Education Required"
    )

    add_text(
        story,
        jd.get("education_required")
    )

    add_heading(
        story,
        "Employment Type"
    )

    add_text(
        story,
        jd.get("employment_type")
    )

    add_heading(
        story,
        "Location"
    )

    add_text(
        story,
        jd.get("location")
    )


##################################################
# PDF Build
##################################################

def build_pdf(
    doc,
    story
):
    """
    PDF 생성
    """

    doc.build(
        story
    )


##################################################
# Matching Input 생성
##################################################

def create_matching_input():
    """
    Resume JSON + JD JSON

            ↓

    Matching_Input.pdf 생성
    """

    print()

    print("=" * 60)

    print("Matching Input PDF 생성")

    print("=" * 60)

    print()

    ##################################################
    # Resume Load
    ##################################################

    print("Resume JSON Load...")

    resume = load_json(
        RESUME_JSON
    )

    print("Success")

    ##################################################
    # JD Load
    ##################################################

    print("JD JSON Load...")

    jd = load_json(
        JD_JSON
    )

    print("Success")

    print()

    ##################################################
    # PDF 생성
    ##################################################

    print("PDF Document 생성...")

    doc = create_document()

    story = create_story()

    print("Success")

    print()

    ##################################################
    # Resume
    ##################################################

    print("Resume 작성...")

    add_resume(
        story,
        resume
    )

    print("Success")

    ##################################################
    # Page Break 대신 여백
    ##################################################

    story.append(

        Spacer(
            1,
            1 * cm
        )

    )

    ##################################################
    # JD
    ##################################################

    print("Job Description 작성...")

    add_job_description(
        story,
        jd
    )

    print("Success")

    print()

    ##################################################
    # PDF 저장
    ##################################################

    print("PDF 저장...")

    build_pdf(
        doc,
        story
    )

    print("Success")

    print()

    print("Matching_Input.pdf 저장 완료")

    print(MATCHING_PDF)

    print()

    return MATCHING_PDF







