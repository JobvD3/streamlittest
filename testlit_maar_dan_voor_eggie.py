import streamlit as st
import pandas as pd
from feasability_check import is_bus_planning_feasible

with st.sidebar:
    timetable = st.file_uploader("Upload here your timetable")
    bus_plan = st.file_uploader("Upload here your bus plan")
    distance_matrix = st.file_uploader("Upload here your distance matrix")

if (timetable != None) and (distance_matrix != None):
    if bus_plan != None:
        df = pd.read_csv(bus_plan)
        st.write(type(df))
        # [feasible, error, df_bus_plan] = is_bus_planning_feasible(bus_plan, distance_matrix)
        # st.write(f"Is the bus plan feasible? {feasible}")
        # st.write(error)
