"""
Module for handling and processing MQTT messages related to "SL20" ultrasonic level meters.

This module provides the MQTTMessageHandler class, which is designed to extract, 
process, and format relevant data from raw MQTT messages. The main data points of interest 
include PG data, RW data, and timestamps.
"""

import json
from datetime import datetime
import numpy as np


class MQTTMessageHandler:
    """
    Handler for processing MQTT messages related to "SL20" ultrasonic level meters.

    This class provides methods to extract and process relevant data from the MQTT 
    messages, including PG data, RW data, and timestamps.
    """

    def __init__(self, message):
        """
        Initialize the handler with a raw MQTT message.

        Args:
        - message: The raw MQTT message to be processed.
        """
        self.message = message
        self.data = json.loads(self.message.payload.decode())
        self.pg = {}
        self.date = ""
        self.rw_x = []
        self.rw_y = []

    def process_message(self):
        """
        Process the raw MQTT message to extract relevant data.
        """
        self._handle_pg_data()
        self._handle_rw_data()
        self._handle_date()

    def _handle_pg_data(self):
        """
        Extract and process PG data from the MQTT message.
        """
        pg_registers = ["TVGAIN0",
                        "TVGAIN1",
                        "TVGAIN2",
                        "TVGAIN3",
                        "TVGAIN4",
                        "TVGAIN5",
                        "TVGAIN6",
                        "INIT_GAINAFE",
                        "FREQUENCY",
                        "DEADTIME",
                        "PULSE_P1",
                        "PULSE_P2",
                        "CURR_LIM_P1",
                        "CURR_LIM_P2",
                        "REC_LENGTH",
                        "FREQ_DIAG",
                        "SAT_FDIAG_TH",
                        "FVOLT_DEC",
                        "DECPL_TEMP",
                        "DSP_SCALE",
                        "TEMP_TRIM",
                        "P1_GAIN_CTRL",
                        "P2_GAIN_CTRL"]

        pg_data = self.data.get("PG", [])[0]
        pg_data = [pg_data[i:i+2] for i in range(0, len(pg_data), 2)]
        pg_data = [int(hex, 16) for hex in pg_data]
        self.pg = dict(zip(pg_registers, pg_data))

    def _handle_rw_data(self):
        """
        Extract and process RW data for chart from the MQTT message.
        """
        rw_data = self.data.get("RW", [])[0]
        self.rw_y = [int(rw_data[i:i+2], 16)
                     for i in range(0, len(rw_data), 2)]
        self.rw_x = np.linspace(
            0, self.pg['REC_LENGTH'] >> 4, len(self.rw_y)).tolist()

    def _handle_date(self):
        """
        Extract and format the timestamp from the MQTT message.
        """
        timestamp = int(self.data.get("date", 0))
        self.date = datetime.utcfromtimestamp(
            timestamp).strftime('%H:%M %d %B %Y')
