import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


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

        single_bus_schedule['duration'] = single_bus_schedule['end time'] - single_bus_schedule['start time']
        single_bus_schedule['color'] = single_bus_schedule['activity']
        colors_list = ['Purple','Blue','Gray','Green']
        for activities in single_bus_schedule['activity'].index:
            index_activity = activities_list.index(single_bus_schedule['activity'].loc[activities])
            single_bus_schedule.loc[activities,['color']] = colors_list[index_activity]
        
        x_rans = list(zip(list(single_bus_schedule['start time']),list(single_bus_schedule['duration'])))
        ax.broken_barh(xranges = x_rans, yrange = (single_bus_schedule['bus'].iloc[0],0.8),color = single_bus_schedule['color'],
                        edgecolor = ['black'])

    #patches = []
    
    # dict_color_activity = [{colors_list[x]: activities_list[x]} for x in range(len(colors_list))]
    # for i, (color, activity) in enumerate(dict_color_activity):
        # st.text(f'{color=}, {activity=}, {i=}')
        # st.text('space')
        # patches.append([mps.Patch(color= color)])

    ax.invert_yaxis()
    ax.set_title('Gantt chart of the bus plan')
    ax.set_xlim(auto=True)
    ax.set_xticks((list(range(5,25)) + list(range(0,5))))
    ax.set_yticks(list(bus_scedules_dict))
    ax.grid(True)
    # ax.legend(handles=patches)
    st.pyplot(fig)