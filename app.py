# app.py -- 우리 반 성적 분석 대시보드 (화면)
import json
import os
import streamlit as st
from utils import (total_score, average_score, to_grade, grade_to_gpa,
                   subject_average, subject_top, grade_distribution,
                   rank_list, pass_rate)

st.set_page_config(page_title="성적 분석 대시보드", layout="wide")

# ── 데이터 영속성: JSON 파일로 저장/불러오기 ──────────────────────────────
DATA_FILE = "students.json"

SAMPLE_STUDENTS = [
    {"이름": "김민준", "국어": 92,  "영어": 85, "수학": 78},
    {"이름": "이서연", "국어": 88,  "영어": 90, "수학": 95},
    {"이름": "박도윤", "국어": 60,  "영어": 55, "수학": 72},
    {"이름": "최지우", "국어": 100, "영어": 80, "수학": 90},
    {"이름": "정하준", "국어": 45,  "영어": 60, "수학": 58},
]


def load_students():
    """JSON 파일에서 학생 데이터를 불러온다. 없으면 샘플 데이터 반환."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return list(SAMPLE_STUDENTS)


def save_students(students):
    """학생 데이터를 JSON 파일에 저장한다."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(students, f, ensure_ascii=False, indent=2)


# 처음 실행 시 파일에서 불러와 세션에 보관
if "students" not in st.session_state:
    st.session_state.students = load_students()

students = st.session_state.students

# ── 상단 배너 이미지 ──────────────────────────────────────────────────────
st.image("banner.png", width="stretch")
st.title("우리 반 성적 분석 대시보드")

SUBJECTS = ["국어", "영어", "수학"]

# ── 상단 요약 지표 ────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("응시 인원", f"{len(students)}명")

avgs = [average_score(stu) for stu in students]
overall = sum(avgs) / len(avgs)
col2.metric("전체 평균", round(overall, 2))
col3.metric("합격률", f"{pass_rate(students):.1f}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["✏️ 학생 입력", "📋 학생별 성적", "📊 과목별 통계", "🏆 석차 & 분포"])

# ── Tab 1 : 학생 추가 ─────────────────────────────────────────────────────
with tab1:
    st.header("학생 추가")
    name = st.text_input("이름")
    kor = st.number_input("국어", 0, 100, 0)
    eng = st.number_input("영어", 0, 100, 0)
    mat = st.number_input("수학", 0, 100, 0)
    if st.button("추가"):
        if name.strip() == "":
            st.warning("이름을 입력해 주세요.")
        else:
            new_student = {"이름": name.strip(), "국어": int(kor), "영어": int(eng), "수학": int(mat)}
            students.append(new_student)
            save_students(students)
            st.success(f"✅ {name} 학생을 추가했습니다.")
            st.rerun()

    st.divider()
    st.subheader("현재 명단")
    if students:
        for i, stu in enumerate(students):
            st.write(f"{i+1}. {stu['이름']} — 국어: {stu['국어']}, 영어: {stu['영어']}, 수학: {stu['수학']}")
    else:
        st.info("등록된 학생이 없습니다.")

# ── Tab 2 : 학생별 성적표 ─────────────────────────────────────────────────
with tab2:
    st.header("학생별 성적표")
    table = []
    for stu in students:
        avg = average_score(stu)
        grade = to_grade(avg)
        table.append({
            "이름": stu["이름"],
            "국어": stu["국어"],
            "영어": stu["영어"],
            "수학": stu["수학"],
            "총점": total_score(stu),
            "평균": round(avg, 2),
            "학점": grade,
            "평점(GPA)": grade_to_gpa(grade),
            "합격여부": "합격" if avg >= 60 else "불합격",
        })
    st.table(table)

# ── Tab 3 : 과목별 통계 ───────────────────────────────────────────────────
with tab3:
    st.header("과목별 통계")
    cols = st.columns(3)
    for i in range(len(SUBJECTS)):
        subject = SUBJECTS[i]
        with cols[i]:
            st.subheader(subject)
            avg_val = subject_average(students, subject)
            top_val = subject_top(students, subject)
            st.metric("평균", avg_val)
            st.metric("최고점", top_val)

    st.subheader("과목별 평균 비교")
    chart_data = [{"과목": subject, "평균": subject_average(students, subject)} for subject in SUBJECTS]
    st.bar_chart(chart_data, x="과목", y="평균", horizontal=True, height=400)

# ── Tab 4 : 석차 & 학점 분포 ─────────────────────────────────────────────
with tab4:
    st.header("석차")
    ranked = rank_list(students)
    rank_table = []
    rank = 1
    for stu in ranked:
        avg = average_score(stu)
        grade = to_grade(avg)
        rank_table.append({
            "석차": rank,
            "이름": stu["이름"],
            "총점": total_score(stu),
            "평균": round(avg, 2),
            "학점": grade,
            "합격여부": "합격" if avg >= 60 else "불합격",
        })
        rank = rank + 1
    st.table(rank_table)

    st.header("학점 분포")
    dist = grade_distribution(students)
    dist_data = [{"학점": g, "인원": dist[g]} for g in ["A", "B", "C", "D", "F"]]
    st.bar_chart(dist_data, x="학점", y="인원", horizontal=True, height=400)
