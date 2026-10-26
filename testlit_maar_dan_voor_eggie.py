import streamlit as st
import pandas as pd

from opmaak import background_image
from make_data_usable import str_to_time
from feasability_check import is_bus_planning_feasible
from bus_plan_check import bus_plan_timetable_check
from Improvement_Code import improving_plan
from KPI_calculator import calculate_kpis
from gantt_chart import plot_gantt_chart

def switch_tab(tab):
    st.session_state.tab = tab

def on_tab_change():
    st.toast(f"You opened the {st.session_state.tab} tab.")

imag = background_image("images (1).png")
st.markdown(imag, unsafe_allow_html=True)

st.title("Bus plan improver for Transdev")

[tab1, tab2, tab3, tab4, tab5, tab6] = st.tabs(["Home", "All", "Original plan", "Improved plan", "KPI's", "Gantt-Chart"], on_change=on_tab_change, key="tab")

if "timetable" not in st.session_state:
    st.session_state.timetable = False

if "bus_plan" not in st.session_state:
    st.session_state.bus_plan = False

if "distance_matrix" not in st.session_state:
    st.session_state.distance_matrix = False

if "improved_plan" not in st.session_state:
    st.session_state.improved_plan = False

if "df_kpi" not in st.session_state:
    st.session_state.df_kpi = False

with st.sidebar:
    st.title("Import here your data as excel files")
    timetable = st.file_uploader("Upload here your timetable", type="xlsx")
    bus_plan = st.file_uploader("Upload here your bus plan", type="xlsx")
    distance_matrix = st.file_uploader("Upload here your distance matrix", type="xlsx")
    st.markdown("Press this button to Re-Run the page")
    st.button("Re-Run", width="stretch")

with tab1:
    st.header("Welcome to the bus planner tool for line 400 and 401")
    st.markdown("This is the homepage of the tool, here you will find general information about the tool like instrunctions, but for those who want to dive straight in you can go to one of our other pages to get straight into action.")

    st.subheader("Choose page")

    [alles, org, impr, kpi, gantt] = st.columns(5)

    alles.button("All", on_click=switch_tab, args=("All",), width="stretch")
    org.button("Original plan", on_click=switch_tab, args=("Original plan",), width="stretch")
    impr.button("Improved plan", on_click=switch_tab, args=("Improved plan",), width="stretch")
    kpi.button("KPI's", on_click=switch_tab, args=("KPI's",), width="stretch")
    gantt.button("Gantt-Chart", on_click=switch_tab, args=("Gantt-Chart",), width="stretch")


