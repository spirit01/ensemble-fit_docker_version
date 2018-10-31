import datetime
from operator import itemgetter

status_shortcuts = {"accepted": "a", "checked": "c", "preprocessed": "p", "storage_ready": "sr", "optim_completed": "oc", "running": "r", "queued": "q", "done": "d", "user_error": "ue", "server_error": "se"}


def sort_computations(computations, sort_option, sort_order):
    if sort_order == 1 and sort_option == "progress":
        return sorted(computations, key=lambda x: float(x[sort_option]))
    if sort_order == -1 and sort_option == "progress":
        return sorted(computations, key=lambda x: float(x[sort_option]), reverse=True)
    if sort_order == 1 and sort_option != "date":
        return sorted(computations, key=itemgetter(sort_option))
    if sort_order == -1 and sort_option != "date":
        return sorted(computations, key=itemgetter(sort_option), reverse=True)
    if sort_order == 1 and sort_option == "date":
        return sorted(computations, key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'))
    if sort_order == -1 and sort_option == "date":
        return sorted(computations, key=lambda x: datetime.datetime.strptime(x['date'], '%d/%m/%Y'), reverse=True)


def filter_computations(computations, filter_values):
    for key in filter_values.keys():
        computations = list(item for item in computations if custom_filter(item, key, filter_values))
    return computations


def custom_filter(item, key, filter_values):
    if key == "progress":
        return compare_progress(item[key], filter_values[key])
    if key == "date":
        return compare_date(item[key], filter_values[key])
    if key == "status":
        return compare_status(item[key], filter_values[key])
    if key == "name":
        v = filter_values[key] in item[key]
        return v
    return False


def compare_status(value, expected_values):
    expression = expected_values.strip().split(' ')
    return value in expression or status_shortcuts[value] in expression


def compare_progress(value, expected_value):
    expression = expected_value.strip().split(' ')
    try:
        if len(expression) == 1:
            return float(value) == float(expression[0])
        if len(expression) == 2:
            if expression[0] == "=":
                return float(value) == float(expression[1])
            if expression[0] == "<":
                return float(value) < float(expression[1])
            if expression[0] == "<=":
                return float(value) <= float(expression[1])
            if expression[0] == ">":
                return float(value) > float(expression[1])
            if expression[0] == ">=":
                return float(value) >= float(expression[1])
        if len(expression) == 3:
            return float(expression[0]) <= float(value) <= float(expression[2])
    except ValueError:
        return False


def compare_date(value, expected_value):
    expression = expected_value.strip().split(' ')
    date_value = datetime.datetime.strptime(value, '%d/%m/%Y')

    try:
        if len(expression) == 1:
            return date_value == datetime.datetime.strptime(expression[0], '%d/%m/%Y')
        if len(expression) == 2:
            if expression[0] == "=":
                return date_value == datetime.datetime.strptime(expression[1], '%d/%m/%Y')
            if expression[0] == "<":
                return date_value < datetime.datetime.strptime(expression[1], '%d/%m/%Y')
            if expression[0] == "<=":
                return date_value <= datetime.datetime.strptime(expression[1], '%d/%m/%Y')
            if expression[0] == ">":
                return date_value > datetime.datetime.strptime(expression[1], '%d/%m/%Y')
            if expression[0] == ">=":
                return date_value >= datetime.datetime.strptime(expression[1], '%d/%m/%Y')
        if len(expression) == 3:
            return datetime.datetime.strptime(expression[0], '%d/%m/%Y') <= date_value <= datetime.datetime.strptime(expression[2], '%d/%m/%Y')
    except ValueError:
        return False
