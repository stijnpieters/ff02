from flask import url_for, render_template, request, redirect, session, g
from flask import current_app as app
import socket
import time
import threading
from random import randint


@app.route('/data', methods="GET")
def get_data():
    if request.method == "GET":
        serial_number = request.args["serial"]
        measurement = request.args["measurement"]
        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")
        result = client_influx.query("select * from $measurement where time >= now()-30m and serienummer_meter=$serial",
            bind_params={'measurement': measurement, 'serial': serial_number})
        data = list(result.get_points(measurement=measurement))
        return data

