#!/usr/bin/python
from argparse import Action
from concurrent.futures import thread
import json
from mimetypes import init
from XUtility import *

import requests
import tensorflow as tf
from pathlib import Path
import os, sys
import random
from secrets import choice
from tkinter import N
from tokenize import Double
from urllib.error import HTTPError
from random import expovariate, gauss, randint, randrange, sample, seed, uniform
from configparser import ConfigParser
from matplotlib.lines import lineStyles
from matplotlib.patches import StepPatch
import numpy as np
import pandas as pd
import csv as csv
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt  
from XLoadProcessor import *
from XUtility import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from itertools import count

import gymnasium as gym
from gymnasium.spaces import MultiDiscrete, Discrete, Box
from typing import Optional, List, Dict, Tuple

from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.evaluation import evaluate_policy

from stable_baselines3.common.logger import TensorBoardOutputFormat
from stable_baselines3 import A2C
from scipy.integrate import simpson

# from utility import control, LoadProfile
import logging

# APIs URLs
os.environ["RATING_URL"]  = "http://localhost:5000/api/Transfo"  
os.environ["API_URL"]     = 'http://10.0.2.15:8000/jakobface'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models_dir= "cooling"
log_dir = "logs"
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# FAN MODEL EBM-PAPST  EC TRANSFORMER FANS O 990 Type W3G990 Motor M3G150-IF       

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


# if gpu is to be used
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

   
class CoolingEnvironment(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, equipId, num_episodes, cooling_config, opmode):
        super(CoolingEnvironment, self).__init__()
        self.equipId            = equipId 
        self.num_episodes       = num_episodes
        self.mode               = "REFERENCE"
        self.opmode             = opmode
        self.lprocess           = LoadProcessor(equipId, self.mode, opmode)
        self.ref_state          = self.lprocess.get_load_references()
        self.observation        = {}

        self.NUM_FANS           = cooling_config["num_fans"] 
        self.NUM_PUMPS          = cooling_config["num_pumps"] 
        self.FAN_POWERS         = cooling_config["fan_powers"]       
        self.PUMP_POWERS        = cooling_config["pump_powers"]       
        
        self.min_Power = 0.0 #  min(cooling_config["pump_powers"])  
        self.max_Power = 1.0 # self.NUM_PUMPS * max(cooling_config["pump_powers"]) + self.NUM_FANS * max(cooling_config["fan_powers"])
        print("\n\n\n================================================================")
        print(f"\n==Reference state to be assessed==\n {self.ref_state} - {self.NUM_FANS} - {self.NUM_PUMPS} - {len(self.FAN_POWERS)} - {len(self.PUMP_POWERS)}")

        self.uppamb         = self.ref_state['opamb'] 
        self.lowamb         = 0.5 * self.ref_state['opamb']

        self.uphot          = self.ref_state['ophotspot'] 
        self.lowhot         = self.ref_state['optopoil']

        self.uptop          = self.ref_state['optopoil']               
        self.lowtop         = self.ref_state['opbottom']

        self.upload         = self.ref_state['opload'] 
        self.lowload        = self.ref_state['obload']  
          
        self.lownoise       = 0.01*self.ref_state['opnoise'] 
        self.upnoise        = self.ref_state['opnoise']

        self.observation_space = Box(low=np.array([self.lowamb, self.lowtop, self.lowhot,  self.lowload, self.lownoise]), 
                                     high=np.array([self.uppamb, self.uptop, self.uphot, self.upload, self.upnoise]), dtype=np.float32)
        
        self.action_space      = Box(low=np.array([self.min_Power for _ in range(LOADCYCLE)]), 
                                     high=np.array([self.max_Power for _ in range(LOADCYCLE)]), dtype=np.float32)

    def _get_info(self):
        return { }

    def _get_obs(self):
        return self.observation_space.sample()
     

    def reward(self, mpcPower):
        ref_state                   = self.ref_state 
        mpc_curve_obs               = self.observation
        mpc_curve                   = self.lprocess.perform_curve_calculation(mpcPower, mpc_curve_obs)  

        # -----------------------------------------#
        #           Quadratic cost                 #
        # -----------------------------------------#
        ref_opload       = simpson(ref_state['opload'], dx=1)
        ref_optopoil     = simpson(ref_state['optopoil'], dx=1)
        ref_ophotspot    = simpson(ref_state['ophotspot'], dx=1)

        opload           = simpson(mpc_curve['opload'], dx=1)
        optopoil         = simpson(mpc_curve['optopoil'], dx=1)
        ophotspot        = simpson(mpc_curve['ophotspot'], dx=1)

        if opload > ref_opload: opload_reward = 0 
        else: opload_reward = 1
        if optopoil > ref_optopoil:optopoil_reward  = 0  
        else: optopoil_reward = 1
        if ophotspot > ref_ophotspot:ophotspot_reward = 0 
        else: ophotspot_reward = 1

        reward           = opload_reward + optopoil_reward + ophotspot_reward

        mpc_curve['opamb']      = np.clip(mpc_curve['opamb'], self.lowamb, self.uppamb) # [np.clip(mpc_curve['opamb'][i], self.lowamb[i], self.uppamb[i]) for i in range(LOADCYCLE)]
        mpc_curve['optopoil']   = np.clip(mpc_curve['optopoil'], self.lowtop, self.uptop)# [np.clip(mpc_curve['optopoil'][i], self.lowtop[i], self.uptop[i]) for i in range(LOADCYCLE)]
        mpc_curve['ophotspot']  = np.clip(mpc_curve['ophotspot'], self.lowhot, self.uphot) #[np.clip(mpc_curve['ophotspot'][i], self.lowhot[i], self.uphot[i]) for i in range(LOADCYCLE)]
        mpc_curve['opload']     = np.clip(mpc_curve['opload'], self.lowload, self.upload) # [np.clip(mpc_curve['opload'][i], self.lowload[i], self.upload[i]) for i in range(LOADCYCLE)]
        mpc_curve['opnoise']    = np.clip(mpc_curve['opnoise'], self.lownoise, self.upnoise) # [np.clip(mpc_curve['opnoise'][i], self.lownoise[i], self.upnoise[i]) for i in range(LOADCYCLE)]

        # Convert to a compatible Box object
        observation_space_values = np.array([
           mpc_curve['opamb'],
           mpc_curve['optopoil'],
           mpc_curve['ophotspot'],
           mpc_curve['opload'],
           mpc_curve['opnoise']
        ], dtype=np.float32)

        observation_space_box = Box(low=observation_space_values, high=observation_space_values, dtype=np.float32)
        next_state = observation_space_box.sample()

        # print("---------")
        # print(next_state)
        info             = self._get_info()
        return next_state, info, reward


    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        super().reset(seed=seed)
        self.env_step       = 0
        info                = self._get_info()
        observation         = self._get_obs()
        self.observation    = observation
        return observation, info

    def step(self, mpcAction):
        truncated = False
        terminated = False
        observation, info, reward = self.reward(mpcAction)
        self.observation = observation

        if self.env_step == LOADCYCLE:
            terminated = True
            truncated = True
            self.env_step = 0
        else:
            self.env_step += 1

        return observation, reward, terminated, truncated, info
    
    def render(self, mode='human'):
        pass

    def close (self):
        pass


