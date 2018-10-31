from flask import render_template, current_app
from . import main


class NewComputationRequestSubmitError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


@main.app_errorhandler(404)
def page_not_found(err):
    current_app.logger.warning('Page Not Found', exc_info=err)
    return render_template('error/error_page.html', message="Sorry, but the page you are looking for has not been found. Check the url for errors, then refresh the page.",
                           error_icon="error404.png"), 404


@main.app_errorhandler(400)
def key_error(err):
    current_app.logger.warning('Invalid request resulted in KeyError', exc_info=err)
    return render_template('error/error_page.html', message=""), 400


@main.app_errorhandler(500)
def internal_server_error(err):
    current_app.logger.warning('Internal Server Error', exc_info=err)
    return render_template('error/error_page.html', message="An error occurred while processing your request. This is our fault and we are looking into it.",
                           error_icon="error.png"), 500


@main.app_errorhandler(Exception)
def unhandled_exception(err):
    current_app.logger.error('An unhandled exception is being displayed to the end user', exc_info=err)
    return render_template('error/error_page.html', message="An error occurred while processing your request. This is our fault and we are looking into it.",
                           error_icon="error.png"), 500
