import streamlit as st
import pandas as pd


# -----------------------------
# 화면 설정
# -----------------------------
st.set_page_config(
    page_title="서울-양평 도시 열섬 분석",
    page_icon="🌡️",
    layout="wide"
)


# -----------------------------
# CSS 디자인
# -----------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }

    .title-box {
        background: linear-gradient(90deg,#4facfe,#00f2fe);
        padding: 25px;
        border-radius: 15px;
        color:white;
        text-align:center;
        margin-bottom:30px;
    }

    .card {
        background:white;
        padding:20px;
        border-radius:15px;
        box-shadow:0 4px 10px rgba(0,0,0,0.08);
        text-align:center;
    }

    h1 {
        font-size:40px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# 제목
# -----------------------------
st.markdown(
    """
    <div class="title-box">
        <h1>🌡️ 서울 vs 양평 기온 비교</h1>
        <h3>도시 열섬현상 분석 웹 대시보드</h3>
    </div>
    """,
    unsafe_allow_html=True
)


st.write(
    """
    서울(도시 지역)과 양평(비도시 지역)의 시간별 기온 데이터를 비교하여
    도시 열섬 현상이 언제, 어느 계절에 강하게 나타나는지 분석합니다.
    """
)



# -----------------------------
# 데이터 읽기
# -----------------------------
@st.cache_data
def load_data():

    seoul = pd.read_csv(
        "서울_기온.csv",
        encoding="cp949"
    )

    yang = pd.read_csv(
        "양평_기온.csv",
        encoding="cp949"
    )

    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yang["일시"] = pd.to_datetime(yang["일시"])

    return seoul, yang


seoul, yang = load_data()



# -----------------------------
# 데이터 정리
# -----------------------------
seoul = seoul.rename(
    columns={"기온(°C)": "서울기온"}
)

yang = yang.rename(
    columns={"기온(°C)": "양평기온"}
)


df = pd.merge(
    seoul[["일시","서울기온"]],
    yang[["일시","양평기온"]],
    on="일시"
)


df["시각"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

df["기온차"] = (
    df["서울기온"]
    -
    df["양평기온"]
)



# -----------------------------
# 요약 카드
# -----------------------------
st.subheader("📌 전체 분석 결과")


avg = df["기온차"].mean()
max_diff = df["기온차"].max()
max_time = df.loc[
    df["기온차"].idxmax(),
    "일시"
]


c1,c2,c3 = st.columns(3)


with c1:
    st.metric(
        "평균 서울-양평 기온차",
        f"{avg:.2f} ℃"
    )

with c2:
    st.metric(
        "최대 기온차",
        f"{max_diff:.2f} ℃"
    )

with c3:
    st.metric(
        "최대 발생 시간",
        max_time.strftime("%m월 %d일 %H시")
    )



# -----------------------------
# 탭 구성
# -----------------------------
tab1, tab2, tab3 = st.tabs(
    [
        "📈 연간 변화",
        "🕒 시간별 분석",
        "📅 월별 분석"
    ]
)



# 1년 변화
with tab1:

    st.subheader(
        "서울과 양평의 1년간 기온 변화"
    )

    chart = df.set_index("일시")[
        [
            "서울기온",
            "양평기온"
        ]
    ]

    st.line_chart(
        chart,
        height=500
    )



# 시간별
with tab2:

    st.subheader(
        "시간대별 평균 기온차"
    )

    hour = (
        df.groupby("시각")
        ["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )

    hour.columns=[
        "서울-양평 평균 기온차(℃)"
    ]

    st.bar_chart(
        hour,
        height=450
    )


    st.caption(
        "※ 양수 값이 클수록 서울의 열섬 효과가 강함"
    )



# 월별
with tab3:

    st.subheader(
        "월별 평균 기온차"
    )

    month = (
        df.groupby("월")
        ["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )


    month.columns=[
        "서울-양평 평균 기온차(℃)"
    ]

    st.bar_chart(
        month,
        height=450
    )



# -----------------------------
# 데이터 보기
# -----------------------------
with st.expander("📄 원본 데이터 확인"):

    st.dataframe(
        df.head(100),
        use_container_width=True
    )
