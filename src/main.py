"""Handles the main logic of the Oxygen CS application"""

import logging
import json
import time
import requests
from signalrcore.hub_connection_builder import HubConnectionBuilder

# pylint: disable=broad-exception-caught, unnecessary-pass


class App:
    """Main class to handle the Oxygen CS application"""

    def __init__(self):
        self._hub_connection = None
        self.ticks = 10

        # To be configured by your team
        self.host = None  # Setup your host here
        self.token = None  # Setup your token here
        self.t_max = None  # Setup your max temperature here
        self.t_min = None  # Setup your min temperature here
        self.database_url = None  # Setup your database here

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
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(
            f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}", timeout=5
        )
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        print(timestamp, temperature, flush=True)
        try:
            # To implement
            pass
        except requests.exceptions.RequestException as e:
            print(e)
            # To implement
            pass


if __name__ == "__main__":
    app = App()
    app.start()
