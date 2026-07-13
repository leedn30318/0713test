import streamlit as st
 
st.title("부엉이가 수영할 때 나는 소리는?")
st.write("첨부엉 첨부엉")

﻿﻿﻿숫자 = st.slider("좋아하는 숫자", 0, 100)
st.write("고른 숫자:", 숫자)
 
if st.button("풍선 날리기"):
	st.balloons()