class CoolingCallback(BaseCallback):
    """
    Custom callback for plotting additional values in tensorboard.
    """
    def __init__(self, log_dir, verbose=0):
        self.is_tb_set = False
        self.total_rewards   = 0.0
        self.reward_record        = []
        self.summary_result       = []
        self.local_reward         = []
        self.episode_count        = 0        
        self._log_freq            = 10  # log every 10 calls
        self.episode              = 0
        self.episode_call         = 5
        self.best_mean_reward     = -np.inf

        super(CoolingCallback, self).__init__(verbose)

        self.save_path            = os.path.join(log_dir, "cooling_agent_model")
       
    def _init_callback(self) -> None:
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    # def _on_training_start(self):
    #     self._log_freq       = 10  # log every 10 calls
    #     self.total_rewards   = 0.0
    #     output_formats = self.logger.output_formats
    #     self.tb_formatter = next(formatter for formatter in output_formats if isinstance(formatter, TensorBoardOutputFormat))

    def _on_step(self) -> bool:
        self.reward_record.append(self.locals['rewards'][0])                      
        if self.locals['dones'][0] == True:    # one episode has passed
            self.local_reward.append(sum(self.reward_record))
            local_reward    = np.mean(self.local_reward)
            std_reward      = np.std(self.local_reward)
            self.summary_result.append((self.episode_count, local_reward, std_reward))

            print("============sumary=======")
            print(self.summary_result)
            self.episode_count+=1

            self.reward_record.clear()
            if local_reward > self.best_mean_reward:
                self.best_mean_reward   = local_reward
                self.best_model         = self.model
                self.best_model_info    = self.locals['infos'][0]
                logger.info(f"Saving new best model to :{self.save_path} at timesteps: {self.num_timesteps} - Best mean reward: {local_reward:.2f} ")
                self.model.save(self.save_path)

        return True