with tab2:
    if (timetable != None) and (distance_matrix != None):
        df_timetable = pd.read_excel(timetable)
        df_distance_matrix = pd.read_excel(distance_matrix)

        df_timetable = str_to_time(df_timetable)

        if bus_plan != None:
            df_bus_plan = pd.read_excel(bus_plan)
            [feasible, error_feasible, df_bus_plan_v2] = is_bus_planning_feasible(df_bus_plan, df_distance_matrix)
            [check, error_check] = bus_plan_timetable_check(df_bus_plan_v2, df_timetable)

            with st.container(border=True):
                st.subheader("Is the bus plan feasible?")
                st.write(feasible)

                if feasible == False:
                    st.subheader("The bus plan has errors")
                    with st.container(border=True, height=100):
                        error_list = error_feasible.split("\n")
                        st.write(error_list)

            with st.container(border=True):
                st.subheader("Does the bus plan schedule all trips from the timetable?")
                st.write(check)

                if check == False:
                    st.subheader("The trips that are not acounted for are")
                    with st.container(border=True, height=100):
                        error_list = error_check.split("\n")
                        st.write(error_list)

            st.session_state.bus_plan = bus_plan

        if (distance_matrix != st.session_state.distance_matrix) or (timetable != st.session_state.timetable):
            improved_plan = improving_plan(df_timetable, df_distance_matrix)[1]
        else:
            improved_plan = st.session_state.improved_plan
        
        [impr_feasible, impr_error_feasible, improved_plan_v2] = is_bus_planning_feasible(improved_plan, df_distance_matrix)
        [impr_check, impr_error_check] = bus_plan_timetable_check(improved_plan_v2, df_timetable)

        with st.container(border=True):
            st.subheader("Is the improved bus plan feasible?")
            st.write(impr_feasible)

            if impr_feasible == False:
                st.subheader("The improved bus plan has errors")
                with st.container(border=True, height=100):
                    error_list = impr_error_feasible.split("\n")
                    st.write(error_list)

        with st.container(border=True):
            st.subheader("Does the improved bus plan schedule all trips from the timetable?")
            st.write(impr_check)

            if impr_check == False:
                st.subheader("The trips that are not acounted for are")
                with st.container(border=True, height=100):
                    error_list = impr_error_check.split("\n")
                    st.write(error_list)

        with st.container(border=True):
            st.subheader("KPI's")
            [impr_bus, impr_ec, impr_stnd] = calculate_kpis(improved_plan_v2)
            df_kpi = pd.DataFrame(index=["Total busses", "Total energy consumption", "Time not moving"])

            if (bus_plan != None) or (bus_plan != False):
                [org_bus, org_ec, org_stnd] = calculate_kpis(df_bus_plan_v2)
                df_kpi["Original plan"] = [org_bus, org_ec, org_stnd]
                df_kpi["Improved plan"] = [impr_bus, impr_ec, impr_stnd]
                st.write(df_kpi)
            else:
                df_kpi["Improved plan"] = [impr_bus, impr_ec, impr_stnd]
                st.write(df_kpi)

        if bus_plan != None:
            with st.container(border=True):
                st.subheader("Gantt-Chart of the original bus planning")
                all_buses = list(pd.unique(df_bus_plan_v2['bus']))
                buses = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                        all_buses,
                                                                        default=all_buses,
                                                                        key=1)
        
                plot_gantt_chart(df_bus_plan_v2, buses)
    
        with st.container(border=True):
            st.subheader("Gantt-Chart of the improved bus planning")
            impr_all_buses = list(pd.unique(improved_plan_v2['bus']))
            impr_buses = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    impr_all_buses,
                                                                    default=impr_all_buses,
                                                                    key=2)
    
            plot_gantt_chart(improved_plan_v2, impr_buses)

        st.session_state.improved_plan = improved_plan
        st.session_state.timetable = timetable
        st.session_state.distance_matrix = distance_matrix
        st.session_state.df_kpi = df_kpi

with tab3:
    if type(st.session_state.bus_plan) != bool:
        with st.container(border=True):
            st.subheader("Is the bus plan feasible?")
            st.write(feasible)

            if feasible == False:
                st.subheader("The bus plan has errors")
                with st.container(border=True, height=100):
                    error_list = error_feasible.split("\n")
                    st.write(error_list)

        with st.container(border=True):
            st.subheader("Does the bus plan schedule all trips from the timetable?")
            st.write(check)

            if check == False:
                st.subheader("The trips that are not acounted for are")
                with st.container(border=True, height=100):
                    error_list = error_check.split("\n")
                    st.write(error_list)
    else:
        st.subheader("Upload bus plan")

with tab4:
    if type(st.session_state.improved_plan) != bool:
        with st.container(border=True):
            st.subheader("Is the improved bus plan feasible?")
            st.write(impr_feasible)

            if impr_feasible == False:
                st.subheader("The improved bus plan has errors")
                with st.container(border=True, height=100):
                    error_list = impr_error_feasible.split("\n")
                    st.write(error_list)

        with st.container(border=True):
            st.subheader("Does the improved bus plan schedule all trips from the timetable?")
            st.write(impr_check)

            if impr_check == False:
                st.subheader("The trips that are not acounted for are")
                with st.container(border=True, height=100):
                    error_list = impr_error_check.split("\n")
                    st.write(error_list)

with tab5:
    if type(st.session_state.df_kpi) != bool:
        with st.container(border=True):
            st.write(df_kpi)

with tab6:
    if type(st.session_state.bus_plan) != bool:
        with st.container(border=True):
            st.subheader("Gantt-Chart of the original bus planning")
            all_buses = list(pd.unique(df_bus_plan_v2['bus']))
            buses_2 = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    all_buses,
                                                                    default=all_buses,
                                                                    key=3)
    
            plot_gantt_chart(df_bus_plan_v2, buses_2)

    if type(st.session_state.improved_plan) != bool:
        with st.container(border=True):
            st.subheader("Gantt-Chart of the improved bus planning")
            impr_all_buses = list(pd.unique(improved_plan_v2['bus']))
            impr_buses_2 = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    impr_all_buses,
                                                                    default=impr_all_buses,
                                                                    key=4)

            plot_gantt_chart(improved_plan_v2, impr_buses_2)
