from datetime import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mlt
from io import BytesIO

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

    min_time = 24
    max_time = 0
    nr_bus = 0
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
                       yrange = (nr_bus,0.8),
                       color = single_bus_schedule['color'],
                       edgecolor = ['black'])

        if min(single_bus_schedule["start time"])//1 < min_time:
            min_time = int(min(single_bus_schedule["start time"])//1)

        if max(single_bus_schedule["end time"])//1 + 1 > max_time:
            max_time = int(max(single_bus_schedule["end time"])//1 + 1)

        nr_bus += 1

    legenda = []
    for x in range(len(activities_list)):
        legenda.append(mlt.Patch(color=colors_list[x], label=activities_list[x]))

    if max_time > 24:
        time_over = max_time - 24
        hours = [*range(min_time - 1, 24)]
        hours += [*range(0, time_over + 1)]
    else:
        hours = range(min_time-1, max_time+1)

    ax.invert_yaxis()
    ax.set_title('Gantt chart of the bus plan')
    ax.set_xlim(min_time, max_time)
    ax.set_xticks(range(min_time - 1, max_time + 1))
    ax.set_xticklabels(hours)
    ax.set_yticks(range(0,nr_bus))
    ax.set_yticklabels(busses_list)
    ax.grid(True)

    ax.legend(handles=legenda, bbox_to_anchor=(0, -1, 1, -1), loc="lower center", mode="expand", ncol=len(activities_list))
    fig.set_figheight(nr_bus*0.8)
    fig.set_figwidth((max_time - min_time))

    return fig