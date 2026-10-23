import streamlit as st
import pandas as pd
print("yo")
from feasability_check import is_bus_planning_feasible

with st.sidebar:
    timetable = st.file_uploader("Upload here your timetable", type="xlsx")
    bus_plan = st.file_uploader("Upload here your bus plan", type="xlsx")
    distance_matrix = st.file_uploader("Upload here your distance matrix", type="xlsx")

if (timetable != None) and (distance_matrix != None):
    df_timetable = pd.read_excel(timetable)
    df_distance_matrix = pd.read_excel(distance_matrix)
    if bus_plan != None:
        df_bus_plan = pd.read_excel(bus_plan)
        [feasible, error, df_bus_plan_v2] = is_bus_planning_feasible(df_bus_plan, df_distance_matrix)
        st.write(f"Is the bus plan feasible? {feasible}")
        st.write(error)