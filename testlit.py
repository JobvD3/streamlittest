import streamlit as st
from wiskundaaaaaaaa import sommetje

sidebar_logo = "Untitled.png"
main_logo = "images (1).png"
st.logo(sidebar_logo, icon_image=main_logo, size="large")

st.html("""
  <style>
    [alt=Logo] {
      height: 5rem;
    }
  </style>
        """)

if "crush" not in st.session_state:
    st.session_state.crush = "name"

if "nummer" not in st.session_state:
    st.session_state.nummer = 0

st.title("Dafuq is going on here!!!!!!!")

with st.sidebar:
    crush = st.text_input("Write your crush")

    nummer = st.number_input("Gibbe me a Number!!!!")

st.write(f"Hey {crush}... You probably don't know who I am... B-but I really l-like you!")

antwoord = sommetje(nummer)
st.write(f"You have {antwoord} banana's in your house")

with st.container(border=True):
    st.subheader("Previous")

    st.write(f"Hey {st.session_state.crush}... You probably don't know who I am... B-but I really l-like you!")

    antwoord = sommetje(st.session_state.nummer)
    st.write(f"You have {antwoord} banana's in your house")

    st.session_state.crush = crush
    st.session_state.nummer = nummer
