"""Handles the main logic of the Oxygen CS application"""

import logging
import json
import time
import os
import psycopg2
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder

# pylint: disable=broad-exception-caught, unnecessary-pass


class App:
    """Main class to handle the Oxygen CS application"""

    def __init__(self):
        self._hub_connection = None
        self.ticks = 10

        # To be configured by your team
        self.host = os.getenv("HOST", "Host URL not found")
        self.token = os.getenv("TOKEN", "Token not found")
        self.t_max = os.getenv("T_MAX", "Max temp not found")
        self.t_min = os.getenv("T_MIN", "Min temp not found")
        self.database_url = os.getenv("DATABASE_URL", "Database URL not found")

        self.conn = psycopg2.connect(self.database_url)

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature, timestamp)
            self.save_temperature_to_database(timestamp, temperature, "temperaturelog")
        except Exception as err:
            print(err)

    def take_action(self, temperature, timestamp):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.t_max):
            action = "TurnOnAc"
            self.send_action_to_hvac(action)
            self.save_hvac_action_to_database(timestamp, action, temperature, self.t_max, "hvacactionlog")
        elif float(temperature) <= float(self.t_min):
            action = "TurnOnHeater"
            self.send_action_to_hvac(action)
            self.save_hvac_action_to_database(timestamp, action, temperature, self.t_min, "hvacactionlog")


    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}", timeout=5
        )
        details = json.loads(r.text)
        print(details, flush=True)

    def save_temperature_to_database(self, timestamp, temperature, tableName):
        """Save sensor data into database."""
        if None not in (temperature, timestamp):
            sql = f"""INSERT INTO {tableName}(timestamp, temperature) VALUES(TIMESTAMP '{timestamp}',{temperature})"""
            try:
                with self.conn:
                    with self.conn.cursor() as self.cur:
                        self.cur.execute(sql)
            except (requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
                print(e)

    def save_hvac_action_to_database(self, timestamp, action, temperature, targettemperature, tableName):
        """Save HVAC action to database"""
        if None not in (temperature, timestamp, action):
            sql = f"INSERT INTO {tableName}(timestamp, action, temperature, targetTemperature) VALUES(TIMESTAMP '{timestamp}', '{action}', {temperature}, {targettemperature})"
            try:
                with self.conn:
                    with self.conn.cursor() as self.cur:
                        self.cur.execute(sql)
            except(requests.exceptions.RequestException, psycopg2.DatabaseError) as e:
                print(e)


if __name__ == "__main__":
    app = App()
    app.start()
