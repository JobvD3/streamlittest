import streamlit as st
import pandas as pd

from feasability_check import is_bus_planning_feasible

st.title("Improve bus plan for bus lines 400 and 401")

with st.sidebar:
    st.subheader("Import here your data as excel files")
    timetable = st.file_uploader("Upload here your timetable", type="xlsx")
    bus_plan = st.file_uploader("Upload here your bus plan", type="xlsx")
    distance_matrix = st.file_uploader("Upload here your distance matrix", type="xlsx")

if (timetable != None) and (distance_matrix != None):
    df_timetable = pd.read_excel(timetable)
    df_distance_matrix = pd.read_excel(distance_matrix)
    if bus_plan != None:
        df_bus_plan = pd.read_excel(bus_plan)
        [feasible, error, df_bus_plan_v2] = is_bus_planning_feasible(df_bus_plan, df_distance_matrix)

        st.subheader(f"Is the bus plan feasible?")
        st.write(feasible)
        if feasible == False:
            st.subheader("The bus plan has errors")
            error_list = error.split("\n")
            st.write(error_list)
            st.write([1,2,3,5])