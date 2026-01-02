#!/usr/bin/python
from datetime import datetime
import concurrent
import logging
from re import match
from threading import Lock
import numpy as np
import pandas as pd
import csv as csv
import arrow
from datetime import timedelta

from pandas._libs.tslibs.offsets import Hour
from XUtility import *
from sqlalchemy.orm import Session
from sqlalchemy import Insert, update, Integer, false, select, true




class Watchdog:

    def __init__(self, asset_id, asset_type, alarm_vars, alarm_configs, action_vars, _lock, p_sessions):

        self.asset_id           = asset_id
        self.asset_type         = asset_type
        self.alarm_vars         = alarm_vars
        self.alarm_configs      = alarm_configs
        self.action_vars        = action_vars
        self._lock              =_lock
        self.p_session          = p_sessions


    def setup_alarm(self, alm_name, alm_source, parameter):

        normal      = self.alarm_vars[["TTF", "Normal"]]
        caution     = self.alarm_vars[["TTF", "Caution"]]
        alert       = self.alarm_vars[["TTF", "Alert"]]
        alarm       = self.alarm_vars[["TTF", "Alarm"]]
        emergency   = self.alarm_vars[["TTF", "Emergency"]]


        alm_item            = alarmitem()
        alm_item.Eqsernum   = self.asset_id
        alm_item.Category   = self.asset_type
        alm_item.AlarmName  = alm_name
        alm_item.Source     = alm_source
        alm_item.Score      = str(max(parameter))


        while (len(parameter) < len(normal)):
            parameter.append(0)

        if sum([1 if float(normal['Normal'][i]) - float(parameter[i]) >= 0 else 0 for i in normal.index]) == 0:
            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.NORMAL.value)
            alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
                                                            (self.action_vars["AlarmType"] == Severity.NORMAL.value)), "Statement"].item()

        elif sum([1 if float(normal['Normal'][i]) < float(parameter[i]) <= float(caution['Caution'][i]) else 0 for i in caution.index]) == 0:
            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.CAUTION.value)
            # print(f"alm_source ======<<<<>>>>>>>: {alm_source} \n  {self.action_vars}")
            # alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
            #                                                 (self.action_vars["AlarmType"] == Severity.CAUTION.value)), "Statement"].item()

        elif sum([1 if float(caution['Caution'][i]) < float(parameter[i]) <= float(alert['Alert'][i]) else 0 for i in alert.index]) == 0:

            print(f"alm_source ======<<<<>>>>>>>: {alm_source} \n  {self.action_vars}")
            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.ALERT.value)
            # alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
            #                                                 (self.action_vars["AlarmType"] == Severity.ALERT.value)), "Statement"].item()

        elif sum([1 if float(alert['Alert'][i]) < float(parameter[i]) <= float(alarm['Alarm'][i]) else 0 for i in alarm.index]) == 0:
            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.ALARM.value)
            alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
                                                            (self.action_vars["AlarmType"] == Severity.ALARM.value)), "Statement"].item()

        elif sum([1 if float(alarm['Alarm'][i]) < float(parameter[i]) <= float(emergency['Emergency'][i]) else 0 for i in emergency.index]) == 0:

            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.EMERGENCY.value)
            alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
                                                            (self.action_vars["AlarmType"] == Severity.EMERGENCY.value)), "Statement"].item()

        elif sum([1 if float(parameter[i]) - float(emergency['Emergency'][i]) >= 0 else 0 for i in emergency.index]) == 0:
            alm_item.Status         = str(EvtStatus.PENDING.value)
            alm_item.IsActive       = True
            alm_item.LastSeen       = str(arrow.now().int_timestamp)
            alm_item.FirstSeen      = str(arrow.now().int_timestamp)
            alm_item.Aseverity      = str(Severity.BLACKOUT.value)
            alm_item.Information    = self.action_vars.loc[((self.action_vars["Component"] == int(alm_source)) & 
                                                            (self.action_vars["AlarmType"] == Severity.BLACKOUT.value)), "Statement"].item()

        record_check = pd.DataFrame(self.p_session.execute(select(alarmitems)
                                                    .where(alarmitems.c.Eqsernum  == alm_item.Eqsernum)
                                                    .where(alarmitems.c.AlarmName == alm_item.AlarmName)
                                                    .where(alarmitems.c.Source    == alm_item.Source)).mappings())
        if (record_check.empty == False):

            update_stmt = (update(alarmitems).where(alarmitems.c.Eqsernum == alm_item.Eqsernum)
                                             .where(alarmitems.c.AlarmName == alm_item.AlarmName)
                                             .where(alarmitems.c.Source == alm_item.Source)
                                             .values({alarmitems.c.Aseverity: alm_item.Aseverity,
                                                      alarmitems.c.Status: alm_item.Status,
                                                      alarmitems.c.LastSeen: str(arrow.now().int_timestamp),
                                                      alarmitems.c.Information: alm_item.Information }))
            self.p_session.execute(update_stmt)
        else:
            p_session.execute(alarmitems.insert(), alm_item.__dict__)
        self.p_session.commit()



    def start_alarm_watch(self):

        for alm_name in self.alarm_configs["AlarmName"]:
            print(alm_name)
            thresho_type    = self.alarm_configs.loc[self.alarm_configs['AlarmName'] == alm_name, 'ThreshType'].item()
            alm_rate        = 10 # self.alarm_configs.loc[self.alarm_configs['AlarmName'] == alm_name, 'CollectorType'].item()
            target_type     = self.alarm_configs.loc[self.alarm_configs['AlarmName'] == alm_name, 'TargetType'].item()
            stat_type       = self.alarm_configs.loc[self.alarm_configs['AlarmName'] == alm_name, 'StatisticType'].item()
            alm_vars        = self.alarm_vars.loc[self.alarm_vars['AlarmName'] == alm_name]

            # print("=======")
            # print(f"alm_name :      {alm_name}")
            # print(f"alm_rate :      {alm_rate}")
            # print(f"alm_vars:       {alm_vars}")
            # print(f"thresho_type:   {thresho_type}")
            # print(f"target_type:    {target_type}")
            # print(f"stat_type:      {stat_type}")
                
            current_time = arrow.now()
            start_time   = current_time.shift(minutes=-int(alm_rate))

            with self._lock:

                health_scores = self.p_session.execute(select(healthresults).where(healthresults.c.assetId == self.asset_id)
                                                                       .where(healthresults.c.datetimeTs.cast(Integer) < current_time.int_timestamp)
                                                                       .where(healthresults.c.datetimeTs.cast(Integer) >= start_time.int_timestamp)).all()

                # print(f"------ Health Scores -------: {health_scores}")

                if (len(health_scores) > 0):

                    if (int(target_type) == AssetCond.THERMAL_CONDITION.value):
                        temperature_reading = [o.temperature_reading for o in health_scores]
                        print(f"------ Temperature Reading -------: {temperature_reading}")
                        self.setup_alarm(alm_name, target_type, temperature_reading)

                    elif (int(target_type) == AssetCond.OIL_CONDITION.value):
                        dissolved_reading = [o.dissolved_gas for o in health_scores]
                        print(f"------ Oil condition -------: {dissolved_reading}")
                        self.setup_alarm(alm_name, target_type, dissolved_reading)
                
                    elif (int(target_type) == AssetCond.MAIN_TANK_CONDITION.value):
                        main_tank_scores = [o.main_tank for o in health_scores]
                        print(f"------ Main tank condition -------: {main_tank_scores}")
                        self.setup_alarm(alm_name, target_type, main_tank_scores)    
                    
                    # elif (int(target_type) == AssetCond.INTERNAL_CONDITION.value):
                    #     internal_cond_scores = [o.internal_tap for o in health_scores]
                    #     self.setup_alarm(asset_id, alm_name, alm_vars, target_type, internal_cond_scores)  
                
                    # elif (int(target_type) == AssetCond.EXTERNAL_CONDITON.value):
                    #     external_cond_scores = [o.external_tap for o in health_scores]
                    #     self.setup_alarm(asset_id, alm_name, alm_vars, target_type, external_cond_scores)  
                                    
                    # elif (int(target_type) == AssetCond.DRIVE_MECHANISM.value):
                    #     drive_mechanism_cond_scores = [o.mechnism_cond for o in health_scores]
                    #     self.setup_alarm(asset_id, alm_name, alm_vars, target_type, drive_mechanism_cond_scores)  
                
                    # elif (int(target_type) == AssetCond.BUSHINGS_CONDITION.value):
                    #     bushings_cond_scores = [o.bushings for o in health_scores]
                    #     self.setup_alarm(asset_id, alm_name, alm_vars, target_type, bushings_cond_scores)  

                    # elif (int(target_type) == AssetCond.COOLERS_RADIATOR_CONDITION.value):
                    #     cooling_cond_scores = [o.coolers_radiator for o in health_scores]
                    #     self.setup_alarm(asset_id, alm_name, alm_vars, target_type, cooling_cond_scores)  

                    elif (int(target_type) == AssetCond.PAPER_CONDITION.value):
                        paper_cond_scores = [o.paper_condition for o in health_scores]
                        print(f"------ Paper condition -------: {paper_cond_scores}")
                        self.setup_alarm(alm_name, target_type, paper_cond_scores)  

                    elif (int(target_type) == AssetCond.PARTIAL_DISCHARGE.value):
                        partial_discharge_tf_cond_scores = [o.partial_discharge_tf for o in health_scores]
                        print(f"------ Partial discharges condition -------: {partial_discharge_tf_cond_scores}")
                        self.setup_alarm(alm_name, target_type, partial_discharge_tf_cond_scores)  
            
                    elif (int(target_type) == AssetCond.TAP_CHANGER.value):
                        tap_cond_scores = [o.mechnism_cond for o in health_scores]
                        print(f"------ Tap Changer condition -------: {tap_cond_scores}")
                        self.setup_alarm(alm_name, target_type, tap_cond_scores) 



    def collect_reliable_data(self):

            reliable_items = pd.DataFrame(self.p_session.execute(select(alarmitems)
                                                        .where(alarmitems.c.Eqsernum  == self.asset_id)
                                                        .where(alarmitems.c.Aseverity == Severity.ALARM.value or
                                                               alarmitems.c.Aseverity == Severity.ALERT.value or
                                                               alarmitems.c.Aseverity == Severity.EMERGENCY.value)).mappings())

            if reliable_items.empty == False:
                for realb_item in reliable_items:
                    reliable_item           = timetofail()
                    reliable_item.Eqsernum  = self.asset_id
                    reliable_item.Score     = realb_item["Score"],
                    reliable_item.TTF       = realb_item["FirstSeen"],
                    self.p_session.execute(reliableitems.insert(), reliable_item.__dict__)


