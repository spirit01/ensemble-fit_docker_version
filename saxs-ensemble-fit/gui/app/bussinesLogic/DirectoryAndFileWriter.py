import os, time, shutil, uuid, errno, pwd, grp
from flask import current_app
from werkzeug import secure_filename
from app.main.errors import NewComputationRequestSubmitError


# creates an experiment - creates a directory, uploads and creates required files
# form - a reference to a form with data required to create a new experiment
def create_experiment(form, user_id):
    comp_id = str(uuid.uuid4())
    create_computation_directory(user_id, comp_id)
    create_params_file(os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_id), form)
    filename = secure_filename(form.models.data.filename)
    extension = filename.split(os.extsep)[1]
    upload_file(form.models.data, os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_id), "model", extension)
    upload_file(form.expData.data, os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_id), "saxs", "dat")
    create_status_file(os.path.join(current_app.config['EXP_DIRECTORY'], user_id, comp_id))


# create a directory for a new user
def create_user_directory(user_id):
    os.chdir(os.path.join(current_app.config['EXP_DIRECTORY']))
    try:
        os.mkdir(str(user_id))
        uid, gid = pwd.getpwnam('www-data').pw_uid, grp.getgrnam('saxsfit').gr_gid
        os.chown(str(user_id), uid, gid)
    except OSError as err:
        current_app.logger.error('Error while trying to create user directory for user with id - ' + str(user_id), exc_info=err)
        raise err


# create a directory for a new computation
def create_computation_directory(user_id, comp_id):
    os.chdir(os.path.join(current_app.config['EXP_DIRECTORY'], user_id))
    try:
        os.mkdir(comp_id)
        uid, gid = pwd.getpwnam('www-data').pw_uid, grp.getgrnam('saxsfit').gr_gid
        os.chown(comp_id, uid, gid)
        os.chmod(comp_id, 0o770)
    except OSError as err:
        current_app.logger.error('Error while trying to create computation directory for user with id - ' + str(user_id), exc_info=err)
        raise NewComputationRequestSubmitError("Error occurred while trying to submit a computation request.")


# uploads a file to a specified directory
# file - a reference to a file to upload
# path - a path to a directory where the  file will be uploaded
def upload_file(file, path, name, extension):
    try:
        file.save(os.path.join(path, name + '.' + extension))
    except Exception as err:
        current_app.logger.error('Error while trying to upload file to computation directory\n'
                                 'function arguments: path - ' + path + ', filename - ' + name + ' (name of file to upload), extension - ' + extension, exc_info=err)
        raise NewComputationRequestSubmitError("Error occurred while trying to submit a computation request.")


# creates file params.txt in specified directory with data from form
# path - a path to a directory where the params.txt file will be created
# form - a reference to a form with data which will be written in params.txt
def create_params_file(path, form):
    file_path = os.path.join(path, "params.txt")
    try:
        with open(file_path, "w") as params:
            params.write('NAME="' + form.title.data + '"\n')
            params.write('DATE="' + time.strftime("%d/%m/%Y") + '"\n')
            params.write('DESCRIPTION' + '="' + form.description.data + '"\n')
            params.write('STRUCTURES_FILE="model.pdb"\n')
            params.write('OPTIM_STEPS="' + str(form.calcSteps.data) + '"\n')
            params.write('OPTIM_SYNC="' + str(form.stepsBetweenSync.data) + '"\n')
            params.write('OPTIM_ALPHA="' + str(form.alpha.data) + '"\n')
            params.write('OPTIM_BETA="' + str(form.beta.data) + '"\n')
            params.write('OPTIM_GAMMA="' + str(form.gamma.data) + '"\n')
            params.write('OPTIM_ALGORITHM="' + str(form.calcType.data) + '"\n')
            params.write('MAX_Q="' + str(form.qRange.data) + '"\n')
    except OSError as err:
        current_app.logger.error('Error while trying to create and write to a params.txt file in specified directory\n'
                                 'function arguments: file_path - ' + file_path, exc_info=err)
        raise NewComputationRequestSubmitError("Error occurred while trying to submit a computation request.")


# creates file result.dat in specified directory
# path - a path to a directory where the result.dat file will be created
def create_status_file(path):
    file_path = os.path.join(path, "status.txt")
    umask_orig = os.umask(0)
    try:
        with os.fdopen(os.open(file_path, os.O_WRONLY | os.O_CREAT, 0o660), "w") as status:
            status.write("accepted\n")
    except OSError as err:
        current_app.logger.error('Error while trying to create and write to a status.txt file in specified directory\n'
                         'function arguments: file_path - ' + file_path, exc_info=err)
        raise NewComputationRequestSubmitError("Error occurred while trying to submit a computation request.")
    finally:
        os.umask(umask_orig)


# gets a file with model to display and moves it to a directory on a server to read and for user to download
# user_id - an id of a user that represents a directory where experiment data are stored
# exp_guid - an identificator of a experiment
def get_model_data(user_id, exp_guid):
    src_file_path = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, exp_guid, "model.pdb")
    dst_dir = os.path.join(current_app.config['APP_ROOT'], "app/static/uploads", exp_guid)

    try:
        os.mkdir(dst_dir)
        dst_file_path_models = os.path.join(dst_dir, "model.pdb")
        shutil.copyfile(src_file_path, dst_file_path_models)
    except OSError as err:
        if err.errno != errno.EEXIST:
            current_app.logger.error('Error while trying to create a new directory in specified directory or trying to copy model.pdb to \'static/uploads/[exp_guid]\'\n'
                                     'arguments: dst_dir - ' + dst_dir, exc_info=err)
            raise err


def delete_computations(info, user_id):
    if info['all'] == 'True':
        for item in os.listdir(os.path.join(current_app.config['EXP_DIRECTORY'], user_id)):
            shutil.rmtree(os.path.join(current_app.config['EXP_DIRECTORY'], user_id, item))
    else:
        directory_to_delete = os.path.join(current_app.config['EXP_DIRECTORY'], user_id, info['comp_guid'])
        shutil.rmtree(directory_to_delete)
