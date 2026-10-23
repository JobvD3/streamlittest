"""
Calculations for kpi
"""
import datetime as dt
import pandas as pd

def number_of_busses(bus_plan : pd.DataFrame) -> int:
    """
    Calculates the numbere of unique busses

    Returns the number of busses as int
    """

    num_bus = len(bus_plan.bus.unique())
    return num_bus

def total_energy_consumption(bus_plan : pd.DataFrame) -> float:
    """
    Calculates the total energy consumption

    Returns the total energy consumption as a float
    """

    df = bus_plan.loc[bus_plan.activity != "charging"].copy()
    total_ec = df["energy consumption"].sum()
    return total_ec

def time_not_moving(bus_plan : pd.DataFrame) -> dt.timedelta:
    """
    Calculates the total time that busses aren't moving

    Returns the total time that busses are standing still as dt.timedelta
    """

    df = bus_plan.loc[(bus_plan.activity == "idle") | (bus_plan.activity == "charging")].copy()
    df["task_time"] = df["end time"] - df["start time"]
    total_time_standing_still = df.task_time.sum()
    return total_time_standing_still

def calculate_kpis(bus_plan : pd.DataFrame) -> tuple[int, float, dt.timedelta]:
    """
    Calculates the kpi's

    Returns busses as an int, energy consumption as float and still time as dt.timedelta
    """

    busses = number_of_busses(bus_plan)

    energy_consumption = total_energy_consumption(bus_plan)

    still_time = time_not_moving(bus_plan)

    return busses, energy_consumption, still_time