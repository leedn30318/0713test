import streamlit as st
import pandas as pd


# =========================
# 화면 설정
# =========================
st.set_page_config(
    page_title="서울 양평 열섬 및 전력 분석",
    layout="wide"
)

st.title("🌡️ 서울·양평 열섬현상 & 전력수요 분석")



# =========================
# 데이터 읽기
# =========================
@st.cache_data
def read_data():

    seoul = pd.read_csv(
        "서울_기온.csv",
        encoding="cp949"
    )

    yang = pd.read_csv(
        "양평_기온.csv",
        encoding="cp949"
    )

    power = pd.read_csv(
        "전력수요.csv",
        encoding="cp949"
    )


    seoul["일시"] = pd.to_datetime(
        seoul["일시"]
    )

    yang["일시"] = pd.to_datetime(
        yang["일시"]
    )

    power["일시"] = pd.to_datetime(
        power["일시"]
    )


    return seoul, yang, power



try:
    seoul, yang, power = read_data()

except Exception as e:
    st.error("파일을 읽을 수 없습니다.")
    st.write(e)
    st.stop()



# =========================
# 컬럼 이름 변경
# =========================
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



# =========================
# 탭 생성
# =========================
tab1, tab2 = st.tabs(
    [
        "🏙️ 열섬 분석",
        "⚡ 전력 연결"
    ]
)



# =================================================
# 탭1 열섬 분석
# =================================================

with tab1:

    st.header("🏙️ 서울-양평 도시 열섬 분석")


    heat = pd.merge(
        seoul[["일시", "서울기온"]],
        yang[["일시", "양평기온"]],
        on="일시"
    )


    if len(heat) == 0:
        st.error("서울과 양평의 일시가 일치하는 데이터가 없습니다.")
        st.stop()


    heat["시각"] = heat["일시"].dt.hour
    heat["월"] = heat["일시"].dt.month

    heat["기온차"] = (
        heat["서울기온"]
        -
        heat["양평기온"]
    )


    # -----------------------
    # ① 연간 변화
    # -----------------------

    st.subheader(
        "① 서울과 양평의 1년간 기온 변화"
    )


    line_data = heat.set_index(
        "일시"
    )[[
        "서울기온",
        "양평기온"
    ]]


    st.line_chart(
        line_data
    )



    # -----------------------
    # ② 시간별 차이
    # -----------------------

    st.subheader(
        "② 시간별 평균 기온차 (서울-양평)"
    )


    hour = (
        heat.groupby("시각")
        ["기온차"]
        .mean()
    )


    hour_df = pd.DataFrame(
        {
            "시간": hour.index,
            "기온차": hour.values
        }
    )

    hour_df = hour_df.set_index(
        "시간"
    )


    st.bar_chart(
        hour_df
    )



    # -----------------------
    # ③ 월별 차이
    # -----------------------

    st.subheader(
        "③ 월별 평균 기온차 (서울-양평)"
    )


    month = (
        heat.groupby("월")
        ["기온차"]
        .mean()
    )


    month_df = pd.DataFrame(
        {
            "월": month.index,
            "기온차": month.values
        }
    )


    month_df = month_df.set_index(
        "월"
    )


    st.bar_chart(
        month_df
    )




# =================================================
# 탭2 전력 연결
# =================================================

with tab2:

    st.header(
        "⚡ 서울 기온과 전력수요 관계"
    )


    power_df = pd.merge(
        seoul[[
            "일시",
            "서울기온"
        ]],
        power[[
            "일시",
            "전력수요(MWh)"
        ]],
        on="일시"
    )


    if len(power_df) == 0:
        st.error(
            "서울 기온과 전력 데이터의 시간이 맞지 않습니다."
        )
        st.stop()



    power_df["월"] = (
        power_df["일시"]
        .dt.month
    )


    # -----------------------
    # ① 산점도
    # -----------------------

    st.subheader(
        "① 기온과 전력수요 산점도"
    )


    scatter_df = power_df[
        [
            "서울기온",
            "전력수요(MWh)"
        ]
    ]


    st.scatter_chart(
        scatter_df
    )



    # -----------------------
    # ② 기온 구간별 평균
    # -----------------------

    st.subheader(
        "② 기온 구간별 평균 전력수요"
    )


    power_df["기온구간"] = pd.cut(
        power_df["서울기온"],
        bins=[
            -50,
            0,
            10,
            20,
            30,
            50
        ],
        labels=[
            "0℃ 미만",
            "0~10℃",
            "10~20℃",
            "20~30℃",
            "30℃ 이상"
        ]
    )


    temp_power = (
        power_df
        .groupby("기온구간")
        ["전력수요(MWh)"]
        .mean()
    )


    temp_power = temp_power.dropna()


    temp_power_df = pd.DataFrame(
        {
            "기온구간": temp_power.index,
            "평균전력": temp_power.values
        }
    )


    temp_power_df = temp_power_df.set_index(
        "기온구간"
    )


    st.bar_chart(
        temp_power_df
    )



    # -----------------------
    # ③ 월별 평균 전력
    # -----------------------

    st.subheader(
        "③ 월별 평균 전력수요"
    )


    month_power = (
        power_df
        .groupby("월")
        ["전력수요(MWh)"]
        .mean()
    )


    month_power_df = pd.DataFrame(
        {
            "월": month_power.index,
            "평균전력": month_power.values
        }
    )


    month_power_df = month_power_df.set_index(
        "월"
    )


    st.bar_chart(
        month_power_df
    )
