import datetime as dt
import pandas as pd

def str_to_time(df_timetable : pd.DataFrame) -> pd.DataFrame:
    timetable = df_timetable.copy()
    timetable_times = []
    for row in timetable.iterrows():
        task = row[1]
        if type(task.departure_time) == str:
            task.departure_time = dt.datetime.strptime(task.departure_time, "%H:%M").time()
        timetable_times.append(task.departure_time)
    timetable.departure_time = timetable_times
    return timetable