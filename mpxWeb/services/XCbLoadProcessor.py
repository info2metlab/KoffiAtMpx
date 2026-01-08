#!/usr/bin/python
from datetime import datetime
import json
import math
from pathlib import Path
import os, sys
from secrets import choice
from tokenize import Double
from urllib.error import HTTPError
from random import expovariate, gauss, randint, random, uniform
from configparser import ConfigParser
import numpy as np
import pandas as pd
import requests
import csv as csv
import time
import asyncio
from sqlalchemy import extract, func
from datetime import timedelta
    
from XUtility import *
from XPoFailure import *
from HelpSolverService import SolverService



# APIs URLs
os.environ["RATING_URL"]  = "http://localhost:5050/api/Transfo"
# os.environ["API_URL"] = 'http://10.0.2.15:8000/jakobface'

MAX_LOAD_PROFILE = 25
PERIODIC_USER = "User"


# LOAD ASSESSMENT CLASS
class LoadProcessor:


    def __init__(self, dynamic_cycle, states, seasonal_profile, loading_cases, simulation_time):

        self.cycle             = dynamic_cycle
        self.states            = states
        self.load_profile      = list()        
        self.loading_case      = loading_cases
        self.horizon           = simulation_time # in hours 
        self.sim_samples       = 100
        self.asset_vars        = pd.DataFrame()
        self.action_config     = {}
        self.pof_static_config = {}
        self.pof_dynamic_config= {}
        self.load_curve        = []
        self.ref_state         = []
        self.seasonal_profile = seasonal_profile        
        self.sim_samples                = 5
        self.horizon                    = simulation_time

        # Default Loading standard
        thermalStd = LoadingStd()
        thermalStd.pubDate = arrow.now().format("YYYY-MM-DD")
        thermalStd.pubName = LoadingStandard.IEEEG
        thermalStd.pubTitle= "Default IEEE Guide for Loading"
        self.thermalStd =  thermalStd
        # Initialize health_samples with one row per horizon step
        try:
            n_steps = int(self.horizon)
            if n_steps < 0:
                n_steps = 0
        except Exception:
            n_steps = 0

        self.health_samples = pd.DataFrame({
            'opyear'      :   np.arange(n_steps, dtype=int),
            'score'       :   np.zeros(n_steps, dtype=float),
            'score_min'   :   np.zeros(n_steps, dtype=float),
            'score_max'   :   np.zeros(n_steps, dtype=float),
            'score_std'   :   np.zeros(n_steps, dtype=float),
        })
        # - Safely derive the number of variables from self.states (handle None, dict, DataFrame).
        # - Initialize self.Z, self.a, self.b, self.sigma as simple float lists of length n_vars.
        # - Keep behavior compatible with later code that overwrites entries (e.g., self.Z[k] = np.zeros(...)).

        if isinstance(self.states, pd.DataFrame) and "varname" in self.states.columns:
            _var_names = list(self.states["varname"])
        elif isinstance(self.states, dict) and "varname" in self.states:
            _var_names = list(self.states["varname"])
        else:
            _var_names = []
        n_vars = len(_var_names)

        self.Z     = [0.0] * n_vars
        self.a     = [0.0] * n_vars
        self.b     = [0.0] * n_vars
        self.sigma = [0.0] * n_vars
        self.pof_static_config         = dict()
        self.pof_dynamic_config        = dict()
        self.dt                        = 1.0

    def time_to_minute(self, tm_str):

        if tm_str =="24:00": return 1440
        total_min = time.strptime(tm_str, "%H:%M")
        return (total_min.tm_hour)*60 + total_min.tm_min

    def init_load_from_csv(self):
        csv_profile = pd.read_csv(LOAD_DATA_FILE, usecols=[0, 1, 2, 3], names=['time','sumamb', 'sumpul','sumcool'], header=None)
        print(csv_profile)
        for index, row_data in csv_profile.iterrows():
            load_profile            = loadprofiles()
            load_profile.sessionId  = PERIODIC_USER
            load_profile.xfrmId     = "MPX-100M"
            load_profile.IsSelected = True
            load_profile.profileName= "PERIODIC"
            load_profile.time       = self.time_to_minute(row_data['time'])
            load_profile.sumamb     = row_data['sumamb']
            load_profile.sumpul     = row_data['sumpul']
            load_profile.sumcool    = row_data['sumcool']
            if load_profile.time % 60 == 0 :
                self.load_profile.append(load_profile)  
            # print("------------")
            # print ("load profile : ", load_profile.time, load_profile.sumamb, load_profile.sumpul, load_profile.sumcool)
   
    def init_static_config(self):
         
        with Session(p_engine) as p_session: 
            self.asset_vars   = pd.DataFrame(p_session.execute(select(datadictionaries)
                                                               .where(datadictionaries.c.groupname.in_(["nameplate", "diagnostic", "Intervention", "INTERVENTION", "Monitoring"]))).mappings())
           
            self.action_config = {

                "program":                        self.asset_vars.loc[self.asset_vars['varname']  ==  "main_program", 'value'].item(),
                "end_of_life_threshold":          self.asset_vars.loc[self.asset_vars['varname']  ==  "end_of_life_threshold", 'value'].item(),
                "routine_servicing_threshold":    self.asset_vars.loc[self.asset_vars['varname']  ==  "routine_servicing_threshold", 'value'].item(),
                "inspec_testing_threshold":       self.asset_vars.loc[self.asset_vars['varname']  ==  "inspec_testing_threshold", 'value'].item(),
                "condition_monitoring_threshold": self.asset_vars.loc[self.asset_vars['varname']  ==  "condition_monitoring_threshold", 'value'].item(),
                "minimum_repair_threshold":       self.asset_vars.loc[self.asset_vars['varname']  ==  "minimum_repair_threshold", 'value'].item(),
                "pm_replacement_threshold":       self.asset_vars.loc[self.asset_vars['varname']  ==  "pm_replacement_threshold", 'value'].item(),
                "cm_replacement_threshold":       self.asset_vars.loc[self.asset_vars['varname']  ==  "cm_replacement_threshold", 'value'].item(),
                "em_replacement_threshold":       self.asset_vars.loc[self.asset_vars['varname']  ==  "em_replacement_threshold", 'value'].item(),
                "refurbishment_threshold":        self.asset_vars.loc[self.asset_vars['varname']  ==  "refurbishment_threshold", 'value'].item(),
            }
            print(f"----actions--------")  
            print(self.action_config)

            self.pof_static_config =  {
                "transformer_type"              : self.asset_vars.loc[self.asset_vars['varname'] ==  "assettype", 'value'].item(), 
                "year_of_manufacture"           : self.asset_vars.loc[self.asset_vars['varname'] ==  "manyear", 'value'].item(),  
                "no_taps"                       : self.asset_vars.loc[self.asset_vars['varname'] ==  "notaps", 'value'].item(),
                "utilisation_pct"               : self.asset_vars.loc[self.asset_vars['varname'] ==  "puload", 'value'].item(),
                "placement"                     : self.asset_vars.loc[self.asset_vars['varname'] ==  "placement", 'value'].item(),
                "altitude_m"                    : self.asset_vars.loc[self.asset_vars['varname'] ==  "altitude", 'value'].item(), 
                "distance_from_coast_km"        : self.asset_vars.loc[self.asset_vars['varname'] ==  "coastaldist", 'value'].item(),
                "corrosion_category_index"      : self.asset_vars.loc[self.asset_vars['varname'] ==  "corrosion", 'value'].item(),
                # "age_tf"                        : asset_vars.Age,
                # "age_tc"                        : static_vars.loc[static_vars['Varname'] ==  "tapage", 'Value'].item(),
                "avg_daily_tap"                 : self.asset_vars.loc[self.asset_vars['varname'] ==  "avgtapops", 'value'].item(),
                "gridoredge"                    : self.asset_vars.loc[self.asset_vars['varname'] ==  "gridoredge", 'value'].item(),
                "reliability_factor"            : self.asset_vars.loc[self.asset_vars['varname'] ==  "reliability", 'value'].item(), 
                "k_value"                       : "0.000078",
                "c_value"                       : "1.087",
                "normal_expected_life_tf"       : self.asset_vars.loc[self.asset_vars['varname'] ==  "tflifetime", 'value'].item(), 
                "normal_expected_life_tc"       : self.asset_vars.loc[self.asset_vars['varname'] ==  "tclifetime", 'value'].item(), 
                "moisture"                      : "0.5",   # states.loc[states['VarName'] ==  "moisture", 'Value'].item(),
                "acidity"                       : "2.5",   # states.loc[states['VarName'] ==  "acidity", 'Value'].item(),
                "bd_strength"                   : "25",    # states.loc[states['VarName'] ==  "obreakdwn", 'Value'].item(),
                "hydrogen"                      : "1625",  # states.loc[states['VarName'] ==  "ah2ppm", 'Value'].item(),
                "methane"                       : "1400",  # states.loc[states['VarName'] ==  "ach4ppm", 'Value'].item(),
                "ethylene"                      : "1300",  # states.loc[states['VarName'] ==  "ac2h4ppm", 'Value'].item(),
                "ethane"                        : "1200",  # states.loc[states['VarName'] ==  "ac2h6ppm", 'Value'].item(),
                "acetylene"                     : "1100",  # states.loc[states['VarName'] ==  "ac2h2ppm", 'Value'].item(),
                "hydrogen_pre"                  : "1200",  # states.loc[states['VarName'] ==  "preh2ppm", 'Value'].item(),
                "methane_pre"                   : "1300",  # states.loc[states['VarName'] ==  "prech4ppm", 'Value'].item(),
                "ethylene_pre"                  : "1100",  # states.loc[states['VarName'] ==  "prec2h4ppm", 'Value'].item(),
                "ethane_pre"                    : "900",  # states.loc[states['VarName'] ==  "prec2h6ppm", 'Value'].item(),
                "acetylene_pre"                 : "800",  # states.loc[states['VarName'] ==  "prec2h2ppm", 'Value'].item(),
                "furfuraldehyde"                : "700",  # states.loc[states['VarName'] ==  "fural", 'Value'].item()
            }
                
        print(f"----pof_static_config--------")
        print(self.pof_static_config)

    def scale_seasonal_load(self, scale=1.0, load_col=None) -> pd.DataFrame:
        """
        Multiply the load field in `self.seasonal_profile` by the given scale factor.
        Returns a new DataFrame; original is not mutated.
        If `load_col` is None, it tries 'puload', 'sumpul', then 'load'.
        """
        df = self.seasonal_profile.copy() if isinstance(self.seasonal_profile, pd.DataFrame) else pd.DataFrame()
        if df.empty:
            return df
            
        target_col = None
        if load_col and load_col in df.columns:
            target_col = load_col
        else:
            for c in ('puload', 'sumpul', 'load'):
                if c in df.columns:
                    target_col = c
                    break

        if not target_col:
            return df

        df[target_col] = pd.to_numeric(df[target_col], errors='coerce').fillna(0.0) * float(scale)

        return df

    def init_dynamic_config(self):
        self.pof_dynamic_config = {     
            "age_tf"                        : self.asset_vars.loc[self.asset_vars['varname'] ==  "age", 'value'].item(),
            "age_tc"                        : self.asset_vars.loc[self.asset_vars['varname'] ==  "tapage", 'value'].item(),
            "partial_discharge_tf"          : self.asset_vars.loc[self.asset_vars['varname'] ==  "partial_discharge_tf", 'value'].item(),
            "partial_discharge_tc"          : self.asset_vars.loc[self.asset_vars['varname'] ==  "partial_discharge_tc", 'value'].item(), 
            "temperature_reading"           : self.asset_vars.loc[self.asset_vars['varname'] ==  "temperature_reading", 'value'].item(),
            "main_tank"                     : self.asset_vars.loc[self.asset_vars['varname'] ==  "main_tank", 'value'].item(),
            "coolers_radiator"              : self.asset_vars.loc[self.asset_vars['varname'] ==  "coolers_radiator", 'value'].item(),
            "bushings"                      : self.asset_vars.loc[self.asset_vars['varname'] ==  "bushings", 'value'].item(),
            "kiosk"                         : self.asset_vars.loc[self.asset_vars['varname'] ==  "kiosk", 'value'].item(),
            "cable_boxes"                   : self.asset_vars.loc[self.asset_vars['varname'] ==  "cable_boxes", 'value'].item(),
            "external_tap"                  : self.asset_vars.loc[self.asset_vars['varname'] ==  "external_tap", 'value'].item(),
            "internal_tap"                  : self.asset_vars.loc[self.asset_vars['varname'] ==  "internal_tap", 'value'].item(),
            "mechnism_cond"                 : self.asset_vars.loc[self.asset_vars['varname'] ==  "mechnism_cond", 'value'].item(),
            "diverter_contacts"             : self.asset_vars.loc[self.asset_vars['varname'] ==  "diverter_contacts", 'value'].item(),
            "diverter_braids"               : self.asset_vars.loc[self.asset_vars['varname'] ==  "diverter_braids", 'value'].item(),
            # "dissolved_gas"                 : states.loc[states['VarName'] ==  "dissolved_gas", 'value'].item(),
            # "oil_quality"                   : states.loc[states['VarName'] ==  "oil_quality", 'value'].item()
        }
        print(f"----pof_dynamic_config--------")
        print(self.pof_dynamic_config)

    def get_load_samp (self):
            
        try:
            response = requests.post(os.environ["RATING_URL"]  + '/getloadsmp', data={'equipId':self.equipId})                         
            df = pd.DataFrame(response.json())
            # print("Retrieved load profile from database\n", df)
            samples = df.iloc[-1]
            self.samples = np.array([pd.to_numeric(samples['topoil']), \
                          max(pd.to_numeric(samples['hotspotx']), 
                              pd.to_numeric(samples['hotspoty']), 
                              pd.to_numeric(samples['hotspotz'])), \
                          max(pd.to_numeric(samples['puloadx']), 
                              pd.to_numeric(samples['puloady']), 
                              pd.to_numeric(samples['puloadz']))])

            df.reset_index()
            rec_count  = 0
            self.load_profile.clear()
            while rec_count < LOADCYCLE :
                load_profile            = loadprofiles()
                load_profile.sessionId  = PERIODIC_USER
                load_profile.xfrmId     = "MPX-100M"
                load_profile.IsSelected = True
                load_profile.profileName= "PERIODIC"
                load_profile.time       = str(rec_count*60)
                load_profile.sumamb     = str(df.iloc[rec_count]['ambient']) # str((pd.to_numeric(df['ambient'])))
                load_profile.sumpul     = str(max(pd.to_numeric(df.iloc[rec_count]['puloadx']), 
                                                  pd.to_numeric(df.iloc[rec_count]['puloady']), 
                                                  pd.to_numeric(df.iloc[rec_count]['puloadz'])
                                            ))

                load_profile.sumcool    = "1000"
                self.load_profile.append(load_profile)
                rec_count = rec_count + 1

            # print("\n\n\n================================================================")
            # print("\n==Reformatted load profile to be assessed==\n", json.dumps([obj.__dict__ for obj in self.load_profile], default=str)) 
            # print("================================================================\n\n\n")

        except HTTPError as http_err:
            print(f'HTTP error occured: {http_err}')
        except ConnectionError as errc:
            print(f'Connection error occured: {errc}')
        except TimeoutError as errt:
            print(f'Timeout error occured: {errt}')
        except requests.RequestException as erreq:
            print(f'Timeout error occured: {erreq}')
        except Exception as err:
            print(f'HTTP error occured: {err}')

    def perform_curve_calculation (self, mpcPower=[], mpc_curve_obs=[]):

            rla_all_state               =  pd.DataFrame(mpc_curve_obs.transpose(), columns=['opamb','optopoil','ophotspot','opload', 'opnoise'])
            rla_all_state.reset_index()       
            self.load_profile.clear()
            print("=======mpcPower ======")
            print(mpcPower)

            # dynamic load profile
            for index, row_data in rla_all_state.iterrows():
                load_profile            = LoadProfile()
                load_profile.sessionId  = PERIODIC_USER
                load_profile.xfrmId     = "MPX-100M"
                load_profile.IsSelected = True
                load_profile.profileName= "PERIODIC"

                load_profile.time       = str(index * 60)
                load_profile.sumamb     = str(rla_all_state['opamb'][index])
                load_profile.sumpul     = str(rla_all_state['opload'][index])
                load_profile.sumcool    = str(mpcPower[index])
                self.load_profile.append(load_profile)

            # print(json.dumps([obj.__dict__ for obj in self.load_profile]))
            mpcArgs = {
                "xfrmId": "MPX-100", 
                "sessionId":PERIODIC_USER, 
                "mpcProfile": [obj.__dict__ for obj in self.load_profile],
                "mpcScenario": self.loading_case.__dict__,
            }  
            
            try:
                response = requests.post(os.environ["RATING_URL"]  +'/DoRealForecast',  data = json.dumps(mpcArgs)) 
                mpc_results = response.json() 
                
                if mpc_results.__len__():
                    nameplate   = mpc_results["NamePlateResults"]
                    thermal     = mpc_results["ThermalResults"] 
                    df       = pd.DataFrame(thermal)
                    df2      = df[["time", "sumamb", "sumpul", "IEEEGBOT", "IEEEGTOT", "IEEEGHST", "IEEEGPULoad"]]

                    df2.rename(columns={"time":"otime", "sumamb":"opamb", "sumpul":"obload", "IEEEGBOT":"opbottom", 
                                        "IEEEGTOT":"optopoil", "IEEEGHST":"ophotspot", "IEEEGPULoad":"opload"}, inplace=True)
                    print("=======calc observation ======")
                    print(df2)
                    if df2.__len__():
                        df2['otime']        = df2['otime'].astype('float')
                        df2['opamb']        = df2['opamb'].astype('float')
                        df2['optopoil']     = df2['optopoil'].astype('float')
                        df2['ophotspot']    = df2['ophotspot'].astype('float')
                        df2['opload']       = df2['opload'].astype('float')
                        df2['opbottom']     = df2['opbottom'].astype('float')
                        df2['obload']       = df2['obload'].astype('float')
                        df2['opnoise']      = create_random_step_curve(df2.__len__(), 3)     
                        df2                 = df2.sort_values(['otime'])
                    
                    return df2

            except HTTPError as http_err:
                print(f'HTTP error occured: {http_err}')
            except ConnectionError as errc:
                print(f'Connection error occured: {errc}')
            except TimeoutError as errt:
                print(f'Timeout error occured: {errt}')
            except requests.RequestException as erreq:
                print(f'Timeout error occured: {erreq}')
            except Exception as err:
                print(f'HTTP error occured: {err}')

    async def perform_load_diagnostic (self, mpcPof, loading_case):
                        
            if self.load_profile.__len__() < MAX_LOAD_PROFILE :
                # print(f'Load profile length not adequate :{self.load_profile}')
                return
            # Simple dict-style arguments for solver (easier to serialize/test)
            mpc_args = mpcArgs()
            mpc_args.xfrmId = "MPX-100M"
            mpc_args.sessionId = PERIODIC_USER
            mpc_args.mpcPof = mpcPof
            mpc_args.loadProfile = self.load_profile
            mpc_args.loadingCase = loading_case
            # {
            #     "xfrmId": "MPX-100M",
            #     "sessionId": PERIODIC_USER,
            #     "mpcPof": mpcPof,
            #     # convert LoadProfile objects to plain dicts for downstream use
            #     "loadProfile": [obj.__dict__ for obj in self.load_profile],
            #     # loadingCase may be an object; pass plain dict when possible
            #     "loadingCase": loading_case.__dict__ if hasattr(loading_case, "__dict__") else loading_case,
            # }
            # print(f"----seasonal load profile at step : ----{self.asset_id}--\n--")
            # print( loading_case.__dict__)
            # print("-------====--------")
            # [print(f"{load_profile.time} {load_profile.sumamb} {load_profile.sumpul} {load_profile.sumcool}") for load_profile in self.load_profile]

            try:

                solver_service       = SolverService(self.thermalStd) 
                self.mpc_results     = await solver_service.solve_dynamic_plate(mpc_args)
                # response = requests.post(os.environ["RATING_URL"]  +'/DoRealForecast',  data = json.dumps(mpcArgs)) 
                # print("======================\n", self.mpc_results)
                # self.mpc_results = response.json()           
                df_thermal = pd.DataFrame()
                df_nameplate = pd.DataFrame()

                if self.mpc_results:
                    nameplate = self.mpc_results.name_plate_results
                    thermal   = self.mpc_results.thermal_results
                    print("=======thermal results ======")
                    df = pd.DataFrame(thermal)                                        
                    if not df.empty:
                        thermal_cols_map = {
                            "LoadType":    "loadtype",
                            "time":        "otime",
                            "sumamb":      "opamb",
                            "sumpul":      "obload",
                            "IEEEGLOL":    "oplife",
                            "IEEEGBOT":    "opbottom",
                            "IEEEGTOT":    "optopoil",
                            "IEEEGHST":    "ophotspot",
                            "IEEEGPULoad": "opload",
                            "IEEEGMargin": "margin"
                        }
                        available_thermal = {src: dst for src, dst in thermal_cols_map.items() if src in df.columns}
                        if available_thermal:
                            df_thermal = df.loc[:, list(available_thermal.keys())].copy().rename(columns=available_thermal)
                            for col in ["otime", "opamb", "obload", "oplife", "opbottom", "optopoil", "ophotspot", "opload", "margin"]:
                                if col in df_thermal.columns:
                                    df_thermal[col] = pd.to_numeric(df_thermal[col], errors="coerce")
                            if "otime" in df_thermal.columns:
                                df_thermal = df_thermal.sort_values(["otime"])
                        print(df_thermal)
                    # Nameplate results
                    df_n = pd.DataFrame(nameplate)
                    print(f"=======nameplate results ======\n{df_n}")
                    if not df_n.empty:
                        nameplate_cols_map = {
                            "LoadType":         "loadtype",
                            "IEEEGPeakTopOil":  "uptopoil",
                            "IEEEGPeakHotSpot": "uphotspot",
                            "IEEEGPeakPUL":     "upload",
                            "IEEEGPeakBottom":  "upbottom",
                            "IEEEGPeakLoL":     "uplife",
                            "IEEEGttpTOT":      "ttptop",
                            "IEEEGttpHST":      "ttphot",
                            "IEEEGttpMVA":      "ttpmva",
                            "IEEEGMargin":      "margin"
                        }
                        available_nameplate = {src: dst for src, dst in nameplate_cols_map.items() if src in df_n.columns}
                        if available_nameplate:
                            df_nameplate = df_n.loc[:, list(available_nameplate.keys())].copy().rename(columns=nameplate_cols_map)
                            for col in ["uptopoil", "uphotspot", "upload", "upbottom", "uplife", "ttptop", "ttphot", "ttpmva", "margin"]:
                                df_nameplate[col] = pd.to_numeric(df_nameplate[col], errors="coerce")

                return df_thermal, df_nameplate
            except TimeoutError as errt:
                print(f'Timeout error occured: {errt}')
            except Exception as err:
                print(f'HTTP error occured: {err}')

    def clear_load_result(self):
        try:
            requests.post(os.environ["RATING_URL"] + '/clearesults', data={})   
        except Exception as err:
            print(f'HTTP error occured: {err}')                       

    def save_load_result (self):
        if self.mpc_results.__len__():
            # print("\n======= Getting New loading assessment results =====")
            # print("======= nameplate =====", self.mpc_results["NamePlateResults"])
            # print("\n\n")
            # print("======= thermal =====", self.mpc_results["ThermalResults"])

            nameplate   = self.mpc_results["NamePlateResults"]
            thermal     = self.mpc_results["ThermalResults"] 
            load_curve  = []

            for p in nameplate:
                upper_load_item           = loadresults()
                upper_load_item.sampdate  = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") 
                upper_load_item.uptopoil  = str(p["IEEEGPeakTopOil"])
                upper_load_item.uphotspot = str(p["IEEEGPeakHotSpot"])
                upper_load_item.upload    = str(p["IEEEGPeakPUL"])
                upper_load_item.upbottom  = str(p["IEEEGPeakBottom"])
                upper_load_item.uplife    = str(p["IEEEGPeakLoL"])
                upper_load_item.ttptop    = str(p["IEEEGttpTOT"])
                upper_load_item.ttphot    = str(p["IEEEGttpHST"])
                upper_load_item.ttpmva    = str(p["IEEEGttpMVA"])
                upper_load_item.upsimu    = self.mode
                try:
                    response = requests.post(os.environ["RATING_URL"] + '/saveloadres', data=json.dumps(upper_load_item.__dict__, default=str))                          
                    data = response.json()
                    # print("New upper loading results  =====", data)
                except HTTPError as http_err:
                    print(f'HTTP error occured: {http_err}')
                except ConnectionError as errc:
                    print(f'Connection error occured: {errc}')
                except TimeoutError as errt:
                    print(f'Timeout error occured: {errt}')
                except requests.RequestException as erreq:
                    print(f'Timeout error occured: {erreq}')
                except Exception as err:
                    print(f'HTTP error occured: {err}')

            for q in thermal:
                load_cur_item           = loadcurves()
                load_cur_item.sampdate  = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") 
                load_cur_item.otime     = str(q["time"])
                load_cur_item.opamb     = str(q["sumamb"])
                load_cur_item.obload    = str(q["sumpul"])
                load_cur_item.optopoil  = str(q["IEEEGTOT"])
                load_cur_item.ophotspot = str(q["IEEEGHST"])
                load_cur_item.opload    = str(q["IEEEGPULoad"])
                load_cur_item.opbottom  = str(q["IEEEGBOT"])
                load_cur_item.oplife    = str(q["IEEEGLOL"])
                load_cur_item.opage     = str(q["IEEEGBOT"])  
                load_cur_item.osimu     = self.mode         
                load_curve.append(load_cur_item)

                try:
                    response = requests.post(os.environ["RATING_URL"] + '/saveloadcurve', data=json.dumps(load_cur_item.__dict__, default=str))                          
                    data = response.json()
                    # print("New loading curve posted =====", data)
                except HTTPError as http_err:
                    print(f'HTTP error occured: {http_err}')
                except ConnectionError as errc:
                    print(f'Connection error occured: {errc}')
                except TimeoutError as errt:
                    print(f'Timeout error occured: {errt}')
                except requests.RequestException as erreq:
                    print(f'Timeout error occured: {erreq}')
                except Exception as err:
                    print(f'HTTP error occured: {err}')

            self.load_curve = pd.DataFrame([obj.__dict__ for obj in load_curve])

    def perform_load_assessment(self, mpcPof, mode = LOADING.SEASONAL.value):

        if mode == LOADING.REFERENCE.value:
            self.init_load_from_csv()
        df_thermal_all = pd.DataFrame()
        df_nameplate_all = pd.DataFrame()
        # self.clear_load_result()
        for loading_case_item in self.loading_case:
            print(f"Performing load assessment for loading case: {loading_case_item.LoadType}")
            loading_case                 = LoadingCase()
            loading_case.sessionId       = PERIODIC_USER
            loading_case.xfrmId          = "MPX-100M"
            loading_case.LoadType        = loading_case_item.LoadType 
            loading_case.LoLLimit        = float(loading_case_item.LoLLimit)
            loading_case.BubblingLimit   = float(loading_case_item.BubblingLimit)
            loading_case.BeginOverTime   = float(loading_case_item.BeginOverTime)
            loading_case.EndOverTime     = float(loading_case_item.EndOverTime)
            loading_case.InsLifeExp      = float(loading_case_item.InsLifeExp)
            loading_case.OxyContent      = float(loading_case_item.OxyContent)
            loading_case.MoisContent     = float(loading_case_item.MoisContent)
            loading_case.HSPressure      = float(loading_case_item.HSPressure)
            loading_case.LtcPosition     = int(loading_case_item.LtcPosition)
            loading_case.LtcAmpacity     = float(loading_case_item.LtcAmpacity)
            loading_case.OptimError      = float(loading_case_item.OptimError)
            loading_case.Scheduled       = loading_case_item.Scheduled
            loading_case.CoolPWLimit     = float(loading_case_item.CoolPWLimit)
            loading_case.HotSpotLimit    = float(loading_case_item.HotSpotLimit)
            loading_case.TopOilLimit     = float(loading_case_item.TopOilLimit)
            loading_case.PULLimit        = float(loading_case_item.PULLimit)

            res = asyncio.run(self.perform_load_diagnostic(mpcPof, loading_case))
            if res:
                df_thermal, df_nameplate = res
            else:
                df_thermal, df_nameplate = pd.DataFrame(), pd.DataFrame()
            df_nameplate_all = pd.concat([df_nameplate_all, df_nameplate], ignore_index=True)
            df_thermal_all   = pd.concat([df_thermal_all, df_thermal], ignore_index=True)
        # print("--------------Completed load assessment----------------")
        # print(df_thermal_all)
        return df_thermal_all, df_nameplate_all

    def get_load_references(self):
        self.init_load_from_csv()
        self.perform_load_diagnostic(0.0)
        # self.save_load_result() 
        mpc_results = self.mpc_results    
        if mpc_results.__len__():
            nameplate   = mpc_results["NamePlateResults"]
            thermal     = mpc_results["ThermalResults"] 
            df       = pd.DataFrame(thermal)
            df2      = df[["time", "sumamb", "sumpul", "IEEEGBOT", "IEEEGTOT", "IEEEGHST", "IEEEGPULoad"]]

            df2.rename(columns={"time":"otime", "sumamb":"opamb", "sumpul":"obload", "IEEEGBOT":"opbottom", 
                                "IEEEGTOT":"optopoil", "IEEEGHST":"ophotspot", "IEEEGPULoad":"opload"}, inplace=True)
            print("=======calc observation ======")
            print(df2)
            if df2.__len__():
                df2['otime']        = df2['otime'].astype('float')
                df2['opamb']        = df2['opamb'].astype('float')
                df2['optopoil']     = df2['optopoil'].astype('float')
                df2['ophotspot']    = df2['ophotspot'].astype('float')
                df2['opload']       = df2['opload'].astype('float')
                df['opbottom']      = df2['opbottom'].astype('float')
                df2['obload']       = df2['obload'].astype('float')
                df2["opnoise"]      = create_random_step_curve(df2.__len__(), 3)        
                df2                 = df2.sort_values(['otime'])
            return df2

    # =========================
    # Load Forecasting Actions
    # =========================

    def xfrm_reactive_load_forecast(self, step):
                  
         end_of_life_threshold                       = float(self.action_config["end_of_life_threshold"]) 
         tapage                                      = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "tapage", 'value'].item())
         age_tf                                      = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "age", 'value'].item()) 
                  
         self.pof_dynamic_config["age_tf" ]          = age_tf
         self.pof_dynamic_config["age_tc" ]          = tapage + step
         pof_vars                                    = self.pof_static_config | self.pof_dynamic_config
                  

         pof                                         = PoF(pof_vars)
                  
         print("==========================================")
         print(f"Reactive Maintenance - - pof:{pof_vars}")
         print("==========================================")
         current_health_score, current_pof           = pof.pof_transformer()
         df_thermal, df_nameplate                    = self.perform_load_assessment(current_pof, LOADING.SEASONAL.value)

         return current_health_score, df_thermal, df_nameplate
     
    def xfrm_preventative_load_forecast(self, step):
         end_of_life_threshold                       = float(self.action_config["end_of_life_threshold"]) 
         tapage                                      = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "tapage", 'value'].item())
         age_tf                                      = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "age", 'value'].item()) 
                  
         self.pof_dynamic_config["age_tf" ]          = age_tf
         self.pof_dynamic_config["age_tc" ]          = tapage + step
                  
         pof_vars                                    = self.pof_static_config | self.pof_dynamic_config
         pof                                         = PoF(self.utility, self.asset_id,  pof_vars)
         current_health_score, current_pof           = pof.pof_transformer()
         df_thermal, df_nameplate                    = self.perform_load_assessment(current_pof, LOADING.SEASONAL.value)

         if current_health_score >  float(self.action_config["pm_replacement_threshold"]) and current_health_score <= float(self.action_config["end_of_life_threshold"]):
            # MaintAction.PM_REPLACEMENT.value: 
                 for i in range(len(self.states["varname"])):
                     self.Z[i][step] = uniform(0.1, 0.3)

         elif current_health_score >  float(self.action_config["routine_servicing_threshold"]) and current_health_score <= float(self.action_config["pm_replacement_threshold"]):
            # perform maintenance MaintAction.ROUTINE_SERVICING.value:
            for i in range(len(self.states["varname"])):
                self.Z[i][step]                  = uniform(0.5, 0.6) 

         elif current_health_score >  float(self.action_config["minimum_repair_threshold"]) and current_health_score <= float(self.action_config["pm_replacement_threshold"]): 
            # perform maintenance MaintAction.MINIMUM_REPAIR.value:
            for i in range(len(self.states["varname"])):
                self.Z[i][step]                  = uniform(0.5, 0.6) 
         
         else:
             print("==========================================")
             print("No Preventive maintenance action performed - health_score : {current_health_score} - pof:{current_pof}");
             print("=========================================="); 

         return current_health_score, df_thermal, df_nameplate

    def xfrm_condb_load_forecast(self, step):
         end_of_life_threshold                   = float(self.action_config["end_of_life_threshold"]) 
         tapage                                  = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "tapage", 'value'].item())
         age_tf                                  = int(self.asset_vars.loc[self.asset_vars['varname'] ==  "age", 'value'].item()) 
                  
         self.pof_dynamic_config["age_tf" ]      = age_tf
         self.pof_dynamic_config["age_tc" ]      = tapage + step
         pof_vars                                = self.pof_static_config | self.pof_dynamic_config
         pof                                     =  PoF(self.utility, self.asset_id,  pof_vars)
         current_health_score, current_pof       =  pof.pof_transformer()
         df_thermal, df_nameplate                = self.perform_load_assessment(current_pof, LOADING.SEASONAL.value)     
         
         if current_health_score >= float(self.action_config["cm_replacement_threshold"]) and current_health_score <= float(self.action_config["end_of_life_threshold"]):
            # perform maintenance MaintAction.CM_REPLACEMENT.value
            for i in range(len(self.states["varname"])):
                self.Z[i][step]                  = uniform(0.1, 0.25) 

         elif current_health_score >  float(self.action_config["routine_servicing_threshold"]) and current_health_score <= float(self.action_config["cm_replacement_threshold"]):
            # perform maintenance MaintAction.ROUTINE_SERVICING.value:
            for i in range(len(self.states["varname"])):
                self.Z[i][step]                  = uniform(0.5, 0.6) 

         elif current_health_score >  float(self.action_config["minimum_repair_threshold"]) and current_health_score <= float(self.action_config["routine_servicing_threshold"]): 
            # perform maintenance MaintAction.MINIMUM_REPAIR.value:
            for i in range(len(self.states["varname"])):
                self.Z[i][step]                  = uniform(0.5, 0.6) 
         else:
             print("===============================================");
             print(f"No Condition-based Maintenance action performed - health_score : {current_health_score} - pof:{current_pof}");
             print("===============================================");

         return current_health_score, df_thermal, df_nameplate

    def generate_config(self, step):
        var_name        = self.states["varname"]
        for i in range(len(var_name)):
            self.Z[i][step]                        = self.Z[i][step - 1] +  ((self.a[i] * (self.dt)**self.b[i])/(9.5)) + (self.sigma[i]/9.5) * np.sqrt(self.dt) * normal()
            self.pof_dynamic_config['time']        = step  
            self.pof_dynamic_config[var_name[i]]   = round(np.clip(self.Z[i][step], 0.0, 10.0), 3)
            # Scale seasonal profile load and store as plain records for downstream use
            scale = 1.0 + self.growthRate * step
            # scale = getattr(self, "load_scale", 1.0)
        seasonal_load = self.scale_seasonal_load(scale)
          
        def _to_minutes(val):
            if isinstance(val, str):
                return self.time_to_minute(val)
            try:
                v = float(val)
            except Exception:
                return 0
            return int(v * 60) if 0 <= v <= 24 else int(v)

        def _num(x, default=0.0):
            try:
                v = float(x)
                return v if math.isfinite(v) else default
            except Exception:
                return default
                
        self.load_profile.clear()
        try:
            seasonal_load['hour']     = seasonal_load['hour'].apply(_to_minutes)
            seasonal_load['ambient']  = seasonal_load['ambient'].apply(lambda x: _num(x, 0.0))
            seasonal_load['puload']   = seasonal_load['puload'].apply(lambda x: _num(x, 0.0))
            seasonal_load['cooling']  = seasonal_load['cooling'].apply(lambda x: _num(x, 1000.0))
            for row in seasonal_load.itertuples(index=False):
                time_min = getattr(row, 'hour', 0)
                amb      = getattr(row, 'ambient', 0.0)
                pul      = getattr(row, 'puload', 0.0)
                cool     = getattr(row, 'cooling', 1000.0)

                load_profile                 = LoadProfile()
                load_profile.sessionId       = PERIODIC_USER
                load_profile.xfrmId          = "MPX-100M"
                load_profile.IsSelected      = True
                load_profile.profileName     = "PERIODIC"
                load_profile.time            = time_min
                load_profile.sumamb          = amb
                load_profile.sumpul          = pul
                load_profile.sumcool         = cool

                if int(time_min) % 60 == 0:                            
                    self.load_profile.append(load_profile)

        except Exception as e:
            print(f"Error processing seasonal load data: {e}")
            return


    def compute_replication_stats(self, nameplate_samples, thermal_samples):
        """
        Aggregate replication samples and compute summary statistics.

        Returns:
            - nameplate_stats_list: list of LoadDistro objects aggregated by ['asset_id','load_type','opyear'] (means)
            - thermal_stats_df: DataFrame aggregated by ['asset_id','load_type','opyear','otime'] with mean/min/max/std/count
        """
        # helpers
        def _to_num_safe(v, default=np.nan):
            try:
                if isinstance(v, (list, tuple, np.ndarray, pd.Series)):
                    arr = np.asarray(v, dtype=float)
                    arr = arr[np.isfinite(arr)]
                    return float(np.mean(arr)) if arr.size > 0 else default
                x = float(v)
                return x if np.isfinite(x) else default
            except Exception:
                return default

        def _obj_to_row(o):
            if o is None:
                return {}
            if isinstance(o, dict):
                return {k: v for k, v in o.items() if not (isinstance(k, str) and k.startswith("_"))}
            d = getattr(o, "__dict__", None)
            if isinstance(d, dict):
                return {k: v for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))}
            return {}

        # --- Nameplate aggregation ---
        # Build DataFrame from nameplate_samples (list of objects/dicts) or pass through if it's already a DataFrame
        if isinstance(nameplate_samples, pd.DataFrame):
            np_df = nameplate_samples.copy()
        else:
            rows = []
            if nameplate_samples:
                for s in nameplate_samples:
                    rows.append(_obj_to_row(s))
            np_df = pd.DataFrame(rows)

        nameplate_stats_list = []
        if not np_df.empty:
            # normalize column names if expected names use different casing
            # ensure opyear numeric
            if 'opyear' in np_df.columns:
                np_df['opyear'] = pd.to_numeric(np_df['opyear'], errors='coerce')

            # Identify metric columns starting with react_/prev_/condb_
            metric_prefixes = ('react_', 'prev_', 'condb_')
            metric_cols = [c for c in np_df.columns if any(c.startswith(pref) for pref in metric_prefixes)]
            group_cols = [c for c in ('asset_id', 'load_type', 'opyear') if c in np_df.columns]
            if group_cols and metric_cols:
                # coerce numeric metrics
                for c in metric_cols:
                    np_df[c] = pd.to_numeric(np_df[c], errors='coerce')

                # compute means
                grouped = np_df.groupby(group_cols, dropna=False)
                mean_df = grouped[metric_cols].mean().reset_index()

                # convert each row to loaddistros
                for row in mean_df.itertuples(index=False):
                    ld = loaddistros()
                    # safe set attributes if columns exist
                    for gc in group_cols:
                        try:
                            setattr(ld, gc, getattr(row, gc))
                        except Exception:
                            try:
                                setattr(ld, gc, row[mean_df.columns.get_loc(gc)])
                            except Exception:
                                pass
                    for mc in metric_cols:
                        val = getattr(row, mc)
                        try:
                            setattr(ld, mc, float(val) if np.isfinite(val) else 0.0)
                        except Exception:
                            setattr(ld, mc, 0.0)
                    nameplate_stats_list.append(ld)

        # --- Thermal aggregation ---
        if isinstance(thermal_samples, pd.DataFrame):
            th_df = thermal_samples.copy()
        else:
            # if thermal_samples is a list of dicts/objects, convert
            rows = []
            if thermal_samples:
                if isinstance(thermal_samples, (list, tuple)):
                    for s in thermal_samples:
                        rows.append(_obj_to_row(s))
            th_df = pd.DataFrame(rows)

        thermal_stats_df = pd.DataFrame()
        if not th_df.empty:
            # Ensure required columns exist and coerce numeric
            for c in ('opyear', 'otime'):
                if c in th_df.columns:
                    th_df[c] = pd.to_numeric(th_df[c], errors='coerce')

            metric_prefixes = ('react_', 'prev_', 'condb_')
            metric_cols_th = [c for c in th_df.columns if any(c.startswith(pref) for pref in metric_prefixes)]

            group_keys = [k for k in ('load_type', 'opyear', 'otime') if k in th_df.columns]
            if group_keys and metric_cols_th:
                # coerce numeric metrics
                for c in metric_cols_th:
                    th_df[c] = pd.to_numeric(th_df[c], errors='coerce')

                # aggregate: mean/min/max/std and count
                aggs = {}
                for c in metric_cols_th:
                    aggs[c + '_mean'] = (c, 'mean')
                    aggs[c + '_min'] = (c, 'min')
                    aggs[c + '_max'] = (c, 'max')
                    aggs[c + '_std'] = (c, 'std')

                thermal_stats_df = th_df.groupby(group_keys, dropna=False).agg(**aggs).reset_index()
                # sample counts
                counts = th_df.groupby(group_keys, dropna=False).size().reset_index(name='samples')
                thermal_stats_df = thermal_stats_df.merge(counts, on=group_keys, how='left')

        # --- Health samples aggregation and merge into self.health_samples ---
        try:
            if not getattr(self, 'health_samples', pd.DataFrame()).empty:
                hs = self.health_samples.copy()
                if 'opyear' in hs.columns:
                    hs['opyear'] = pd.to_numeric(hs['opyear'], errors='coerce').fillna(0).astype(int)

                health_metrics = ['score']
                present_metrics = [m for m in health_metrics if m in hs.columns]

                if present_metrics:
                    # compute per-opyear stats using groupby -> will produce a MultiIndex columns, flatten them
                    gb = hs.groupby('opyear', sort=True)[present_metrics]
                    # Use .agg with dict to ensure order of agg results
                    agg_df = gb.agg(['mean', 'min', 'max', 'std'])
                    # Flatten column MultiIndex to desired names:
                    # mean -> metric (overwrite the sample-level metric with aggregated mean)
                    # min  -> metric + '_min'
                    # max  -> metric + '_max'
                    # std  -> metric + '_std'
                    agg_df.columns = [
                        f"{m}" if func == 'mean' else f"{m}_{func}"
                        for m, func in agg_df.columns
                    ]
                    # Now agg_df index = opyear. Convert to DataFrame with opyear column
                    stats_df = agg_df.reset_index()

                    # Map each stats column back to hs by opyear (avoid merge to prevent suffixes)
                    for col in stats_df.columns:
                        if col == 'opyear':
                            continue
                        # Build mapping dict: opyear -> value
                        mapping = stats_df.set_index('opyear')[col].to_dict()
                        # Map values into hs; where mapping returns NaN, keep existing hs value
                        mapped = hs['opyear'].map(mapping)
                        # If original column exists in hs, assign mapped values where notna, otherwise create new column
                        if col in hs.columns:
                            # Only overwrite with mapped finite values; otherwise keep existing
                            # Coerce to numeric and replace non-finite with NaN to avoid accidental propagation
                            mapped_numeric = pd.to_numeric(mapped, errors='coerce')
                            mask = mapped_numeric.notna() & np.isfinite(mapped_numeric)
                            if mask.any():
                                hs.loc[mask, col] = mapped_numeric[mask].astype(float)
                        else:
                            # create column with mapped values, fill NaN with 0.0
                            hs[col] = pd.to_numeric(mapped, errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0.0)

                    # Ensure all numeric columns are finite floats; replace NaN/inf with 0.0
                    for c in hs.columns:
                        if hs[c].dtype.kind in 'fiu' or c.startswith(tuple(health_metrics)):
                            hs[c] = pd.to_numeric(hs[c], errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0.0)

                # assign back
                self.health_samples = hs
        except Exception as ex:
            print(f"Failed to compute/attach health sample stats: {ex}")

        return nameplate_stats_list, thermal_stats_df


    def run(self, maintenance_strategy: str):
                              
         self.init_static_config()
         nameplate_samples           = list()
         thermal_samples             = pd.DataFrame()

         try:
            n_steps = int(self.horizon)
            if n_steps < 0:
                n_steps = 0
         except Exception:
            n_steps = 0

         health_samples     = pd.DataFrame({
            'opyear'            :   np.arange(n_steps, dtype=int),
            'score'             :   np.zeros(n_steps, dtype=float),
            'score_min'         :   np.zeros(n_steps, dtype=float),
            'score_max'         :   np.zeros(n_steps, dtype=float),
            'score_std'         :   np.zeros(n_steps, dtype=float),
         })
        
         var_name      = self.states["varname"]
         alphaMin      = self.states["alphamin"].astype(float)
         alphaMax      = self.states["alphamax"].astype(float)
         betaMin       = self.states["betamin"].astype(float)
         betaMax       = self.states["betamax"].astype(float)
         sigmaMin      = self.states["sigmamin"].astype(float)
         sigmaMax      = self.states["sigmamax"].astype(float)
         scoreMax      = self.states["scoremax"].astype(float)
         scoreMin      = self.states["scoremin"].astype(float) 
         self.growthRate  = 0.02 # self.static_vars.loc[self.static_vars['Varname'] ==  "load_growth_rate", 'Value'].item()
         for i in range(self.sim_samples):           
            # Exploring various degradation paths using Monte Carlo Simulation
            for k in range(len(var_name)):
                self.Z[k]                  = np.zeros(self.horizon) 
                self.Z[k][0]               = scoreMin[k]
                self.a[k]                  = uniform(alphaMin[k], alphaMax[k])
                self.b[k]                  = uniform(betaMin[k], betaMax[k])
                self.sigma[k]              = uniform(sigmaMin[k], sigmaMax[k])   

            # Reading the current health score and PoF data
            self.init_dynamic_config()
                         
            # Reactive Maintenance Evaluation
            if maintenance_strategy == MaintStrategy.REACTIVE.value:
                for step in range(self.horizon):
                    self.generate_config(step)
                    current_health, df_thermal, df_nameplate        = self.xfrm_reactive_load_forecast(step)
                    health_samples.at[step, 'score']                = current_health
                    load_types = (df_nameplate['loadtype'].dropna().drop_duplicates().tolist())


            # Preventive Maintenance Evaluation
            if maintenance_strategy == MaintStrategy.PREVENTATIVE.value:
                for k in range(len(var_name)):
                    self.Z[k]                  = np.zeros(self.horizon) 
                    self.Z[k][0]               = scoreMin[k]

                for step in range(self.horizon):
                    self.generate_config(step)
                    current_health, df_thermal, df_nameplate        = self.xfrm_preventative_load_forecast(step)
                    health_samples.at[step, 'prev_score']           = current_health
                    load_types = (df_nameplate['loadtype'].dropna().drop_duplicates().tolist())


            # Condition-based Maintenance Evaluation
            if maintenance_strategy == MaintStrategy.CONDITION_BASED.value:
                for k in range(len(var_name)):
                    self.Z[k]                  = np.zeros(self.horizon) 
                    self.Z[k][0]               = scoreMin[k]

                for step in range(self.horizon):
                    self.generate_config(step)             
                    current_health, df_thermal, df_nameplate        = self.xfrm_condb_load_forecast(step)
                    health_samples.at[step, 'condb_score']            = current_health
                    load_types = (df_nameplate['loadtype'].dropna().drop_duplicates().tolist())
   
                
            for lt in load_types:
                print(f"--- Reactive Maintenance Load Results for \n {df_nameplate} at step {step} and load type ---")
                row_first                   = df_nameplate.loc[df_nameplate['loadtype'] == lt].iloc[0]
                load_item                   = loaddistros()
                load_item.opyear            = step                 
                # load_item.asset_id          = self.asset_id
                load_item.load_type         = lt
                load_item.margin            = row_first['margin']
                load_item.uphotspot         = row_first['uphotspot']
                load_item.upbottom          = row_first['upbottom']
                load_item.uptopoil          = row_first['uptopoil']
                load_item.uplife            = row_first['uplife']
                load_item.upload            = row_first['upload']
                nameplate_samples.append(load_item)
                thermal_match = df_thermal.loc[df_thermal['loadtype'] == lt]
                if not thermal_match.empty:
                    df_item = pd.DataFrame({
                        'load_type'      : np.full(len(thermal_match['otime']), lt),
                        'opyear'         : np.full(len(thermal_match['otime']), step, dtype=int),
                        'otime'          : pd.to_numeric(thermal_match['otime'], errors='coerce'),
                        'opamb'          : pd.to_numeric(thermal_match['opamb'], errors='coerce'),
                        'obload'         : pd.to_numeric(thermal_match['obload'], errors='coerce'),
                        'margin'         : pd.to_numeric(thermal_match['margin'], errors='coerce'),
                        'opbottom'       : pd.to_numeric(thermal_match['opbottom'], errors='coerce'),
                        'ophotspot'      : pd.to_numeric(thermal_match['ophotspot'], errors='coerce'),
                        'optopoil'       : pd.to_numeric(thermal_match['optopoil'], errors='coerce'),
                        'oplife'         : pd.to_numeric(thermal_match['oplife'], errors='coerce'),
                        'opload'         : pd.to_numeric(thermal_match['opload'], errors='coerce'),
                    })

                # Ensure thermal_samples is a DataFrame, then append rows
                if not isinstance(thermal_samples, pd.DataFrame) or thermal_samples.empty:
                    thermal_samples = df_item.copy()
                else:
                    thermal_samples = pd.concat([thermal_samples, df_item], ignore_index=True)    
         
         # print("=================thermal_samples===========================")
         # with pd.option_context(
         #        'display.max_rows', None,             # show all rows
         #        'display.max_columns', None,          # show all columns
         #        'display.width', 2000,                # wide console width to avoid wrapping
         #        'display.max_colwidth', None,         # do not truncate column contents
         #        'display.expand_frame_repr', False    # keep DataFrame on a single line if possible
         #    ):
         #        # Use to_string to bypass any residual truncation logic
         #    print(thermal_samples.to_string(index=False))
         nameplate_samples, thermal_samples = self.compute_replication_stats(nameplate_samples, thermal_samples)

         return self.health_samples, nameplate_samples, thermal_samples


