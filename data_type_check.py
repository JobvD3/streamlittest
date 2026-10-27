import datetime as dt
import pandas as pd

def type_check(dataframe, column, expected_types, tekst) -> tuple[bool, str]:
    """
    
    """
    error = ""
    feasible = True
    error_row = "In row {}, column {} has a wrong data type {}, expected data type is {}\n"
    error_column = "Column {} has {} rows with the wrong data type, expected data type is {}\n"

    nr_error = 0
    if "nan" in expected_types:
        for i in dataframe.iterrows():
            ind = i[0]
            row = i[1]
            if (type(row[column]) not in expected_types) and (row[column] == row[column]):
                nr_error += 1
                error += error_row.format(ind + 2, column, type(row[column]), tekst)
                feasible = False
        
        if nr_error > 10:
            error = error_column.format(column, nr_error, tekst)

    else:
        for i in dataframe.iterrows():
            ind = i[0]
            row = i[1]
            if type(row[column]) not in expected_types:
                nr_error += 1
                error += error_row.format(ind + 2, column, type(row[column]), tekst)
                feasible = False
        
        if nr_error > 10:
            error = error_column.format(column, nr_error, tekst)

    return feasible, error

def timetable_type_check(timetable : pd.DataFrame) -> tuple[bool, str]:
    """
    
    """
    error = ""
    feasible = True

    check = type_check(timetable, "start", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(timetable, "departure_time", [str, dt.time], "tekst or time")
    feasible = check[0]
    error += check[1]

    check = type_check(timetable, "end", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(timetable, "line", [int], "number")
    feasible = check[0]
    error += check[1]

    return feasible, error

def distance_matrix_type_check(distance_matrix : pd.DataFrame) -> tuple[bool, str]:
    """
     
    """
    error = ""
    feasible = True

    check = type_check(distance_matrix, "start", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(distance_matrix, "end", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(distance_matrix, "min_travel_time", [int, float], "number")
    feasible = check[0]
    error += check[1]

    check = type_check(distance_matrix, "max_travel_time", [int, float], "number")
    feasible = check[0]
    error += check[1]

    check = type_check(distance_matrix, "distance_m", [int, float], "number")
    feasible = check[0]
    error += check[1]

    check = type_check(distance_matrix, "line", [int, float, "nan"], "number or empty")
    feasible = check[0]
    error += check[1]

    return feasible, error

def bus_plan_type_check(bus_plan : pd.DataFrame) -> tuple[bool, str]:
    """
    
    """
    error = ""
    feasible = True

    check = type_check(bus_plan, "start location", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "end location", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "start time", [str, dt.time, dt.datetime], "tekst or time")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "end time", [str, dt.time, dt.datetime], "tekst or time")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "activity", [str], "tekst")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "line", [int, "nan"], "tekst or empty")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "energy consumption", [int, float], "number")
    feasible = check[0]
    error += check[1]

    check = type_check(bus_plan, "bus", [int], "number")
    feasible = check[0]
    error += check[1]

    return feasible, error