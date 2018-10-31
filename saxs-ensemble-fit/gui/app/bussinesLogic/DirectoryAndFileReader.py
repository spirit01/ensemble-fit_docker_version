import os, errno
from flask import current_app
from math import log
from app.bussinesLogic import Filtering

status_shortcuts = {"accepted": "a", "running": "r", "queued": "q", "done": "d"}


#
#
#
#
def get_subset_of_computations_for_one_page(user_id, page, sort_option, sort_order, search_filters):
    count = current_app.config['EXPERIMENTS_ON_ONE_PAGE']
    start = page * count
    end = page * count + count

    result = get_computations(user_id, sort_option, sort_order, search_filters)
    if start >= len(result):
        start -= count
        end -= count
    return result[start:end]


# reads a directory for a current logged in user and return his computations
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# page - a list of computations shows a certain number of them on 1 page. This parameter represents which page should be displayed
#
# returns an subarray of dictionaries - each dictionary has 4 keys - title, date, status and progress, which hold informations about an computation
def get_computations(user_id, sort_option, sort_order, search_filters):
    computations = []

    for computation_dir in os.listdir(os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id))):
        info = {"comp_guid": computation_dir, "user_id": user_id}
        read_file(os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), computation_dir, "params.txt"), info, ["NAME", "DATE"])
        read_row(os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), computation_dir, "status.txt"), info, "status")

        path_to_result_file = os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), computation_dir, "result.dat")
        if check_for_computation_results(user_id, computation_dir, info["status"]):
            read_row(path_to_result_file, info, "progress")
        else:
            info["progress"] = "0"

        if info["status"] == "user_error" or info["status"] == "server_error":
            path_to_error_message = os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), computation_dir, "error_message.txt")
            read_row(path_to_error_message, info, "error_message")

        computations.append(info)

    computations = Filtering.filter_computations(computations, search_filters)
    if sort_option == '0':
        return computations
    return Filtering.sort_computations(computations, sort_option, sort_order)


# returns true, if directory for given computation for given user exist, otherwise return false
def check_if_computation_exist(user_id, comp_guid):
    return os.path.isdir(os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), comp_guid))


# return true, if given computation has got all required data to show user results, otherwise returns false
# status must be running or done, file result.dat and directory ComputedValues must be present in computation directory
def check_for_computation_results(user_id, comp_guid, status):
    path_to_result_file = os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), comp_guid, "result.dat")
    path_to_required_dir = os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), comp_guid, "ComputedCurves")

    return os.path.isfile(path_to_result_file) and os.path.isdir(path_to_required_dir) and (status == "running" or status == "done")


# reads a file 'status.txt' in a computation directory specified by 'comp_guid' argument and returns its content
def get_computation_status(user_id, comp_guid):
    file_path = os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id), comp_guid, "status.txt")
    info = {}
    read_row(file_path, info, "status")
    return info["status"]


# reads a directory with computations for a current logged in user and return number of pagination controls to be created
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
#
def get_pagination_controls_count(user_id=None, computations=None):
    if computations is not None:
        pages = 1.0 * len(computations) / current_app.config['EXPERIMENTS_ON_ONE_PAGE']
    else:
        exps_count = len(os.listdir(os.path.join(current_app.config['EXP_DIRECTORY'], str(user_id))))
        pages = 1.0 * exps_count / current_app.config['EXPERIMENTS_ON_ONE_PAGE']

    if pages.is_integer():
        pages_array = [0] * int(pages)
        return pages_array

    pages_array = [0] * (int(pages) + 1)
    return pages_array


# reads a directory with computed curves of specified computation
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an array of objects where object represents a computed curve for one model. It has one attribute 'model' with value 'points'.
# 'points' is an array of objects, which represents a single point on a chart. It has attributes 'q_value' and 'intensity'
def get_computed_curves(user_id, comp_guid):
    directory = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid)
    solutions = {}

    for i in range(len(os.listdir(os.path.join(directory, "ComputedCurves")))):
        models = {}

        for j in range(len(os.listdir(os.path.join(directory, "ComputedCurves", str(i + 1))))):
            file_path = os.path.join(directory, "ComputedCurves", str(i + 1), "final_m" + str(j + 1) + ".pdb.dat")

            try:
                with open(file_path) as file:
                    lines = file.readlines()
            except OSError as err:
                if err.errno == errno.ENOENT:
                    current_app.logger.error('File with computed curve for 1 model doesn\'t exist\nfunction arguments: file_path - ' + file_path, exc_info=err)
                current_app.logger.error(
                    'Error while trying to access or while reading a file with computed curve for 1 model in specified directory\n'
                    'function arguments: file_path - ' + file_path, exc_info=err)
                raise err

            points = []
            for line in lines[2:]:
                values_in_line = line.split()
                points.append({"q_value": float(values_in_line[0].strip()),
                               "intensity": float(values_in_line[1].strip())})

            models[str(j + 1)] = points

        solutions['solution' + str(i + 1)] = models

    return solutions


