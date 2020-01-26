from flask import url_for, render_template, request, redirect, session, g
from flask import current_app as app
import socket
import time
import threading
from influxdb import InfluxDBClient
from random import randint


@app.route('/data', methods=["GET"])
def get_data():
    if request.method == "GET":
        serial_number = request.args["serial"]
        measurement = request.args["measurement"]
        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")
        query = 'select "Waarde" from {0} WHERE (Serienummer_meter=$serial) AND time >= now()- 30m'.format(measurement)
        result = client_influx.query(query, bind_params={'serial': serial_number})
        return result.raw["series"][0]

