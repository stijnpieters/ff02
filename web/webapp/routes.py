from flask import url_for, render_template, request, redirect, session, g
from flask import current_app as app
import socket
import time
import threading
import datetime
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
        return {'values': result.raw["series"][0]["values"]}


@app.route('/electricityconsumption', methods=["GET"])
def get_consumption():
    if request.method == "GET":
        serial_number = request.args["serial"]

        today = datetime.date.today()

        measurement = "Actueel_vermogen_uit_net"
        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")

        query = 'select sum("Waarde") from {0} WHERE (Serienummer_meter=$serial) AND time >= now() - {1}d'.format(measurement, today.day - 1)
        result = client_influx.query(query, bind_params={'serial': serial_number})
        return {'values': result.raw["series"][0]["values"]}


@app.route('/solarpanelyield', methods=["GET"])
def get_production():
    if request.method == "GET":
        serial_number = request.args["serial"]

        today = datetime.date.today()

        measurement = "Actueel_vermogen_naar_net"
        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")
        query = 'select sum("Waarde") from {0} WHERE (Serienummer_meter=$serial) AND time >= now() - {1}d'.format(measurement, today.day - 1)
        result = client_influx.query(query, bind_params={'serial': serial_number})
        return {'values': result.raw["series"][0]["values"]}


@app.route('/import', methods=["GET"])
def get_imports():
    consumption = get_consumption()["values"][0][1]
    production = get_production()["values"][0][1]
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
