import streamlit as st
import pandas as pd
from io import BytesIO

from opmaak import background_image
from data_type_check import timetable_type_check
from data_type_check import bus_plan_type_check
from data_type_check import distance_matrix_type_check
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

if "bus_plan_v2" not in st.session_state:
    st.session_state.bus_plan_v2 = [False, False, False, False, False]

if "distance_matrix" not in st.session_state:
    st.session_state.distance_matrix = False

if "improved_plan" not in st.session_state:
    st.session_state.improved_plan = False

if "improved_plan_v2" not in st.session_state:
    st.session_state.improved_plan_v2 = [False, False, False, False, False]

if "df_kpi" not in st.session_state:
    st.session_state.df_kpi = False

with st.sidebar:
    st.title("Import here your data as excel files")
    timetable = st.file_uploader("Upload here your timetable", type="xlsx")
    bus_plan = st.file_uploader("Upload here your bus plan", type="xlsx")
    distance_matrix = st.file_uploader("Upload here your distance matrix", type="xlsx")

    if type(st.session_state.improved_plan) != bool:
        st.title("Here you can download the improved plan")
        df = st.session_state.improved_plan
        flnme = st.text_input('Enter Excel file name (e.g. email_data.xlsx)')
        if flnme != "":
            if flnme.endswith(".xlsx") == False:  # add file extension if it is forgotten
                flnme = flnme + ".xlsx"

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='plan', index=False)

            st.download_button(label="Download Excel workbook", data=buffer.getvalue(), file_name=flnme, mime="application/vnd.ms-excel", icon=":material/download:", type="primary")


    st.markdown("Press this button to Re-Run the page")
    if st.button("Re-Run", width="stretch", type="secondary"):
        st.session_state.timetable = False
        st.session_state.bus_plan = False
        st.session_state.bus_plan_v2 = [False, False, False, False, False]
        st.session_state.distance_matrix = False
        st.session_state.improved_plan = False
        st.session_state.improved_plan_v2 = [False, False, False, False, False]
        st.session_state.df_kpi = False
        st.rerun()

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

        with st.container(border=True):
            [feasible_tt, error_tt] = timetable_type_check(df_timetable)
            [feasible_dm, error_dm] = distance_matrix_type_check(df_distance_matrix)

            if feasible_tt == False:
                st.header("The timetable has unexpected data")
                with st.container(border=True, height=100):
                    st.markdown(error_tt.split("\n"))

            if feasible_dm == False:
                st.header("The distance matrix has unexpected data")
                with st.container(border=True, height=100):
                    st.markdown(error_dm.split("\n"))
            
            if bus_plan != None:
                df_bus_plan = pd.read_excel(bus_plan)
                [feasible_bp, error_bp] = bus_plan_type_check(df_bus_plan)
                if feasible_bp == False:
                    st.header("The original bus plan has unexpected data")
                    with st.container(border=True, height=100):
                        st.markdown(error_bp.split("\n"))

        if feasible_tt == True and feasible_dm == True:
            df_timetable = str_to_time(df_timetable)

            if bus_plan != None and feasible_bp == True:
                if bus_plan != st.session_state.bus_plan:
                    [feasible, error_feasible, df_bus_plan_v2] = is_bus_planning_feasible(df_bus_plan, df_distance_matrix)
                    [check, error_check] = bus_plan_timetable_check(df_bus_plan_v2, df_timetable)
                else:
                    [feasible, error_feasible, df_bus_plan_v2] = st.session_state.bus_plan_v2[0:3]
                    [check, error_check] = st.session_state.bus_plan_v2[3:]
                
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
                st.session_state.bus_plan_v2 = [feasible, error_feasible, df_bus_plan_v2, check, error_check]

            if (distance_matrix != st.session_state.distance_matrix) or (timetable != st.session_state.timetable):
                improved_plan = improving_plan(df_timetable, df_distance_matrix)[1]
                [impr_feasible, impr_error_feasible, improved_plan_v2] = is_bus_planning_feasible(improved_plan, df_distance_matrix)
                [impr_check, impr_error_check] = bus_plan_timetable_check(improved_plan_v2, df_timetable)
            else:
                improved_plan = st.session_state.improved_plan
                [impr_feasible, impr_error_feasible, improved_plan_v2] = st.session_state.improved_plan_v2[0:3]
                [impr_check, impr_error_check] = st.session_state.improved_plan_v2[3:]

            st.session_state.improved_plan = improved_plan

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

            st.session_state.improved_plan_v2 = [impr_feasible, impr_error_feasible, improved_plan_v2, impr_check, impr_error_check]

            with st.container(border=True):
                st.subheader("KPI's")
                [impr_bus, impr_ec, impr_stnd] = calculate_kpis(improved_plan_v2)
                df_kpi = pd.DataFrame(index=["Total busses", "Total energy consumption", "Time not moving"])

                if (bus_plan != None) and (bus_plan != False):
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

    if type(st.session_state.bus_plan) != bool:
        with st.container(border=True):
            st.subheader("Gantt-Chart of the original bus planning")
            all_buses = list(pd.unique(df_bus_plan_v2['bus']))
            buses_2 = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    all_buses,
                                                                    default=all_buses,
                                                                    key=3)

            plot_gantt_chart(df_bus_plan_v2, buses_2)

    if type(st.session_state.df_kpi) != bool:
        if "Original plan" in df_kpi.columns:
            with st.container(border=True):
                st.write(df_kpi["Original plan"])

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

    if type(st.session_state.improved_plan) != bool:
        with st.container(border=True):
            st.subheader("Gantt-Chart of the improved bus planning")
            impr_all_buses = list(pd.unique(improved_plan_v2['bus']))
            impr_buses_2 = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    impr_all_buses,
                                                                    default=impr_all_buses,
                                                                    key=4)

            plot_gantt_chart(improved_plan_v2, impr_buses_2)

    if type(st.session_state.df_kpi) != bool:
        with st.container(border=True):
            st.write(df_kpi["Improved plan"])

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
                                                                    key=5)
    
            plot_gantt_chart(df_bus_plan_v2, buses_2)

    if type(st.session_state.improved_plan) != bool:
        with st.container(border=True):
            st.subheader("Gantt-Chart of the improved bus planning")
            impr_all_buses = list(pd.unique(improved_plan_v2['bus']))
            impr_buses_2 = st.multiselect('Which bus of the bus plan do you want to see the table of',
                                                                    impr_all_buses,
                                                                    default=impr_all_buses,
                                                                    key=6)

            plot_gantt_chart(improved_plan_v2, impr_buses_2)
