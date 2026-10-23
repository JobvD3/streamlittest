import streamlit as st
from wiskundaaaaaaaa import sommetje

crush = st.text_input("Write your crush")
st.write(f"Hey {crush}... You probably don't know who I am... B-but I really l-like you!")

nummer = st.number_input("Gibbe me a Number!!!!")
antwoord = sommetje(nummer)
st.write(f"You have {antwoord} banana's in your house")