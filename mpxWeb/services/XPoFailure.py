from math import exp, factorial, isnan
import math
from numpy.random import normal, uniform
import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy import select
from XUtility import *


class PoF:
        
        def __init__(self, PofConfig):
                        
            self.year_of_manufacture             = PofConfig["year_of_manufacture"]
            self.current_health_score_tf         = 0.0
            self.current_health_score_tc         = 0.0
            self.utilisation_pct                 = np.double(PofConfig["utilisation_pct"])
            self.altitude_m                      = np.double(PofConfig["altitude_m"])
            self.distance_from_coast_km          = np.double(PofConfig["distance_from_coast_km"])
            self.corrosion_category_index        = np.double(PofConfig["corrosion_category_index"])

            self.simulation_end_year             = int(PofConfig["year_of_manufacture"])
            self.age_tf                          = float(PofConfig["age_tf"])
            self.age_tc                          = float(PofConfig["age_tc"])
            self.avg_daily_tap                   = int(PofConfig["avg_daily_tap"])

            self.grid_or_edge                    = PofConfig["gridoredge"]
            self.placement                       = PofConfig["placement"]

            self.no_taps                         = PofConfig["no_taps"]
            self.transformer_type                = self._coerce_asset_cat(PofConfig["transformer_type"])
            self.partial_discharge_tf            = PofConfig["partial_discharge_tf"]
            self.partial_discharge_tc            = PofConfig["partial_discharge_tc"]
            self.temperature_reading             = PofConfig["temperature_reading"]
            self.main_tank                       = float(PofConfig["main_tank"])
            self.coolers_radiator                = PofConfig["coolers_radiator"]
            self.bushings                        = PofConfig["bushings"]
            self.kiosk                           = PofConfig["kiosk"]
            self.cable_boxes                     = PofConfig["cable_boxes"]
            self.external_tap                    = PofConfig["external_tap"]
            self.internal_tap                    = PofConfig["internal_tap"]
            self.mechnism_cond                   = PofConfig["mechnism_cond"]
            self.diverter_contacts               = PofConfig["diverter_contacts"]
            self.diverter_braids                 = PofConfig["diverter_braids"]

            self.moisture                        = float(PofConfig["moisture"])
            self.acidity                         = float(PofConfig["acidity"])
            self.bd_strength                     = float(PofConfig["bd_strength"])

            self.hydrogen                        = float(PofConfig["hydrogen"])
            self.methane                         = float(PofConfig["methane"])
            self.ethylene                        = float(PofConfig["ethylene"])
            self.ethane                          = float(PofConfig["ethane"])
            self.acetylene                       = float(PofConfig["acetylene"])

            self.hydrogen_pre                    = float(PofConfig["hydrogen_pre"])
            self.methane_pre                     = float(PofConfig["methane_pre"])
            self.ethylene_pre                    = float(PofConfig["ethylene_pre"])
            self.ethane_pre                      = float(PofConfig["ethane_pre"])
            self.acetylene                       = float(PofConfig["acetylene"])

            self.furfuraldehyde                  = 10 #float(PofConfig["furfuraldehyde"])
            self.reliability_factor              = float(PofConfig["reliability_factor"])

            self.normal_expected_life_tf         = float(PofConfig["normal_expected_life_tf"])
            self.normal_expected_life_tc         = float(PofConfig["normal_expected_life_tc"])

            self.k_value                         = float(PofConfig["k_value"])
            self.c_value                         = float(PofConfig["c_value"]) 

            
        def _coerce_asset_cat(self, value):
            if isinstance(value, AssetCat):
                return value
            if isinstance(value, str):
                try:
                    return AssetCat[value].name
                except KeyError:
                    return value
            try:
                return AssetCat(value).name
            except (ValueError, TypeError):
                return value

        def map_score_value (self, value, cond_type):
            
            if(cond_type == AssetCond.EXTERNAL_CONDITON.name):
                if (value < 0.3): return CondState.NO_DETERIORATION.name #
                elif(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SLIGHT_DETERIORATION.name
                elif(6.5 <= value < 8): return CondState.SOME_DETERIORATION.name
                elif(8 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
                
            elif(cond_type == AssetCond.CABLE_BOX_CONDITION.name):
                # if (value < 0.3): return CondState.NO_DETERIORATION.name #
                if(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
            
            elif(cond_type == AssetCond.MAIN_TANK_CONDITION.name):
                # if (value < 0.3): return CondState.NO_DETERIORATION.name #
                if(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
            
            elif(cond_type == AssetCond.COOLERS_RADIATOR_CONDITION.name):
                # if (value < 0.3): return CondState.NO_DETERIORATION.name #
                if(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
                
            elif(cond_type == AssetCond.BUSHINGS_CONDITION.name):
                # if (value < 0.3): return CondState.NO_DETERIORATION.name #
                if(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name

            elif(cond_type == AssetCond.KIOSK_CONDITION.name):
                # if (value < 0.3): return CondState.NO_DETERIORATION.name #
                if(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
                
            elif(cond_type == AssetCond.INTERNAL_CONDITION.name):          # TAP CHANGER
                if (value < 0.3): return CondState.NO_DETERIORATION.name   #
                elif(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
                
            elif(cond_type == AssetCond.DRIVE_MECHANISM.name):             # TAP CHANGER
                if (value < 0.3): return CondState.NO_DETERIORATION.name 
                elif(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name
                
            elif(cond_type == AssetCond.SELECTOR_DIVERTER_CONTACTS.name):  # TAP CHANGER
                if (value < 0.3): return CondState.NO_DETERIORATION.name 
                elif(0.3 <= value < 5.5): return CondState.SUPERFICIAL_MINOR_DETERIORATION.name #
                elif(5.5 <= value < 6.5): return CondState.SOME_DETERIORATION.name
                elif(6.5 <= value < 15): return CondState.SUBSTANTIAL_DETERIORATION.name
                else: return CondState.DEFAULT.name

            elif(cond_type == AssetCond.PARTIAL_DISCHARGE.name):           # TAP CHANGER
                if (value < 0.3): return CondState.LOW.name 
                elif(0.3 <= value < 5.5): return CondState.MEDIUM.name 
                elif(5.5 <= value < 6.5): return CondState.HIGH_NOT_CONFIRMED.name
                elif(6.5 <= value < 15): return CondState.HIGH_CONFIRMED.name
                else: return CondState.DEFAULT.name

            elif(cond_type == AssetCond.TEMPERATURE_READINGS.name):        # TAP CHANGER
                if (value < 0.3): return CondState.NORMAL.name 
                elif(0.3 <= value < 6.5): return CondState.MODERATELY_HIGH.name #
                elif(6.5 <= value < 15): return CondState.VERY_HIGH.name
                else: return CondState.DEFAULT.name

        def Mmi(self, factors, factor_divider_1, factor_divider_2, max_no_combined_factors):
             var_1 = 0.0 
             var_2 = 0.0
             var_3 = 0.0       

             if (len([r for r in factors if(r > 1)]) > 1):
                  var_1 = max(factors)
                  if  (len([r for r in factors if(r == var_1)]) == 1):
                       factors = [g for g in factors if g!= var_1] 
                  else:
                       factors = np.unique(factors)

                  factors = [g for g in factors if g!= var_1] 
                  remaining_factors = [g for g in factors if g - 1 > 0]
                  if (max_no_combined_factors - 1 < 1 or len(remaining_factors) == 0):
                       var_2 = 0
                  else:
                       var_2 = sum(remaining_factors)
                       
                  var_3 = var_2 / factor_divider_1
             else:
                  var_1 = min(factors)
                  # print(factors)
                  if (len([r for r in factors if(r == var_1)]) == 1):
                       factors = [g for g in factors if g!= var_1] 
                  else:
                       factors = np.unique(factors)

                  var_2 = min(factors)
                  var_3 = (var_2 - 1) / factor_divider_2
                  # print(f"var_1 :{var_1} var_2: {var_2} var_3: {var_3}")
             # combined factor
             return (var_1 + var_3)

        # -------------------------------------------------------------------#
        #        B.10 Ageing Reduction Factor                                #
        # ------------------------------------------------------------------ #

        def aging_reduction_factor(self, current_health_score):
            if (current_health_score <= 2):
                return 1
            elif (current_health_score > 2 and current_health_score <= 5.5):
                return ((current_health_score - 2) / 7) + 1
            else:
                return 1.5
        

        # -------------------------------------------------------------------#
        #        B.10 Duty  Factor                                           #
        # ------------------------------------------------------------------ #

        def get_tf_duty_factor(self):
            if (self.grid_or_edge == GridEdge.PRIMARY) : # DISTRIBUTION or PRIMARY
                if (self.utilisation_pct <= 0.5): return 0.9
                elif (0.5 < self.utilisation_pct and self.utilisation_pct <= 0.7): return 0.95
                elif (0.7 < self.utilisation_pct and self.utilisation_pct <= 1.0): return 1.0
                elif (self.utilisation_pct > 1.0): return 1.4
                else: return 1.0
            else:
                # GRID or PRIMARY
                if (self.utilisation_pct <= 0.5): return 1.0
                elif (0.5 < self.utilisation_pct and self.utilisation_pct <= 0.7): return 1.05
                elif (0.7 < self.utilisation_pct and self.utilisation_pct <= 1.0): return 1.1
                elif (self.utilisation_pct > 1.0): return 1.4
                else: return 1.0

        def get_tc_duty_factor(self):
            if (self.avg_daily_tap <= 7): return 0.9
            elif (7 < self.avg_daily_tap and self.avg_daily_tap <= 14): return 1
            elif (14 < self.avg_daily_tap and self.avg_daily_tap <= 28): return 1.2
            elif (self.avg_daily_tap > 28): return 1.3
            else: return 1.0

        def get_expected_life(self, normal_expected_life, duty_factor, location_factor):
            # print(f"normal_expected_life : {normal_expected_life} duty_factor:{duty_factor} location_factor: {location_factor}")
            return normal_expected_life / (duty_factor * location_factor)

        #'beta_1(expected_life_years = 10)
        def beta_1(self, expected_life_years):
            # the Health Score of a new asset
            h_new = 0.5
            # the Health Score of the asset when it reaches its Expected Life
            h_expected_life = 5.5
            # print(f"beta_1 ======>>>>> : { np.log(h_expected_life / h_new) / expected_life_years}")
            return (math.log(h_expected_life / h_new) / expected_life_years)

        #' @examples
        #'beta_2(current_health_score = 1, age = 25)
        def beta_2(self, current_health_score, age):
             # the Health Score of a new asset
            h_new = 0.5
            # print(f"beta_2 ======>>>>> : current_health_score: { current_health_score }  beta_2:{ np.log(current_health_score / h_new) / age}  age : { age}")
            return (math.log(current_health_score / h_new) / age)

        #' # 6.6/ 11 kv transformer age 10 years and an initial age rate of 0.05
        #' initial_health(b1 = 0.05, age = 10)
        def initial_health(self, b1, age):
            # the Health Score of a new asset
            h_new = 0.5
            # initial_health_score is capped at 5.5
            # return (min(0.5, h_new * np.exp(b1 * age)))
            return  h_new * np.exp(b1 * age)

        #' # An asset e.g. a transformer with an expcted life of 50 years
        #' expected_life(normal_expected_life = 50,
        #'               duty_factor = 1,
        #'               location_factor = 1)
        def expected_life(self, normal_expected_life, duty_factor, location_factor):
            return (normal_expected_life / (duty_factor * location_factor))


        #'current_health(initial_health_score = 0.5,
        #'               health_score_factor = 0.33,
        #'               health_score_cap = 10,
        #'               health_score_collar = 0.5,
        #'               reliability_factor = 1)
        def current_health(self, initial_health_score,
                            health_score_factor,
                            health_score_cap,
                            health_score_collar,
                            reliability_factor):
            # print(f"initial_health_score: {initial_health_score} health_score_factor:{health_score_factor}")
            # Default Values
            if (health_score_cap == 0): health_score_cap = 10
            if (health_score_collar == 0): health_score_collar = 0.5
            if (reliability_factor == 0): reliability_factor = 1

            # Eq. 5
            current_health_score = (float(initial_health_score) * float(health_score_factor) * reliability_factor)
            # print(f"{initial_health_score} current_health_score: {current_health_score} health_score_factor: { health_score_factor} health_score_cap: { health_score_cap} health_score_collar { health_score_collar} reliability_factor : {reliability_factor}")
            # Eq. 6
            if (current_health_score > health_score_cap):
                current_health_score = health_score_cap

            # Eq. 7
            reliability_collar = health_score_collar

            if (current_health_score < min(health_score_collar, reliability_collar)):
                current_health_score = max(health_score_collar, reliability_collar)

            # See page 25 and the example on page 219
            if (current_health_score > 10): current_health_score = 10
            if (current_health_score < 0.5): current_health_score = 0.5
            return current_health_score

        # -------------------------------------------------------------------#
        #        B.3 Location Factor                                         #
        #        TABLE 22: DISTANCE FROM COAST FACTOR LOOKUP TABLE           #
        #        TABLE 23: ALTITUDE FACTOR LOOKUP TABLE                      #
        #        TABLE 24: CORROSION CATEGORY FACTOR LOOKUP TABLE            #
        #        TABLE 25: INCREMENT CONSTANTS                               #
        # ------------------------------------------------------------------ #
        # def get_location_factor(self, placement,
        #                         altitude_m,
        #                         distance_from_coast_km,
        #                         corrosion_category_index,
        #                         asset_type):
        
        def get_location_factor(self):
             increment       = 0.05  #  For Transformers
             distance_from_coast_factor = 0
             altitude_factor = 0
             corrosion_factor = 0
             initial_location_factor = 0
             n_factor_greater_than_1 = 0
             
             # TABLE 22: DISTANCE FROM COAST FACTOR LOOKUP TABLE
             if (self.distance_from_coast_km <= 1): self.distance_from_coast_factor = 1.35
             elif (1 < self.distance_from_coast_km and self.distance_from_coast_km <= 5): self.distance_from_coast_factor = 1.1
             elif (5 < self.distance_from_coast_km and self.distance_from_coast_km <= 10): self.distance_from_coast_factor = 1.05
             elif (10 < self.distance_from_coast_km and self.distance_from_coast_km <= 20): self.distance_from_coast_factor = 1
             elif (self.distance_from_coast_km > 20): self.distance_from_coast_factor = 0.9
             else: self.distance_from_coast_factor = 1

             min_distance_from_coast_km = 0.9
             if (distance_from_coast_factor > 1): n_factor_greater_than_1 = n_factor_greater_than_1 + 1

             # TABLE 23: ALTITUDE FACTOR LOOKUP TABLE
             if (self.altitude_m <= 100): altitude_factor = 0.9
             elif (100 < self.altitude_m and self.altitude_m <= 200): altitude_factor = 1
             elif (200 < self.altitude_m and self.altitude_m <= 300): altitude_factor = 1.05
             elif (self.altitude_m > 300): altitude_factor = 1.1
             else: altitude_factor = 1

             min_altitude_factor = 0.9
             if (altitude_factor > 1): n_factor_greater_than_1 = n_factor_greater_than_1 + 1;

             # TABLE 24: CORROSION CATEGORY FACTOR LOOKUP TABLE
             if (self.corrosion_category_index == 1): corrosion_factor = 0.9
             elif (self.corrosion_category_index == 2): corrosion_factor = 0.95
             elif (self.corrosion_category_index == 3): corrosion_factor = 1
             elif (self.corrosion_category_index == 4): corrosion_factor = 1.1
             elif (self.corrosion_category_index == 5): corrosion_factor = 1.25
             else: corrosion_factor = 1

             min_corrosion_factor = 0.9
             if (corrosion_factor > 1): n_factor_greater_than_1 = n_factor_greater_than_1 + 1
             
             if (self.placement == Env.OUTDOOR):
                if (max(distance_from_coast_factor, max(altitude_factor, corrosion_factor)) > 1):
                    return (max(distance_from_coast_factor, max(altitude_factor, corrosion_factor)) + (n_factor_greater_than_1 - 1) * increment);
                else:
                    return min(distance_from_coast_factor, min(altitude_factor, corrosion_factor))
             else:
                if (max(distance_from_coast_factor, max(altitude_factor, corrosion_factor)) > 1):
                    initial_location_factor = (max(distance_from_coast_factor, max(altitude_factor, corrosion_factor)) + (n_factor_greater_than_1 - 1) * increment);
                else:
                    initial_location_factor = (max(distance_from_coast_factor, max(altitude_factor, corrosion_factor)));

                min_initial_location_factor = (min(min_distance_from_coast_km, min(min_altitude_factor, min_corrosion_factor)))

                return 0.25 * (initial_location_factor - min_initial_location_factor) + min_initial_location_factor

        def get_health_score_modifier(self, health_score_factor, health_score_cap, health_score_collar):
            return {
                "health_score_factor"  : health_score_factor,
                "health_score_cap"     : health_score_cap,
                "health_score_collar"  : health_score_collar 
            }

        def get_meas_cond_modifier(self, measured_condition_factor,measured_condition_cap, measured_condition_collar):

            return {
                 "measured_condition_factor": measured_condition_factor,
                 "measured_condition_cap"   : measured_condition_cap ,
                 "measured_condition_collar": measured_condition_collar
            }

        def get_observ_cond_modifier(self, observed_condition_factor, observed_condition_cap, observed_condition_collar):
            return  {
                 "observed_condition_factor": observed_condition_factor,
                 "observed_condition_cap"   : observed_condition_cap,
                 "observed_condition_collar": observed_condition_collar
            }

        def get_oil_test_modifier(self):

             oil_ret_val = get_oil_condition_vars(self.transformer_type, self.moisture, self.acidity, self.bd_strength)
             
             # Oil condition score
             oil_condition_score = 80 * oil_ret_val["moisture_score"] \
             + 125 * oil_ret_val["acidity_score"] \
             + 80 * oil_ret_val["bd_strength_score"]
             
             # Oil condition factor | Oil condition collar
             oil_cap_val = get_oil_condition_caps(self.transformer_type, oil_condition_score)
             oil_condition_factor   = oil_cap_val["oil_factor"]
             oil_condition_collar   = oil_cap_val["oil_collar"]
             oil_condition_cap      = 10
                             
             # print("\n----")
             # print(f" oil_condition_factor: {oil_condition_factor}  oil_condition_collar: { oil_condition_collar } oil_condition_cap: {oil_condition_cap}")

             return {
                    "oil_condition_factor": oil_condition_factor,
                    "oil_condition_collar": oil_condition_collar,
                    "oil_condition_cap":oil_condition_cap
             }
                
        def get_dga_test_modifier(self):
                # dga_scores = self.utility.GetDGAScores(self.transformer_type, self.hydrogen, self.methane, self.ethylene,
                #     self.acetylene, self.ethane, self.hydrogen_pre, self.methane_pre, self.acetylene_pre, self.ethylene_pre, self.ethane_pre)
                
                # DGA tests score ----------------------------------------------------------
                # dga_test_score_pre = (50 * dga_scores["hydrogen_pre_score"]) + (30 * dga_scores["methane_pre_score"])
                # + (30 * dga_scores["ethylene_pre_score"]) + (30 * dga_scores["ethane_pre_score"])
                # + (120 * dga_scores["acetylene_pre_score"])

                # dga_test_score     = (50 * dga_scores["hydrogen_score"]) + (30 * dga_scores["methane_score"])
                # + (30 * dga_scores["ethylene_score"]) + (30 * dga_scores["ethane_score"])
                # + (120 * dga_scores["acetylene_score"])
                
                dga_scores = get_dga_attributes(self.transformer_type)
                dga_test_score      = dga_scores["dga_test_score"]
                dga_test_score_pre  = dga_scores["dga_test_score_pre"]


                dga_test_changes = ((dga_test_score / dga_test_score_pre) - 1) * 100

                # DGA Test Collar
                dga_test_collar = 0
                if (dga_test_score / 220 < 1): dga_test_collar = 1
                else: dga_test_collar = dga_test_score / 220
                if (dga_test_collar > 7): dga_test_collar = 7

                # DGA Test Factor
                dga_test_rec    = pd.DataFrame(get_condition_score(self.transformer_type, Modes.DGA_TEST_FACTOR.name, dga_test_changes))                              
                dga_test_factor = float(dga_test_rec["score"].item())


                # DGA Test Cap
                dga_test_cap = 10
                # print("\n----")
                # print(f" dga_test_factor: {dga_test_factor}  dga_test_collar: { dga_test_collar } dga_test_cap: {dga_test_cap}")
                
                return {
                    "dga_test_factor": dga_test_factor,
                    "dga_test_collar": dga_test_collar,
                    "dga_test_cap"   : dga_test_cap 
                }

        def get_ffa_test_modifier(self):
            # ffa test factor
            ffa_test_rec = pd.DataFrame(get_condition_score(self.transformer_type, Modes.FFA_TEST_FACTOR.name, self.furfuraldehyde))
            ffa_test_factor = float(ffa_test_rec["score"].item())
            # ffa test cap
            ffa_test_cap = 10

            # ffa test collar
            ffa_test_collar = 0
            if (np.isnan(2.33 * math.pow(self.furfuraldehyde, 0.68))): ffa_test_collar = 0.5
            else: ffa_test_collar = float(2.33 * math.pow(self.furfuraldehyde, 0.68))

            if (ffa_test_collar > 7): ffa_test_collar = 7
            # print("\n----")
            # print(f" ffa_test_factor: {ffa_test_factor} ffa_test_cap: {ffa_test_cap} ffa_test_collar: {ffa_test_collar}")

            return {
                     "ffa_test_factor": ffa_test_factor,
                     "ffa_test_cap": ffa_test_cap,
                     "ffa_test_collar": ffa_test_collar
            }


        def pof_main_tank(self):
            # Normal expected life for transformer (tf) and tapchanger (tc) -----------

            # Duty factor -----------------------------------------------------------------
            duty_factor_tf = self.get_tf_duty_factor()

            # Location factor --------------------------------------------------------------
            location_factor_transformer = self.get_location_factor()
            
            # Expected life for transformer ------------------------------------------------
            expected_life_years_tf = self.get_expected_life(self.normal_expected_life_tf, duty_factor_tf, location_factor_transformer)
            # print(f" duty_factor_tf : { duty_factor_tf } location_factor_transformer: {location_factor_transformer} expected_life_years_tf: {expected_life_years_tf}")

            # -----------------------------------------------------------------------------------------------------#
            # Typically, the Health Score Collar is 0.5 and Health Score Cap is 10, implying no overriding         #
            # of the Health Score. However, in some instances these parameters are set to other values in the      #
            # Health Score Modifier calibration tables. These overriding values are shown in Table 35 to Table 202 #
            # and Table 207 in Appendix B.                                                                         #
            # -----------------------------------------------------------------------------------------------------#
            
            # Measured condition inputs ---------------------------------------------
            mcm_mmi_cal_df                      = pd.DataFrame(get_mmi_factors(self.transformer_type, Modes.MEASURED_CONDTION_MODIFIER.name))
            print(f"mcm_mmi_cal_df-{self.transformer_type} - {mcm_mmi_cal_df}")
            factor_divider_1_tf                 = float(mcm_mmi_cal_df.loc[mcm_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'df1'].item()) 
            factor_divider_2_tf                 = float(mcm_mmi_cal_df.loc[mcm_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'df2'].item())
            max_no_combined_factors_tf          = float(mcm_mmi_cal_df.loc[mcm_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'maxnofc'].item()) 
            print(f"factor_divider_1_tf : { factor_divider_1_tf } factor_divider_2_tf: { factor_divider_2_tf} max_no_combined_factors_tf: {max_no_combined_factors_tf}")

            # Partial discharge transformer ----------------------------------------------
            partial_discharge_tf             = self.map_score_value(self.partial_discharge_tf, AssetCond.PARTIAL_DISCHARGE.name)
            mci_tf_partial_discharge         = pd.DataFrame(get_meas_ci_factors(self.transformer_type, partial_discharge_tf, AssetCond.PARTIAL_DISCHARGE.name))                       
            ci_factor_partial_discharge_tf   = float(mci_tf_partial_discharge.loc[mci_tf_partial_discharge['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())  # mci_tf.Infactor
            ci_cap_partial_discharge_tf      = float(mci_tf_partial_discharge.loc[mci_tf_partial_discharge['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())     # mci_tf.Incap
            ci_collar_partial_discharge_tf   = float(mci_tf_partial_discharge.loc[mci_tf_partial_discharge['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())   # mci_tf.Incollar
            print(f"ci_factor_partial_discharge_tf :{ci_factor_partial_discharge_tf} ci_cap_partial_discharge_tf: {ci_cap_partial_discharge_tf} ci_collar_partial_discharge_tf:{ ci_collar_partial_discharge_tf}")

            # Temperature readings ----------------------------------------------------
            temperature_reading              = self.map_score_value(self.temperature_reading, AssetCond.TEMPERATURE_READINGS.name)
            mci_tf_temp_readings             = pd.DataFrame(get_meas_ci_factors(self.transformer_type, temperature_reading, AssetCond.TEMPERATURE_READINGS.name))
            ci_factor_temp_reading           = float(mci_tf_temp_readings.loc[mci_tf_temp_readings['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item()) # mci_tf_temp.Infactor
            ci_cap_temp_reading              = float(mci_tf_temp_readings.loc[mci_tf_temp_readings['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())    # mci_tf_temp.Incap
            ci_collar_temp_reading           = float(mci_tf_temp_readings.loc[mci_tf_temp_readings['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item()) # mci_tf_temp.Incollar
            print(f"ci_factor_temp_reading : {ci_factor_temp_reading} ci_cap_temp_reading:{ci_cap_temp_reading} ci_collar_temp_reading:{ci_collar_temp_reading}")

            # Measured condition factor -----------------------------------------------
            factors_tf = [ci_factor_partial_discharge_tf, ci_factor_temp_reading ]
            measured_condition_factor_tf = self.Mmi(factors_tf,
                                factor_divider_1_tf,
                                factor_divider_2_tf,
                                max_no_combined_factors_tf)

            measured_condition_cap_tf        = min(ci_cap_partial_discharge_tf, ci_cap_temp_reading)
            measured_condition_collar_tf     = max(ci_collar_partial_discharge_tf, ci_collar_temp_reading)
            measured_condition_modifier_tf   = self.get_meas_cond_modifier(measured_condition_factor_tf,
                                                                            measured_condition_cap_tf,
                                                                            measured_condition_collar_tf)
            print(f"measured_condition_cap_tf : { measured_condition_cap_tf} measured_condition_collar_tf: {measured_condition_collar_tf} measured_condition_modifier_tf:{measured_condition_modifier_tf}")

            # Observed condition inputs ---------------------------------------------
            oci_mmi_cal_df                   = pd.DataFrame(get_mmi_factors(self.transformer_type, Modes.OBSERVED_CONDTION_MODIFIER.name))
            factor_divider_1_tf_obs          = float(oci_mmi_cal_df.loc[oci_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'df1'].item())  # oci_mmi.Df1
            factor_divider_2_tf_obs          = float(oci_mmi_cal_df.loc[oci_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'df2'].item())  # oci_mmi.Df2
            max_no_combined_factors_tf_obs   = float(oci_mmi_cal_df.loc[oci_mmi_cal_df['subcomp'] == SubAsset.MAIN_TANK.name, 'maxnofc'].item())  # oci_mmi.Maxnofc
            print(f"MmiFactors : factor_divider_1_tf_obs:{ factor_divider_1_tf_obs} factor_divider_2_tf_obs:{ factor_divider_2_tf_obs} max_no_combined_factors_tf_obs : {max_no_combined_factors_tf_obs}")

            # Main tank condition
            main_tank                        = self.map_score_value(self.main_tank, AssetCond.MAIN_TANK_CONDITION.name)
            
            oci_tf_main_tank_cond            = pd.DataFrame(get_obs_ci_factors(self.transformer_type, main_tank, AssetCond.MAIN_TANK_CONDITION.name))
            Oi_factor_main_tank              = float(oci_tf_main_tank_cond.loc[oci_tf_main_tank_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())   # oci_tank_tf.Infactor
            Oi_cap_main_tank                 = float(oci_tf_main_tank_cond.loc[oci_tf_main_tank_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())      # oci_tank_tf.Incap
            Oi_collar_main_tank              = float(oci_tf_main_tank_cond.loc[oci_tf_main_tank_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())   # oci_tank_tf.Incollar
            print(f"Oi_factor_main_tank : { Oi_factor_main_tank} Oi_collar_main_tank: {Oi_collar_main_tank} Oi_cap_main_tank: { Oi_cap_main_tank}")
                
            # Coolers/Radiator condition
            coolers_radiator                 = self.map_score_value(self.coolers_radiator, AssetCond.COOLERS_RADIATOR_CONDITION.name)
            oci_tf_cooler_radiatr_cond       = pd.DataFrame(get_obs_ci_factors(self.transformer_type, coolers_radiator, AssetCond.COOLERS_RADIATOR_CONDITION.name))
            Oi_factor_coolers_radiator       = float(oci_tf_cooler_radiatr_cond.loc[oci_tf_cooler_radiatr_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())     # oci_tf_cooler.Infactor;
            Oi_cap_coolers_radiator          = float(oci_tf_cooler_radiatr_cond.loc[oci_tf_cooler_radiatr_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())        # oci_tf_cooler.Incap;
            Oi_collar_coolers_radiator       = float(oci_tf_cooler_radiatr_cond.loc[oci_tf_cooler_radiatr_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())     # oci_tf_cooler.Incollar;
            print(f"Oi_factor_coolers_radiator : { Oi_factor_coolers_radiator} Oi_cap_coolers_radiator: { Oi_cap_coolers_radiator} Oi_collar_coolers_radiator: {Oi_collar_coolers_radiator}")

            # Bushings
            bushings                         = self.map_score_value(self.bushings, AssetCond.BUSHINGS_CONDITION.name)
            oci_tf_bushings_cond             = pd.DataFrame(get_obs_ci_factors(self.transformer_type, bushings, AssetCond.BUSHINGS_CONDITION.name))
            Oi_factor_bushings               = float(oci_tf_bushings_cond.loc[oci_tf_bushings_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())     # oci_tf_bushings.Infactor;
            Oi_cap_bushings                  = float(oci_tf_bushings_cond.loc[oci_tf_bushings_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())        # oci_tf_bushings.Incap;
            Oi_collar_bushings               = float(oci_tf_bushings_cond.loc[oci_tf_bushings_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())     # oci_tf_bushings.Incollar;
            print(f"Oi_factor_bushings : {Oi_factor_bushings} Oi_cap_bushings: {Oi_cap_bushings} Oi_collar_bushings: {Oi_collar_bushings}")
                       
            # Kiosk
            kiosk                            = self.map_score_value(self.kiosk, AssetCond.KIOSK_CONDITION.name)
            oci_tf_kiosk_cond                = pd.DataFrame(get_obs_ci_factors(self.transformer_type, kiosk, AssetCond.KIOSK_CONDITION.name))
            Oi_factor_kiosk                  = float(oci_tf_kiosk_cond.loc[oci_tf_kiosk_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())     # oci_tf_kiosk.Infactor;
            Oi_cap_kiosk                     = float(oci_tf_kiosk_cond.loc[oci_tf_kiosk_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())        # oci_tf_kiosk.Incap;
            Oi_collar_kiosk                  = float(oci_tf_kiosk_cond.loc[oci_tf_kiosk_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())     # oci_tf_kiosk.Incollar;
            print(f"Oi_factor_kiosk : {Oi_factor_kiosk} Oi_cap_kiosk: {Oi_cap_kiosk} Oi_collar_kiosk: {Oi_collar_kiosk}")
                
            # Cable box
            cable_boxes                      = self.map_score_value(self.cable_boxes, AssetCond.CABLE_BOX_CONDITION.name)
            oci_tf_cable_boxes_cond          = pd.DataFrame(get_obs_ci_factors(self.transformer_type, cable_boxes, AssetCond.CABLE_BOX_CONDITION.name))
            Oi_factor_cable_boxes            = float(oci_tf_cable_boxes_cond.loc[oci_tf_cable_boxes_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'infactor'].item())     # oci_tf_cable.Infactor;
            Oi_cap_cable_boxes               = float(oci_tf_cable_boxes_cond.loc[oci_tf_cable_boxes_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incap'].item())        # oci_tf_cable.Incap;
            Oi_collar_cable_boxes            = float(oci_tf_cable_boxes_cond.loc[oci_tf_cable_boxes_cond['subcomp'] == SubAsset.MAIN_TANK.name, 'incollar'].item())     # oci_tf_cable.Incollar;
            print(f"Oi_factor_cable_boxes :{Oi_factor_cable_boxes} Oi_cap_cable_boxes: {Oi_cap_cable_boxes} Oi_collar_cable_boxes:{Oi_collar_cable_boxes}")

            # Observed condition factor, cap, collar, modifier ----------------------
            factors_tf_obs                  = [Oi_factor_main_tank,  Oi_factor_coolers_radiator, Oi_factor_bushings, Oi_factor_kiosk, Oi_factor_cable_boxes]
            observed_condition_factor_tf    = self.Mmi(factors_tf_obs, factor_divider_1_tf_obs, factor_divider_2_tf_obs, max_no_combined_factors_tf_obs)
            observed_condition_cap_tf       = min(min(Oi_cap_main_tank, Oi_cap_coolers_radiator), min(min(Oi_cap_bushings, Oi_cap_kiosk), Oi_cap_cable_boxes))
            observed_condition_collar_tf    = max(max(Oi_collar_main_tank, Oi_collar_coolers_radiator), max(max(Oi_collar_bushings, Oi_collar_kiosk), Oi_collar_cable_boxes))
            observed_condition_modifier_tf  = self.get_observ_cond_modifier(observed_condition_factor_tf, observed_condition_cap_tf, observed_condition_collar_tf)
    
            # Oil, DGA, and FFA test modifiers --------------------------------------
            oil_test_mod = self.get_oil_test_modifier()
            dga_test_mod = self.get_dga_test_modifier()
            print(f"observed_condition_factor_tf : {observed_condition_factor_tf} observed_condition_cap_tf: {observed_condition_cap_tf} observed_condition_collar_tf:{observed_condition_collar_tf}")

            ffa_test_mod = self.get_ffa_test_modifier()
            print(f"oil_test_mod : {oil_test_mod} dga_test_mod: {dga_test_mod} ffa_test_mod:{ffa_test_mod}")
                
            # Health score factor ---------------------------------------------------
            health_score_factor_for_main        = pd.DataFrame(get_mmi_factors(self.transformer_type, Modes.HEALTH_SCORE_MODIFIER.name))
            factor_divider_1_tf_health          = float(health_score_factor_for_main.loc[health_score_factor_for_main['subcomp'] == SubAsset.MAIN_TANK.name, 'df1'].item()) # health_score.Df1;
            factor_divider_2_tf_health          = float(health_score_factor_for_main.loc[health_score_factor_for_main['subcomp'] == SubAsset.MAIN_TANK.name, 'df2'].item()) # health_score.Df2;
            max_no_combined_factors_tf_health   = float(health_score_factor_for_main.loc[health_score_factor_for_main['subcomp'] == SubAsset.MAIN_TANK.name, 'maxnofc'].item()) # health_score.Maxnofc;
            print(f"factor_divider_1_tf_health : { factor_divider_1_tf_health} factor_divider_2_tf_health: {factor_divider_2_tf_health} max_no_combined_factors_tf_health:{max_no_combined_factors_tf_health}")
                                    
            # Health score modifier --------------------------------------------------
            obs_tf_factor                    = observed_condition_modifier_tf["observed_condition_factor"]
            mea_tf_factor                    = measured_condition_modifier_tf["measured_condition_factor"]
            oil_factor                       = oil_test_mod["oil_condition_factor"]
            dga_factor                       = dga_test_mod["dga_test_factor"]
            ffa_factor                       = ffa_test_mod["ffa_test_factor"]

            factors_tf_health                = [obs_tf_factor, mea_tf_factor, oil_factor, dga_factor, ffa_factor]

            health_score_factor_tf           = self.Mmi(factors_tf_health, factor_divider_1_tf_health, factor_divider_2_tf_health, max_no_combined_factors_tf_health)
            
            health_score_cap_tf              = min(min(observed_condition_modifier_tf["observed_condition_cap"], measured_condition_modifier_tf["measured_condition_cap"]),
                                                        min(min(oil_test_mod["oil_condition_cap"], dga_test_mod["dga_test_cap"]), ffa_test_mod["ffa_test_cap"]))
            
            health_score_collar_tf           = max(max(observed_condition_modifier_tf["observed_condition_collar"], measured_condition_modifier_tf["measured_condition_collar"]),
                                                        max(max(oil_test_mod["oil_condition_collar"], dga_test_mod["dga_test_collar"]), ffa_test_mod["ffa_test_collar"]))
            
            health_score_modifier_tf         = self.get_health_score_modifier(health_score_factor_tf, health_score_cap_tf, health_score_collar_tf)

            # print(f"health_score_factor_tf: {health_score_factor_tf}   health_score_cap_tf : {health_score_cap_tf } health_score_collar_tf: {health_score_collar_tf}")


            # b1 (Initial Ageing Rate) -----------------------------------------------------
            b1_tf = self.beta_1(expected_life_years_tf)
            
            # Initial health score ---------------------------------------------------------
            initial_health_score_tf = self.initial_health(b1_tf, self.age_tf)
            
            current_health_score_tf = self.current_health(initial_health_score_tf,
                                        health_score_modifier_tf["health_score_factor"],
                                        health_score_modifier_tf["health_score_cap"],
                                        health_score_modifier_tf["health_score_collar"], self.reliability_factor)

            # print("\n----")
            # print(f"initial_health_score_tf {initial_health_score_tf} current_health_score_tf: { current_health_score_tf} b1_tf :{b1_tf}")
            return (current_health_score_tf, b1_tf)

        def pof_tap_changer(self):
            
            # Duty factor, Location factor, Expected life for tapchanger ------------------
            duty_factor_tc                  = self.get_tc_duty_factor()
            location_factor_transformer     = self.get_location_factor()
            expected_life_years_tc          = self.get_expected_life(self.normal_expected_life_tc, duty_factor_tc, location_factor_transformer)
            # print(f"duty_factor_tc: {duty_factor_tc} location_factor_transformer:{location_factor_transformer} expected_life_years_tc:{expected_life_years_tc}")


            # Measured condition inputs ---------------------------------------------
            mcm_mmi_cal_df                  = get_mmi_factors(self.transformer_type, Modes.MEASURED_CONDTION_MODIFIER.name)
            mmi_tc                          = mcm_mmi_cal_df.where(mcm_mmi_cal_df.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            factor_divider_1_tc             = mmi_tc.df1
            factor_divider_2_tc             = mmi_tc.df2
            max_no_combined_factors_tc      = mmi_tc.maxnofc

            print(f"factor_divider_1_tc : {factor_divider_1_tc} factor_divider_2_tc: {factor_divider_2_tc} max_no_combined_factors_tc:{max_no_combined_factors_tc}")

            # Partial discharge transformer -------------------------------------------
            mci_tc_partial_discharge        = get_meas_ci_factors(self.partial_discharge_tf, AssetCond.PARTIAL_DISCHARGE.name)
            mci_tc                          = mci_tc_partial_discharge.where(mci_tc_partial_discharge.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            ci_factor_partial_discharge_tc  = mci_tc.infactor
            ci_cap_partial_discharge_tc     = mci_tc.incap
            ci_collar_partial_discharge_tc  = mci_tc.incollar

            # print(f"ci_factor_partial_discharge_tc : {ci_factor_partial_discharge_tc} ci_cap_partial_discharge_tc:{ci_cap_partial_discharge_tc} ci_collar_partial_discharge_tc {ci_collar_partial_discharge_tc}")

            # Measured condition factor, cap, collar and modifier --------------------
            factors_tc                      = { ci_factor_partial_discharge_tc }
            measured_condition_factor_tc    = self.Mmi(factors_tc, factor_divider_1_tc, factor_divider_2_tc, max_no_combined_factors_tc)

            # # print(f"measured_condition_factor_tc :{measured_condition_factor_tc}")
            measured_condition_cap_tc       = ci_cap_partial_discharge_tc
            measured_condition_collar_tc    = ci_collar_partial_discharge_tc
            measured_condition_modifier_tc  = self.get_meas_cond_modifier(measured_condition_factor_tc, measured_condition_cap_tc, measured_condition_collar_tc)

            # Observed condition inputs ---------------------------------------------
            oci_mmi_cal_df                  = get_mmi_factors(self.transformer_type, Modes.OBSERVED_CONDTION_MODIFIER.name)
            oci_mmi                         = oci_mmi_cal_df.where(oci_mmi_cal_df.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            factor_divider_1_tc_obs         = oci_mmi.df1
            factor_divider_2_tc_obs         = oci_mmi.df2
            max_no_combined_factors_tc_obs  = oci_mmi.maxnofc

            # External condition
            oci_tf_tapchanger_ext_cond      = get_obs_ci_factors(self.external_tap, AssetCond.EXTERNAL_CONDITON.name)
            oci_tf_ext_tap                  = oci_tf_tapchanger_ext_cond.where(oci_tf_tapchanger_ext_cond.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            Oi_factor_external_tap          = oci_tf_ext_tap.infactor
            Oi_collar_external_tap          = oci_tf_ext_tap.incap
            Oi_cap_external_tap             = oci_tf_ext_tap.incollar

                # Internal condition
            oci_tf_tapchanger_int_cond      = get_obs_ci_factors(self.internal_tap, AssetCond.INTERNAL_CONDITION.name)
            oci_tf_int_tap                  = oci_tf_tapchanger_int_cond.where(oci_tf_tapchanger_int_cond.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            Oi_factor_internal_tap          = oci_tf_int_tap.infactor
            Oi_collar_internal_tap          = oci_tf_int_tap.incap
            Oi_cap_internal_tap             = oci_tf_int_tap.incollar

            # Drive mechanism
            oci_tf_drive_mechnism_cond      = get_obs_ci_factors(self.mechnism_cond, AssetCond.DRIVE_MECHANISM.name)
            oci_tf_drive                    = oci_tf_drive_mechnism_cond.where(oci_tf_drive_mechnism_cond.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            Oi_factor_mechnism_cond         = oci_tf_drive.infactor
            Oi_cap_mechnism_cond            = oci_tf_drive.incap
            Oi_collar_mechnism_cond         = oci_tf_drive.incollar

            # Selecter diverter contacts
            oci_tf_cond_select_divrter_cst  = get_obs_ci_factors(self.diverter_contacts, AssetCond.SELECTOR_DIVERTER_CONTACTS.name)
            oci_tf_divrter                  = oci_tf_cond_select_divrter_cst.where(oci_tf_cond_select_divrter_cst.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            Oi_factor_diverter_contacts     = oci_tf_divrter.infactor
            Oi_cap_diverter_contacts        = oci_tf_divrter.incap
            Oi_collar_diverter_contacts     = oci_tf_divrter.incollar
            # Selecter diverter braids
            oci_tf_cond_select_divrter_brd  = get_obs_ci_factors(self.diverter_braids, AssetCond.SELECTOR_DIVERTER_BRAIDS.name)
            oci_tf_braids                   = oci_tf_cond_select_divrter_brd.where(oci_tf_cond_select_divrter_brd.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            Oi_factor_diverter_braids       = oci_tf_braids.infactor
            Oi_cap_diverter_braids          = oci_tf_braids.incap
            Oi_collar_diverter_braids       = oci_tf_braids.incollar

            # Observed condition factor, cap, collar, modifier --------------------------------------

            factors_tc_obs                  =  { Oi_factor_external_tap, Oi_factor_internal_tap, Oi_factor_mechnism_cond,
                                                            Oi_factor_diverter_contacts, Oi_factor_diverter_braids }

            observed_condition_factor_tc    = self.Mmi(factors_tc_obs, factor_divider_1_tc_obs,
                                                            factor_divider_2_tc_obs, max_no_combined_factors_tc_obs)

            observed_condition_cap_tc       = min(min(Oi_cap_external_tap, Oi_cap_internal_tap),
                                              min(min(Oi_cap_mechnism_cond, Oi_cap_diverter_contacts), Oi_cap_diverter_braids))
            observed_condition_collar_tc    = min(min(Oi_collar_external_tap, Oi_collar_internal_tap),
                                              min(min(Oi_collar_mechnism_cond, Oi_collar_diverter_contacts), Oi_collar_diverter_braids))
            observed_condition_modifier_tc  = self.get_observ_cond_modifier(observed_condition_factor_tc, observed_condition_cap_tc, observed_condition_collar_tc)

            # Oil, DGA, FFA  test modifier -------------------------------------------------------
            oil_test_mod = self.get_oil_test_modifier()
            dga_test_mod = self.get_dga_test_modifier()
            ffa_test_mod = self.get_ffa_test_modifier()

            # Health score factor ---------------------------------------------------
            health_score_factor_for_tap         = get_mmi_factors(self.transformer_type, Modes.HEALTH_SCORE_MODIFIER.name)
            health_score                        = health_score_factor_for_tap.where(health_score_factor_for_tap.c.subcomp == SubAsset.TAP_CHANGER.name).scalar() 
            # health_score_factor_for_tap.Where(p => p.Subcomp == SubAsset.TAP_CHANGER).FirstOrDefault()
            factor_divider_1_tc_health          = health_score.df1
            factor_divider_2_tc_health          = health_score.df2
            max_no_combined_factors_tc_health   = health_score.maxnofc

            #  Health score factor, cap, collar, modifier ----------------------------
            obs_tc_factor = observed_condition_modifier_tc["observed_condition_factor"]
            meas_tc_factor = measured_condition_modifier_tc["measured_condition_factor"]
            oil_factor = oil_test_mod["oil_condition_factor"]
            dga_factor = dga_test_mod["dga_test_factor"]
            ffa_factor = ffa_test_mod["ffa_test_factor"]

            factors_tc_health = { obs_tc_factor, meas_tc_factor, oil_factor }

            health_score_factor_tc = self.Mmi(factors_tc_health, factor_divider_1_tc_health,
                                                    factor_divider_2_tc_health, max_no_combined_factors_tc_health)

            health_score_cap_tc = min(min(observed_condition_modifier_tc["observed_condition_cap"], measured_condition_modifier_tc["measured_condition_cap"]),
                                  min(min(oil_test_mod["oil_condition_cap"], dga_test_mod["dga_test_cap"]), ffa_test_mod["ffa_test_cap"]))

            health_score_collar_tc = max(max(observed_condition_modifier_tc["observed_condition_collar"], measured_condition_modifier_tc["measured_condition_collar"]),
                                     max(max(oil_test_mod["oil_condition_collar"], dga_test_mod["dga_test_collar"]), ffa_test_mod["ffa_test_collar"]))

            health_score_modifier_tc = self.get_health_score_modifier(health_score_factor_tc, health_score_cap_tc, health_score_collar_tc)

            # b1 (Initial Ageing Rate) -----------------------------------------------------
            b1_tc = self.beta_1(expected_life_years_tc)
            # Initial health score ---------------------------------------------------------
            initial_health_score_tc = self.initial_health(b1_tc, self.age_tc)

            # Current health score ----------------------------------------------------
            current_health_score_tc = self.current_health(initial_health_score_tc,
                                        health_score_modifier_tc["health_score_factor"],
                                        health_score_modifier_tc["health_score_cap"],
                                        health_score_modifier_tc["health_score_collar"], self.reliability_factor)

            return (current_health_score_tc, b1_tc)

        def pof_transformer(self):
            current_health_score_tf, b1_tf = self.pof_main_tank()
            ageing_reduction_factor_tf   = self.aging_reduction_factor(current_health_score_tf)
            ageing_reduction_factor_tc   = 0
            current_health_score         = current_health_score_tf
            print("----------------------")
            print(current_health_score)            
            print("----------------------")
            b1_tc = 0
            b2_tc = 0

            # the Health Score of the asset when it reaches its Expected Life
            b2_tf = self.beta_2(current_health_score_tf, self.age_tf)
            current_health_score_tc = 0

            if (b2_tf > 2 * b1_tf): b2_tf = b1_tf
            elif (current_health_score_tf == 0.5): b2_tf = b1_tf
            # print(f" age_tf :{ self.age_tf} current_health_score_tf: { current_health_score_tf } b2_tf: {b2_tf } b1_tf:{b1_tf}")

            # Tapchanger
            if (self.no_taps == YesNoTap.WITH_TAP):
                # print("There is a tap connected ===<<<<<< >>>>>")
                current_health_score_tc, b1_tc = self.pof_tap_changer()
                b2_tc = self.beta_2(current_health_score_tc, self.age_tc)

                if (b2_tc > 2 * b1_tc):
                    b2_tc = b1_tc
                elif (current_health_score_tc == 0.5):
                    b2_tc = b1_tc

                ageing_reduction_factor_tc  = self.aging_reduction_factor(current_health_score_tc)
                current_health_score        = max(current_health_score_tf, current_health_score_tc)

            # Future probability of failure -------------------------------------------
            H_new = 0.5
            probability_of_failure = (self.k_value * (1 + ((self.c_value * current_health_score) 
                                                           + (math.pow((self.c_value * current_health_score), 2) / math.factorial(2)) 
                                                           + (math.pow((self.c_value * current_health_score), 3) / math.factorial(3)))))

            # print(f"k_value : {self.k_value} c_value: { self.c_value} current_health_score: {current_health_score}")
            # print(f"age_tf: {self.age_tf}  probability_of_failure: {probability_of_failure} current_health_score: {current_health_score}")
            print("======================")
            print(f"probability_of_failure: {probability_of_failure} - health score: {current_health_score}")
            print("======================")
            return current_health_score, probability_of_failure