class RLALearner():
       
    def __init__(self, equipId, num_episodes, cooling_config, opmode):  
        self.equipId            = equipId    
        self.episode_durations  = []
        self.num_episodes       = num_episodes       
        self.env                = CoolingEnvironment(equipId, num_episodes, cooling_config, opmode)
        self.model              = {}
        self.model_name         = f'{models_dir}/{equipId}-best_cooling_model.zip'
        self.cooling_config     = cooling_config

    
    def rla_learner(self):
        check_env(self.env)
        try :
            if(A2C.load(f'{models_dir}/{self.model_name}')): return
        except: 
            print("\n\n----------------------------------------------\n")
            print("   A2C Agent Training now in progress ... \n")
            print("----------------------------------------------\n\n")

            eval_callback = CoolingCallback(log_dir=models_dir, verbose=1)
            model = A2C("MlpPolicy", self.env, verbose=0)
            model.learn(total_timesteps=self.num_episodes, callback= eval_callback)
            # model.learn(total_timesteps=self.num_episodes, callback= eval_callback, reset_num_timesteps=False, tb_log_name=self.model_name)
            # mean_reward, std_reward     = evaluate_policy(model, 
            #                                               self.env, 
            #                                               n_eval_episodes        = num_episodes, 
            #                                               deterministic          = True, 
            #                                               render                 = False, 
            #                                               callback               = self._log_learning_callback, 
            #                                               return_episode_rewards = True)

            print("\n\n----------------------------------------------\n")
            print("   A2C Agent Training now complete   ...  \n")
            print("----------------------------------------------\n\n")
   

    def serving_real_cooling_plan (self):

        chd_model       = A2C.load(self.model_name)
        obs             = get_real_data()
        if obs.__len__() == 0:
            logger.error("No data found for serving mode. Please train the model first.") 
            return
        else:
            obs             = obs.to_numpy()
            obs             = np.array(obs).reshape((1, 5, LOADCYCLE))
            obs             = np.transpose(obs, (0, 2, 1))
            obs             = obs[0]
        action, _states = chd_model.predict(obs) 
        
        return action

    def serving_simulated_cooling_plan (self):

        env_parameters          = {}  
        observations            = []
        actions                 = []
   
        cooling_model           = A2C.load(self.model_name)
        cooling_env             = CoolingEnvironment(self.equipId, self.num_episodes, self.cooling_config)
        obs, _                  = cooling_env.reset()

        while True:
            action, _states = cooling_model.predict(obs)  
            obs, rewards, terminated, truncated, info = cooling_env.step(action)

            actions.append(action)
            observations.append(obs)
            if terminated or truncated:
                break


if __name__ == '__main__':

    equipId         = "Airdrie"
    num_episodes    = 1000
    opmode          = LoadType.NLEL

    # RLAController
    rla_cooling_model  = f'{models_dir}/{equipId}-best_cooling_model.zip'
    cooling_config     = {"num_fans": 8, "num_pumps": 2, "fan_powers":[1030, 1030, 1030, 1030, 1030, 1030, 1030, 1030], "pump_powers":[100, 100],
                          "fan_efficiency": 0.95, "pump_efficiency": 0.95, "fan_speed": [300, 300, 300, 300], 
                          "pump_speed": [100, 100], "fan_type": ["EC", "AC"], "pump_type": ["VFD", "VFD"], 
                          "fan_mode": ["ON", "OFF"], "pump_mode": ["ON", "OFF"]} #get_cooling_config()
    
    # meas_conditions = p_session.execute(select(self.meas_conditions)
    #                                             .where(self.meas_conditions.c.eqsernum == equipId)
    #                                             .where(

    coolrla_controller = RLALearner(equipId, num_episodes, cooling_config, opmode)

    rla_controller_mode = PredictionMode.LEARNING_MODE

    if rla_controller_mode == PredictionMode.SERVING_MODE_SIMULATED:

        if os.path.exists(rla_cooling_model):
            coolrla_controller.serving_simulated_cooling_plan()
        else:
            logger.error("No model found for serving mode. Please train the model first.") 

    elif rla_controller_mode == PredictionMode.SERVING_MODE_ROUTINE:

        if os.path.exists(rla_cooling_model):
           coolrla_controller.serving_real_cooling_plan()
        else:
            logger.error("No model found for serving mode. Please train the model first.")

    elif rla_controller_mode == PredictionMode.LEARNING_MODE:
        coolrla_controller.rla_learner()







