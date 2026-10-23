import streamlit as st
import pandas as pd
from feasability_check import is_bus_planning_feasible

with st.sidebar:
    timetable = st.file_uploader("Upload here your timetable", type="xlsx")
    bus_plan = st.file_uploader("Upload here your bus plan", type="xlsx")
    distance_matrix = st.file_uploader("Upload here your distance matrix", type="xlsx")

if (timetable != None) and (distance_matrix != None):
    if bus_plan != None:
        st.write(bus_plan)
        df = pd.DataFrame({"x" : [1,2,3,4],
                           "y" : [5,6,7,8]})
        st.write(df)
        # [feasible, error, df_bus_plan] = is_bus_planning_feasible(bus_plan, distance_matrix)
        # st.write(f"Is the bus plan feasible? {feasible}")
        # st.write(error)