def extract_seasonal_24h_profile(season: str, asset_id: str = None) -> pd.DataFrame:
        """
        Extract a 24-hour seasonal profile of ambient and load (puload) averages.
        Args:
            season: One of {"WINTER","SUMMER","SPRING","FALL","AUTUMN"} (case-insensitive).
            asset_id: Optional asset filter if column exists in meas_conditions.
        Returns:
            pd.DataFrame with columns: ['hour','ambient','puload'] where hour in [0..23].
        """
            
        def time_to_minute(tm_str):

            if tm_str =="24:00": return 1440
            total_min = time.strptime(tm_str, "%H:%M")
            return (total_min.tm_hour)*60 + total_min.tm_min

        try:
            season_key = (season or "").strip().upper()
            season_to_months = {
                "WINTER": [12, 1, 2],
                "SUMMER": [6, 7, 8],
                "SPRING": [3, 4, 5],
                "FALL":   [9, 10, 11],
                "AUTUMN": [9, 10, 11],
            }
            if season_key not in season_to_months:
                raise ValueError(f"Unsupported season '{season}'. Use WINTER, SUMMER, SPRING, FALL/AUTUMN.")

            months = season_to_months[season_key]

            hour_col = func.extract('hour', measconditions.c.sampdate).label('hour')
            puload_expr = (
                (func.coalesce(measconditions.c.puloadx, 0.0) +
                func.coalesce(measconditions.c.puloady, 0.0) +
                func.coalesce(measconditions.c.puloadz, 0.0)) / 3.0
            )

            stmt = (select(hour_col,
                        func.avg(measconditions.c.ambient).label('ambient'),
                        func.avg(puload_expr).label('puload'),
                        func.avg(measconditions.c.fanspeedc1).label('cooling'))
                    .where(extract('month', measconditions.c.sampdate).in_(months))
                    .group_by(hour_col)
                    .order_by(hour_col))

            # Optional asset filter if column exists
            if hasattr(measconditions.c, "eqsernum") and asset_id:
                stmt = stmt.where(measconditions.c.eqsernum == asset_id)

            with Session(p_engine) as p_session:
                rows = p_session.execute(stmt).all()
                df = pd.DataFrame(rows, columns=['hour', 'ambient', 'puload', 'cooling'])

            # Ensure full 24 hours present and clean types
            if df.empty:
                df = pd.read_csv(LOAD_DATA_FILE, usecols=[0, 1, 2, 3], names=['hour','ambient', 'puload','cooling'], header=None)
                # return df

            print("-----------------------")
            print(f"Extracted seasonal profile for {season} and asset {asset_id}:\n{df}")
            return df

        except Exception as err:
            print(f'HTTP error occured: {err}')
            return pd.DataFrame(columns=['hour', 'ambient', 'puload', 'cooling'])


