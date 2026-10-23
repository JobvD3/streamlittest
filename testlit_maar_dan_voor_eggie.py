import streamlit as st
import pandas as pd
print("yo")
from feasability_check import is_bus_planning_feasible

with st.sidebar:
    timetable = pd.read_excel(st.file_uploader("Upload here your timetable", type="xlsx"))
    bus_plan = pd.read_excel(st.file_uploader("Upload here your bus plan", type="xlsx"))
    distance_matrix = pd.read_excel(st.file_uploader("Upload here your distance matrix", type="xlsx"))

if (timetable != None) and (distance_matrix != None):
    if bus_plan != None:
        [feasible, error, df_bus_plan] = is_bus_planning_feasible(bus_plan, distance_matrix)
        st.write(f"Is the bus plan feasible? {feasible}")
        st.write(error)