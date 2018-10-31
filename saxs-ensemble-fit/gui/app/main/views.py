from flask import render_template, redirect, flash, jsonify, request, current_app, url_for
from . import main
from app.forms import Computation
from app.bussinesLogic import DirectoryAndFileReader, DirectoryAndFileWriter
from app.models import User
from app.main.errors import NewComputationRequestSubmitError


@main.route('/')
@main.route('/home', methods=['GET', 'POST'])
def home():
    user_details = get_user_details()

    if not is_user_registered(user_details[0]):
        return redirect(url_for('userManagement.sign_up'))

    form = Computation()
    user_id = get_user_id(user_details[0])
    if form.validate_on_submit():  # this block of code is executed when browser sent POST request(user submitted form)
        try:
            DirectoryAndFileWriter.create_experiment(form, str(user_id))
            flash(current_app.config['EXPERIMENT_SUBMITTED'], "info")
            return redirect('/home')
        except NewComputationRequestSubmitError:
            flash(current_app.config['EXPERIMENT_SUBMISSION_FAILED'], "error")
            return redirect('/home')

    if is_user_registered(user_details[0]) and is_user_confirmed(user_details[0]):
        return render_template('home.html', form=form, username=get_user_username(user_details[0]), is_admin=is_user_admin(user_details[0]),
                               pages=DirectoryAndFileReader.get_pagination_controls_count(user_id),
                               comps=DirectoryAndFileReader.get_subset_of_computations_for_one_page(
                                   get_user_id(user_details[0]), 0, 'date', -1, {}))
    elif is_user_registered(user_details[0]) and not is_user_confirmed(user_details[0]):
        return redirect(url_for('userManagement.unconfirmed'))


@main.route('/view_experiment/<user_id>/<comp_guid>')
def view_experiment(user_id, comp_guid):
    user_details = get_user_details()

    if not is_user_registered(user_details[0]):
        return redirect(url_for('userManagement.sign_up'))

    elif is_user_registered(user_details[0]) and not is_user_confirmed(user_details[0]):
        return redirect(url_for('userManagement.unconfirmed'))

    if not DirectoryAndFileReader.check_if_computation_exist(user_id, comp_guid):
        return render_template("unavailable.html", message="Requested computation results don't exist. Make sure the url is correct", icon="info.png")
    if not DirectoryAndFileReader.check_for_computation_results(user_id, comp_guid, DirectoryAndFileReader.get_computation_status(user_id, comp_guid)):
        return render_template("unavailable.html", message="Requested results cannot be displayed, because server has not finished the computation. Try again later", icon="gears.gif")
    DirectoryAndFileWriter.get_model_data(user_id, comp_guid)
    return render_template("view_experiment.html", username=user_details[1], is_admin=is_user_admin(user_details[0]),
                           best_results=DirectoryAndFileReader.get_best_solutions_of_computation(user_id, comp_guid),
                           computation_details=DirectoryAndFileReader.get_computation_parameters(user_id, comp_guid))


@main.route('/get_experiments/<page>/<sort_option>/<sort_order>', methods=['GET', 'POST'])
def get_experiments(page, sort_option, sort_order):
    user_details = get_user_details()
    user_id = get_user_id(user_details[0])

    if not is_user_registered(user_details[0]):
        return redirect(url_for('userManagement.sign_up'))

    elif is_user_registered(user_details[0]) and not is_user_confirmed(user_details[0]):
        return redirect(url_for('userManagement.unconfirmed'))

    return jsonify(comps=DirectoryAndFileReader.get_subset_of_computations_for_one_page(user_id, int(page), sort_option, int(sort_order), request.json),
                   pages=len(DirectoryAndFileReader.get_pagination_controls_count(computations=DirectoryAndFileReader.get_computations(user_id, sort_option, int(sort_order), request.json))))


@main.route('/delete_computations/<page>/<sort_option>/<sort_order>', methods=['GET', 'POST'])
def delete_computations(page, sort_option, sort_order):
    user_details = get_user_details()
    user_id = get_user_id(user_details[0])

    if not is_user_registered(user_details[0]):
        return redirect(url_for('userManagement.sign_up'))

    elif is_user_registered(user_details[0]) and not is_user_confirmed(user_details[0]):
        return redirect(url_for('userManagement.unconfirmed'))

    DirectoryAndFileWriter.delete_computations(request.json, str(user_id))
    return jsonify(comps=DirectoryAndFileReader.get_subset_of_computations_for_one_page(user_id, int(page), sort_option, int(sort_order), request.json['filter_values']),
                   pages=len(DirectoryAndFileReader.get_pagination_controls_count(computations=DirectoryAndFileReader.get_computations(user_id, sort_option, int(sort_order), request.json['filter_values']))))


@main.route('/get_experiment_data')
def get_experiment_data():
    user_details = get_user_details()

    if not is_user_registered(user_details[0]):
        return redirect(url_for('userManagement.sign_up'))

    elif is_user_registered(user_details[0]) and not is_user_confirmed(user_details[0]):
        return redirect(url_for('userManagement.unconfirmed'))

    user_id = request.args.get("user_id")
    comp_guid = request.args.get("comp_guid")
    json = jsonify(weights=DirectoryAndFileReader.get_weights(user_id, comp_guid),
                   computedCurves=DirectoryAndFileReader.get_computed_curves(user_id, comp_guid),
                   experimentData=DirectoryAndFileReader.get_experiment_data(user_id, comp_guid))
    return json


def get_user_details():
    result = [request.environ["HTTP_EPPN"], request.environ["HTTP_CN"].decode("unicode_escape"), request.environ["HTTP_MAIL"].decode("unicode_escape")]
    return result


def is_user_registered(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None


def is_user_confirmed(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None and user.confirmed


def is_user_admin(eppn):
    user = User.query.filter_by(eppn=eppn).first()
    return user is not None and user.role_id == 1


def get_user_id(eppn):
    return User.query.filter_by(eppn=eppn).first().id


def get_user_username(eppn):
    return User.query.filter_by(eppn=eppn).first().username


