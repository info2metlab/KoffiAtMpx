
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import numpy as np
from XUtility import *
from HelpSolverAnalytics import SolverAnalytics



class ThermalSolver:

    def __init__(self) -> None:
        
        self.XfoRatings: Optional[ThermalPlate] = None
        self.ALLResults: List[Thermal] = []
        self.ixLoadPro: List[LoadProfile] = []
        self.AxLoadPro: List[LoadProfile] = []
        self.baPULoad: List[float] = []
        self.sessionId: str = ""
        
        self.DT         = DELTA_TEMP
        self.K_W        = 0.0
        self.K_HS       = 0.0
        self.u_wr       = 0.0
        self.u_hsr      = 0.0
        self.u_hs       = 0.0
        self.u_w        = 0.0

        self.Q_Gen_W    = 0.0
        self.Q_Lost_W   = 0.0
        self.Q_Gen_HS   = 0.0
        self.Q_Lost_HS  = 0.0
        self.Q_Lost_O   = 0.0
        self.Q_Stray    = 0.0
        self.coeff      = 0.0
        self.DTetaToBo  = 0.0
        self.DTetaDoBo  = 0.0

        self.PULoad             = 0.0
        self.Ambient            = 0.0
        self.CalcAvgWind        = 0.0
        self.CalcAvgDuctOil     = 0.0
        self.CalcBottomOil      = 0.0
        self.CalcTopDuctOil     = 0.0
        self.CalcDuctOilAtHS    = 0.0
        self.HottestSpot        = 0.0
        self.CalcTopOil         = 0.0
        self.CalcAvgOil         = 0.0

        self.Aging              = 0.0
        self.TMOAging           = 0.0
        self.IEC_1SGradient     = 0.0
        self.IEC_2SGradient     = 0.0
        self.TOTimeCst          = 0.0
        self.WindTimeCst        = 0.0

        self.SampleTime         = 0.0
        self.runCounter         = 0

        self.OxyContent         = 0.0
        self.MoisWCPContent     = 0.0
        self.InsulationType: Optional[PaperTypes] = None

        self.currentPUFactor = 0.0
        self.OptimalPUFactor = 0.0
        self.ThermalAnalytics = SolverAnalytics()

    def IEC60354_Assessment(self) -> None:
        runCounter              = 0
        converge = 0
        self.Aging              = 0.0
        self.TMOAging           = 0.0
        self.IEC_1SGradient     = 0.0

        IEC_1SGradient = (
            self.ThermalAnalytics.k21_cst
            * self.ThermalAnalytics.rated_hsr_to_tor
            * math.pow(self.ixLoadPro[runCounter].sumpul, self.ThermalAnalytics.winding_exp)
        )
        IEC_2SGradient = (
            (self.ThermalAnalytics.k21_cst - 1)
            * self.ThermalAnalytics.rated_hsr_to_tor
            * math.pow(self.ixLoadPro[runCounter].sumpul, self.ThermalAnalytics.winding_exp)
        )

        dTetaTo_i = self.ThermalAnalytics.rated_top_oil * math.pow(
            (self.ThermalAnalytics.loss_ratio * math.pow(self.ixLoadPro[runCounter].sumpul, 2.0) + 1)
            / (self.ThermalAnalytics.loss_ratio + 1),
            self.ThermalAnalytics.oil_exp,
        )
        self.CalcTopOil = dTetaTo_i + self.ixLoadPro[runCounter].sumamb
        self.HottestSpot = self.CalcTopOil + (IEC_1SGradient - IEC_2SGradient)

        self.ALLResults[runCounter].IECPULoad = self.ixLoadPro[runCounter].sumpul
        self.ALLResults[runCounter].IECMva = (
            self.ixLoadPro[runCounter].sumpul * self.ThermalAnalytics.per_unit_base_kva
        ) / 1000
        self.ALLResults[runCounter].IECHST = self.HottestSpot
        self.ALLResults[runCounter].IECTOT = self.CalcTopOil
        self.ALLResults[runCounter].IECLOL = 0.0

        TOTimeCst = self.ThermalAnalytics.iec_to_time_cst
        WindTimeCst = self.ThermalAnalytics.iec_wind_time_cst

        while True:
            self.SampleTime = 0
            for runCounter in range(1, len(self.ixLoadPro)):
                self.SampleTime = self.ixLoadPro[runCounter].time
                PULoad = self.ixLoadPro[runCounter].sumpul
                Ambient = self.ixLoadPro[runCounter].sumamb

                coeff = TOTimeCst * self.ThermalAnalytics.k11_cst / self.ThermalAnalytics.dt
                self.CalcTopOil = (1 / (1 + coeff)) * (
                    self.ThermalAnalytics.rated_top_oil
                    * math.pow((self.ThermalAnalytics.loss_ratio * math.pow(PULoad, 2.0) + 1)
                        / (self.ThermalAnalytics.loss_ratio + 1),
                        self.ThermalAnalytics.iec_oil_exp,
                    )
                    + (coeff * self.CalcTopOil)
                    + Ambient
                )

                coeff = self.ThermalAnalytics.k22_cst * WindTimeCst / self.ThermalAnalytics.dt
                IEC_1SGradient = (1 / (1 + coeff)) * (
                    self.ThermalAnalytics.k21_cst
                    * self.ThermalAnalytics.rated_hsr_to_tor
                    * math.pow(PULoad, self.ThermalAnalytics.iec_winding_exp)
                    + coeff * IEC_1SGradient
                )

                coeff = TOTimeCst / (self.ThermalAnalytics.k22_cst * self.ThermalAnalytics.dt)
                IEC_2SGradient = (1 / (1 + coeff)) * (
                    (self.ThermalAnalytics.k21_cst - 1)
                    * self.ThermalAnalytics.rated_hsr_to_tor
                    * math.pow(PULoad, self.ThermalAnalytics.iec_winding_exp)
                    + coeff * IEC_2SGradient
                )

                self.HottestSpot = self.CalcTopOil + (IEC_1SGradient - IEC_2SGradient)

                self.TMOAging += self.ThermalAnalytics.tmo_loss_of_life(
                    self.HottestSpot,
                    self.OxyContent,
                    self.MoisWCPContent,
                    LoadingStandard.IEC60354,
                    self.InsulationType,
                ) * self.ThermalAnalytics.dt

                current = self.ALLResults[runCounter]
                current.IECPULoad = PULoad
                current.IECHST = self.HottestSpot
                current.IECTOT = self.CalcTopOil
                current.IECLOL = round(
                    ((self.TMOAging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100)
                    / self.ThermalAnalytics.life_time,
                    4,
                )
                current.IECMva = (PULoad * self.ThermalAnalytics.per_unit_base_kva) / 1000
                current.IECMargin = current.IECMva - current.basicMVA

            if abs(self.ALLResults[-1].IECHST - self.ALLResults[0].IECHST) < 0.01:
                self.XfoRatings.IECPeakTopOil = max(t.IECTOT for t in self.ALLResults)
                self.XfoRatings.IECPeakHotSpot = max(t.IECHST for t in self.ALLResults)
                self.XfoRatings.IECPeakLoL = (
                    (self.TMOAging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100
                ) / self.ThermalAnalytics.life_time

                self.XfoRatings.IECPeakPUL = max(t.IECPULoad for t in self.ALLResults)
                self.XfoRatings.IECPeakMVA = max(t.IECMva for t in self.ALLResults)
                self.XfoRatings.IECMargin = max(t.IECMargin for t in self.ALLResults)
                if self.XfoRatings.IECMargin <= 0:
                    self.XfoRatings.IECMargin = min(t.IECMargin for t in self.ALLResults)

                self.XfoRatings.IECttpTOT = next(
                    (t.time for t in self.ALLResults if t.IECTOT == self.XfoRatings.IECPeakTopOil),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IECttpHST = next(
                    (t.time for t in self.ALLResults if t.IECHST == self.XfoRatings.IECPeakHotSpot),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IECttpMVA = next(
                    (t.time for t in self.ALLResults if t.IECMva == self.XfoRatings.IECPeakMVA),
                    self.ALLResults[-1].time,
                )
                break

            converge += 1
            runCounter = 0
            self.Aging = 0.0
            self.TMOAging = 0.0
            self.ALLResults[runCounter].IECPULoad = self.ixLoadPro[runCounter].sumpul
            self.ALLResults[runCounter].IECHST = self.ALLResults[-1].IECHST
            self.ALLResults[runCounter].IECTOT = self.ALLResults[-1].IECTOT
            self.ALLResults[runCounter].IECLOL = 0.0

            if converge > CONVERGE_MAX:
                logger.info("The IEC calculation is not converging for %s", self.XfoRatings.LoadType)
                break

    def IEEE7_Assessment(self) -> None:
        run_counter = 0
        converge = 0
        self.Aging = 0.0
        self.TMOAging = 0.0

        d_teta_to_i = self.ThermalAnalytics.top_oil_rise * math.pow(
            (self.ThermalAnalytics.loss_ratio * math.pow(self.ixLoadPro[run_counter].sumpul, 2.0) + 1)
            / (self.ThermalAnalytics.loss_ratio + 1),
            self.ThermalAnalytics.oil_exp,
        )
        self.CalcTopOil = d_teta_to_i + self.ixLoadPro[run_counter].sumamb
        self.HottestSpot = (
            self.ThermalAnalytics.rated_hsr_to_tor
            * math.pow(self.ixLoadPro[run_counter].sumpul, 2 * self.ThermalAnalytics.winding_exp)
            + self.CalcTopOil
        )

        current = self.ALLResults[run_counter]
        current.IEEE7PULoad = self.ixLoadPro[run_counter].sumpul
        current.IEEE7Mva = (self.ixLoadPro[run_counter].sumpul * self.ThermalAnalytics.per_unit_base_kva) / 1000
        current.IEEE7HST = self.HottestSpot
        current.IEEE7TOT = self.CalcTopOil
        current.IEEE7LOL = 0.0

        TOTimeCst = self.ThermalAnalytics.iec_to_time_cst

        while True:
            self.SampleTime = 0
            for run_counter in range(1, len(self.ixLoadPro)):
                self.SampleTime = self.ixLoadPro[run_counter].time
                PULoad = self.ixLoadPro[run_counter].sumpul
                Ambient = self.ixLoadPro[run_counter].sumamb
                d_teta_to_u = self.ThermalAnalytics.top_oil_rise * math.pow(
                    (self.ThermalAnalytics.loss_ratio * math.pow(PULoad, 2.0) + 1)
                    / (self.ThermalAnalytics.loss_ratio + 1),
                    self.ThermalAnalytics.oil_exp,
                )

                coeff = TOTimeCst / self.ThermalAnalytics.dt
                self.CalcTopOil = (1 / (1 + coeff)) * (d_teta_to_u + (coeff * self.CalcTopOil) + Ambient)

                coeff = self.ThermalAnalytics.wind_time_cst / self.ThermalAnalytics.dt
                self.HottestSpot = (1 / (1 + coeff)) * (
                    self.ThermalAnalytics.rated_hsr_to_tor * math.pow(PULoad, 2 * self.ThermalAnalytics.winding_exp)
                    + (coeff * self.HottestSpot)
                    + self.CalcTopOil
                )

                self.TMOAging += self.ThermalAnalytics.tmo_loss_of_life(
                    self.HottestSpot,
                    self.OxyContent,
                    self.MoisWCPContent,
                    LoadingStandard.IEEE7,
                    self.InsulationType,
                ) * self.ThermalAnalytics.dt

                current = self.ALLResults[run_counter]
                current.IEEE7PULoad = self.ixLoadPro[run_counter].sumpul
                current.IEEE7HST = self.HottestSpot
                current.IEEE7TOT = self.CalcTopOil
                current.IEEE7LOL = round(
                    ((self.TMOAging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100)
                    / self.ThermalAnalytics.life_time,
                    4,
                )
                current.IEEE7Mva = (self.ixLoadPro[run_counter].sumpul * self.ThermalAnalytics.per_unit_base_kva) / 1000
                current.IEEE7Margin = current.IEEE7Mva - current.basicMVA

            if abs(self.ALLResults[-1].IEEE7HST - self.ALLResults[0].IEEE7HST) < 0.01:
                self.XfoRatings.IEEE7PeakTopOil = max(t.IEEE7TOT for t in self.ALLResults)
                self.XfoRatings.IEEE7PeakHotSpot = max(t.IEEE7HST for t in self.ALLResults)
                self.XfoRatings.IEEE7PeakLoL = (
                    (self.TMOAging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100
                ) / self.ThermalAnalytics.life_time
                self.XfoRatings.IEEE7PeakPUL = max(t.IEEE7PULoad for t in self.ALLResults)
                self.XfoRatings.IEEE7PeakMVA = max(t.IEEE7Mva for t in self.ALLResults)
                self.XfoRatings.IEEE7Margin = max(t.IEEE7Margin for t in self.ALLResults)
                if self.XfoRatings.IEEE7Margin <= 0:
                    self.XfoRatings.IEEE7Margin = min(t.IEEE7Margin for t in self.ALLResults)

                self.XfoRatings.IEEE7ttpTOT = next(
                    (t.time for t in self.ALLResults if t.IEEE7TOT == self.XfoRatings.IEEE7PeakTopOil),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IEEE7ttpHST = next(
                    (t.time for t in self.ALLResults if t.IEEE7HST == self.XfoRatings.IEEE7PeakHotSpot),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IEEE7ttpMVA = next(
                    (t.time for t in self.ALLResults if t.IEEE7Mva == self.XfoRatings.IEEE7PeakMVA),
                    self.ALLResults[-1].time,
                )
                break

            converge += 1
            run_counter = 0
            self.Aging = 0.0
            self.TMOAging = 0.0
            first = self.ALLResults[run_counter]
            first.IEEE7PULoad = self.ixLoadPro[run_counter].sumpul
            first.IEEE7HST = self.ALLResults[-1].IEEE7HST
            first.IEEE7TOT = self.ALLResults[-1].IEEE7TOT
            first.IEEE7LOL = 0.0
            if converge > CONVERGE_MAX:
                logger.info(
                    "The IEEE7 calculation is not converging for %s", getattr(self.XfoRatings, "LoadType", "unknown")
                )
                break

    def IEEEG_Assessment(self) -> bool:
        self.HottestSpot = self.ThermalAnalytics.rated_hot_spot
        self.CalcAvgWind = self.ThermalAnalytics.tested_rated_avg_wind
        self.CalcTopOil = self.ThermalAnalytics.rated_top_oil
        self.CalcTopDuctOil = self.ThermalAnalytics.rated_top_duct_oil
        self.CalcBottomOil = self.ThermalAnalytics.rated_bottom_oil
        self.CalcAvgOil = self.ThermalAnalytics.rated_avg_oil
        self.CalcAvgDuctOil = self.ThermalAnalytics.rated_duct_avg_oil
        self.CalcDuctOilAtHS = self.ThermalAnalytics.rated_duct_oil_at_hs

        Q_Lost_O = 0.0
        Q_Lost_W = 0.0
        Q_Gen_HS = 0.0
        Q_Gen_W = 0.0
        Q_Lost_HS = 0.0
        Q_Stray = 0.0
        run_counter = 0
        self.Aging = 0.0
        self.TMOAging = 0.0
        converge = 0
        result = False

        current = self.ALLResults[run_counter]
        current.IEEEGPULoad = self.ixLoadPro[run_counter].sumpul
        current.IEEEGMva = (self.ixLoadPro[run_counter].sumpul * self.ThermalAnalytics.per_unit_base_kva) / 1000
        current.IEEEGHST = self.HottestSpot
        current.IEEEGAWT = self.CalcAvgWind
        current.IEEEGTOT = self.CalcTopOil
        current.IEEEGTDO = self.CalcTopDuctOil
        current.IEEEGBOT = self.CalcBottomOil
        current.IEEEGAOT = self.CalcAvgOil
        current.IEEEGDAO = self.CalcAvgDuctOil
        current.IEEEGWOT = self.CalcDuctOilAtHS
        current.IEEEGLOL = 0.0

        while True:
            self.SampleTime = 0
            for run_counter in range(1, len(self.ixLoadPro)):
                self.SampleTime = self.ixLoadPro[run_counter].time
                pu_load = self.ixLoadPro[run_counter].sumpul
                ambient = self.ixLoadPro[run_counter].sumamb

                self.CalcAvgDuctOil = (self.CalcTopDuctOil + self.CalcBottomOil) / 2.0
                self.CalcDuctOilAtHS = self.CalcBottomOil + self.ThermalAnalytics.per_unit_heigh_to_hot_spot * (
                    self.CalcTopDuctOil - self.CalcBottomOil
                )

                K_W = (self.CalcAvgWind + self.ThermalAnalytics.temp_factor) / (
                    self.ThermalAnalytics.rated_avg_wind + self.ThermalAnalytics.temp_factor
                )
                Q_Gen_W = self.ThermalAnalytics.dt * math.pow(pu_load, 2) * (
                    K_W * self.ThermalAnalytics.wind_i2r_losses + self.ThermalAnalytics.wind_eddy_loss / K_W
                )

                cooling_modes = {
                    "OA",
                    "OA/FA",
                    "OA/FA/FA",
                    "OA/FOW",
                    "OA/FOA",
                    "OA/FA/FOA",
                    "OA/FOA/FOA",
                    "ONAN",
                    "ONAF",
                    "ONAN/ONAF",
                    "ONAN/ODAF",
                    "ONAN/OFAF",
                    "ONAN/ONAF/ONAF",
                    "ONAN/ONAF/OFAF",
                    "ONAN/OFAF/OFAF",
                    "OA/FA/FOA*",
                }

                if self.CalcAvgWind > self.CalcAvgDuctOil:
                    u_wr = self.ThermalAnalytics.viscosity(
                        (self.ThermalAnalytics.tested_rated_avg_wind + self.ThermalAnalytics.rated_duct_avg_oil) / 2.0
                    )
                    u_w = self.ThermalAnalytics.viscosity((self.CalcAvgWind + self.CalcAvgDuctOil) / 2.0)
                    if self.ThermalAnalytics.i3e_cooling in cooling_modes:
                        Q_Lost_W = math.pow(
                            (self.CalcAvgWind - self.CalcAvgDuctOil)
                            / (self.ThermalAnalytics.tested_rated_avg_wind - self.ThermalAnalytics.rated_duct_avg_oil),
                            1.25,
                        ) * math.pow(u_wr / u_w, 0.25) * (
                            self.ThermalAnalytics.wind_eddy_loss + self.ThermalAnalytics.wind_i2r_losses
                        ) * self.ThermalAnalytics.dt
                    else:
                        Q_Lost_W = (
                            (self.CalcAvgWind - self.CalcAvgDuctOil)
                            / (self.ThermalAnalytics.tested_rated_avg_wind - self.ThermalAnalytics.rated_duct_avg_oil)
                        ) * (self.ThermalAnalytics.wind_eddy_loss + self.ThermalAnalytics.wind_i2r_losses) * self.ThermalAnalytics.dt
                else:
                    Q_Lost_W = 0.0

                if self.CalcAvgWind < self.CalcBottomOil:
                    self.CalcAvgWind = self.CalcBottomOil

                self.CalcAvgWind = ((Q_Gen_W - Q_Lost_W) / self.ThermalAnalytics.mw_cw) + self.CalcAvgWind

                DTetaDoBo = (
                    self.ThermalAnalytics.rated_top_duct_oil - self.ThermalAnalytics.rated_bottom_oil
                ) * math.pow(
                    Q_Lost_W
                    / (
                        (self.ThermalAnalytics.wind_eddy_loss + self.ThermalAnalytics.wind_i2r_losses)
                        * self.ThermalAnalytics.dt
                    ),
                    self.ThermalAnalytics.duct_oil_exp,
                )
                self.CalcTopDuctOil = self.CalcBottomOil + DTetaDoBo

                self.CalcAvgDuctOil = (self.CalcTopDuctOil + self.CalcBottomOil) / 2.0
                self.CalcDuctOilAtHS = self.CalcBottomOil + (
                    DTetaDoBo * self.ThermalAnalytics.per_unit_heigh_to_hot_spot
                )
                K_HS = (self.HottestSpot + self.ThermalAnalytics.temp_factor) / (
                    self.ThermalAnalytics.rated_hot_spot + self.ThermalAnalytics.temp_factor
                )

                if self.CalcTopDuctOil + 0.1 < self.CalcTopOil:
                    self.CalcDuctOilAtHS = self.CalcTopOil

                if self.HottestSpot < self.CalcAvgWind:
                    self.HottestSpot = self.CalcAvgWind

                if self.HottestSpot < self.CalcDuctOilAtHS:
                    self.HottestSpot = self.CalcDuctOilAtHS

                Q_Gen_HS = math.pow(pu_load, 2) * (
                    (self.ThermalAnalytics.pwhs * K_HS) + (self.ThermalAnalytics.pehs / K_HS)
                ) * self.ThermalAnalytics.dt
                u_hsr = self.ThermalAnalytics.viscosity(
                    (self.ThermalAnalytics.rated_hot_spot + self.ThermalAnalytics.rated_duct_oil_at_hs) / 2.0
                )
                u_hs = self.ThermalAnalytics.viscosity((self.HottestSpot + self.CalcDuctOilAtHS) / 2.0)

                if self.HottestSpot > self.CalcDuctOilAtHS:
                    if self.ThermalAnalytics.i3e_cooling in cooling_modes:
                        Q_Lost_HS = math.pow(
                            (self.HottestSpot - self.CalcDuctOilAtHS)
                            / (self.ThermalAnalytics.rated_hot_spot - self.ThermalAnalytics.rated_duct_oil_at_hs),
                            1.25,
                        ) * math.pow(u_hsr / u_hs, 0.25) * (
                            self.ThermalAnalytics.pwhs + self.ThermalAnalytics.pehs
                        ) * self.ThermalAnalytics.dt
                    else:
                        Q_Lost_HS = (
                            (self.HottestSpot - self.CalcDuctOilAtHS)
                            / (self.ThermalAnalytics.rated_hot_spot - self.ThermalAnalytics.rated_duct_oil_at_hs)
                        ) * (self.ThermalAnalytics.pwhs + self.ThermalAnalytics.pehs) * self.ThermalAnalytics.dt
                else:
                    Q_Lost_HS = 0.0

                self.HottestSpot = ((Q_Gen_HS - Q_Lost_HS) / self.ThermalAnalytics.mw_cw) + self.HottestSpot

                Q_Stray = (
                    math.pow(pu_load, 2)
                    * self.ThermalAnalytics.wind_stray_losses
                    * self.ThermalAnalytics.dt
                    / K_W
                )

                if self.CalcAvgOil > ambient:
                    Q_Lost_O = math.pow(
                        (self.CalcAvgOil - ambient)
                        / (self.ThermalAnalytics.rated_avg_oil - self.ThermalAnalytics.rated_ambient),
                        1 / self.ThermalAnalytics.avg_oil_exp,
                    ) * self.ThermalAnalytics.total_losses * self.ThermalAnalytics.dt
                else:
                    Q_Lost_O = 0.0

                self.CalcAvgOil = ((Q_Lost_W + Q_Stray + self.ThermalAnalytics.q_core - Q_Lost_O) / self.ThermalAnalytics.mass_sum) + self.CalcAvgOil

                DTetaToBo = (self.ThermalAnalytics.rated_top_oil - self.ThermalAnalytics.rated_bottom_oil) * math.pow(
                    Q_Lost_O / (self.ThermalAnalytics.total_losses * self.ThermalAnalytics.dt),
                    self.ThermalAnalytics.top_bo_exp,
                )
                self.CalcTopOil = self.CalcAvgOil + (DTetaToBo / 2.0)
                self.CalcBottomOil = self.CalcAvgOil - (DTetaToBo / 2.0)

                if self.CalcBottomOil < ambient:
                    self.CalcBottomOil = ambient

                if self.CalcTopDuctOil < self.CalcBottomOil:
                    self.CalcTopDuctOil = self.CalcBottomOil

                self.Aging += self.ThermalAnalytics.loss_of_life(self.HottestSpot, LoadingStandard.IEEEG) * self.ThermalAnalytics.dt

                current = self.ALLResults[run_counter]
                current.IEEEGPULoad = self.ixLoadPro[run_counter].sumpul
                current.IEEEGHST = self.HottestSpot
                current.IEEEGAWT = self.CalcAvgWind
                current.IEEEGTOT = self.CalcTopOil
                current.IEEEGTDO = self.CalcTopDuctOil
                current.IEEEGBOT = self.CalcBottomOil
                current.IEEEGAOT = self.CalcAvgOil
                current.IEEEGDAO = self.CalcAvgDuctOil
                current.IEEEGWOT = self.CalcDuctOilAtHS
                current.IEEEGLOL = round(
                    ((self.Aging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100)
                    / self.ThermalAnalytics.life_time,
                    4,
                )

                current.IEEEGMva = (
                    self.ixLoadPro[run_counter].sumpul * self.ThermalAnalytics.per_unit_base_kva
                ) / 1000
                current.IEEEGMargin = current.IEEEGMva - current.basicMVA

                current.PerVoltDrop = 0.0
                current.LvMVAOutput = current.IEEEGMva * (1 - current.PerVoltDrop / 100)
                current.LoadLossKW = self.r((current.PerResistance / 100) * current.IEEEGMva)
                current.IEEEGTOR = current.IEEEGTOT - current.sumamb
                current.HalfDelta = (current.IEEEGTOT - current.IEEEGBOT) / 2.0

                current.Wdg2mHotSpGrad = 0.0
                current.IEEEGTOR = self.r(current.IEEEGTOT - current.sumamb)
                current.IEEEGAOR = self.r(current.IEEEGTOR - current.HalfDelta)
                current.IEEEGAWR = self.r(current.IEEEGAOR - current.Wdg2mHotSpGrad)

                current.PerResistance = self.r(self.ThermalAnalytics.per_resistance * self.ixLoadPro[run_counter].sumpul)
                current.PerImpedance = self.r(self.ThermalAnalytics.per_impedance * self.ixLoadPro[run_counter].sumpul)
                current.PerReactance = self.r(
                    math.sqrt(self.ThermalAnalytics.per_impedance) - math.pow(current.PerResistance, 2)
                )

            if abs(self.ALLResults[-1].IEEEGHST - self.ALLResults[0].IEEEGHST) < 0.01:
                self.XfoRatings.IEEEGPeakTopOil = max(0, max(t.IEEEGTOT for t in self.ALLResults))
                self.XfoRatings.IEEEGPeakHotSpot = max(0, max(t.IEEEGHST for t in self.ALLResults))
                self.XfoRatings.IEEEGPeakBottom = max(t.IEEEGBOT for t in self.ALLResults)
                self.XfoRatings.IEEEGPeakLoL = (
                    (self.Aging / self.SampleTime) * self.ThermalAnalytics.load_cycle_period * 100
                ) / self.ThermalAnalytics.life_time

                self.XfoRatings.IEEEGPeakPUL = max(t.IEEEGPULoad for t in self.ALLResults)
                self.XfoRatings.IEEEGPeakMVA = max(t.IEEEGMva for t in self.ALLResults)
                self.XfoRatings.IEEEGMargin = max(t.IEEEGMargin for t in self.ALLResults)

                if self.XfoRatings.IEEEGMargin <= 0:
                    self.XfoRatings.IEEEGMargin = min(t.IEEEGMargin for t in self.ALLResults)

                self.XfoRatings.IEEEGttpTOT = next(
                    (t.time for t in self.ALLResults if t.IEEEGTOT == self.XfoRatings.IEEEGPeakTopOil),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IEEEGttpHST = next(
                    (t.time for t in self.ALLResults if t.IEEEGHST == self.XfoRatings.IEEEGPeakHotSpot),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IEEEGttpMVA = next(
                    (t.time for t in self.ALLResults if t.IEEEGMva == self.XfoRatings.IEEEGPeakMVA),
                    self.ALLResults[-1].time,
                )
                self.XfoRatings.IEEEGttpBOT = next(
                    (t.time for t in self.ALLResults if t.IEEEGBOT == self.XfoRatings.IEEEGPeakBottom),
                    self.ALLResults[-1].time,
                )

                result = True
                break

            converge += 1
            run_counter = 0
            self.Aging = 0.0
            self.TMOAging = 0.0
            Q_Lost_O = 0.0
            Q_Lost_W = 0.0
            Q_Gen_HS = 0.0
            Q_Gen_W = 0.0
            Q_Lost_HS = 0.0
            Q_Stray = 0.0

            current = self.ALLResults[run_counter]
            current.IEEEGPULoad = self.ALLResults[-1].sumpul
            current.IEEEGHST = self.ALLResults[-1].IEEEGHST
            current.IEEEGAWT = self.ALLResults[-1].IEEEGAWT
            current.IEEEGTOT = self.ALLResults[-1].IEEEGTOT
            current.IEEEGTDO = self.ALLResults[-1].IEEEGTDO
            current.IEEEGBOT = self.ALLResults[-1].IEEEGBOT
            current.IEEEGAOT = self.ALLResults[-1].IEEEGAOT
            current.IEEEGDAO = self.ALLResults[-1].IEEEGDAO
            current.IEEEGWOT = self.ALLResults[-1].IEEEGWOT
            current.IEEEGLOL = 0.0

            if converge > CONVERGE_MAX:
                result = False
                break

        return result

    def clear_all_results(self, p: Thermal) -> None:
        p.IEEEGPULoad = 0.0
        p.IEEEGHST = 0.0
        p.IEEEGAWT = 0.0
        p.IEEEGTOT = 0.0
        p.IEEEGTDO = 0.0
        p.IEEEGBOT = 0.0
        p.IEEEGAOT = 0.0
        p.IEEEGDAO = 0.0
        p.IEEEGWOT = 0.0
        p.IEEEGLOL = 0.0
        p.PerVoltDrop = 0.0
        p.LvMVAOutput = 0.0
        p.LoadLossKW = 0.0
        p.IEEEGTOR = 0.0
        p.HalfDelta = 0.0
        p.Wdg2mHotSpGrad = 0.0
        p.IEEEGAOR = 0.0
        p.IEEEGAWR = 0.0
        p.PerResistance = 0.0
        p.PerImpedance = 0.0
        p.PerReactance = 0.0
        p.IEEEGMva = 0.0
        p.IEEEGMargin = 0.0

        if self.XfoRatings:
            self.XfoRatings.IEEEGPeakTopOil = 0
            self.XfoRatings.IEEEGPeakHotSpot = 0
            self.XfoRatings.IEEEGPeakBottom = 0
            self.XfoRatings.IEEEGPeakLoL = 0
            self.XfoRatings.IEEEGPeakPUL = 0
            self.XfoRatings.IEEEGPeakMVA = 0
            self.XfoRatings.IEEEGMargin = 0
            self.XfoRatings.IEEEGttpTOT = 0.0
            self.XfoRatings.IEEEGttpHST = 0.0
            self.XfoRatings.IEEEGttpMVA = 0.0
            self.XfoRatings.IEEEGttpBOT = 0.0

    def print_all_results(self, p: Thermal) -> None:
        self.logger.info("IEEEGTOT:%s IEEEGHST:%s IEEEGLOL:%s IEEEGPULoad:%s", p.IEEEGTOT, p.IEEEGHST, p.IEEEGLOL, p.IEEEGPULoad)

    def print_profiles(self, pro: LoadProfile) -> None:
        self.logger.info("time: %s\tsumpul:%s\tsumamb:%s", pro.time, pro.sumpul, pro.sumamb)

    def r(self, value: float) -> float:
        return round(value, 2)

    def mean_mre(self, reference: np.ndarray, prediction: np.ndarray) -> float:
        reference = np.array(reference)
        prediction = np.array(prediction)
        meam_mre = np.mean(np.abs((reference - prediction) / reference))
        return float(meam_mre)

    def save_results(self, thermalPlates: ThermalPlate, thermals: List[Thermal]) -> None:
        for thermal in thermals:
            for attr, value in list(vars(thermal).items()):
                if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                    self.logger.warning("[Thermal] Property %s for %s was %s, setting to 0", attr, thermal.XfrmID, value)
                    setattr(thermal, attr, 0.0)

        for attr, value in list(vars(thermalPlates).items()):
            if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
                self.logger.warning("[ThermalPlate] Property %s was %s, setting to 0", attr, value)
                setattr(thermalPlates, attr, 0.0)

        self.logger.info("Thermal results prepared for persistence (stubbed save). Entries: %s", len(thermals))
        self.ALLResults.clear()

    def sample_load_profile(self, RxLoadPro: List[LoadProfile]) -> List[LoadProfile]:
        SampledProfile: List[LoadProfile] = []
        bSlopePULoad = 0.0
        bSlopeAmbient = 0.0
        self.SampleTime = 0
        self.baPULoad = []
        xfrmId = RxLoadPro[0].XfrmID
        profileName = RxLoadPro[0].profileName
        basicLoad = RxLoadPro[0].sumpul

        newCase = LoadProfile(
            XfrmID=xfrmId,
            time=self.SampleTime,
            sumpul=RxLoadPro[0].sumpul,
            sumamb=RxLoadPro[0].sumamb,
            profileName=profileName,
            sessionId=self.sessionId,
        )
        SampledProfile.append(newCase)
        self.baPULoad.append(basicLoad)

        for k in range(1, len(RxLoadPro)):
            bSlopePULoad = (RxLoadPro[k].sumpul - RxLoadPro[k - 1].sumpul) / (RxLoadPro[k].time - RxLoadPro[k - 1].time)
            bSlopeAmbient = (RxLoadPro[k].sumamb - RxLoadPro[k - 1].sumamb) / (RxLoadPro[k].time - RxLoadPro[k - 1].time)

            while self.SampleTime < RxLoadPro[k].time:
                self.SampleTime += self.ThermalAnalytics.dt
                newCase = LoadProfile(
                    sessionId=self.sessionId,
                    XfrmID=xfrmId,
                    profileName=profileName,
                    time=self.SampleTime,
                    sumpul=RxLoadPro[k - 1].sumpul + bSlopePULoad * (self.SampleTime - RxLoadPro[k - 1].time),
                    sumamb=RxLoadPro[k - 1].sumamb + bSlopeAmbient * (self.SampleTime - RxLoadPro[k - 1].time),
                )
                basicLoad = newCase.sumpul
                SampledProfile.append(newCase)
                self.baPULoad.append(basicLoad)
        return SampledProfile

    def clear_all_resources(self) -> None:
        self.ALLResults.clear()
        self.ixLoadPro.clear()

    def perform_trans_rating(
        self,
        CaseToRate: LoadingCase,
        RxLoadPro: List[LoadProfile],
        ratingStds: List[LoadingStandard],
        rxCooling: Cooling,
        rxAmbient: float,
        pof_failure: float
    ) -> tuple[ThermalPlate, List[Thermal]]:
        PeakTOT = PeakHST = PeakPULoad = PeakLOL = 0.0
        DLMinFactor = DLMaxFactor = 0.0

        self.sessionId = CaseToRate.sessionId
        self.XfoRatings = ThermalPlate()
        self.ALLResults = []
        self.ixLoadPro = []

        self.ThermalAnalytics.life_time = CaseToRate.InsLifeExp
        self.XfoRatings.profileName = RxLoadPro[0].profileName
        self.XfoRatings.sessionId = CaseToRate.sessionId
        self.XfoRatings.XfrmID = CaseToRate.XfrmID
        self.XfoRatings.LoadType = CaseToRate.LoadType
        self.XfoRatings.mvaCooling = rxCooling.XfrmerCoolLevel
        self.XfoRatings.mvaAmbient = rxAmbient
        self.XfoRatings.TimeLimit = CaseToRate.EndOverTime - CaseToRate.BeginOverTime
        self.XfoRatings.HotSpotLimit = CaseToRate.HotSpotLimit
        self.XfoRatings.TopOilLimit = CaseToRate.TopOilLimit
        self.XfoRatings.PULLimit = CaseToRate.PULLimit
        self.XfoRatings.LoLLimit = (CaseToRate.LoLLimit * 100) / CaseToRate.InsLifeExp

        self.OxyContent = CaseToRate.OxyContent
        self.MoisWCPContent = CaseToRate.MoisContent
        self.InsulationType = getattr(self.ThermalAnalytics, "enp_paper_type", None)

        AxLoadPro = self.sample_load_profile(RxLoadPro)

        self.ALLResults = [
            Thermal(
                XfrmID=p.XfrmID,
                sessionId=p.sessionId,
                profileName=p.profileName,
                LoadType=CaseToRate.LoadType,
                time=p.time,
                sumpul=p.sumpul,
                sumamb=p.sumamb,
                basicMVA=(p.sumpul * self.ThermalAnalytics.per_unit_base_kva) / 1000,
                mvaCooling=rxCooling.XfrmerCoolLevel,
                mvaAmbient=rxAmbient,
            )
            for p in AxLoadPro
        ]
        self.XfoRatings.baPeakMVA = max(t.basicMVA for t in self.ALLResults)
        self.XfoRatings.baPeakAMB = max(t.sumamb for t in self.ALLResults)

        for thermalType in ratingStds:
            self.ThermalAnalytics.initialize(rxCooling.XfrmerCooling, CaseToRate.LtcPosition, thermalType)
            DLMinFactor = self.ThermalAnalytics.pu_min_mul
            DLMaxFactor = self.ThermalAnalytics.pu_max_mul
            self.OptimalPUFactor = 1
            CaseLimitedBy = "NO OPTIMAL SOLUTION"

            while abs(DLMaxFactor - DLMinFactor) >= EPSILON:
                self.ixLoadPro.clear()
                self.currentPUFactor = (DLMinFactor + DLMaxFactor) / 2
                for PuPro in AxLoadPro:
                    lRow = LoadProfile(
                        profileName=PuPro.profileName,
                        sessionId=PuPro.sessionId,
                        time=PuPro.time,
                        sumpul=PuPro.sumpul,
                        sumamb=PuPro.sumamb + rxAmbient,
                    )
                    if CaseToRate.BeginOverTime <= lRow.time <= CaseToRate.EndOverTime:
                        lRow.sumpul = lRow.sumpul * self.currentPUFactor
                    self.ixLoadPro.append(lRow)

                if thermalType.pubName == LoadingStandard.IEEEG:
                    self.IEEEG_Assessment()
                    PeakHST = self.XfoRatings.IEEEGPeakHotSpot
                    PeakTOT = self.XfoRatings.IEEEGPeakTopOil
                    PeakLOL = self.XfoRatings.IEEEGPeakLoL
                    PeakPULoad = self.XfoRatings.IEEEGPeakPUL

                elif thermalType.pubName == LoadingStandard.IEEE7:
                    self.IEEE7_Assessment()
                    PeakHST = self.XfoRatings.IEEE7PeakHotSpot
                    PeakTOT = self.XfoRatings.IEEE7PeakTopOil
                    PeakLOL = self.XfoRatings.IEEE7PeakLoL
                    PeakPULoad = self.XfoRatings.IEEE7PeakPUL

                elif thermalType.pubName == LoadingStandard.IEC60354:
                    self.IEC60354_Assessment()
                    PeakHST = self.XfoRatings.IECPeakHotSpot
                    PeakTOT = self.XfoRatings.IECPeakTopOil
                    PeakLOL = self.XfoRatings.IECPeakLoL
                    PeakPULoad = self.XfoRatings.IECPeakPUL

                if (
                    PeakTOT < CaseToRate.TopOilLimit + CaseToRate.OptimError
                    and PeakHST < CaseToRate.HotSpotLimit + CaseToRate.OptimError
                    and PeakLOL < self.XfoRatings.LoLLimit + CaseToRate.OptimError / 1000
                    and PeakPULoad < CaseToRate.PULLimit + CaseToRate.OptimError / 100
                ):
                    DLMinFactor = self.currentPUFactor
                else:
                    DLMaxFactor = self.currentPUFactor

                if (
                    (CaseToRate.TopOilLimit - CaseToRate.OptimError) <= PeakTOT <= CaseToRate.TopOilLimit + CaseToRate.OptimError
                    and PeakHST <= CaseToRate.HotSpotLimit + CaseToRate.OptimError
                    and PeakLOL <= self.XfoRatings.LoLLimit + CaseToRate.OptimError / 1000
                    and PeakPULoad <= CaseToRate.PULLimit + CaseToRate.OptimError / 100
                ):
                    CaseLimitedBy = "TOPOIL"
                    break
                if (
                    (CaseToRate.HotSpotLimit - CaseToRate.OptimError) <= PeakHST <= CaseToRate.HotSpotLimit + CaseToRate.OptimError
                    and PeakTOT <= CaseToRate.TopOilLimit + CaseToRate.OptimError
                    and PeakLOL <= self.XfoRatings.LoLLimit + CaseToRate.OptimError / 1000
                    and PeakPULoad <= CaseToRate.PULLimit
                ):
                    CaseLimitedBy = "HOTSPOT"
                    break
                if (
                    (self.XfoRatings.LoLLimit - CaseToRate.OptimError / 1000) <= PeakLOL <= self.XfoRatings.LoLLimit + CaseToRate.OptimError / 1000
                    and PeakHST <= CaseToRate.HotSpotLimit + CaseToRate.OptimError
                    and PeakTOT <= CaseToRate.TopOilLimit + CaseToRate.OptimError
                    and PeakPULoad <= CaseToRate.PULLimit + CaseToRate.OptimError / 100
                ):
                    CaseLimitedBy = "LOSSoLIFE"
                    self.OptimalPUFactor = (1 - pof_failure) * self.currentPUFactor
                    break
                if (
                    (CaseToRate.PULLimit - CaseToRate.OptimError / 100) <= PeakPULoad <= CaseToRate.PULLimit + CaseToRate.OptimError / 100
                    and PeakTOT <= CaseToRate.TopOilLimit + CaseToRate.OptimError
                    and PeakHST <= CaseToRate.HotSpotLimit + CaseToRate.OptimError
                    and PeakLOL <= self.XfoRatings.LoLLimit + CaseToRate.OptimError / 1000
                ):
                    CaseLimitedBy = "PULOAD"
                    self.OptimalPUFactor = (1 - pof_failure) * self.currentPUFactor
                    break
                if CaseToRate.LtcPosition != -99 and (
                    CaseToRate.LtcAmpacity - CaseToRate.OptimError / 100
                    <= PeakPULoad
                    <= CaseToRate.LtcAmpacity + CaseToRate.OptimError / 100
                ):
                    CaseLimitedBy = "LTC-RATING"
                    self.OptimalPUFactor = (1 - pof_failure) * self.currentPUFactor
                    break
                self.OptimalPUFactor = (1 - pof_failure) * self.currentPUFactor

            if thermalType.pubName == LoadingStandard.IEEEG:
                self.XfoRatings.IEEEGLimitedBy = CaseLimitedBy
            elif thermalType.pubName == LoadingStandard.IEEE7:
                self.XfoRatings.IEEE7LimitedBy = CaseLimitedBy
            elif thermalType.pubName == LoadingStandard.IEC60354:
                self.XfoRatings.IECLimitedBy = CaseLimitedBy

        AxLoadPro.clear()
        thermalPlates = self.XfoRatings
        thermals = [p for p in self.ALLResults if p.time % 60 == 0]
        self.save_results(thermalPlates, thermals)
        return thermalPlates, thermals


