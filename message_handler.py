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

    # Define __pg_registers_keys as a private class attribute
    __pg_registers_keys = [
        "TVGAIN0", "TVGAIN1", "TVGAIN2", "TVGAIN3", "TVGAIN4", "TVGAIN5", "TVGAIN6",
        "INIT_GAINAFE", "FREQUENCY", "DEADTIME", "PULSE_P1", "PULSE_P2", "CURR_LIM_P1",
        "CURR_LIM_P2", "REC_LENGTH", "FREQ_DIAG", "SAT_FDIAG_TH", "FVOLT_DEC",
        "DECPL_TEMP", "DSP_SCALE", "TEMP_TRIM", "P1_GAIN_CTRL", "P2_GAIN_CTRL"
    ]

    __tvg = {0b0000: 100,
             0b0001: 200,
             0b0010: 300,
             0b0011: 400,
             0b0100: 600,
             0b0101: 800,
             0b0110: 1000,
             0b0111: 1200,
             0b1000: 1400,
             0b1001: 2000,
             0b1010: 2400,
             0b1011: 3200,
             0b1100: 4000,
             0b1101: 5200,
             0b1110: 6400,
             0b1111: 8000}

    __afe_gain_rng = {0b00: 58, 0b01: 52, 0b10: 46, 0b11: 32}

    __aproximate_sound_speed = 330

    def __init__(self, message):
        """
        Initialize the handler with a raw MQTT message.

        Args:
        - message: The raw MQTT message to be processed.
        """
        self.message = message
        self.data = json.loads(self.message.payload.decode())
        self.pg_registers = {}
        self.date = ""
        self.rw_x = []
        self.rw_y = []
        self.pg_x = []
        self.pg_y = []
        self._handle_pg_registers()

    def process_message(self):
        """
        Process the raw MQTT message to extract relevant data.
        """
        self._handle_pg_chart()
        self._handle_rw_chart()
        self._handle_th_chart()
        self._handle_date()

    def _handle_pg_chart(self):
        """
        Extract and process RW data for Time-Varying Gain chart from the MQTT message.
        """
        self.pg_x.append(0)
        self.pg_x.append((self.__tvg[(self.pg_registers["TVGAIN0"]
                                      >> 4)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed)
        delta = (self.__tvg[(self.pg_registers["TVGAIN0"]
                             & 0x0f)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed
        self.pg_x.append(self.pg_x[1] + delta)

        delta = (self.__tvg[(self.pg_registers["TVGAIN1"]
                             >> 4)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed
        self.pg_x.append(self.pg_x[2] + delta)

        delta = (self.__tvg[(self.pg_registers["TVGAIN1"]
                             & 0x0f)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed
        self.pg_x.append(self.pg_x[3] + delta)

        delta = (self.__tvg[(self.pg_registers["TVGAIN2"]
                             >> 4)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed
        self.pg_x.append(self.pg_x[4] + delta)

        delta = (self.__tvg[(self.pg_registers["TVGAIN2"]
                             & 0x0f)] / (2 * 1000 * 1000)) * self.__aproximate_sound_speed
        self.pg_x.append(self.pg_x[5] + delta)

        self.pg_x = np.round(self.pg_x, 3).tolist()

        afe_gain = self.__afe_gain_rng[self.pg_registers["DECPL_TEMP"] >> 6]

        tvg_g0 = self.pg_registers["INIT_GAINAFE"] & 0x3f
        tvg_g1 = self.pg_registers["INIT_GAINAFE"] & 0x3f
        tvg_g2 = self.pg_registers["TVGAIN3"] >> 2
        tvg_g3 = ((self.pg_registers["TVGAIN3"] & 0x03) << 4) | (
            self.pg_registers["TVGAIN4"] >> 4)
        tvg_g4 = ((self.pg_registers["TVGAIN4"] & 0x0f)) << 2 | (
            self.pg_registers["TVGAIN5"] >> 6)

        tvg_g5 = self.pg_registers["TVGAIN5"] & 0x3f
        tvg_g6 = self.pg_registers["TVGAIN6"] >> 2

        self.pg_y.append(0.5 * (tvg_g0 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g1 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g2 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g3 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g4 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g5 + 1) + afe_gain)
        self.pg_y.append(0.5 * (tvg_g6 + 1) + afe_gain)

    def _handle_rw_chart(self):
        """
        Extract and process RW data for raw signal chart from the MQTT message.
        """
        rw_data = self.data.get("RW", [])[0]
        self.rw_y = [int(rw_data[i:i+2], 16)
                     for i in range(0, len(rw_data), 2)]
        record_time_length_ms = self.pg_registers['REC_LENGTH'] >> 4
        record_distance = (self.__aproximate_sound_speed *
                           record_time_length_ms/1000) * 2
        self.rw_x = np.round(np.linspace(
            0, record_distance, len(self.rw_y)), 3).tolist()

    def _handle_th_chart(self):
        """
        Extract and process RW data for Threshold chart from the MQTT message.
        """

    def _handle_pg_registers(self):
        """
        Extract and process PG registers data from the MQTT message.
        """

        pg_data = self.data.get("PG", [])[0]
        pg_data = [pg_data[i:i+2]
                   for i in range(0, len(pg_data), 2)]
        pg_data = [int(hex, 16) for hex in pg_data]
        self.pg_registers = dict(zip(self.__pg_registers_keys, pg_data))

    def _handle_date(self):
        """
        Extract and format the timestamp from the MQTT message.
        """
        timestamp = int(self.data.get("date", 0))
        self.date = datetime.utcfromtimestamp(
            timestamp).strftime('%H:%M %d %B %Y')
