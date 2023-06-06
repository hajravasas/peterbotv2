import streamlit as st

st.title("Welcome to CUSTOM ROUTE")


@st.cache
def my_route():
    st.write("Welcome to my new route!")
    st.title("Welcome to CUSTOM ROUTE")
