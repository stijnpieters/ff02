from flask import url_for, render_template, request, redirect, session, g
from flask import current_app as app
import socket
import time
import threading
import datetime
from influxdb import InfluxDBClient
from random import randint


@app.route('/electricityconsumption', methods=["GET"])
def get_consumption():
    if request.method == "GET":
        serial_number = request.args["serial"]
        return get_data(serial_number, "Actueel_vermogen_uit_net")


@app.route('/solarpanelyield', methods=["GET"])
def solarpanelyield():
    if request.method == "GET":
        serial_number = request.args["serial"]
        return get_data(serial_number, "Actueel_vermogen_naar_net")


def get_data(serial, measurement):
    today = datetime.date.today()

    client_influx = InfluxDBClient("35.233.68.4", 8086)
    client_influx.switch_database("demodb")
    query = 'select sum("Waarde") from {0} WHERE (Serienummer_meter=$serial) AND time >= now() - {1}d'.format(
        measurement, today.day - 1)
    result = client_influx.query(query, bind_params={'serial': serial})
    return {'values': result.raw["series"][0]["values"]}


@app.route('/import', methods=["GET"])
def get_imports():
    if request.method == "GET":
        serial = request.args["serial"]
        consumption = get_data(serial, "Actueel_vermogen_uit_net")["values"][0][1]
        production = get_data(serial, "Actueel_vermogen_naar_net")["values"][0][1]
        if consumption - production < 0:
            return abs(consumption - production)
        else:
            return 0


@app.route('/export', methods=["GET"])
def get_exports():
    consumption = get_consumption()["values"][0][1]
    production = get_production()["values"][0][1]
    if consumption - production > 0:
        return abs(production)
    else:
        return 0


@app.route('/selfconsumedpvsolarpanelyield', methods=["GET"])
def get_selfconsumedpvsolarpanelyield():
    pass
