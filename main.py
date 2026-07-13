import streamlit as st
import pandas as pd


# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="서울·양평 열섬 및 전력 분석",
    page_icon="🌡️",
    layout="wide"
)


st.title("🌡️ 서울·양평 기온 기반 열섬현상 및 전력수요 분석")

st.write(
    "2025년 시간별 기온 데이터를 이용하여 "
    "서울과 양평의 도시 열섬현상 및 기온과 전력수요의 관계를 분석합니다."
)



# =========================
# 데이터 불러오기
# =========================
@st.cache_data
def load_csv():

    try:
        seoul = pd.read_csv(
            "서울_기온.csv",
            encoding="cp949"
        )

        yangpyeong = pd.read_csv(
            "양평_기온.csv",
            encoding="cp949"
        )

        power = pd.read_csv(
            "전력수요.csv",
            encoding="cp949"
        )

    except Exception as e:
        st.error("CSV 파일을 불러오는 중 오류가 발생했습니다.")
        st.error(e)
        st.stop()


    # 날짜 변환
    seoul["일시"] = pd.to_datetime(
        seoul["일시"],
        errors="coerce"
    )

    yangpyeong["일시"] = pd.to_datetime(
        yangpyeong["일시"],
        errors="coerce"
    )

    power["일시"] = pd.to_datetime(
        power["일시"],
        errors="coerce"
    )


    return seoul, yangpyeong, power



seoul, yangpyeong, power = load_csv()



# =========================
# 컬럼명 변경
# =========================
seoul = seoul.rename(
    columns={
        "기온(°C)": "서울기온"
    }
)

yangpyeong = yangpyeong.rename(
    columns={
        "기온(°C)": "양평기온"
    }
)



# =========================
# 탭 생성
# =========================
tab1, tab2 = st.tabs(
    [
        "🏙️ 열섬 분석",
        "⚡ 전력 연결"
    ]
)



# =====================================================
# 탭1 : 열섬 분석
# =====================================================
with tab1:

    st.header("🏙️ 서울-양평 도시 열섬현상 분석")


    # 서울 + 양평 합치기
    heat = pd.merge(
        seoul[
            [
                "일시",
                "서울기온"
            ]
        ],
        yangpyeong[
            [
                "일시",
                "양평기온"
            ]
        ],
        on="일시",
        how="inner"
    )


    heat["시각"] = heat["일시"].dt.hour
    heat["월"] = heat["일시"].dt.month


    # 서울 - 양평
    heat["기온차"] = (
        heat["서울기온"]
        -
        heat["양평기온"]
    )



    # -------------------------
    # 1. 연간 기온 변화
    # -------------------------
    st.subheader(
        "① 1년간 서울과 양평의 기온 변화"
    )


    year_chart = heat.set_index(
        "일시"
    )[
        [
            "서울기온",
            "양평기온"
        ]
    ]


    st.line_chart(
        year_chart,
        height=450
    )



    # -------------------------
    # 2. 시간별 평균 차이
    # -------------------------
    st.subheader(
        "② 시각별 평균 기온차 (서울-양평)"
    )


    hour_diff = (
        heat
        .groupby("시각")["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )


    hour_diff.columns = [
        "평균 기온차(℃)"
    ]


    st.bar_chart(
        hour_diff,
        height=400
    )



    # -------------------------
    # 3. 월별 평균 차이
    # -------------------------
    st.subheader(
        "③ 월별 평균 기온차 (서울-양평)"
    )


    month_diff = (
        heat
        .groupby("월")["기온차"]
        .mean()
        .round(2)
        .to_frame()
    )


    month_diff.columns = [
        "평균 기온차(℃)"
    ]


    st.bar_chart(
        month_diff,
        height=400
    )



# =====================================================
# 탭2 : 전력 연결
# =====================================================
with tab2:

    st.header(
        "⚡ 서울 기온과 전력수요 관계 분석"
    )


    # 서울 기온 + 전력 합치기
    power_data = pd.merge(
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
        on="일시",
        how="inner"
    )


    power_data["월"] = (
        power_data["일시"]
        .dt.month
    )



    # -------------------------
    # 1. 산점도
    # -------------------------
    st.subheader(
        "① 기온과 전력수요 관계"
    )


    scatter_data = power_data[
        [
            "서울기온",
            "전력수요(MWh)"
        ]
    ]


    st.scatter_chart(
        scatter_data,
        height=450
    )



    # -------------------------
    # 2. 기온 구간별 평균 전력
    # -------------------------
    st.subheader(
        "② 기온 구간별 평균 전력수요"
    )


    power_data["기온구간"] = pd.cut(
        power_data["서울기온"],
        bins=[
            -20,
            0,
            5,
            10,
            15,
            20,
            25,
            30,
            40
        ],
        labels=[
            "-20~0℃",
            "0~5℃",
            "5~10℃",
            "10~15℃",
            "15~20℃",
            "20~25℃",
            "25~30℃",
            "30℃ 이상"
        ]
    )


    temp_power = (
        power_data
        .groupby("기온구간")
        ["전력수요(MWh)"]
        .mean()
        .round(1)
        .dropna()
        .to_frame()
    )


    st.bar_chart(
        temp_power,
        height=400
    )



    # -------------------------
    # 3. 월별 평균 전력
    # -------------------------
    st.subheader(
        "③ 월별 평균 전력수요"
    )


    month_power = (
        power_data
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



# =========================
# 데이터 확인
# =========================
with st.expander("📄 데이터 확인"):

    st.write("열섬 분석 데이터")
    st.dataframe(
        heat.head(20),
        use_container_width=True
    )


    st.write("전력 분석 데이터")
    st.dataframe(
        power_data.head(20),
        use_container_width=True
    )
