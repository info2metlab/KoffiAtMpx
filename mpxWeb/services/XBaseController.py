#!/usr/bin/python
from argparse import Action
from concurrent.futures import thread
from datetime import datetime
import json
import tensorflow as tf
from pathlib import Path
import os, sys
import random
from secrets import choice
from tokenize import Double
from urllib.error import HTTPError
from random import expovariate, gauss, randint, randrange, sample, seed, uniform
from configparser import ConfigParser
from matplotlib.lines import lineStyles
from matplotlib.patches import StepPatch
import numpy as np
import pandas as pd
import requests
import csv as csv
import time 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt  
# from loadprocessor import LoadProcessor
from scipy.integrate import simpson
# from utility import control, LoadProfile
from XUtility import *



# APIs URLs
os.environ["RATING_URL"]  = 'http://localhost:5000/api/Transfo'
os.environ["API_URL"] = 'http://10.0.2.15:8000/jakobface'


models_dir= "cooling"
log_dir = "logs"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Nominal Fan Power : 1030 W  
# FAN_SPEED_MAX       = [300, 300, 300, 300, 450, 450, 450, 450, 540, 540, 540, 540, 650, 650, 650, 650] #Nominal Fan speed : 650 RPM 
# FAN_NOISE           =  [68, 65, 64, 63, 77, 74, 73, 72, 81, 78, 77, 76, 85, 82, 81, 80] Max Noise level while operating : 85 dB
# FAN_AIR_FLOW        = 31000     # Fan air flow capacity : 22100 cubic meter 
# N_FAN_EFFY          = 0.95       # Fan Motor Power Efficiency
# PUMPS MODEL 
# # PUMP_EFFY           = 0.75      # Pumps Efficiency (n_m)
# MAX_FLOW_RATE       = 100       # m3/h
# PUMPS_MOTOR_EFFY    = 0.95      # Pumps Motor Power Efficiency (n_vfd)



# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display


