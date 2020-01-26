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
            return {'value': abs(consumption - production)}
        else:
            return {'value': 0}


@app.route('/export', methods=["GET"])
def get_exports():
    if request.method == "GET":
        serial = request.args["serial"]
        consumption = get_data(serial, "Actueel_vermogen_uit_net")["values"][0][1]
        production = get_data(serial, "Actueel_vermogen_naar_net")["values"][0][1]
        if consumption - production > 0:
            return {'value': abs(production)}
        else:
            return {'value': 0}


@app.route('/selfconsumedpvsolarpanelyield', methods=["GET"])
def get_selfconsumedpvsolarpanelyield():
    if request.method == "GET":
        serial = request.args["serial"]
        consumption = get_data(serial, "Actueel_vermogen_uit_net")["values"][0][1]
        production = get_data(serial, "Actueel_vermogen_naar_net")["values"][0][1]
        if production - consumption < 0:
            return {'value': consumption}
        else:
            return {'value': production}


@app.route('/selfconsumption', methods=["GET"])
def get_selfconsumption():
    if request.method == "GET":
        serial = request.args["serial"]
        production = get_data(serial, "Actueel_vermogen_naar_net")["values"][0][1]
        selfconsumedpvsolarpanelyield = get_selfconsumedpvsolarpanelyield()['value']
        return {'value': selfconsumedpvsolarpanelyield / production}


@app.route('/selfusage', methods=["GET"])
def get_selfusage():
    if request.method == "GET":
        serial = request.args["serial"]
        consumption = get_data(serial, "Actueel_vermogen_uit_net")["values"][0][1]
        selfconsumedpvsolarpanelyield = get_selfconsumedpvsolarpanelyield()['value']
        return {'value': selfconsumedpvsolarpanelyield / consumption}


@app.route('/groupedconsumption', methods=["GET"])
def get_grouped_consumption():
    if request.method == "GET":
        today = datetime.date.today()
        measurement = "Actueel_vermogen_uit_net"
        serial = request.args["serial"]

        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")
        query = 'select sum("Waarde") from {0} WHERE (Serienummer_meter=$serial) AND time >= now() - {1}d GROUP BY time(1h)'.format(
            measurement, today.day - 1)
        result = client_influx.query(query, bind_params={'serial': serial})
        return {'values': result.raw["series"][0]["values"]}


@app.route('/groupedsolarpanelyield', methods=["GET"])
def get_grouped_solarpanelyield():
    if request.method == "GET":
        today = datetime.date.today()
        measurement = "Actueel_vermogen_naar_net"
        serial = request.args["serial"]

        client_influx = InfluxDBClient("35.233.68.4", 8086)
        client_influx.switch_database("demodb")
        query = 'select sum("Waarde") from {0} WHERE (Serienummer_meter=$serial) AND time >= now() - {1}d GROUP BY time(1h)'.format(
            measurement, today.day - 1)
        result = client_influx.query(query, bind_params={'serial': serial})
        return {'values': result.raw["series"][0]["values"]}
