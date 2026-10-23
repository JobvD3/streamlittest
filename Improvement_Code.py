"""
The function for the improving of the bus plan
"""
import datetime as dt
import pandas as pd
import numpy as np

def update_timetable(timetable : pd.DataFrame) -> pd.DataFrame:
    """
    This function updates the timetable so that it can be use for the improvement code

    Returns the timetable where departure_time type is datetime.datetime en er is een nieuw
    column "done" toegevoegt om aan te kunnen geven of een task klaar is of niet. 
    """

    df = timetable.sort_values(["line", "start"]).copy()
    df = df.reset_index(drop=True)

    #Creates a new column for if the task is done or not
    df["done"] = [False for i in timetable.index]

    #Changes the departure_time from dt.time to dt.datetime
    date = dt.date(2000,1,1)
    for task in df.index:
        df.loc[task, "departure_time"] = dt.datetime.combine(date, df.departure_time.loc[task])

    for line in df.line.unique():
        for start in df.start.unique():
            df_trip = df.loc[(df.line == line) & (df.start == start)]
            next_day = False
            for task in range(1,len(df_trip)):
                #Adds an extra day if nessesery to the departure_time
                if (df_trip.departure_time.iloc[task] - df_trip.departure_time.iloc[task - 1] < dt.timedelta(0)) and (df.line.loc[task]):
                    ind = df_trip.index[task]
                    df.loc[ind, "departure_time"] = df.loc[ind, "departure_time"] + dt.timedelta(days=1)
                    next_day = True
                elif next_day == True:
                    ind = df_trip.index[task]
                    df.loc[ind, "departure_time"] = df.loc[ind, "departure_time"] + dt.timedelta(days=1)

    df = df.sort_values("departure_time")
    return df

