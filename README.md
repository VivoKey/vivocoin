About
=====

VivoCoin is a demo app for third-party integration with VivoKey. It demonstrates two different uses of the VivoKey API: logging in with VivoKey (using OpenID Connect), and requesting an authorisation with VivoKey.

Installation
============
VivoCoin is written in Python. Installation using a virtualenv is highly recommended:

    $ virtualenv vivocoin-virtualenv
    $ source vivicoin-virtualenv/bin/activate

Once in the virtualenv, you can install the requirements using pip:

    pip install -r requirements.txt

Configuration
=============
Before you start, you will need a custom application set up on the VivoKey server. Specifically, you will need your OpenID client ID and client secret. If you don't have these, contact your friendly VivoKey representative.

Set the following environment variables:

 * VIVO_SERVER: "https://api.vivokey.com/"
 * VALIDATION_CALLBACK: "http://your-server-location/validation_complete/"
 * OIDC_RP_CLIENT_ID: Your OpenID Connect client ID
 * OIDC_RP_CLIENT_SECRET: Your OpenID Connect client secret

Here is an example configuration:

    export VIVO_SERVER="https://api.vivokey.com/"
	export VALIDATION_CALLBACK="http://192.168.0.2:8000/validation_complete/"
	export OIDC_RP_CLIENT_ID="29485022"
	export OIDC_RP_CLIENT_SECRET="980a949209b9028498fe0932839e09809"

Running the server (development)
================================
VivoCoin is a Django application. You can therefore run a test server using manage.py, like this:

    python3 manage.py runserver 0.0.0.0:8000

Running the server (production)
===============================
VivoCoin is an API demo and is not intended to be run in production. However, if you do wish to expose VivoCoin to the Internet, make the following changes to `vivocoin/settings.py` before doing so:

 * Change `DEBUG = True` to `DEBUG = False`.
 * Change `SECRET_KEY`.
 * Restrict `ALLOWED_HOSTS` to the name of the server that VivoCoin is running on (e.g. if your server is at https://vivocoin.mycompany.com/, set `ALLOWED_HOSTS` to `['vivocoin.mycompany.com']`.

If running in production, you should run VivoCoin behind a real web server (such as nginx or Apache), using WSGI or similar.

