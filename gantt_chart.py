from datetime import datetime as dt
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

def reformat_time(bus_schedule_time : pd.Series) -> pd.Series:
    '''
    reformats the time in the inputted row from '%H:%M:%S' to total hours
    '''

    TFM = '%H:%M:%S'
    reformed_bus_schedule_time = [
    round(float((x-dt.strptime('00:00:00', TFM)).total_seconds()/3600),4)
    for x in bus_schedule_time
    ]
    return reformed_bus_schedule_time

def plot_gantt_chart(datas: pd.DataFrame, busses_list: list):
    """
    Makes a Gantt chart of the busses in the busses_list of the data
    """
    
    bus_scedules_dict = {}
    fig, ax = plt.subplots()
    
    activities_list = list(pd.unique(datas['activity'])) #[material, idle, service, charging]
    for busses in busses_list:
        single_bus_schedule = datas[datas['bus']==busses]
        bus_scedules_dict[busses] = single_bus_schedule

        single_bus_schedule['end time'] = reformat_time(single_bus_schedule['end time'])
        single_bus_schedule['start time'] = reformat_time(single_bus_schedule['start time'])
        single_bus_schedule['duration'] = single_bus_schedule['end time'] - single_bus_schedule['start time']
        single_bus_schedule['color'] = single_bus_schedule['activity']
        colors_list = ['Purple','Blue','Gray','Green']
        for activities in single_bus_schedule['activity'].index:
            index_activity = activities_list.index(single_bus_schedule['activity'].loc[activities])
            single_bus_schedule.loc[activities,['color']] = colors_list[index_activity]
        
        x_rans = list(zip(list(single_bus_schedule['start time']),list(single_bus_schedule['duration'])))
        ax.broken_barh(xranges = x_rans,
                       yrange = (single_bus_schedule['bus'].iloc[0],0.8),
                       color = single_bus_schedule['color'],
                       edgecolor = ['black'])

    #patches = []
    
    # dict_color_activity = [{colors_list[x]: activities_list[x]} for x in range(len(colors_list))]
    # for i, (color, activity) in enumerate(dict_color_activity):
        # st.text(f'{color=}, {activity=}, {i=}')
        # st.text('space')
        # patches.append([mps.Patch(color= color)])

    if (max(single_bus_schedule["end time"])//1 + 1) > 24:
        time_over = max(single_bus_schedule["end time"])//1 + 1 - 24
        hours = range(min(single_bus_schedule["start time"])//1, 25)
        hours.append(range(0, time_over + 1))
    else:
        hours = range(min(single_bus_schedule["start time"])//1, max(single_bus_schedule["end time"])//1 + 1)

    ax.invert_yaxis()
    ax.set_title('Gantt chart of the bus plan')
    ax.set_xlim(min(single_bus_schedule["start time"])//1, max(single_bus_schedule["end time"])//1 + 1)
    ax.set_xticks(hours)
    ax.set_yticks(list(bus_scedules_dict))
    ax.grid(True)
    # ax.legend(handles=patches)
    st.pyplot(fig)