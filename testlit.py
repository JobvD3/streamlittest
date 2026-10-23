import streamlit as st
from wiskundaaaaaaaa import sommetje

st.title("Dafuq is going on here!!!!!!!")

with st.sidebar:
    crush = st.text_input("Write your crush")
    nummer = st.number_input("Gibbe me a Number!!!!")

st.write(f"Hey {crush}... You probably don't know who I am... B-but I really l-like you!")

antwoord = sommetje(nummer)
st.write(f"You have {antwoord} banana's in your house")