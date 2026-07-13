import streamlit as st
import pandas as pd


# 페이지 설정
st.set_page_config(
    page_title="서울-양평 도시 열섬현상 분석",
    layout="wide"
)

st.title("🌡️ 서울과 양평의 기온 비교 - 도시 열섬현상 분석")


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():

    seoul = pd.read_csv(
        "서울_기온.csv",
        encoding="cp949"
    )

    yangpyeong = pd.read_csv(
        "양평_기온.csv",
        encoding="cp949"
    )

    # 날짜 변환
    seoul["일시"] = pd.to_datetime(seoul["일시"])
    yangpyeong["일시"] = pd.to_datetime(yangpyeong["일시"])

    return seoul, yangpyeong


seoul, yangpyeong = load_data()


# -----------------------------
# 데이터 전처리
# -----------------------------
seoul = seoul.rename(columns={"기온(°C)": "서울기온"})
yangpyeong = yangpyeong.rename(columns={"기온(°C)": "양평기온"})


# 날짜 기준 병합
df = pd.merge(
    seoul[["일시", "서울기온"]],
    yangpyeong[["일시", "양평기온"]],
    on="일시"
)


# 시간, 월 추출
df["시각"] = df["일시"].dt.hour
df["월"] = df["일시"].dt.month

# 서울-양평 기온 차
df["기온차"] = df["서울기온"] - df["양평기온"]



# -----------------------------
# ① 1년간 기온 변화
# -----------------------------
st.header("① 1년간 서울과 양평의 기온 변화")

temperature_chart = df.set_index("일시")[
    ["서울기온", "양평기온"]
]

st.line_chart(temperature_chart)


# -----------------------------
# ② 시간별 평균 기온차
# -----------------------------
st.header("② 시간(0~23시)별 평균 기온차")

hour_diff = (
    df.groupby("시각")["기온차"]
    .mean()
    .to_frame()
)

hour_diff.columns = ["서울-양평 평균 기온차(°C)"]

st.bar_chart(hour_diff)



# -----------------------------
# ③ 월별 평균 기온차
# -----------------------------
st.header("③ 월(1~12월)별 평균 기온차")

month_diff = (
    df.groupby("월")["기온차"]
    .mean()
    .to_frame()
)

month_diff.columns = ["서울-양평 평균 기온차(°C)"]

st.bar_chart(month_diff)



# -----------------------------
# 요약 정보
# -----------------------------
st.header("📊 열섬현상 요약")

avg_difference = df["기온차"].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "연평균 서울-양평 기온차",
        f"{avg_difference:.2f} °C"
    )

with col2:
    st.metric(
        "최대 기온차",
        f"{df['기온차'].max():.2f} °C"
    )

with col3:
    st.metric(
        "최소 기온차",
        f"{df['기온차'].min():.2f} °C"
    )


st.info(
    "서울의 기온이 양평보다 높게 나타나는 경우(양수)는 "
    "도시 열섬효과가 강하게 나타나는 시간 또는 계절로 해석할 수 있습니다."
)
