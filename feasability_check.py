"""Je moeder"""

import datetime as dt
import pandas as pd

def start_end_location_buses(bus_planning: pd.DataFrame) -> tuple[dict, dict]:
    """
    This function returns two dict(dictionaries), in both dictionaries are the keys the buses.
    The values in the first dict are the start locations of the first activity that a bus does,
    and in the second dict are the values the end location of the last activity.
    """
    buses = []
    end_locations = []
    start_locations = []
    for bus_nr in bus_planning.bus.unique():
        end_location = bus_planning.loc[bus_planning.bus == bus_nr]["end location"].iloc[-1]
        start_location = bus_planning.loc[bus_planning.bus == bus_nr]["start location"].iloc[0]
        buses.append(bus_nr)
        end_locations.append(end_location)
        start_locations.append(start_location)
    bus_end_locations = dict(zip(buses, end_locations))
    bus_start_locations = dict(zip(buses, start_locations))
    return bus_start_locations, bus_end_locations

def parameters_bus_planning() -> dict:
    """
    This function returns a dictionary where the keys represent a parameter
    and the values represents the value of the parameter.
    """
    parameters = {
        "min_batery" : 300*0.85*0.1,
        "min_batery_percentage" : 10,
        "max_batery" : 300*0.85,
        "begin_batery" : 300*0.85,
        "min_charge_time" : dt.timedelta(minutes=15),
        "charge_speed_0_90" : 450/3600,
        "charge_speed_90_100" : 60/3600,
        "min_energy_consumption_km" : 0.7,
        "max_energy_consumption_km" : 2.5,
        "idle_energy_consumption" : 5
        }
    return parameters

def batery_charge(bus_planning : pd.DataFrame) -> pd.DataFrame:
    """
    There will be added a new column that tracks the battery charge in kwh, for the original
    battery charge it's assumed that all busses start with the begin_battery kwh of charge
    from the parameters.

    Based on the battery charge column there will also be made a battery percentage column that 
    tracks the battery charge in percentages compared to the begin_battery percentage.
    Returns an updated pd.DataFrame with extra columns battery charge and battery percentage.
    """
    df = bus_planning.copy()

    begin_batery_capacity = parameters_bus_planning()["begin_batery"]
    df["batery_charge"] = [begin_batery_capacity for i in df.index]

    for bus_nr in df.bus.unique():
        df_bus = df.loc[df.bus == bus_nr].copy()
        df_bus.batery_charge = [df_bus.batery_charge.iloc[0]
         - sum(df_bus["energy consumption"].iloc[:i + 1]) for i in range(len(df_bus))]

        df.loc[df.bus == bus_nr, "batery_charge"] = df_bus.batery_charge

    df["batery_percentage"] = df.batery_charge/begin_batery_capacity*100
    return df