def alm_thread_function(alm_process):
    # with health_process._lock:
    #     if isinstance(health_process, HealthIndexing):
            print(f"Starting health watch for asset ID: {alm_process.asset_id}")
            alm_process.start_alarm_watch()    

def main(args):
     
    _lock               = Lock()     
    alm_thread_list     = list()
    p_session           = args[0]

    print("------------------------------------")
    print("Launching Alarm Watchdogs Routine...")
    print("------------------------------------")  

    asset_list      = p_session.execute(select(xfrmmaps)).all() 

    for asset_item in asset_list:
        asset_id        = asset_item.XfrmID  
        asset_type      = p_session.execute(select(xfrmmaps).where(xfrmmaps.c.XfrmID == asset_id)).fetchone().Catgory
        alarm_configs   = pd.DataFrame(p_session.execute(select(alarmconfigs).where(alarmconfigs.c.Eqsernum == asset_id)).mappings())
        alarm_vars      = pd.DataFrame(p_session.execute(select(alarmentries).where(alarmentries.c.Eqsernum == asset_id)).mappings())
        action_vars     = pd.DataFrame(p_session.execute(select(actionentries).where(actionentries.c.AssetType == asset_type)).mappings())

        if alarm_configs.empty == False:
                print(f"self.action_vars ======<<<<>>>>>>>:{asset_id} alarm_configs:{alarm_configs} action_vars:{action_vars} alarm_vars: {alarm_vars}")
                watch_dog      = Watchdog(asset_id, asset_type, alarm_vars, alarm_configs, action_vars, _lock, p_session)
                alm_thread_list.append(watch_dog)

    if len(alm_thread_list) > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(alm_thread_list)) as executor:              
            for alm_result in executor.map(alm_thread_function, iter(alm_thread_list)):
                print(f"Executing workers thread...")            

if __name__ == '__main__':

    with Session(p_engine) as p_session:  
        health_rate = 10
        health_indexing_thread  = RepeatEvery(int(health_rate), main, [p_session])
        health_indexing_thread.run()