def choose_service_trip(timetable : pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """
    This function chooses the next service trip that needs to be made, and assings it as done

    Returns the choosen trip as a pd.Seties and the updated timetable
    """

    #makes DataFrame from only the tasks that are not done
    df = timetable.loc[timetable.done == False].copy()

    #Gets the pd.Series of the choosesn task
    trip = df.sort_values("departure_time").iloc[0]
    ind = df.sort_values("departure_time").index[0]

    #Updates the timetable
    timetable.loc[ind, "done"] = True
    return trip, timetable

def idle_busses(improve_plan : pd.DataFrame, time_trip : dt.datetime) -> pd.DataFrame:
    """
    This function assigns busses that aren't operating as idle

    Returns updated bus plan
    """
    from feasability_check import parameters_bus_planning

    df = improve_plan.sort_values(["bus", "end time"]).copy()
    end = time_trip

    busses = df.bus.unique()
    for bus in busses:
        s_bus = df.loc[df.bus == bus].iloc[-1]
        if s_bus["end time"] < end:
            ind = df.loc[df.bus == bus].index[-1]
            if s_bus.activity == "idle":
                df.loc[ind, "end time"] = end
                start = s_bus["start time"]
                task_time = end - start
                energy_consumption = parameters_bus_planning()["idle_energy_consumption"]*task_time.seconds/3600
                battery = s_bus.battery_charge - (energy_consumption - s_bus["energy consumption"])

                df.loc[ind, "task_time"] = task_time
                df.loc[ind, "energy consumption"] = energy_consumption
                df.loc[ind, "battery_charge"] = battery

            elif s_bus["end location"] != "ehvgar":
                location = s_bus["end location"]
                start = s_bus["end time"]
                task_time = end - start
                energy_consumption = parameters_bus_planning()["idle_energy_consumption"]*task_time.seconds/3600
                battery = s_bus.battery_charge - energy_consumption
                df.loc[len(df)] = [location,
                                location,
                                start,
                                end,
                                task_time,
                                "idle",
                                np.nan,
                                energy_consumption,
                                battery,
                                bus
                                ]
    df = df.sort_values(["bus", "start time"])
    return df

def need_charging(improve_plan : pd.DataFrame, end_trip : str, time_trip : dt.datetime, duration_trip : pd.Timedelta, trip_ec : float, distance_matrix : pd.DataFrame) -> pd.DataFrame:
    """
    This function checks if there are busses that need to be charged and sends those busses to
    the garage. It also updates the time that the bus is charging for when a bus is already
    charging.

    Returns updated bus plan
    """

    #Gets the bus plan parameters
    from feasability_check import parameters_bus_planning
    min_battery = parameters_bus_planning()["min_batery"]
    charge_speed = parameters_bus_planning()["charge_speed_0_90"]
    max_battery = parameters_bus_planning()["max_batery"]
    idle_ec = parameters_bus_planning()["idle_energy_consumption"]

    df = improve_plan.copy()
    #Sorts the bus plan by bus and start time
    df = df.sort_values(["bus", "end time"])

    end_time = time_trip + duration_trip 
    busses = df.bus.unique()
    for bus in busses:
        s_bus = df.loc[df.bus == bus].iloc[-1]
        ind = df.loc[df.bus == bus].index[-1]
        start_time = s_bus["start time"]
        [garage_time_end, garage_ec_end] = trip_information(distance_matrix, end_trip, "ehvgar", np.nan)
        [bst_time, bst_ec] = trip_information(distance_matrix, "ehvgar", "ehvbst", np.nan)
        if s_bus["end location"] != "ehvgar":
            [garage_time_start, garage_ec_start] = trip_information(distance_matrix, s_bus["end location"], "ehvgar", np.nan)
        else:
            garage_time_start = dt.timedelta(days=0)
            garage_ec_start = 0

        if s_bus.activity == "charging":
            task_time = df.task_time.loc[ind]
            df.loc[ind, "end time"] = df["end time"].loc[ind] + duration_trip
            df.loc[ind, "task_time"] = df["end time"].loc[ind] - df["start time"].loc[ind]
            df.loc[ind, "energy consumption"] = -1*charge_speed*df["task_time"].loc[ind].seconds
            df.loc[ind, "battery_charge"] -= -1*charge_speed*(df.task_time.loc[ind] - task_time).seconds
            
            if df.battery_charge.loc[ind] > max_battery*0.9:
                over_charge = df.battery_charge.loc[ind] - max_battery*0.9
                over_time = dt.timedelta(seconds=over_charge/charge_speed)
                df.loc[ind, "end time"] = df["end time"].loc[ind] - over_time
                df.loc[ind, "task_time"] = df["end time"].loc[ind] - df["start time"].loc[ind]
                df.loc[ind, "energy consumption"] += over_charge
                df.loc[ind, "battery_charge"] = max_battery*0.9

                df.loc[len(df)] = ["ehvgar",
                                   "ehvbst",
                                   df["end time"].loc[ind],
                                   df["end time"].loc[ind] + bst_time,
                                   bst_time,
                                   "material trip",
                                   np.nan,
                                   bst_ec,
                                   df.battery_charge.loc[ind] - bst_ec,
                                   bus
                                   ]

                if df["end time"].loc[ind] + bst_time < end_time:
                    task_time = end_time - df["end time"].loc[ind] + bst_time
                    df.loc[len(df)] = ["ehvbst",
                                       "ehvbst",
                                       df["end time"].loc[ind] + bst_time,
                                       end_time,
                                       task_time,
                                       "idle",
                                       np.nan,
                                       task_time.seconds*idle_ec/3600,
                                       df.battery_charge.loc[ind] - bst_ec - task_time.seconds*idle_ec/3600,
                                       bus
                                       ]
        
        elif ((s_bus.battery_charge - garage_ec_end - trip_ec) <= min_battery) and (s_bus.activity == "idle"):
            time_diff = s_bus.task_time
            ec_diff = time_diff.seconds*idle_ec/3600
            df.loc[ind] = [s_bus["end location"],
                           "ehvgar",
                           s_bus["start time"],
                           s_bus["start time"] + garage_time_start,
                           garage_time_start,
                           "material trip",
                           np.nan,
                           garage_ec_start,
                           s_bus.battery_charge - garage_ec_start + ec_diff,
                           bus]

            start_time = s_bus["start time"] + garage_time_start
            task_time = end_time - start_time
            energy_consumption = -1*charge_speed*task_time.seconds
            df.loc[len(df)] = ["ehvgar",
                                "ehvgar",
                                start_time,
                                end_time,
                                task_time,
                                "charging",
                                np.nan,
                                energy_consumption,
                                s_bus.battery_charge - garage_ec_start - energy_consumption,
                                bus]
            
        elif (s_bus.battery_charge - garage_ec_end - trip_ec <= min_battery) and (s_bus.activity != "idle"):
            if garage_ec_start != 0:
                df.loc[len(df)] = [s_bus["end location"],
                                    "ehvgar",
                                    s_bus["end time"],
                                    s_bus["end time"] + garage_time_start,
                                    garage_time_start,
                                    "material trip",
                                    np.nan,
                                    garage_ec_start,
                                    s_bus.battery_charge - garage_ec_start,
                                    bus]
            
            start_time = s_bus["end time"] + garage_time_start
            if start_time < end_time:
                task_time = end_time - start_time
                energy_consumption = -1*charge_speed*task_time.seconds
                df.loc[len(df)] = ["ehvgar",
                                    "ehvgar",
                                    start_time,
                                    end_time,
                                    task_time,
                                    "charging",
                                    np.nan,
                                    energy_consumption,
                                    s_bus.battery_charge - garage_ec_start - energy_consumption,
                                    bus]
    
    df = df.sort_values(["bus", "start time"])
    return df

def trip_information(distance_matrix : pd.DataFrame, start_trip : str, end_trip : str, line_trip) -> tuple[dt.timedelta, float]:
    """
    This function retriefs the trip information from the distance_matrix

    Returns trip duration as dt.timedelta and trip energy consumption as float
    """
    #Gets the parameters of the bus planning
    from feasability_check import parameters_bus_planning

    #Gets the min and max energy consumptie per kilometer
    max_ec_km = parameters_bus_planning()["max_energy_consumption_km"]
    min_ec_km = parameters_bus_planning()["min_energy_consumption_km"]

    #If the line is an actual line
    if line_trip == line_trip:
        #Gets the min expected travel time from the distance matrix
        min_expected_time = distance_matrix.min_travel_time.loc[(distance_matrix.start == start_trip) &
                                                                (distance_matrix.end == end_trip) &
                                                                (distance_matrix.line == line_trip)].iloc[0]

        #Gets the max expected travel time
        max_expected_time = distance_matrix.max_travel_time.loc[(distance_matrix.start == start_trip) &
                                                                (distance_matrix.end == end_trip) &
                                                                (distance_matrix.line == line_trip)].iloc[0]

        #Calculates the min expected energy consumption for the trip
        min_expected_ec = distance_matrix.distance_m.loc[(distance_matrix.start == start_trip) &
                                                        (distance_matrix.end == end_trip) &
                                                        (distance_matrix.line == line_trip)].iloc[0]*min_ec_km/1000

        #Calcuates the max expected energy consumption
        max_expected_ec = distance_matrix.distance_m.loc[(distance_matrix.start == start_trip) &
                                                        (distance_matrix.end == end_trip) &
                                                        (distance_matrix.line == line_trip)].iloc[0]*max_ec_km/1000

    #Else if the line is a np.nan
    else:
        min_expected_time = distance_matrix.min_travel_time.loc[(distance_matrix.start == start_trip) &
                                                                (distance_matrix.end == end_trip) &
                                                                (distance_matrix.line != distance_matrix.line)].iloc[0]
        
        max_expected_time = distance_matrix.max_travel_time.loc[(distance_matrix.start == start_trip) &
                                                                (distance_matrix.end == end_trip) &
                                                                (distance_matrix.line != distance_matrix.line)].iloc[0]

        min_expected_ec = distance_matrix.distance_m.loc[(distance_matrix.start == start_trip) &
                                                        (distance_matrix.end == end_trip) &
                                                        (distance_matrix.line != distance_matrix.line)].iloc[0]*min_ec_km/1000

        max_expected_ec = distance_matrix.distance_m.loc[(distance_matrix.start == start_trip) &
                                                        (distance_matrix.end == end_trip) &
                                                        (distance_matrix.line != distance_matrix.line)].iloc[0]*max_ec_km/1000

    
    return dt.timedelta(minutes=int(max_expected_time)), (min_expected_ec + max_expected_ec)/2

def update_plan(improve_plan : pd.DataFrame, trip : pd.Series, distance_matrix : pd.DataFrame) -> pd.DataFrame:
    """
    This function assigns the bus to the choosen task and updates the bus plan

    Returns updated bus plan
    """
    #Gets the parameters for the bus plan
    from feasability_check import parameters_bus_planning

    df = improve_plan.copy()

    #Gets the data from the choosen trip
    start_trip = trip.start
    end_trip = trip.end
    time_trip = trip.departure_time
    line_trip = trip.line
    [duration_trip, energy_consumption_trip] = trip_information(distance_matrix, start_trip, end_trip, line_trip)

    #Gets the data for if a bus needs to come from the other station
    [material_time, material_ec] = trip_information(distance_matrix, end_trip, start_trip, np.nan)

    #Gets the data for if a bus needs to come from the garage
    min_charge_time = parameters_bus_planning()["min_charge_time"]
    [garage_time, garage_ec] = trip_information(distance_matrix, "ehvgar", start_trip, np.nan)

    #Updates the idle and charging of the bus plan
    if len(df) > 0:
        df = idle_busses(df, time_trip)
        df = need_charging(df, end_trip, time_trip, duration_trip, energy_consumption_trip, distance_matrix)

    #Creates a DataFrame of all the busses that are at the start location of the new trip
    df_trip_location = df.loc[(df["end location"] == start_trip) & (df["end time"] == time_trip)]
    #Creates a DataFrame from the above DataFrame of all the busses that are idle 
    df_idle_trip_location = df_trip_location.loc[df_trip_location.activity == "idle"]
    #Creates a DataFrame from the above^2 DataFrame of all the busses that are not idle
    df_arriving_trip_location = df_trip_location.loc[df_trip_location.activity != "idle"]

    #Creates a DataFrame of all the busses that are at the other location of the new trip
    df_other_location = df.loc[(df["end location"] == end_trip) & (df["end time"] == time_trip)]
    #Creates a DataFrame from the above DataFrame of all the busses that are idle
    df_idle_other_location = df_other_location.loc[df_other_location.activity == "idle"]
    #Creates a DataFrame from the above DataFrame of all the busses that can make a material
    #trip from the other location to the start location
    df_idle_over_material = df_idle_other_location.loc[df_idle_other_location.task_time >= material_time]

    #Creates a DataFrame of all busses that are charging over min_charge_time and can make it
    #in time at the start location
    df_charging = df.loc[(df.activity == "charging") & (df.task_time > (min_charge_time + garage_time))]

    #If there is a bus at the station take the one with the lowes SoC
    if len(df_idle_trip_location) > 0:
        #makes a pd.Series from the last task of the choosen bus
        s_bus = df_idle_trip_location.sort_values(["task_time", "battery_charge"], ascending=[False, True]).iloc[0]
        #gives the bus number
        bus = s_bus.bus
        #gives the battery_charge of the bus
        battery = s_bus.battery_charge

    #Else if there are busses ariving at the station pick of those the one with the lowest SoC
    elif len(df_arriving_trip_location) > 0:
        s_bus = df_arriving_trip_location.sort_values("battery_charge").iloc[0]
        bus = s_bus.bus
        battery = s_bus.battery_charge

    #Else if there are busses that can make a material trip in time from the other station
    #pick of those the one with the lowest SoC
    elif len(df_idle_over_material) > 0:
        #Gets the index of the last task of the choosen bus
        ind = df_idle_over_material.sort_values("task_time", ascending = False).index[0]
        s_bus = df.loc[ind]
        bus = s_bus.bus

        #updates the idle task of the choosen bus
        #calculates the new task time
        new_time = s_bus.task_time - material_time
        #calculates the new end time
        #updates the idle task of the choosen bus
        new_end = s_bus["start time"] + new_time
        df.loc[ind, "task_time"] = new_time
        df.loc[ind, "end time"] = new_end
        df.loc[ind, "energy consumption"] = new_time.seconds*parameters_bus_planning()["idle_energy_consumption"]/3600
        df.loc[ind, "battery_charge"] += s_bus["energy consumption"] - df["energy consumption"].loc[ind]

        #adds a new row to send the bus to the start location
        df.loc[len(df)] = [end_trip,
                           start_trip,
                           new_end,
                           time_trip,
                           material_time,
                           "material trip",
                           np.nan,
                           material_ec,
                           df.battery_charge.loc[ind] - material_ec,
                           bus]

        battery = df.battery_charge.loc[ind] - material_ec

    #Else if there are busses that can come from the garage pick of those the one with the
    #highest SoC
    elif len(df_charging) > 0:
        ind = df_charging.sort_values("battery_charge", ascending = False).index[0]
        s_bus = df.loc[ind]
        bus = s_bus.bus

        #updates the charging task
        new_time = s_bus.task_time - garage_time
        new_end = s_bus["start time"] + new_time
        #updates the charging task
        df.loc[ind, "task_time"] = new_time
        df.loc[ind, "end time"] = new_end

        #adds a new row to send the bus to the start location
        df.loc[len(df)] = ["ehvgar",
                           start_trip,
                           new_end,
                           time_trip,
                           garage_time,
                           "material trip",
                           np.nan,
                           garage_ec,
                           s_bus.battery_charge - garage_ec,
                           bus]

        battery = s_bus.battery_charge - garage_ec
        
    #Else send a new bus from the garage 
    else:
        #Stuur een nieuwe bus...
        if len(df) > 0:
            bus = max(df.bus) + 1
        else:
            bus = 1
        battery = parameters_bus_planning()["max_batery"] - garage_ec
        new_end = time_trip - garage_time
        df.loc[len(df)] = ["ehvgar",
                           start_trip,
                           new_end,
                           time_trip,
                           garage_time,
                           "material trip",
                           np.nan,
                           garage_ec,
                           battery,
                           bus]

    #Adds the new service trip
    df.loc[len(df)] = [start_trip,
                       end_trip,
                       time_trip,
                       time_trip + duration_trip,
                       duration_trip,
                       "service trip",
                       line_trip,
                       energy_consumption_trip,
                       battery - energy_consumption_trip,
                       bus]

    #Sorts the bus plan by bus and start time
    df = df.sort_values(["bus", "start time"])
    return df

def send_busses_to_garage(improve_plan : pd.DataFrame, distance_matrix : pd.DataFrame) -> pd.DataFrame:
    """
    This function makes sure that if all service trips are assigned that then all busses that
    are not at the garage are send to the garage.

    Returns updated busplan
    """

    df = improve_plan.copy()
    busses = df.bus.unique()

    #Checks all busses
    for bus in busses:
        s_bus = df.loc[df.bus == bus].iloc[-1]
        ind = df.loc[df.bus == bus].index[-1]

        #Checks if the bus is charging and if so drops that row, because then the last thing
        #that the bus does is going to the garage
        if s_bus.activity == "charging":
            df = df.drop(ind)

        #Checks if the bus is idle and if so changes that row to a material trip to the garage
        elif s_bus.activity == "idle":
            start_loc = s_bus["end location"]
            start_time = s_bus["start time"]
            old_ec = s_bus["energy consumption"]
            [garage_time, garage_ec] = trip_information(distance_matrix, start_loc, "ehvgar", np.nan)

            df.loc[ind] = [start_loc,
                           "ehvgar",
                           start_time,
                           start_time + garage_time,
                           garage_time,
                           "material trip",
                           np.nan,
                           garage_ec,
                           s_bus.battery_charge - garage_ec + old_ec,
                           bus]

        #Checks if the bus isn't at the garage and if so ads a new row where the bus is send to
        #the garage
        elif s_bus["end location"] != "ehvgar":
            start_loc = s_bus["end location"]
            start_time = s_bus["end time"]
            [garage_time, garage_ec] = trip_information(distance_matrix, start_loc, "ehvgar", np.nan)

            df.loc[len(df)] = [start_loc,
                        "ehvgar",
                        start_time,
                        start_time + garage_time,
                        garage_time,
                        "material trip",
                        np.nan,
                        garage_ec,
                        s_bus.battery_charge - garage_ec,
                        bus]

    #Sorts the bus plan by bus and start time
    df = df.sort_values(["bus", "start time"])
    return df

def send_busses_to_garagev2(improve_plan : pd.DataFrame, distance_matrix : pd.DataFrame) -> pd.DataFrame:
    """
    This function makes sure that if all service trips are assigned that then all busses that
    are not at the garage are send to the garage.

    Returns updated busplan
    """           

    df = improve_plan.copy()

    for bus in df.bus.unique():
        df_bus = df.loc[df.bus == bus].reset_index().copy()
        ind = df_bus.loc[df_bus.activity == "service trip"].index[-1]
        s_bus = df_bus.loc[ind]
        if ind + 1 < len(df_bus):
            original_ind = df_bus["index"].loc[int(ind+1)]
            if ind + 2 < len(df_bus):
                drop_list = df_bus["index"].loc[ind+2:]
                df = df.drop(drop_list)
        else:
            original_ind = max(df.index) + 1

        start_loc = s_bus["end location"]
        start_time = s_bus["end time"]
        [garage_time, garage_ec] = trip_information(distance_matrix, start_loc, "ehvgar", np.nan)

        df.loc[original_ind] = [start_loc,
                                "ehvgar",
                                start_time,
                                start_time + garage_time,
                                garage_time,
                                "material trip",
                                np.nan,
                                garage_ec,
                                s_bus.battery_charge - garage_ec,
                                bus]
        
    df = df.sort_values(["bus", "start time"])
    return df

def make_plan_like_original(improve_plan : pd.DataFrame) -> pd.DataFrame:
    """
    This function changes the template of the created bus plan to the template of the original

    returns bus plan
    """

    df = improve_plan.copy()

    #Removes columns that aren't in the original
    df = df.drop(["task_time", "battery_charge"], axis=1)

    #df["energy consumption"] = df["energy consumption"]//0.001/1000

    #Changes the times from dt.datetime to strings
    df["start time"] = df["start time"].astype(str)
    df["end time"] = df["end time"].astype(str)

    #Removes the dates from the strings
    for ind in df.index:
        df.loc[ind, "start time"] = df["start time"].loc[ind][11:19]
        df.loc[ind, "end time"] = df["end time"].loc[ind][11:19]

    #Resets the index of the bus plan
    df = df.reset_index(drop=True)
    return df

def improving_plan(timetable : pd.DataFrame, distance_matrix : pd.DataFrame) -> pd.DataFrame:
    """
    This function creates a improved bus plan based on the given timetable and distance_matrix

    Returns improved bus plan
    """

    #makes the timetable usable
    df_timetable = update_timetable(timetable)

    #Creates an empty pd.DataFrame with all the neccerie columns
    bus_plan = pd.DataFrame(columns=["start location",
                                      "end location",
                                      "start time",
                                      "end time",
                                      "task_time",
                                      "activity",
                                      "line",
                                      "energy consumption",
                                      "battery_charge",
                                      "bus"])

    #runs the constructive heuristic until all service trips are assigned
    while len(df_timetable[df_timetable.done == False]) > 0:
        [trip, df_timetable] = choose_service_trip(df_timetable)
        bus_plan = update_plan(bus_plan, trip, distance_matrix)

    #sends all busses to the garage
    bus_plan = send_busses_to_garagev2(bus_plan, distance_matrix)

    #gives the improved bus plan the same template as the original
    bus_plan_original = make_plan_like_original(bus_plan)
    return bus_plan, bus_plan_original

