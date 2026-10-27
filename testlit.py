import streamlit as st
import pandas as pd
from io import BytesIO

from wiskundaaaaaaaa import sommetje
from opmaak import background_image

img = background_image("images (1).png")
st.markdown(img, unsafe_allow_html=True)

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

with st.container(border=True):
    df=pd.DataFrame({'Num_col': [1000, 2000, 3000], 'Comma_col': [4000, 5000, 6000], 'PC_col': [18, 83, 64]})
    st.dataframe(df)

    flnme = st.text_input('Enter Excel file name (e.g. email_data.xlsx)')
    if flnme != "":
        if flnme.endswith(".xlsx") == False:  # add file extension if it is forgotten
            flnme = flnme + ".xlsx"

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Report')

        st.download_button(label="Download Excel workbook", data=buffer.getvalue(), file_name=flnme, mime="application/vnd.ms-excel")