def time_to_datetime(bus_planning : pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the start time and end time data from string to dt.datetime.
    Returns a pd.DataFrame with updated start time and end time columns.
    """
    #Importand need to ad something for if a busplan goes over 24:00 that it ads an extra day
    df = bus_planning.copy()

    start_times = []
    end_times = []
    for i in range(len(df)):
        start_time = str(df["start time"].iloc[i])
        start_times.append(dt.datetime.strptime(start_time, "%H:%M:%S"))

        end_time = str(df["end time"].iloc[i])
        end_times.append(dt.datetime.strptime(end_time, "%H:%M:%S"))

    df["start time"] = start_times
    df["end time"] = end_times

    for bus in df.bus.unique():
        df_bus = df.loc[df.bus == bus]
        next_day = False
        for ind in df_bus.index[1:]:
            if (df_bus["end time"].loc[ind] - df["start time"].loc[ind]) < dt.timedelta(hours=-10):
                df.loc[ind, "end time"] += dt.timedelta(days=1)
                next_day = True
            elif (df_bus["start time"].loc[ind] - df_bus["start time"].loc[ind - 1]) < dt.timedelta(hours=-10):
                df.loc[ind, "start time"] += dt.timedelta(days=1)
                df.loc[ind, "end time"] += dt.timedelta(days=1)
                next_day = True
            elif next_day == True:
                df.loc[ind, "start time"] += dt.timedelta(days=1)
                df.loc[ind, "end time"] += dt.timedelta(days=1)
    return df

def minimum_batery_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if the battery percentage of a bus goes below min_battery_percentage, if a battery
    goes below it then it returns feasible = False and a string for where the error is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    if min(bus_planning.batery_percentage) < parameters_bus_planning()["min_batery_percentage"]:
        low_bateries = bus_planning.loc[bus_planning.batery_percentage < parameters_bus_planning()["min_batery_percentage"]].copy()
        error_low_batery = "In row {} of the bus_planning, bus {}'s batery goes below {}%\n"
        
        for row in low_bateries.iterrows():
            error += error_low_batery.format(row[0], row[1].bus, parameters_bus_planning()["min_batery_percentage"])
        feasible = False
    return feasible, error

def maximum_batery_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if the battery chargenof a bus goes above the max_battery charge, if a battery goes 
    above it then it returns feasible = False and a string for where and what the error is
    
    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    if max(bus_planning.batery_charge) > parameters_bus_planning()["max_batery"]:
        high_bateries = bus_planning.loc[bus_planning.batery_charge > parameters_bus_planning()["max_batery"]].copy()
        error_high_batery = "In row {} of the bus_planning, bus {}'s batery goes over {}kWh\n"

        for row in high_bateries.iterrows():
            error += error_high_batery.format(row[0], row[1].bus, parameters_bus_planning()["max_batery"])
        feasible = False
    return feasible, error

def overlap_same_bus_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if a bus has overlap in its tasks, if a bus has overlap in tasks then it returns
    feasible = False and a string for where and what the error is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    for bus in bus_planning.bus.unique():
        df_bus = bus_planning.loc[bus_planning.bus == bus].copy()
        end_start_bus = [df_bus["start time"].iloc[i] - df_bus["end time"].iloc[i - 1] for i in range(1,len(df_bus))]
        if min(end_start_bus) < dt.timedelta():
            df_bus["overlap_time"] = [dt.timedelta()] + end_start_bus
            overlap_bus = df_bus.loc[df_bus.overlap_time < dt.timedelta()]
            error_overlap = "In rows {} and {} there's overlap in the times of bus {}\n"

            for row in overlap_bus.index:
                error += error_overlap.format(row - 1, row, bus)
            feasible = False
    return feasible, error

def task_end_start_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if the end time is earlier than the start time of a task, if the end time is earlier
    then it returns feasible = False and a string for where and what the error is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    for bus in bus_planning.bus.unique():
        df_bus = bus_planning.loc[bus_planning.bus == bus].copy()
        end_start_bus = [df_bus["end time"].iloc[i] - df_bus["start time"].iloc[i] for i in range(len(df_bus))]
        if min(end_start_bus) < dt.timedelta():
            df_bus["start_end"] =  end_start_bus
            overlap_bus = df_bus.loc[df_bus.start_end < dt.timedelta()]
            error_overlap = "In row {} the task of bus {} ends sooner than it starts\n"

            for row in overlap_bus.index:
                error += error_overlap.format(row, bus)
                feasible = False
    return feasible, error

def start_end_location_task_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """

    """
    feasible = True

    error = ""
    error_start_end = "In row {} the task of bus {} starts at a different location than where the last ended\n"
    for bus in bus_planning.bus.unique():
        df_bus = bus_planning.loc[bus_planning.bus == bus].copy()
        for ind in df_bus.index[1:]:
            end_previous = df_bus["end location"].loc[ind - 1]
            start = df_bus["start location"].loc[ind]

            if end_previous != start:
                error += error_start_end.format(ind, bus)
                feasible = False
    return feasible, error

def start_end_location_day_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if a bus starts the day at ehvgar and ends at ehvgar, if a bus does not start
    or end there then it returns feasible = False and a string for what the error is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    [bus_start_location, bus_end_location] = start_end_location_buses(bus_planning)

    for bus, start in bus_start_location.items():
        if start != "ehvgar":
            error += f"Bus {bus} does not start at ehvgar\n"
            feasible = False
    
    for bus, end in bus_end_location.items():
        if end != "ehvgar":
            error += f"Bus {bus} does not end at ehvgar\n"
            feasible = False
    return feasible, error

def minimum_charge_time_check(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if a bus charges for less than 15 minutes, if a bus charges for les than 15 minutes
    then return feasible = False and a string for where and what the error massage is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    feasible = True

    error = ""
    df_charging = bus_planning.loc[bus_planning.activity == "charging"].copy()
    if len(df_charging) > 0:
        if min(df_charging["end time"] - df_charging["start time"]) < parameters_bus_planning()["min_charge_time"]:
            slow_charge = df_charging.loc[(df_charging["end time"] - df_charging["start time"]) < parameters_bus_planning()["min_charge_time"]]
            error_slow_charge = "In row {} of the bus_planning, bus {} has a charging time that is shorter than 15 minutes\n"

            for row in slow_charge.iterrows():
                error += error_slow_charge.format(row[0], row[1].bus)
            feasible = False
    return feasible, error

def expected_charge(bus_planning : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks that when a bus is charging it charges the expected amount of eneregy (including
    that the bus charges slower when the battery percentage is over 90%), if a bus charges an
    unexpected amount then return feasible = False and a string for where and what the error
    is.

    Returns a string with the error massage and a bool for if the bus plan is feasible or not.
    """
    df = bus_planning.copy()

    feasible = True

    error = ""
    error_unexpected_charge = "In row {} of the bus_planning, bus {} has an unexpected energy consumption\n"

    df_charging = df.loc[df.activity == "charging"]
    for row in df_charging.iterrows():
        time_diff = (row[1]["end time"] - row[1]["start time"]).seconds
        if row[1].batery_charge > parameters_bus_planning()["begin_batery"]*0.9:
            time_90_min = (row[1].batery_charge - parameters_bus_planning()["begin_batery"]*0.9)/parameters_bus_planning()["charge_speed_0_90"]
            time_90_max = (row[1].batery_charge - parameters_bus_planning()["max_batery"]*0.9)/parameters_bus_planning()["charge_speed_0_90"]

            min_expected_charge = (time_diff - time_90_min)*parameters_bus_planning()["charge_speed_0_90"] + time_90_min*parameters_bus_planning()["charge_speed_90_100"]
            max_expected_charge = (time_diff - time_90_max)*parameters_bus_planning()["charge_speed_0_90"] + time_90_max*parameters_bus_planning()["charge_speed_90_100"] + 1

        else:
            min_expected_charge = time_diff*parameters_bus_planning()["charge_speed_0_90"]
            max_expected_charge = min_expected_charge + 1
        
        if (max_expected_charge <= -1*row[1]["energy consumption"]) or (-1*row[1]["energy consumption"] <= min_expected_charge):
            error += error_unexpected_charge.format(row[0], row[1].bus)
            feasible = False
    return feasible, error

def expected_energy_consumption_travel(bus_planning : pd.DataFrame, distance_matrix : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if a bus has an unexpected energy consumption for that task that it's doing that 
    involvse traveling. If the bus has an unexpected energy consumption then return
    feasible = False and a string with where and what the error is.

    Returns a string with the error massage and a bool for if the tool is feasible or not.
    """

    feasible = True

    error = ""
    error_unexpected_ec = "In row {} of the bus_planning, bus {} has an unexpected energy consumption\n"

    df_travel = bus_planning[bus_planning["start location"] != bus_planning["end location"]]
    for row in df_travel.iterrows():
        energy_consumption = row[1]["energy consumption"]
        max_ec_km = parameters_bus_planning()["max_energy_consumption_km"]
        min_ec_km = parameters_bus_planning()["min_energy_consumption_km"]

        if row[1].line == row[1].line:
            max_ec = distance_matrix.distance_m.loc[(distance_matrix.start == row[1]["start location"]) &
                                                  (distance_matrix.end == row[1]["end location"]) &
                                                  (distance_matrix.line == row[1].line)].iloc[0]*max_ec_km/1000

            min_ec = distance_matrix.distance_m.loc[(distance_matrix.start == row[1]["start location"]) &
                                                  (distance_matrix.end == row[1]["end location"]) &
                                                  (distance_matrix.line == row[1].line)].iloc[0]*min_ec_km/1000
        else:
            max_ec = distance_matrix.distance_m.loc[(distance_matrix.start == row[1]["start location"]) &
                                                  (distance_matrix.end == row[1]["end location"]) &
                                                  (distance_matrix.line != distance_matrix.line)].iloc[0]*max_ec_km/1000

            min_ec = distance_matrix.distance_m.loc[(distance_matrix.start == row[1]["start location"]) &
                                                  (distance_matrix.end == row[1]["end location"]) &
                                                  (distance_matrix.line != distance_matrix.line)].iloc[0]*min_ec_km/1000

        if (energy_consumption < min_ec) or (energy_consumption > max_ec):
            error += error_unexpected_ec.format(row[0], row[1].bus)
            feasible = False
    
    return feasible, error

def expected_travel_time(bus_planning : pd.DataFrame, distance_matrix : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks if a bus has an unexpected trave time for that task that it's doing, if the bus has
    an unexpected travel time then return feasible = False and a string with where and what 
    the error is.

    Returns a string with the error massage and a bool for if the tool is feasible or not.
    """
    feasible = True

    error = ""
    error_travel_time = "In row {} of the bus_planning, bus {} has an unexpected travel time\n"

    df_travel = bus_planning[bus_planning["start location"] != bus_planning["end location"]]
    for row in df_travel.iterrows():
        travel_time = (row[1]["end time"] - row[1]["start time"]).seconds/60

        if row[1].line == row[1].line:
            min_expected_time = distance_matrix.min_travel_time.loc[(distance_matrix.start == row[1]["start location"]) &
                                                                    (distance_matrix.end == row[1]["end location"]) &
                                                                    (distance_matrix.line == row[1].line)].iloc[0]

            max_expected_time = distance_matrix.max_travel_time.loc[(distance_matrix.start == row[1]["start location"]) &
                                                                    (distance_matrix.end == row[1]["end location"]) &
                                                                    (distance_matrix.line == row[1].line)].iloc[0]
        else:
            min_expected_time = distance_matrix.min_travel_time.loc[(distance_matrix.start == row[1]["start location"]) &
                                                                    (distance_matrix.end == row[1]["end location"]) &
                                                                    (distance_matrix.line != distance_matrix.line)].iloc[0]
            
            max_expected_time = distance_matrix.max_travel_time.loc[(distance_matrix.start == row[1]["start location"]) &
                                                                    (distance_matrix.end == row[1]["end location"]) &
                                                                    (distance_matrix.line != distance_matrix.line)].iloc[0]

        if (max_expected_time < travel_time) or (travel_time < min_expected_time):
            error += error_travel_time.format(row[0], row[1].bus)
            feasible = False
    return feasible, error

def feasibility_check(bus_planning : pd.DataFrame, distance_matrix : pd.DataFrame) -> tuple[bool, str]:
    """
    Checks all feasibility checks and returns if the bus plan is feasible(bool) and the error
    massages as a string.
    """
    feasible = True

    error = ""
    [feasible_min_batery, error_min_batery] = minimum_batery_check(bus_planning)
    if feasible_min_batery == False:
        error += error_min_batery
        feasible = False
    
    [feasible_max_batery, error_max_batery] = maximum_batery_check(bus_planning)
    if feasible_max_batery == False:
        error += error_max_batery
        feasible = False

    [feasible_overlap, error_overlap] = overlap_same_bus_check(bus_planning)
    if feasible_overlap == False:
        error += error_overlap
        feasible = False

    [feasible_end_start, error_end_start] = task_end_start_check(bus_planning)
    if feasible_end_start == False:
        error += error_end_start
        feasible = False

    [feasible_start_end_task, error_start_end_task] = start_end_location_task_check(bus_planning)
    if feasible_start_end_task == False:
        error += error_start_end_task
        feasible = False

    [feasible_start_end_day, error_start_end_day] = start_end_location_day_check(bus_planning)
    if feasible_start_end_day == False:
        error += error_start_end_day
        feasible = False

    [feasible_min_charge, error_min_charge] = minimum_charge_time_check(bus_planning)
    if feasible_min_charge == False:
        error += error_min_charge
        feasible = False
    
    [feasible_charge, error_charge] = expected_charge(bus_planning)
    if feasible_charge == False:
        error += error_charge
        feasible = False
    
    [feasible_travel_time, error_travel_time] = expected_travel_time(bus_planning, distance_matrix)
    if feasible_travel_time == False:
        error += error_travel_time
        feasible = False

    [feasible_energy_consumption_travel, error_energy_consumption_travel] = expected_energy_consumption_travel(bus_planning, distance_matrix)
    if feasible_energy_consumption_travel == False:
        error += error_energy_consumption_travel
        feasible = False
    return feasible, error

def is_bus_planning_feasible(bus_planning : pd.DataFrame, distance_matrix : pd.DataFrame) -> tuple[bool, str, pd.DataFrame]:
    """
    Adds the columns for the battery charge and battery percentage to the bus plan, changes
    the start time and end time columns to a usable data type and at last checks if the bus
    plan is feasible or not.

    Returns if the bus plan is feasible, the error massages and the updated bus plan.
    """
    bus_planning = batery_charge(bus_planning)

    bus_planning = time_to_datetime(bus_planning)

    [feasible, error] = feasibility_check(bus_planning, distance_matrix)

    return feasible, error, bus_planning