from __init__ import create_app
from json_responses import *

if __name__ == '__main__':
    app = create_app()

    @app.route('/test')
    def hello_world():
        return 'hello!'

    @app.errorhandler(404)
    def invalid_route(e):
        return get_json_fail("Page not found"), 404

    @app.login_manager.unauthorized_handler
    def unauth_handler():
        return get_json_fail("Unauthorized access"), 401

    app.run()