# reads a file 'result.dat' of specified computation and gets its computed weights for every model
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an array of weights
def get_weights(user_id, comp_guid):
    file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid, "result.dat")
    solutions = {}

    try:
        with open(file_path) as file:
            lines = file.readlines()
            lines.pop(0)  # first line removed
            for i, line in enumerate(lines, start=1):
                weights = {}
                values_in_line = line.split(',')
                for j, value in enumerate(values_in_line[4:], start=1):
                    weights[str(j)] = value.strip()

                solutions['solution' + str(i)] = weights

            return solutions
    except OSError as err:
        if err.errno == errno.ENOENT:
            current_app.logger.error('File result.dat doesn\'t exist\nfunction arguments: file_path - ' + file_path, exc_info=err)

        current_app.logger.error('Error while trying to access or while reading result.dat in specified directory\n'
                                 'function arguments: file_path - ' + file_path, exc_info=err)
        raise err


# reads a file 'saxs.dat' with experimental data of specified computation
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an array of arrays with 2 values where each 2-value array represents a single point on a chart with attributes 'q_value' (point x of a curve) and 'intensity' (point y of a curve)
def get_experiment_data(user_id, comp_guid):
    file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid, "saxs.dat")
    points = []

    try:
        with open(file_path) as file:
            lines = file.readlines()
            for line in lines[3:]:
                values_in_line = line.split()
                points.append([float(values_in_line[0].strip()), log(float(values_in_line[1].strip())) + 15])
            return points
    except OSError as err:
        if err.errno == errno.ENOENT:
            current_app.logger.error('File saxs.dat doesn\'t exist\nfunction arguments: file_path - ' + file_path, exc_info=err)

        current_app.logger.error('Error while trying to access or while reading result.dat in specified directory\n'
                                 'function arguments: file_path - ' + file_path, exc_info=err)
        raise err


# reads a file 'result.dat' with weights for every computed curve
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an array of arrays where nested arrays represents 1 computed curve
def get_best_solutions_of_computation(user_id, comp_guid):
    file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid, "result.dat")
    solutions = []

    try:
        with open(file_path) as file:
            lines = file.readlines()
            lines.pop(0)  # first line removed
            for i, line in enumerate(lines, start=1):
                data = [i]
                values_in_line = line.split(',')

                for j, value in enumerate(values_in_line):
                    data.append(float(value.strip()))

                solutions.append(data)

            return solutions
    except OSError as err:
        if err.errno == errno.ENOENT:
            current_app.logger.error('File result.dat doesn\'t exist\nfunction arguments: file_path - ' + file_path, exc_info=err)

        current_app.logger.error('Error while trying to access or while reading result.dat in specified directory\n'
                                 'function arguments: file_path - ' + file_path, exc_info=err)
        raise err


# reads a file 'result.dat' of specified computation and gets its result data 'status' and 'progress'
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an object with 2 attributes - 'status' and 'progress'
# def get_computations_result_data(user_id, comp_guid):
#     result_file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid, "result.dat")
#
#     info = {}
#     read_file(result_file_path, info, ["status", "progress"])
#
#     return info


# reads a file 'params.txt' of specified computation and gets its parameters
#
# user_id - id of an user which matches a directory on a server where this user has his computations saved
# comp_guid - id of a computation
#
# returns an object with 8 attributes - "title", "date", "comment", "steps", "sync", "alpha", "beta" and "gamma"
def get_computation_parameters(user_id, comp_guid):
    parameters_file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_guid, "params.txt")

    info = {}
    read_file(parameters_file_path, info, ["NAME", "DATE", "DESCRIPTION", "OPTIM_STEPS", "OPTIM_SYNC", "OPTIM_ALPHA", "OPTIM_BETA", "OPTIM_GAMMA", "OPTIM_ALGORITHM", "MAX_Q"])

    return info


# reads a file and adds attribute:value pairs into an object - finds a key string in a file
# and gets its value(a substring after ':' char)
#
# filePath - path of the file to read
# object - reference to a dictionary to which new attribute:value pairs will be appended
# keys - a list of strings to find in a file. Each string represents a key in dictionary
def read_file(file_path, info_dict, keys):
    try:
        with open(file_path) as file:
            lines = file.readlines()
            for key in keys:
                for line in lines:
                    if key in line:
                        info_dict[key.lower()] = line.split('=')[1].strip()[1:-1]
    except OSError as err:
        if err.errno == errno.ENOENT:
            current_app.logger.error('File doesn\'t exist\nfunction arguments: file_path - ' + file_path + ', keys - ' + keys.__str__(), exc_info=err)

        current_app.logger.error('Error while trying to access or while reading file in specified directory\n'
                                 'function arguments: file_path - ' + file_path + ', keys - ' + keys.__str__(), exc_info=err)
        raise err


def read_row(file_path, info_dict, key):
    try:
        with open(file_path) as file:
            info_dict[key] = file.readline().strip()
    except OSError as err:
        if err.errno == errno.ENOENT:
            current_app.logger.error('File result.dat/status.txt or error_message.txt doesn\'t exist\nfunction arguments: file_path - ' + file_path + ', key - ' + key, exc_info=err)

        current_app.logger.error('Error while trying to access or while reading result.dat/status.txt or error_message.txt in specified directory\n'
                                 'function arguments: file_path - ' + file_path + ', key - ' + key, exc_info=err)
        raise err



