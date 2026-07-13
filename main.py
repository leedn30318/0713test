import streamlit as st
import pandas as pd


# ---------------------------------
# 페이지 설정
# ---------------------------------
st.set_page_config(
    page_title="서울·양평 열섬 및 전력 분석",
    page_icon="🌡️",
    layout="wide"
)


st.title("🌡️ 서울·양평 기온 기반 열섬현상 및 전력수요 분석")
st.write(
    "2025년 시간별 데이터를 이용하여 도시 열섬현상과 "
    "기온 변화에 따른 전력수요 관계를 분석합니다."
)



# ---------------------------------
# 데이터 불러오기
# ---------------------------------
@st.cache_data
def load_data():

    seoul_temp = pd.read_csv(
        "서울_기온.csv",
        encoding="cp949"
    )

    yang_temp = pd.read_csv(
        "양평_기온.csv",
        encoding="cp949"
    )

    power = pd.read_csv(
        "전력수요.csv",
        encoding="cp949"
    )


    # 날짜 변환
    seoul_temp["일시"] = pd.to_datetime(
        seoul_temp["일시"]
    )

    yang_temp["일시"] = pd.to_datetime(
        yang_temp["일시"]
    )

    power["일시"] = pd.to_datetime(
        power["일시"]
    )


    return seoul_temp, yang_temp, power



seoul, yang, power = load_data()



# ---------------------------------
# 데이터 전처리
# ---------------------------------

# 기온 컬럼 이름 변경
seoul = seoul.rename(
    columns={
        "기온(°C)": "서울기온"
    }
)

yang = yang.rename(
    columns={
        "기온(°C)": "양평기온"
    }
)



# ================================
# 탭 생성
# ================================
tab1, tab2 = st.tabs(
    [
        "🏙️ 열섬 분석",
        "⚡ 전력 연결"
    ]
)



# =================================================
# 탭1 : 열섬 분석
# =================================================
with tab1:

    st.header("🏙️ 서울-양평 도시 열섬현상 분석")


    # 서울 + 양평 병합
    heat_df = pd.merge(
        seoul[
            ["일시", "서울기온"]
        ],
        yang[
            ["일시", "양평기온"]
        ],
        on="일시"
    )


    heat_df["시각"] = (
        heat_df["일시"]
        .dt.hour
    )

    heat_df["월"] = (
        heat_df["일시"]
        .dt.month
    )


    heat_df["기온차"] = (
        heat_df["서울기온"]
        -
        heat_df["양평기온"]
    )


    # -----------------------------
    # ① 연간 기온 변화
    # -----------------------------
    st.subheader(
        "① 1년간 서울과 양평의 기온 변화"
    )


    yearly = heat_df.set_index(
        "일시"
    )[
        [
            "서울기온",
            "양평기온"
        ]
    ]


    st.line_chart(
        yearly,
        height=450
    )



    # -----------------------------
    # ② 시간별 평균 기온차
    # -----------------------------
    st.subheader(
        "② 시각별 평균 기온차 (서울-양평)"
    )


    hourly_diff = (
        heat_df
        .groupby("시각")["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )


    hourly_diff.columns = [
        "평균 기온차(℃)"
    ]


    st.bar_chart(
        hourly_diff,
        height=400
    )


    st.caption(
        "※ 기온차가 클수록 서울의 도시 열섬 효과가 크게 나타남"
    )



    # -----------------------------
    # ③ 월별 평균 기온차
    # -----------------------------
    st.subheader(
        "③ 월별 평균 기온차 (서울-양평)"
    )


    monthly_diff = (
        heat_df
        .groupby("월")["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )


    monthly_diff.columns = [
        "평균 기온차(℃)"
    ]


    st.bar_chart(
        monthly_diff,
        height=400
    )



# =================================================
# 탭2 : 전력 연결
# =================================================
with tab2:

    st.header(
        "⚡ 서울 기온과 전력수요 관계 분석"
    )


    # 서울 기온 + 전력 병합
    power_df = pd.merge(
        seoul[
            [
                "일시",
                "서울기온"
            ]
        ],
        power[
            [
                "일시",
                "전력수요(MWh)"
            ]
        ],
        on="일시"
    )


    power_df["월"] = (
        power_df["일시"]
        .dt.month
    )


    # -----------------------------
    # ① 산점도
    # -----------------------------
    st.subheader(
        "① 기온과 전력수요 관계"
    )


    scatter = power_df[
        [
            "서울기온",
            "전력수요(MWh)"
        ]
    ]


    st.scatter_chart(
        scatter,
        x="서울기온",
        y="전력수요(MWh)",
        height=450
    )


    st.caption(
        "※ 기온 변화에 따라 전력수요가 어떻게 변하는지 확인"
    )



    # -----------------------------
    # ② 기온 구간별 평균 전력수요
    # -----------------------------
    st.subheader(
        "② 기온 구간별 평균 전력수요"
    )


    # 기온 구간 생성
    power_df["기온구간"] = pd.cut(
        power_df["서울기온"],
        bins=[
            -20,0,5,10,15,20,25,30,40
        ],
        labels=[
            "-20~0",
            "0~5",
            "5~10",
            "10~15",
            "15~20",
            "20~25",
            "25~30",
            "30 이상"
        ]
    )


    temp_power = (
        power_df
        .groupby("기온구간",
                 observed=True)
        ["전력수요(MWh)"]
        .mean()
        .round(1)
        .to_frame()
    )


    st.bar_chart(
        temp_power,
        height=400
    )



    # -----------------------------
    # ③ 월별 평균 전력수요
    # -----------------------------
    st.subheader(
        "③ 월별 평균 전력수요"
    )


    month_power = (
        power_df
        .groupby("월")
        ["전력수요(MWh)"]
        .mean()
        .round(1)
        .to_frame()
    )


    st.bar_chart(
        month_power,
        height=400
    )



# ---------------------------------
# 하단 데이터 확인
# ---------------------------------
with st.expander("📄 데이터 확인"):

    st.write("서울-양평 기온 데이터")
    st.dataframe(
        heat_df.head(20)
    )

    st.write("서울 기온-전력 데이터")
    st.dataframe(
        power_df.head(20)
    )
