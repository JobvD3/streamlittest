"""
Code voor controleren of busplan klopt en om het plan als een Gantt chart te laten zien
"""
import pandas as pd
def controle_bus_plan():
    """
    Doet de bus plan controleren
    """
    from import_data_and_data_orientation import import_data

    error = ''
    error_bus_plan = 'the bus {} in row {} ends a trip at {} but the next trip in row {} stars at {}\n'
    bus_plan = import_data()[0]
    unique_busses = pd.unique(bus_plan['bus'])

    for busses in unique_busses:
        single_bus_plan = bus_plan[bus_plan['bus'] == busses]

        for rows in list(single_bus_plan.index):
            if rows == list(single_bus_plan.index)[-1]:
                continue

            end_time = single_bus_plan.loc[rows]['end time']
            start_time_next = single_bus_plan.loc[rows+1]['start time']
            time_check = end_time <= start_time_next or start_time_next < '00:99:00'

            if time_check is False:
                error += error_bus_plan.format(busses,rows,single_bus_plan.loc[rows]['end time'],
                                            rows+1,single_bus_plan.loc[rows+1]['start time'])
    if error != '':
        print(error)

def bus_plan_timetable_check(bus_plan : pd.DataFrame, timetable : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if all task from the timetable are acounted for in the bus planning
    """
    check = True

    error = ""
    error_check = "Line {} that goes from {} to {} at {} is not in the bus plan\n"

    df_bus_plan = bus_plan.copy()
    df_bus_plan["start time"] = [row[1]["start time"].time() for row in df_bus_plan.iterrows()]
    for row in timetable.iterrows():
        task = row[1]
        df = df_bus_plan.loc[df_bus_plan.line == task.line].copy()
        df = df.loc[df["start location"] == task.start]
        df = df.loc[df["start time"] == task.departure_time]
        if len(df) != 1:
            error += error_check.format(task.line, task.start, task.end, task.departure_time)
            check = False
    return check, error