class BaseController:
    
    def __init__(self, equipId, loadtype):

        self.equipId        = equipId
        self.ref_state      = []
        self.load_profile   = list()
        self.step           = 0   

        self.ref_puload     = []
        self.ref_hotspot    = []
        self.ref_topoil     = []
        self.ref_bottom     = []
        self.bank_setpoints = []
        self.actuation_plan = np.zeros(LOADCYCLE)
        self.active_case = loadtype

        self.n_fans         = 1
        self.n_pumps        = 1
        self.Cw             = 0.1
        self.Cp             = 0.1
            
         
    def fspeed_to_power(self, fspeed):
        for i in range(len(self.fan_speed )):
            if(self.fan_speed[i] < fspeed <= self.fan_speed[i + 1]):
                return self.fan_powers[i+1]

    def oilflow_to_power(self, oilflow):
        for i in range(len(self.flow_rate)):
            if(float(self.flow_rate[i]) <= float(oilflow) <= float(self.flow_rate[i + 1])):
                return float(self.pump_powers[i])   
    def base_initialize(self):   
                
        self.ref_state          = {} # get_load_references()
        response                = {} # get_cooling_config()
        ref_state               = self.ref_state

        # self.NUM_FANS           = 8 # response["num_fans"]  
        # self.NUM_PUMPS          = 2 # response["num_pumps"] 
        # self.FAN_POWERS         = np.random.uniform(0.95, 0.97, 10)     
        # self.PUMP_POWERS        = np.random.uniform(0.95, 0.97, 10) 
        
        self.fan_powers       = np.array([100, 120, 130, 145, 370,  430, 460, 500, 610, 720, 800, 860, 1030, 1230, 1350, 1500]) # response["num_fans"]     
        self.pump_powers      = np.array([430.0, 1070.0, 2950.0, 6920.0, 8830.0])  # response["pump_powers"]
        with Session(p_engine) as p_session:
                width            = 2                          
                loading_curve    = pd.DataFrame(p_session.execute(select(loadcurves)).all())
                load_results     = pd.DataFrame(p_session.execute(select(loadresults).where(loadresults.c.loadtype == self.active_case)).all())
                setpoints_data   = pd.DataFrame(p_session.execute(select(setpoints)).all())
    
        self.bank_setpoints  = [
                                {"CV":SETPOINTS.TOPOIL_TEMPERATURE, 
                                            "lower_curve": 0.75 * loading_curve['optopoil'].values[-1] * np.ones(1), 
                                            "upper_curve": 1.0 *loading_curve['optopoil'].values[-1] * np.ones(1), 
                                            "period"     : 5, 
                                            "Power"      : 4 * self.fan_powers[2] +  2 * self.pump_powers[2], 
                                            "status": 0 },

                                {"CV":SETPOINTS.TOPOIL_TEMPERATURE, 
                                                "lower_curve": 1.0 * loading_curve['opbottom'].values[-1] * np.ones(1), 
                                                "upper_curve": 0.75 * loading_curve['optopoil'].values[-1] * np.ones(1), 
                                                "period"     : 5, 
                                                "Power"      : 8 * self.fan_powers[4] +  2 * self.pump_powers[2], 
                                                "status"     : 0 },

                                {"CV":SETPOINTS.HOTSPOT_TEMPERATURE, 
                                                 "lower_curve": 0.75 *loading_curve['ophotspot'].values[-1] * np.ones(1),  
                                                 "upper_curve": 1.0 * loading_curve['ophotspot'].values[-1] * np.ones(1), 
                                                 "period"     : 5, 
                                                 "Power"      : 8 * self.fan_powers[5] +  2 * self.pump_powers[3],
                                                 "status"     : 0 },
                                
                                {"CV":SETPOINTS.HOTSPOT_TEMPERATURE, 
                                                 "lower_curve": 1.0 *  loading_curve['optopoil'].values[-1] * np.ones(1), 
                                                 "upper_curve": 0.75 *  loading_curve['ophotspot'].values[-1] * np.ones(1),
                                                 "period"     : 5, 
                                                 "Power"      : 8 * self.fan_powers[7] +  2 * self.pump_powers[-1],  
                                                 "status"     : 0 },

                                {"CV":SETPOINTS.TTP_HOTSPOT, 
                                                 "lower_curve": 0.5 *  load_results['ttptop'].values[-1] * np.ones(1), 
                                                 "upper_curve": 0.75 * load_results['ttptop'].values[-1] * np.ones(1),
                                                 "period"     : 0, 
                                                 "Power"      : 8 * self.fan_powers[7] +  2 * self.pump_powers[-1],  
                                                 "status"     : 0 },
                                                                
                                {"CV":SETPOINTS.TTP_HOTSPOT, 
                                                 "lower_curve": 0.75 *  load_results['ttphot'].values[-1] * np.ones(1), 
                                                 "upper_curve": 0.9 * load_results['ttphot'].values[-1] * np.ones(1),
                                                 "period"     : 0, 
                                                 "Power"      : 8 * self.fan_powers[7] +  2 * self.pump_powers[-1],  
                                                 "status"     : 0 },
                                ]

        self.min_fetching_rate = min([u["period"] for u in self.bank_setpoints])
        self.max_fetching_rate = max([u["period"] for u in self.bank_setpoints])

        print(f"Base Controller Initialized with {self.equipId} and {self.max_fetching_rate} seconds fetching rate")

    

    def check_curve_within_range(self, curve, lower_curve, upper_curve, period):
        """
        Check if a curve falls within a specified lower and upper curves range for a specified period of time to trigger an alarm.
        Parameters:
        curve (list or np.ndarray): The main curve data points.
        lower_curve (list or np.ndarray): The lower threshold curve.
        upper_curve (list or np.ndarray): The upper threshold curve.
        period (int): The specified period of time to check.
        Returns: bool: True if the curve falls within the range for the specified period, False otherwise.
        """
        count = 0
        for i in range(len(curve)):
            if lower_curve[i] <= curve[i] <= upper_curve[i]:
                count += 1
                if count >= period:
                    return True
            else:
                count = 0

        return False


    def base_switch_cooling(self):

        measurements= {"topoil" : np.random.uniform(60, 95, self.max_fetching_rate), 
                       "hotspot": np.random.uniform(128, 150, self.max_fetching_rate), 
                       "winding": np.random.uniform(85, 145, self.max_fetching_rate),
                       "puload" : np.random.uniform(0.1, 1.0, self.max_fetching_rate)} # get_meas_conditions(self.equipId, self.max_fetching_rate)


        for bank_setpoint in self.bank_setpoints:
            lower_curve              = bank_setpoint["lower_curve"]
            upper_curve              = bank_setpoint["upper_curve"] 
            period                   = bank_setpoint["period"]

            print(f"Bank Setpoint: {bank_setpoint['CV']} --> Lower Curve: {lower_curve} Upper Curve: {upper_curve} Period: {period}")

            if bank_setpoint["CV"] == SETPOINTS.TOPOIL_TEMPERATURE:
                curve                   =  measurements["topoil"][-period:]

            elif bank_setpoint["CV"] == SETPOINTS.HOTSPOT_TEMPERATURE:
                curve                   = measurements["hotspot"][-period:]

            elif bank_setpoint["CV"] == SETPOINTS.PU_LOAD:
                curve                    = measurements["puload"][-period:]
            
            elif bank_setpoint["CV"] == SETPOINTS.WINDING_TEMPERATURE:
                curve                    = measurements["winding"][-period:]

            print(f"Curve: {curve} Lower Curve: {lower_curve} Upper Curve: {upper_curve} Period: {period}")
            
            # Update the 'status' field with the result of the check_curve_within_range function  
            bank_setpoint.update({"status": self.check_curve_within_range(curve, lower_curve, upper_curve, period)})  
            print(f"Bank Setpoint: {bank_setpoint['CV']} --> Status: {bank_setpoint['status']}")
            
        actuation_power =   [u["Power"] for u in self.bank_setpoints if u["status"]==1] 

        if len(actuation_power) == 0:
            actuation_power = 0.0
        else: actuation_power = max(actuation_power)

        self.actuation_plan[self.step] = actuation_power
        print(f"Step: {self.step} --> Actuation Plan: {self.actuation_plan}")
        if(self.step == LOADCYCLE - 1):
            self.step = 0
            self.actuation_plan = np.zeros(LOADCYCLE)
            # save_actuation_plan(self.equipId, self.actuation_plan)
            print(f"Actuation Plan: {self.actuation_plan} --> Saved to DB")
    
        self.step += 1

        
    def run(self):
        """
        Run the controller.
        """
        self.base_initialize()
        base_controller_thread = RepeatEvery(int(self.max_fetching_rate), self.base_switch_cooling)
        base_controller_thread.start()

if __name__ == '__main__':

    equipId = "MPX-100M"
    base_controller = BaseController(equipId)
    base_controller.run()
    







