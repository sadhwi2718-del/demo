import streamlit as st 

st.title("welcome to streamlit")

name = st.text_input("enter your name")

if name:
    st.success(f"hello {name}")

age = st.slider("select your age hero", 1, 200)

st.write("age:", age)

if st.button("celebrate"):
    st.balloons()
    st.scatter_chart()
