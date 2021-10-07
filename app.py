from gevent import monkey
# Calling monkey patch to handle incoming requests concurrently
# This method is called before all imports which use ssl to avoid ssl errors
monkey.patch_all()

import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
import msal
import app_config
import json
import os
from gevent.pywsgi import WSGIServer
from gevent.pool import Pool
import logging
from werkzeug.middleware.proxy_fix import ProxyFix


if not os.path.exists(app_config.CERTS_FOLDER):
    os.mkdir(app_config.CERTS_FOLDER)

if not os.path.exists(app_config.LOG_FOLDER):
    os.mkdir(app_config.LOG_FOLDER)

# logging config
logging.basicConfig(
    level=logging.DEBUG,
    filename=app_config.LOG_FILE,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    filemode="a",
)
logger = logging.getLogger(__name__)

# App Config
app = Flask(__name__)
app.config.from_object(app_config)
Session(app)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/", methods=["POST", "GET"])
def index():
    """GET and POST method for "/" route for Server1 flask application.

    GET: Shows index/home page where user can select parameters to elevate itself.
    POST: Redirects to display page to show results after running the elevation script.

    """
    if not session.get("user"):
        message = "Login failure due to no user field in the session data."
        logger.error(message)
        return redirect(url_for("login"))

    if request.method == "POST":
        session["elevation_group"] = request.form.get("elevationGroup", "")
        session["elevation_time"] = request.form.get("elevationTime", "")

        debug_message = "Elevation group " + session["elevation_group"]
        logger.debug(debug_message)
        debug_message = "Elevation time " + session["elevation_time"]
        logger.debug(debug_message)

        return redirect(url_for("display")), app_config.POST_REQUEST_STATUS_CODE

    return render_template(
        "index.html",
        user=session["user"],
        admin_groups=app_config.ADMIN_GROUPS_LIST,
        elevation_times=app_config.ELEVATION_TIMES_LIST,
        version=msal.__version__,
    )


@app.route("/display")
def display():
    """GET method for "/display" route for Server1 flask application

    GET: Calls "/" API exposed by Server2 which runs elevation script based on
         group name and time for elevation given by a logged in user, and
         displays the response of the elevation script.
    """
    token = _get_token_from_cache(app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))

    group_name = session.get("elevation_group")

    time = session.get("elevation_time")

    session_user_name = session["user"]["preferred_username"]
    user_name = session_user_name.split("@")[0]

    debug_message = (
        "Username : " + user_name + " Group : " + group_name + " Time : " + time
    )
    logger.debug(debug_message)

    payload = json.dumps({"group": group_name, "user": user_name, "time": time, "key": app_config.SHAN_SERVER_SECRET_KEY})
    headers = {"Content-Type": "application/json"}

    final_result = "Elevation Server is currently down. Please contact your Administrator"

    try:
        response = requests.post(
            app_config.SERVER_2_URL,
            headers=headers,
            data=payload,
        )
        if response.status_code == app_config.POST_REQUEST_STATUS_CODE:
            if response.json:
                response_json = response.json()
                final_result = response_json.get("output", final_result)
            else:
                message = (
                    "No json parameter in the Response object of API call to Server2."
                )
                logger.error(message)
        else:
            message = "Response status code from API call to Server2: " + str(
                response.status_code
            )
            logger.error(message)
    except Exception as e:
        logger.error(e)

    return render_template("display.html", final_result=final_result)


@app.route("/login", methods=["POST", "GET"])
def login():
    """GET AND POST method for "/login" route for Server1 flask application.

    GET: Displays the login page for Server1 flask application.
    POST: Redirects user to Microsoft O365 authentication.

    """
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    auth_url = session["flow"]["auth_uri"]
    if request.method == "POST":
        logger.info("Redirecting to Microsoft O365 authentication")
        return redirect(auth_url), app_config.POST_REQUEST_STATUS_CODE

    logger.info("Login page for SHAN Web Portal")
    return render_template("login.html", auth_url=auth_url, version=msal.__version__)


@app.route(app_config.REDIRECT_PATH)
def authorized():
    """GET method for "REDIRECT_PATH" route for Server1 flask application.

    GET: Authenticates and redirects the user to index/home page of the
         Server1 flask application.

    """
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args
        )
        if "error" in result:
            logger.error("The user could not be authenticated")
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        logger.error("ValueError caused by CSRF(Cross Site Request Forgery)")
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """GET method for "/logout" route for Server1 flask application

    GET: Clears the session object and redirects the user back to login page.

    """
    session.clear()
    return redirect(
        app_config.AUTHORITY
        + "/oauth2/v2.0/logout"
        + "?post_logout_redirect_uri="
        + url_for("index", _external=True)
    )


def _load_cache():
    """Returns either an empty cache object or cache stored in session."""
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    """Saves cache data in session if it's state changes."""
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    """
    Takes cache data(if any) and defined authority(kind of users which are allowed)
    and Creates an MSAL app.
    """
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID,
        authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET,
        token_cache=cache,
    )


def _build_auth_code_flow(authority=None, scopes=None):
    """
    Takes in authority and scope objects (if any) as input and initiates
    code flow for authentication for MSAL app.
    """
    redirect_uri = url_for("authorized", _external=True)
    logger.error("RedirectURI : " + redirect_uri)
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [], redirect_uri=redirect_uri
    )


def _get_token_from_cache(scope=None):
    """Fetches token from cache stored in session, taking scope object (if any) as input"""
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)

if __name__ == "__main__":

    if not os.path.exists(app_config.APP_FOLDER_PATH):
        logger.error("The repo shan-web-server is not cloned inside /opt directory.")
    elif not app_config.CLIENT_ID:
        logger.error("The variable CLIENT_ID is not configured in app_config.py file.")
    elif not app_config.CLIENT_SECRET:
        logger.error("The variable CLIENT_SECRET is not configured in app_config.py file.")
    elif not app_config.TENANT_ID:
        logger.error("The variable TENANT_ID is not configured in app_config.py file.")
    elif not app_config.SERVER_2_URL:
        logger.error("The variable SERVER_2_URL is not configured in app_config.py file.")
    else:
        # If shan-web-server repo is configured in correct location and all necessary variables are set
        logger.info("The repo shan-web-server is configured in correct location and all variables are set.")

        for file in os.listdir(app_config.CERTS_FOLDER):
            if file.endswith("fullchain.pem"):
                app_config.CERTS_CHAIN_FILE = app_config.CERTS_FOLDER + file
            elif file.endswith("privkey.pem"):
                app_config.KEY_FILE = app_config.CERTS_FOLDER + file

        if not app_config.CERTS_CHAIN_FILE:
            logger.error(
                "Certificate chain file not found. Please refer ReadME for certificate configuration."
            )
        elif not app_config.KEY_FILE:
            logger.error(
                "Certificate key file not found. Please refer ReadME for certificate configuration."
            )
        else:
            logger.info("Starting WSGI server...")
            spawn = Pool(app_config.MAX_NUMBER_OF_REQUESTS)
            https_server = WSGIServer(
                (app_config.HTTPS_SERVER, app_config.HTTPS_PORT),
                app,
                keyfile=app_config.KEY_FILE,
                certfile=app_config.CERTS_CHAIN_FILE,
                spawn=spawn
            )
            https_server.serve_forever()

            logger.info("WSGI server is running...")
