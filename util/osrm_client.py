from flask import current_app
import osrm


def osrm_init():
    global client
    client = osrm.Client(host=current_app.config['OSRM_URL'], profile='foot')