def dynamic_loading_function():
                
    simulation_time    = 10 # int(horizon)
        
    def _finite(x, default=0.0):
        try:
            v = float(x)
            return v if math.isfinite(v) else default
        except Exception:
            return default
        
    def _stats(arr):
        """
        Return (avg, min, max, std, p50, p95) with all non-finite values removed.
        If nothing finite remains, zeros are returned.
        """
        a = np.array(arr, dtype=float)
        a = a[np.isfinite(a)]
        if a.size == 0:
            return (0.0, 0.0, 0.0, 0.0)
            # return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return (
            float(np.mean(a)),
            float(np.min(a)),
            float(np.max(a)),
            float(np.std(a, ddof=0)),
            # float(np.percentile(a, 50)),
            # float(np.percentile(a, 95)),
        )

    def _apply_stats(prefix, values, target, rnd=4):
        """
        Write sanitized (finite) statistic values onto target object attributes.
        """
        # avg, vmin, vmax, std, p50, p95 = values
        avg, vmin, vmax, std = values

        def _set(suffix, val):
            setattr(target, f"{prefix}{suffix}", round(_finite(val), rnd))

        _set("", avg)
        _set("_min", vmin)
        _set("_max", vmax)
        _set("_std", std)
        # Percentiles disabled (uncomment if needed, already sanitized)
        # _set("_p50", p50)
        # _set("_p95", p95)

    def _to_num(v):
        """
        Coerce v to finite float or return -1 (acts as sentinel) for non-finite.
        For sequences, mean of finite elements is taken.
        """
        try:
            if isinstance(v, (pd.Series, np.ndarray, list, tuple)):
                arr = np.asarray(v, dtype=float)
                arr = arr[np.isfinite(arr)]
                if arr.size == 0:
                    return -1.0
                return float(np.mean(arr))
            val = float(v)
            return val if math.isfinite(val) else -1.0
        except Exception:
            return -1.0

    def _sanitize_record(d: dict) -> dict:
        """
        Replace any non-finite numeric values in dict with 0.0 for safe DB insert.
        """
        for k, v in d.items():
            if isinstance(v, (int, float)):
                if not math.isfinite(float(v)):
                    d[k] = 0.0
        return d

    def extract_op0_curves(health_samples, nameplate_samples, thermal_samples):

        def _to_dataframe(samples):
            # Convert list of objects or dicts to DataFrame; if already a DataFrame, return as-is.
            if isinstance(samples, pd.DataFrame):
                return samples.copy()
            if isinstance(samples, (list, tuple)):
                rows = []
                for s in samples:
                    if isinstance(s, dict):
                        rows.append({k: v for k, v in s.items() if not (isinstance(k, str) and k.startswith("_"))})
                    else:
                        # Convert object attributes to dict while skipping private attributes
                        d = getattr(s, "__dict__", {})
                        if isinstance(d, dict):
                            rows.append({k: v for k, v in d.items() if not (isinstance(k, str) and k.startswith("_"))})
                return pd.DataFrame(rows)
            # Fallback: try to construct DataFrame
            try:
                return pd.DataFrame(samples)
            except Exception:
                return pd.DataFrame()

        def _filter_op0(df: pd.DataFrame) -> pd.DataFrame:
            if df is None or df.empty:
                return pd.DataFrame(columns=getattr(df, "columns", None))
            if "opyear" not in df.columns:
                # No opyear column, return empty with same columns
                return pd.DataFrame(columns=df.columns)
            df2 = df.copy()
            # Coerce opyear to numeric for robust filtering
            df2["opyear"] = pd.to_numeric(df2["opyear"], errors="coerce")
            mask = df2["opyear"].fillna(-1).astype(int) == 0
            result = df2.loc[mask].copy()

            return result

        # Convert inputs to DataFrames
        health_df    = _to_dataframe(health_samples)
        nameplate_df = _to_dataframe(nameplate_samples)
        thermal_df   = _to_dataframe(thermal_samples)


        # Apply filter
        health_curve    = _filter_op0(health_df)
        if not health_curve.empty:
            asset_id_val = health_curve['asset_id'].iloc[0] if 'asset_id' in health_curve.columns else None
            opyear_val = health_curve['opyear'].iloc[0] if 'opyear' in health_curve.columns else 0
            avg_row = {}
            for col in health_curve.columns:
                if col in ('asset_id', 'opyear'):
                    continue
                col_vals = pd.to_numeric(health_curve[col], errors='coerce').replace([np.inf, -np.inf], np.nan).dropna()
                avg_row[col] = float(col_vals.mean()) if not col_vals.empty else 0.0
            base = {}
            if asset_id_val is not None:
                base['asset_id'] = asset_id_val
            base['opyear'] = opyear_val
            health_curve = pd.DataFrame([{**base, **avg_row}])

        nameplate_curve = _filter_op0(nameplate_df)
        thermal_curve   = _filter_op0(thermal_df)
        if not thermal_curve.empty:
            # Coerce otime to numeric (if present) for consistent grouping
            if 'otime' in thermal_curve.columns:
                thermal_curve['otime'] = pd.to_numeric(thermal_curve['otime'], errors='coerce')
                thermal_curve = thermal_curve.dropna(subset=['otime'])
            # Determine numeric columns excluding identifiers
            numeric_cols = thermal_curve.select_dtypes(include=[np.number]).columns.tolist()
            exclude_cols = {'asset_id', 'opyear', 'otime'}
            agg_cols = [c for c in numeric_cols if c not in exclude_cols]
            group_cols = [c for c in ['load_type', 'otime'] if c in thermal_curve.columns]
            if agg_cols and group_cols:
                thermal_curve = (
                    thermal_curve
                    .groupby(group_cols, dropna=False)[agg_cols]
                    .mean()
                    .reset_index()
                )

        """
        Persist OP=0 snapshots:
          health_curve   -> loadcbdistro
          nameplate_curve-> load_results
          thermal_curve  -> load_curves
        """

        # print(f"\n\n\n\n====================={lr.asset_id}==health_df=====================\n{health_curve}\n\n\n\n ==nameplate_curve>> {nameplate_curve}\n\n\n\n ==")
        # with pd.option_context(
        #         'display.max_rows', None,             # show all rows
        #         'display.max_columns', None,          # show all columns
        #         'display.width', 2000,                # wide console width to avoid wrapping
        #         'display.max_colwidth', None,         # do not truncate column contents
        #         'display.expand_frame_repr', False    # keep DataFrame on a single line if possible
        #     ):
        # reformulate the selected by taking the average stat value of the numerical field returned per load_type and for each  'otime'. Do not include asset_id and opyear in the stat calculaton
        #     print(thermal_curve.to_string(index=False))

        # Health (aggregate row per curve entry)
        if not health_curve.empty:
            health_insert_rows = []
            for row in health_curve.itertuples(index=False):
                record = {
                    'load_type'       : 'ALL',
                    'opyear'          : "Yr 0",
                    'score'     : _finite(getattr(row, 'score', 0.0)),
                    'score_min' : _finite(getattr(row, 'score_min', 0.0)),
                    'score_max' : _finite(getattr(row, 'score_max', 0.0)),
                    'score_std' : _finite(getattr(row, 'score_std', 0.0)),

                }
                health_insert_rows.append(_sanitize_record(record))
            if health_insert_rows:
                p_session.execute(loadcbdistros.insert(), health_insert_rows)
                p_session.commit()

        # Nameplate (store per strategy)
        if not nameplate_curve.empty:
            nameplate_insert_rows = []

            for row in nameplate_curve.itertuples(index=False):
                rm = _finite(getattr(row, 'margin', 0.0))

                # Skip invalid rows (negative margins). Do not terminate the process.
                # if rm < 0.0 or pm < 0.0 or cm < 0.0:
                #     print(f"Skipping invalid nameplate row (negative margin) for load_type: {rm} - {pm} - {cm}",
                #           getattr(row, 'load_type', 'UNK'))
                #     continue
                rec = {
                    'loadtype'        : getattr(row, 'load_type', 'UNK'),
                    # 'opyear'          : "Yr 0",
                    'sampdate'        : arrow.now().int_timestamp,
                    'uptopoil'  : _finite(getattr(row, 'uptopoil', 0.0)),
                    'uphotspot' : _finite(getattr(row, 'uphotspot', 0.0)),
                    'upload'    : _finite(getattr(row, 'upload', 0.0)),
                    'upbottom'  : _finite(getattr(row, 'upbottom', 0.0)),
                    'uplife'    : _finite(getattr(row, 'uplife', 0.0)),
                    'ttptop'    : _finite(getattr(row, 'ttptop', 0.0)),
                    'ttphot'    : _finite(getattr(row, 'ttphot', 0.0)),
                    'ttpmva'    : _finite(getattr(row, 'ttpmva', 0.0)),
                    'margin'    : rm,
                    'cycle'     : dynamic_cycle
                }
                nameplate_insert_rows.append(_sanitize_record(rec))
            if nameplate_insert_rows:
                p_session.execute(loadresults.insert(), nameplate_insert_rows)
                p_session.commit()

        # Thermal (store per strategy & otime)
        if not thermal_curve.empty and 'otime' in thermal_curve.columns:
            thermal_insert_rows = []
            for row in thermal_curve.itertuples(index=False):
                    rec = {
                        'loadtype'        : getattr(row, 'load_type', 'UNK'),
                        # 'opyear'          : "Yr 0",
                        'sampdate'        : arrow.now().int_timestamp,
                        'otime'           : _finite(getattr(row, 'otime', 0.0), 0.0),
                        'opamb'           : _finite(getattr(row, 'opamb', 0.0)),
                        'obload'          : _finite(getattr(row, 'obload', 0.0)),

                        'optopoil'        : _finite(getattr(row, 'optopoil', 0.0)),
                        'ophotspot'       : _finite(getattr(row, 'ophotspot', 0.0)),
                        'oload'           : _finite(getattr(row, 'oload', 0.0)),
                        'obottom'         : _finite(getattr(row, 'obottom', 0.0)),
                        'olife'           : _finite(getattr(row, 'olife', 0.0)),
                        'margin'          : _finite(getattr(row, 'margin', 0.0)),
                        'cycle'           : dynamic_cycle
                    }
                    thermal_insert_rows.append(_sanitize_record(rec))
            if thermal_insert_rows:
                p_session.execute(loadcurves.insert(), thermal_insert_rows)
                p_session.commit()

        return health_curve, nameplate_curve, thermal_curve

    with Session(p_engine) as p_session:
        width            = 2                          
        loading_cases    = p_session.execute(select(loadingcases)).all()
        states   = pd.DataFrame(p_session.execute(select(degradations)).mappings())
        print(f"self.states : {states}")  
            
        # For each asset_id, set the last cooling stage status in the coolings table to "OFF" and all the other stages to "ON" 
        # Set all cooling stages OFF for this asset_id
        p_session.execute(coolings.update().values(Status="OFF"))
        p_session.commit()
            
        # For asset_id Set the field "status" of the last record of cooling stages to "ON"
        try:
                last_row = p_session.execute(select(coolings.c.id).order_by(coolings.c.id.desc()).limit(1)).scalar()
                print(f"Last cooling stage ID  is {last_row}")
                if last_row is not None:
                    print(f"Activating last cooling stage (ID: {last_row})")
                    p_session.execute(coolings.update().where(coolings.c.id == last_row).values(Status="ON"))
                    p_session.commit()
                    
        except Exception as ex:
                print(f"Failed to activate last cooling stage : {ex}")

        dynamic_cycle = p_session.execute(select(datadictionaries.c.value).where(datadictionaries.c.varname == "dynamic_cycle")).scalar()
        dynamic_cycle = int(dynamic_cycle) + 1 if dynamic_cycle is not None else 0
        seasonal_profile = extract_seasonal_24h_profile("SUMMER")
                            
        print("------------------------------------------------------------------")
        print(f"Launching Dynamic Loading                                        ")
        print("------------------------------------------------------------------")      
        load_rater         = LoadProcessor(dynamic_cycle, 
                                           states,
                                           seasonal_profile, 
                                           loading_cases, 
                                           simulation_time)
        try:
            maintenance_strategy = MaintStrategy.REACTIVE.value
            health_samples, nameplate_samples, thermal_samples = load_rater.run(maintenance_strategy)
            print(f"Completed Dynamic Loading for maintenance strategy: {maintenance_strategy} - thermal samples")
            health_curve, nameplate_curve, thermal_curve = extract_op0_curves(health_samples, nameplate_samples, thermal_samples)
            # Persist the latest dynamic_cycle into datadictionaries

        except Exception as ex:
            print(f"Thread failed: {ex}")
            # Ensure downstream variables exist even if run failed
            health_samples = pd.DataFrame()
            nameplate_samples = []
            thermal_samples = pd.DataFrame()

                
        print("--------------------------------------------")
        print(f" Post processing at unit level ...         ")
        print("--------------------------------------------")
        # Extract plain LoadType values from the loading_cases rows for downstream grouping
        load_types = [getattr(case, "LoadType", None) for case in loading_cases if getattr(case, "LoadType", None) is not None]

        # Delete existing `loadcbdistro` records for this asset before any new inserts
        p_session.execute(loadcbdistros.delete())
        p_session.execute(loaddistros.delete())
        p_session.execute(thermaldistros.delete())                   
        p_session.execute(datadictionaries.update()
                .where(datadictionaries.c.varname == "dynamic_cycle")
                .values(value=str(dynamic_cycle))
        )
        p_session.commit()                


        # ----------------------------#
        # Nameplate stats             #
        # ----------------------------#
        for lt in load_types:
            v = width     
            while(v < simulation_time + width):
                window_years = [v - width + 1, v]
                subset = [x for x in nameplate_samples if (x.opyear in window_years and x.load_type == lt)]
                subset_df = pd.DataFrame(subset)
                if not subset_df.empty:
                    l_cdistro                = loaddistros()
                    l_cdistro.load_type      = lt  
                    l_cdistro.opyear         = f"Yr {v - width + 1} - {v}"
                            
                    _apply_stats("margin", _stats([_to_num(x.margin) for x in subset]), l_cdistro, 3)
                    _apply_stats("uptopoil", _stats([_to_num(x.uptopoil) for x in subset]), l_cdistro, 1)
                    _apply_stats("upbottom", _stats([_to_num(x.upbottom) for x in subset]), l_cdistro, 1)
                    _apply_stats("uphotspot", _stats([_to_num(x.uphotspot) for x in subset]), l_cdistro, 1)
                    _apply_stats("upload", _stats([_to_num(x.upload) for x in subset]), l_cdistro, 2)
                    _apply_stats("uplife", _stats([_to_num(x.uplife) for x in subset]), l_cdistro, 4)

                    record_np = {k: v2 for k, v2 in l_cdistro.__dict__.items() if not k.startswith("_") }
                    record_np = _sanitize_record(record_np)
                    p_session.execute(loaddistros.insert(), record_np)
                    p_session.commit()
                v += width   
                
        # ----------------------------#
        # Thermal stats               #
        # ----------------------------#                
        # Normalize thermal_samples to have a canonical 'load_type' column and ensure required numeric columns exist.
        if not isinstance(thermal_samples, pd.DataFrame):
            thermal_samples = pd.DataFrame()
        if 'load_type' not in thermal_samples.columns:
            if 'loadtype' in thermal_samples.columns:
                thermal_samples['load_type'] = thermal_samples['loadtype']
            else:
                thermal_samples['load_type'] = pd.Series(dtype=object)
        if 'opyear' not in thermal_samples.columns:
            thermal_samples['opyear'] = pd.Series(dtype='Int64')
        if 'otime' not in thermal_samples.columns:
            thermal_samples['otime'] = pd.Series(dtype=float)

        for lt in load_types:
            v = width     
            while(v < simulation_time + width):                                                
                window_years = [v - width + 1, v]        
                subset_df = thermal_samples[(thermal_samples['load_type'] == lt) & (thermal_samples['opyear'].isin(window_years))]
                if not subset_df.empty:
                    subset_df = subset_df.copy()
                    subset_df['opyear'] = pd.to_numeric(subset_df['opyear'], errors='coerce').astype('Int64')
                    subset_df['otime']  = pd.to_numeric(subset_df['otime'],  errors='coerce')
                    subset_df = subset_df[subset_df['opyear'].isin(window_years)]
                    subset_df = subset_df.dropna(subset=['otime'])

                    # Helper: safe numeric list from a DataFrame column
                    def _col_vals(df_in, col):
                        if col not in df_in.columns:
                            return []
                        return (pd.to_numeric(df_in[col], errors='coerce').replace([np.inf, -np.inf], np.nan).dropna().tolist())

                    # Compute stats per th_time (otime) across the year window for this load type
                    for th_time, df_t in subset_df.groupby('otime', dropna=True):
                        th_distro                = thermaldistros()
                        th_distro.load_type      = lt.LoadType
                        th_distro.opyear         = f"Yr {v - width + 1} - {v}"    
                        th_distro.th_time        = float(th_time)

                        # Margins
                        _apply_stats("margin", _stats(_col_vals(df_t, 'margin')), th_distro, 3)
                        _apply_stats("optopoil", _stats(_col_vals(df_t, 'optopoil')), th_distro, 1)
                        _apply_stats("ophotspot", _stats(_col_vals(df_t, 'ophotspot')), th_distro, 1)
                        _apply_stats("opbottom", _stats(_col_vals(df_t, 'opbottom')), th_distro, 1)
                        _apply_stats("opload", _stats(_col_vals(df_t, 'opload')), th_distro, 1)
                        _apply_stats("oplife", _stats(_col_vals(df_t, 'oplife')), th_distro, 4)


                        record_th = {k: v2 for k, v2 in th_distro.__dict__.items() if not k.startswith("_")}
                        record_th = _sanitize_record(record_th)
                        p_session.execute(thermaldistros.insert(), record_th)
                        p_session.commit()

                v += width        






if __name__ == '__main__':
               
    print("-----------------------------------")
    print("Launching Dynamic Loading ...      ")
    print("-----------------------------------") 
    monitored_asset = "some_asset_id"
    with Session(p_engine) as p_session:


         monitoring_vars            = pd.DataFrame(p_session.execute(select(datadictionaries).
                                                                     where(datadictionaries.c.groupname == "Monitoring")).mappings())
        
         dynamic_rating_rate        = float(monitoring_vars.loc[monitoring_vars['varname'] ==  "mtrg_rate", 'value'].item()) 
         seasonal_rating_rate       = float(monitoring_vars.loc[monitoring_vars['varname'] ==  "seasonal_rate", 'value'].item()) 

         daily_loading_thread       = RepeatEvery(int(dynamic_rating_rate), dynamic_loading_function)
         daily_loading_thread.run()  
