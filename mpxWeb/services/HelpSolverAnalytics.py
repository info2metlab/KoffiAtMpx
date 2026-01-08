import logging
import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, List, Optional
from XUtility import *


@dataclass
class Ambient:
    min_ambient: float
    max_ambient: float
    amb_step: float
    


class SolverAnalytics:
    
    def __init__(self) -> None:

        self.ieee_cooling: List[str] = [
            "=====IEEE========",
            "OA",
            "FA",
            "FOA",
            "FOW",
            "FOW*",
            "OA/FA",
            "OA/FOA",
            "OA/FOA*",
            "OA/FOW",
            "OA/FOW*",
            "OA/FA/FA",
            "OA/FA/FOA",
            "OA/FOA/FOA",
            "OA/FOA*/FOA*",
            "=====IEC=========",
            "ONAN",
            "ONAF",
            "ODAF",
            "ODWF",
            "OFAF",
            "ONAN/ONAF",
            "ONAN/OFAF",
            "ONAN/ODAF",
            "ONAN/OFWF",
            "ONAN/ODWF",
            "ONAN/ONAF/ONAF",
            "ONAN/ONAF/OFAF",
            "ONAN/ONAF/ODAF",
            "ONAN/OFAF/OFAF",
            "ONAN/ODAF/ODAF",
            "ONAN/ODWF/ODWF",
        ]
        self.logger = logging.getLogger(__name__)
        self.session_id: str = ""
        self.xfrm_id: str = ""

        # Ageing parameters
        self.enp_ieee_ref = 0.0
        self.enp_iec_ref = 0.0
        self.enp_paper_type = PaperTypes.KRAFT
        self.low_oxygen_parm_kraft_a0 = 0.0
        self.low_oxygen_parm_kraft_a1 = 0.0
        self.low_oxygen_parm_kraft_a2 = 0.0
        self.low_oxygen_parm_tuk_a0 = 0.0
        self.low_oxygen_parm_tuk_a1 = 0.0
        self.low_oxygen_parm_tuk_a2 = 0.0
        self.med_oxygen_parm_kraft_a0 = 0.0
        self.med_oxygen_parm_kraft_a1 = 0.0
        self.med_oxygen_parm_kraft_a2 = 0.0
        self.med_oxygen_parm_tuk_a0 = 0.0
        self.med_oxygen_parm_tuk_a1 = 0.0
        self.med_oxygen_parm_tuk_a2 = 0.0
        self.high_oxygen_parm_kraft_a0 = 0.0
        self.high_oxygen_parm_kraft_a1 = 0.0
        self.high_oxygen_parm_kraft_a2 = 0.0
        self.high_oxygen_parm_tuk_a0 = 0.0
        self.high_oxygen_parm_tuk_a1 = 0.0
        self.high_oxygen_parm_tuk_a2 = 0.0
        self.cum_loss_of_life = 0.0
        self.life_time = 0.0

        # Cooling, loss, and thermal exponents
        self.k11_cst                    = 0.0
        self.k21_cst                    = 0.0
        self.k22_cst                    = 0.0
        self.iec_oil_exp                = 0.0
        self.iec_winding_exp            = 0.0
        self.iec_to_time_cst            = 0.0
        self.iec_wind_time_cst          = 0.0
        self.iec_loss_ratio             = 0.0
        self.oil_exp                   = 0.0
        self.winding_exp               = 0.0
        self.avg_oil_exp               = 0.0
        self.duct_oil_exp              = 0.0
        self.top_bo_exp                = 0.0
        self.temp_factor               = 0.0
        self.loss_temp_base            = 0.0
        self.loss_base_kva             = 0.0
        self.per_unit_base_kva         = 0.0
        self.per_unit_hs_eddy_loss     = 0.0
        self.per_unit_heigh_to_hot_spot = 0.0
        self.loss_ratio = 0.0
        self.wind_eddy_loss = 0.0
        self.wind_stray_losses = 0.0
        self.wind_i2r_losses = 0.0
        self.winding_temp_base = 0.0
        self.total_losses = 0.0
        self.core_losses = 0.0
        self.core_losses_over_ex = 0.0
        self.load_loss = 0.0
        self.t_losses = 0.0
        self.total_tap_losses = 0.0
        self.tl_ratio = 0.0
        self.amps_ratio = 0.0
        self.per_cooler_in_serv = 0.0

        # Temperature rises and ratings
        self.dt                         = 0.0
        self.top_oil_rise               = 0.0
        self.hot_spot_rise              = 0.0
        self.avg_oil_rise               = 0.0
        self.avg_winding_rise           = 0.0
        self.bottom_oil_rise            = 0.0
        self.duct_oil_rise              = 0.0
        self.tested_avg_winding_rise    = 0.0
        self.rated_delta_do_bo          = 0.0
        self.rated_duct_avg_oil         = 0.0
        self.rated_ambient              = 0.0
        self.rated_avg_oil              = 0.0
        self.rated_hot_spot             = 0.0
        self.rated_duct_oil_at_hs       = 0.0
        self.rated_avg_wind             = 0.0
        self.rated_hsr_to_tor           = 0.0
        self.tested_rated_avg_wind      = 0.0
        self.rated_bottom_oil           = 0.0
        self.rated_top_oil              = 0.0
        self.rated_top_duct_oil         = 0.0
        self.rated_tap_bottom_oil       = 0.0
        self.rated_tap_top_oil          = 0.0
        self.tested_rated_tap_avg_wind  = 0.0
        self.rated_tap_avg_wind         = 0.0
        self.rated_tap_hot_spot         = 0.0
        self.rated_tap_delta_do_bo      = 0.0
        self.rated_tap_hsr_to_tor       = 0.0
        self.rated_to_time_cst          = 0.0
        # Cooling mode and time constants
        self.i3e_cooling                = ""
        self.wind_time_cst              = 0.0
        self.to_time_cst                = 0.0
        self.d_visc_cst                 = 0.0
        self.g_visc_cst                 = 0.0

        # Nameplate and tap settings
        self.xfrmer_rating              = 0.0
        self.xfrmer_cooling             = ""
        self.xfrmer_cool_level          = 0.0
        self.transfo_type: str          = ""
        self.h_rated_amps               = 0.0
        self.x_rated_amps               = 0.0
        self.t_rated_amps               = 0.0
        self.h_rated_volt               = 0.0
        self.x_rated_volt               = 0.0
        self.t_rated_volt               = 0.0
        self.h_rated_mva               = 0.0
        self.x_rated_mva               = 0.0
        self.t_rated_mva               = 0.0
        self.hx_rated_mva              = 0.0
        self.ht_rated_mva              = 0.0
        self.xt_rated_mva              = 0.0
        self.h_rated_t_losses          = 0.0
        self.x_rated_t_losses          = 0.0
        self.t_rated_t_losses          = 0.0
        self.h_tap_amps                = 0.0
        self.x_tap_amps                = 0.0
        self.t_tap_amps                = 0.0
        self.hx_load_loss              = 0.0
        self.ht_load_loss              = 0.0
        self.xt_load_loss              = 0.0
        self.ltc_tap_range             = 0.0
        self.ltc_tap_step              = 1
        self.ltc_rated_pos             = 0
        self.ltc_min_pos               = 0
        self.ltc_max_pos               = 0
        self.ltc_capacity              = 0.0
        self.mva_capacity              = 0.0
        self.is_tap_changing           = 0
        self.ltc_winding               = Winding.HV

        # Electrical impedances
        self.rated_lv = 0.0
        self.rated_hv = 0.0
        self.per_impedance = 0.0
        self.per_resistance = 0.0
        self.per_reactance = 0.0
        self.number_of_phases = 0

        # Errors and limits
        self.hot_spot_error = 0.0
        self.top_oil_error = 0.0
        self.pu_error = 0.0
        self.lol_error = 0.0
        self.pu_min_mul = 0.0
        self.pu_max_mul = 0.0
        self.rating_group = 0.0
        self.hot_spot_mo_mul = 0.0
        self.hot_spot_depth = 0.0
        self.avg_ins_mois = 0.0
        self.hot_spot_mois = 0.0

        # Fluid and material properties
        self.fluid_type = 0
        self.winding_conductor = 0
        self.over_excitation = 0
        self.time_over_excitation = 0.0
        self.mass_core_coil = 0.0
        self.mass_tank = 0.0
        self.gallons_of_fluid = 0.0
        self.mass_fluid = 0.0
        self.mass_core = 0.0
        self.mass_wind = 0.0
        self.mass_sum = 0.0
        self.fluid_density = 0.0
        self.heat_core = 0.0
        self.heat_fluid = 0.0
        self.heat_tank = 0.0
        self.heat_wind = 0.0
        self.pwhs = 0.0
        self.pehs = 0.0
        self.mw_cw = 0.0
        self.q_core = 0.0

        # Identification and tracking
        self.output_string = ""
        self.customer_id = ""
        self.unit_id = ""
        self.unit_serial_number = ""
        self.load_cycle_period = 0
        self.no_of_cycle_intervals = 0
        self.dl_min_factor = 0.0
        self.dl_max_factor = 0.0

        # Collections and context placeholders
        self.load_case: List[LoadingCase] = []
        self.load_profile: List[Any] = []
        self.load_std: Optional[Any] = None
        self.load_dictionary: List[Any] = []
        self.xfrm_data: Optional[Any] = None

    def loss_of_life(self, temp: float, std: LoadingStandard) -> float:
        """Calculate loss of life based on temperature and loading standard."""
        loss = 0.0
        if self.enp_paper_type == PaperTypes.TUK and std in (LoadingStandard.IEEE7, LoadingStandard.IEEEG):
            loss = math.exp((15000.0 / (self.enp_ieee_ref + 273.0)) - (15000.0 / (temp + 273.0)))
        elif self.enp_paper_type == PaperTypes.KRAFT and std in (LoadingStandard.IEEE7, LoadingStandard.IEEEG):
            loss = math.exp((15000.0 / (self.enp_ieee_ref + 273.0)) - (15000.0 / (temp + 273.0)))
        elif self.enp_paper_type == PaperTypes.TUK and std in (LoadingStandard.IEC60354, LoadingStandard.IEC60076):
            loss = math.exp((15000.0 / (self.enp_iec_ref + 273.0)) - (15000.0 / (temp + 273.0)))
        elif self.enp_paper_type == PaperTypes.KRAFT and std in (LoadingStandard.IEC60354, LoadingStandard.IEC60076):
            loss = math.pow(2.0, (temp - self.enp_iec_ref) / 6.0)
        return loss

    def tmo_loss_of_life(self, temp: float, oxygen_level: float, mois_wcp: float, std: LoadingStandard, ptype: PaperTypes) -> float:
        """Loss of life factoring in temperature, moisture, and oxygen content."""
        return self.loss_of_life(temp, std) * self.reduction_factor_lol(oxygen_level, mois_wcp, ptype)

    def reduction_factor_lol(self, oxygen_level: float, mois_wcp: float, ptype: PaperTypes) -> float:
        """Reduction factor for loss of life based on oxygen and moisture."""
        r_factor = 0.0
        a0 = 0.0
        a1 = 0.0
        a2 = 0.0
        exponent = 3 if ptype == PaperTypes.TUK else 2
        try:
            if oxygen_level <= 0.6:
                if ptype == PaperTypes.KRAFT:
                    a0 = self.low_oxygen_parm_kraft_a0
                    a1 = self.low_oxygen_parm_kraft_a1
                    a2 = self.low_oxygen_parm_kraft_a2
                else:
                    a0 = self.low_oxygen_parm_tuk_a0
                    a1 = self.low_oxygen_parm_tuk_a1
                    a2 = self.low_oxygen_parm_tuk_a2
            elif 0.6 < oxygen_level <= 1.6:
                if ptype == PaperTypes.KRAFT:
                    a0 = self.med_oxygen_parm_kraft_a0
                    a1 = self.med_oxygen_parm_kraft_a1
                    a2 = self.med_oxygen_parm_kraft_a2
                else:
                    a0 = self.med_oxygen_parm_tuk_a0
                    a1 = self.med_oxygen_parm_tuk_a1
                    a2 = self.med_oxygen_parm_tuk_a2
            elif oxygen_level > 1.6:
                if ptype == PaperTypes.KRAFT:
                    a0 = self.high_oxygen_parm_kraft_a0
                    a1 = self.high_oxygen_parm_kraft_a1
                    a2 = self.high_oxygen_parm_kraft_a2
                else:
                    a0 = self.high_oxygen_parm_tuk_a0
                    a1 = self.high_oxygen_parm_tuk_a1
                    a2 = self.high_oxygen_parm_tuk_a2

            if mois_wcp <= 0.5:
                r_factor = math.pow(0.5, exponent) * a2 + 0.5 * a1 + a0
            else:
                r_factor = math.pow(mois_wcp, exponent) * a2 + mois_wcp * a1 + a0
        except Exception as exc:  # pragma: no cover - logging safety net
            self.logger.error("Error while getting Reduction Factor for LoL calculation: %s", exc)
        return r_factor

    def viscosity(self, temp: float) -> float:
        """Oil viscosity based on temperature."""
        return self.d_visc_cst * math.exp(self.g_visc_cst / (temp + 273.0))

    def amp_station(self, ltc_position: int) -> float:
        """Per-unit current adjustment for LTC position."""
        delta = (2 * self.ltc_tap_range / 100.0) * ltc_position / self.ltc_tap_step
        if ltc_position < self.ltc_rated_pos:
            return 1.0 / (1.0 - delta)
        return 1.0 / (1.0 + delta)

    def clone_case(self, cloned_case: LoadingCase) -> LoadingCase:
        """Create a shallow copy of a loading case."""
        new_case = LoadingCase()
        for field in (
            "Id",
            "xfrmId",
            "sessionId",
            "LoadType",
            "HotSpotLimit",
            "TopOilLimit",
            "LoLLimit",
            "PULLimit",
            "BubblingLimit",
            "CoolPWLimit",
            "BeginOverTime",
            "EndOverTime",
            "InsLifeExp",
            "OxyContent",
            "MoisContent",
            "GasContent",
            "HSPressure",
            "LtcPosition",
            "LtcAmpacity",
            "OptimError",
            "ToSimulate",
        ):
            if hasattr(cloned_case, field):
                setattr(new_case, field, getattr(cloned_case, field))
        return new_case

    
    
    
    
    def get_per_unit_load(self, raw_current: float, src: str) -> float:
        """Per-unit measured load current for a winding."""
        if src == "H":
            denom = self.h_rated_amps
        elif src == "X":
            denom = self.x_rated_amps
        else:
            denom = self.t_rated_amps

        if denom == 0:
            self.logger.warning("Rated amps for %s winding is zero; returning 0 pu load", src)
            return 0.0
        return raw_current / denom

    def get_calc_per_unit_load(self, h_pu_l: float, x_pu_l: float, t_pu_l: float) -> float:
        """Combined per-unit load across windings."""
        if self.transfo_type == "AUTOTRANSFORMER" and self.hx_rated_mva > 0 and self.t_rated_mva > 0:
            return ((h_pu_l + x_pu_l) * self.hx_rated_mva + t_pu_l * self.t_rated_mva) / (
                2 * self.hx_rated_mva + self.t_rated_mva
            )
        if self.h_rated_mva > 0 and self.x_rated_mva > 0 and self.t_rated_mva > 0:
            return (
                h_pu_l * self.h_rated_mva
                + x_pu_l * self.x_rated_mva
                + t_pu_l * self.t_rated_mva
            ) / (self.h_rated_mva + self.x_rated_mva + self.t_rated_mva)
        return round(max(h_pu_l, x_pu_l, t_pu_l), 2)

    def get_calc_losses(
        self,
        h_pu_l: float,
        x_pu_l: float,
        t_pu_l: float,
        activ_cooling_power: Optional[float] = None,
        ref_stage_load_loss: Optional[float] = None,
    ) -> float:
        """Calculate load losses based on measured per-unit loads.

        When cross-winding losses are unavailable, provide `activ_cooling_power`
        and `ref_stage_load_loss` to avoid relying on external data sources.
        """
        if self.hx_load_loss > 0 and self.ht_load_loss > 0 and self.xt_load_loss > 0:
            if self.transfo_type == "AUTOTRANSFORMER":
                denom = self.x_rated_amps if self.x_rated_amps else None
                if not denom:
                    self.logger.warning("x_rated_amps is zero; returning 0 losses")
                    return 0.0
                reduction_factor = 1 - ((h_pu_l * self.h_rated_amps) / (denom * x_pu_l if x_pu_l else denom))

                h_losses = 0.5 * ((2 - reduction_factor) * self.hx_load_loss + (reduction_factor * (self.ht_load_loss - self.xt_load_loss)))
                c_losses = 0.5 * (reduction_factor * (self.hx_load_loss - self.ht_load_loss) + (reduction_factor * self.xt_load_loss))
                t_losses = 0.5 * (
                    (-1 / (reduction_factor * self.hx_load_loss))
                    + (1 / (reduction_factor * self.ht_load_loss))
                    + ((2 * reduction_factor - 1) / (reduction_factor * self.xt_load_loss))
                )

                return (
                    math.pow(h_pu_l, 2) * h_losses
                    + math.pow((h_pu_l - ((1 / reduction_factor) * t_pu_l * self.t_rated_mva) / self.hx_rated_mva), 2)
                    * c_losses
                    + math.pow(t_pu_l, 2) * t_losses
                )

            hx_losses = math.pow(self.h_rated_mva / self.hx_rated_mva, 2) * self.hx_load_loss if self.hx_rated_mva else 0.0
            ht_losses = math.pow(self.h_rated_mva / self.ht_rated_mva, 2) * self.ht_load_loss if self.ht_rated_mva else 0.0
            xt_losses = math.pow(self.h_rated_mva / self.xt_rated_mva, 2) * self.xt_load_loss if self.xt_rated_mva else 0.0

            h_losses = (hx_losses + ht_losses - xt_losses) / 2
            x_losses = (hx_losses - ht_losses + xt_losses) / 2
            t_losses = (-hx_losses + ht_losses + xt_losses) / 2
            return math.pow(h_pu_l, 2) * h_losses + math.pow(x_pu_l, 2) * x_losses + math.pow(t_pu_l, 2) * t_losses

        if activ_cooling_power is None or ref_stage_load_loss is None:
            raise NotImplementedError("Cooling data required when cross-winding losses are not provided.")
        return float(ref_stage_load_loss) + float(activ_cooling_power)

    def initialize(self, xfrm_cooling_mode: str, ltc_position: int, thermal_type: LoadingStandard) -> None:
        """Initialize analytics parameters based on cooling mode and tap position."""
        rate_cor_factor = 0.0
        temp_cor_factor = 0.0
        self.rated_avg_wind = 0.0
        self.rated_top_duct_oil = 0.0
        self.rated_duct_oil_at_hs = 0.0
        self.tested_rated_avg_wind = 0.0
        self.rated_bottom_oil = 0.0
        self.rated_ambient = 0.0
        self.rated_hot_spot = 0.0
        self.rated_top_oil = 0.0
        self.rated_duct_avg_oil = 0.0
        self.rated_to_time_cst = 0.0
        self.rated_hsr_to_tor = 0.0
        self.rated_avg_oil = 0.0

        # Set cooling mode parameters
        if xfrm_cooling_mode in ("OA", "ONAN"):
            # OA - x Exponent for duct oil rise, z: exponent for top to bottom fluid
            self.duct_oil_exp = 0.5
            self.avg_oil_exp = 0.8
            self.top_bo_exp = 0.5
            self.rated_duct_oil = self.top_oil_rise  # y exponent for average fluid rise
            self.oil_exp = 0.8
            self.winding_exp = 0.8

            # ONAN
            if self.transfo_type == "DISTRIBUTION":
                self.iec_oil_exp = 0.8
                self.iec_winding_exp = 1.6
                self.k11_cst = 1
                self.k21_cst = 1.0
                self.k22_cst = 2.0
                self.iec_wind_time_cst = 4
                self.iec_to_time_cst = 180
                self.iec_loss_ratio = 5.0
            else:
                self.iec_oil_exp = 0.8
                self.iec_winding_exp = 1.3
                self.k11_cst = 0.5
                self.k21_cst = 2.0
                self.k22_cst = 2.0
                self.iec_wind_time_cst = 10
                self.iec_to_time_cst = 210
                self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FA", "ONAN/ONAF"):
            # OA/FA
            self.duct_oil_exp = 0.5
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 0.5
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # ONAF
            self.iec_oil_exp = 0.8
            self.iec_winding_exp = 1.3
            self.k11_cst = 0.5
            self.k21_cst = 2.0
            self.k22_cst = 2.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 150
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOA", "ONAN/OFAF"):
            # NDFOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # OF
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 1.3
            self.k11_cst = 1.0
            self.k21_cst = 1.3
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOA*", "ONAN/ODAF"):
            # DFOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 1.0
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 1.0
            self.winding_exp = 1.0
            # OD
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 2.0
            self.k11_cst = 1.0
            self.k21_cst = 1.0
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOW", "ONAN/OFWF"):
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 1.0
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # OF
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 1.3
            self.k11_cst = 1.0
            self.k21_cst = 1.3
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOW*", "ONAN/ODWF"):
            # DFOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 1.0
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 1.0
            self.winding_exp = 1.0
            # OD
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 2.0
            self.k11_cst = 1.0
            self.k21_cst = 1.0
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FA/FA", "ONAN/ONAF/ONAF"):
            # OA/FA/FA
            self.duct_oil_exp = 0.5
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 0.5
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # ONAF
            self.iec_oil_exp = 0.8
            self.iec_winding_exp = 1.3
            self.k11_cst = 0.5
            self.k21_cst = 2.0
            self.k22_cst = 2.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 150
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FA/FOA", "ONAN/ONAF/OFAF"):
            # OA/FA/FOA or OA/FOA/FOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.avg_winding_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # OF
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 1.3
            self.k11_cst = 1.0
            self.k21_cst = 1.3
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FA/FOA*", "ONAN/ONAF/ODAF"):
            # OA/FOA/FOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # OD
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 2.0
            self.k11_cst = 1.0
            self.k21_cst = 1.0
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOA/FOA", "ONAN/OFAF/OFAF"):
            # OA/FOA/FOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 0.9
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.avg_winding_rise
            self.oil_exp = 0.9
            self.winding_exp = 0.8
            # OF
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 2.0
            self.k11_cst = 1.0
            self.k21_cst = 1.0
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        elif xfrm_cooling_mode in ("OA/FOA*/FOA*", "ONAN/ODAF/ODAF"):
            # OA/FOA/FOA
            self.duct_oil_exp = 1.0
            self.avg_oil_exp = 1.0
            self.top_bo_exp = 1.0
            self.rated_duct_oil = self.top_oil_rise
            self.oil_exp = 1.0
            self.winding_exp = 1.0
            # OD
            self.iec_oil_exp = 1.0
            self.iec_winding_exp = 2.0
            self.k11_cst = 1.0
            self.k21_cst = 1.0
            self.k22_cst = 1.0
            self.iec_wind_time_cst = 7
            self.iec_to_time_cst = 90
            self.iec_loss_ratio = 6.0

        self.i3e_cooling = xfrm_cooling_mode

        # Fill Fluid's static data
        if self.fluid_type == 1:  # Oil
            self.heat_fluid = 13.92  # [W-min/lb °C]
            self.fluid_density = 0.031621  # lb/in3
            self.d_visc_cst = 0.0013473
            self.g_visc_cst = 2797.3
        elif self.fluid_type == 2:  # Silicone
            self.heat_fluid = 11.49  # [W-min/lb °C]
            self.fluid_density = 0.0347  # lb/in3
            self.d_visc_cst = 0.12127
            self.g_visc_cst = 1782.3
        elif self.fluid_type == 3:  # HTHC
            self.heat_fluid = 14.55  # [W-min/lb °C]
            self.fluid_density = 0.03178  # lb/in3
            self.d_visc_cst = 0.00007343
            self.g_visc_cst = 4434.7

        # Fill Material's static data
        if self.winding_conductor == CONDUCTOR.ALUMINIUM.name:  # ALUMINIUM
            self.heat_wind = 6.798
            self.temp_factor = 225
        elif self.winding_conductor == CONDUCTOR.COPPER.name:  # COPPER
            self.heat_wind = 2.91
            self.temp_factor = 234.5
        
        # Adjusting rises to temperatures
        # Rated average winding temperature at rated load (TWR)
        self.rated_avg_wind = float(self.rated_ambient) + float(self.winding_temp_base)
        
        # Tested average winding temperature at rated load (TWRT)
        self.tested_rated_avg_wind = float(self.rated_ambient) + float(self.avg_winding_rise)   

        # Winding hotspot temperature at rated load (THSR)
        self.rated_hot_spot = float(self.rated_ambient) + float(self.hot_spot_rise)

        # Top oil temperature at rated load (TTOR)
        self.rated_top_oil = float(self.rated_ambient) + float(self.top_oil_rise)

        # Bottom oil temperature at rated load (TBOR)
        self.rated_bottom_oil = float(self.rated_ambient) + float(self.bottom_oil_rise)

        # Top Duct oil temperature at rated load - same as TTOR unless non-directed flow FOA (TTDOR)
        self.rated_top_duct_oil = float(self.rated_ambient) + float(self.rated_duct_oil)

        # Temperature of oil adjacent to winding hotspot at rated load - often same as TTOR (TWOR)
        self.rated_duct_oil_at_hs = self.per_unit_heigh_to_hot_spot * (
            float(self.rated_top_duct_oil) - float(self.rated_bottom_oil)
        ) + float(self.rated_bottom_oil)

        # Average temperature at rated load of oil in the winding cooling ducts - often same as TFAVER (TDAOR)
        self.rated_duct_avg_oil = float(self.rated_top_duct_oil) + float(self.rated_bottom_oil) / 2

        # Average oil temperature at rated load of oil in the tank (TAOR or TFAVER)
        self.rated_avg_oil = (float(self.rated_top_oil) + float(self.rated_bottom_oil)) / 2

        # Rated value of Hot Spot Rise over Top Oil
        self.rated_hsr_to_tor = float(self.hot_spot_rise) - float(self.top_oil_rise)

        # LTC Impacts
        if self.is_tap_changing > 0 and ltc_position != self.ltc_rated_pos:
            self.logger.info("Selected tap position is: %s", ltc_position)

            if thermal_type == LoadingStandard.IEEEG:
                self.amps_ratio = self.amp_station(ltc_position)
                self.tl_ratio = math.pow(self.amps_ratio, 2)

                # Top oil temperature at rated load at a different Tap (TTOR)
                rated_tap_top_oil = self.rated_avg_oil * math.pow(
                    self.tl_ratio, self.avg_oil_exp
                ) + ((self.rated_top_oil - self.rated_bottom_oil) / 2) * math.pow(self.tl_ratio, self.top_bo_exp)

                # Bottom oil temperature at rated load at a different Tap (TBOR)
                rated_tap_bottom_oil = self.rated_avg_oil * math.pow(
                    self.tl_ratio, self.avg_oil_exp
                ) - ((self.rated_top_oil - self.rated_bottom_oil) / 2) * math.pow(self.tl_ratio, self.top_bo_exp)

                if "ONAN" in xfrm_cooling_mode or "ONAF" in xfrm_cooling_mode or "ODAF" in xfrm_cooling_mode:
                    rated_delta_do_bo = self.rated_top_oil - self.rated_bottom_oil
                elif "OFAF" in xfrm_cooling_mode:
                    rated_delta_do_bo = self.tested_rated_avg_wind - self.rated_bottom_oil
                else:
                    rated_delta_do_bo = 0

                rated_tap_delta_do_bo = rated_delta_do_bo * math.pow(self.amps_ratio, 2 * self.duct_oil_exp)

                # Rated average winding temperature at rated load at a different Tap
                if "ONAN" in xfrm_cooling_mode or "ONAF" in xfrm_cooling_mode or "OFAF" in xfrm_cooling_mode:
                    tested_rated_tap_avg_wind = (
                        self.tested_rated_avg_wind - self.rated_bottom_oil - (rated_delta_do_bo / 2)
                    ) * math.pow(self.amps_ratio, 1.6) + rated_tap_bottom_oil + (rated_tap_delta_do_bo / 2)

                    rated_tap_hot_spot = (
                        self.rated_hot_spot - self.rated_bottom_oil - (rated_delta_do_bo / 2)
                    ) * math.pow(self.amps_ratio, 1.6) + rated_tap_bottom_oil + rated_tap_delta_do_bo

                elif "ODAF" in xfrm_cooling_mode:
                    tested_rated_tap_avg_wind = (
                        self.tested_rated_avg_wind - self.rated_bottom_oil - (rated_delta_do_bo / 2)
                    ) * math.pow(self.amps_ratio, 2) + rated_tap_bottom_oil + (rated_tap_delta_do_bo / 2)

                    rated_tap_hot_spot = (
                        self.rated_hot_spot - self.rated_bottom_oil - (rated_delta_do_bo / 2)
                    ) * math.pow(self.amps_ratio, 2) + rated_tap_bottom_oil + rated_tap_delta_do_bo
                else:
                    tested_rated_tap_avg_wind = self.tested_rated_avg_wind
                    rated_tap_hot_spot = self.rated_hot_spot

                # Update values
                self.rated_top_oil          = rated_tap_top_oil
                self.tested_rated_avg_wind  = tested_rated_tap_avg_wind
                self.rated_hot_spot         = rated_tap_hot_spot
                self.rated_bottom_oil       = rated_tap_bottom_oil
                self.rated_avg_oil          = (self.rated_top_oil + self.rated_bottom_oil) / 2
                self.rated_top_duct_oil     = self.rated_ambient + self.rated_duct_oil
                self.rated_duct_avg_oil     = (self.rated_top_duct_oil + self.rated_bottom_oil) / 2
                self.rated_duct_oil_at_hs   = self.per_unit_heigh_to_hot_spot * (
                    self.rated_top_duct_oil - self.rated_bottom_oil
                ) + self.rated_bottom_oil
                self.rated_hsr_to_tor       = self.hot_spot_rise - self.top_oil_rise

                self.total_tap_losses       = self.tl_ratio * self.total_losses

            elif thermal_type == LoadingStandard.IEEE7:
                self.amps_ratio = self.amp_station(ltc_position)
                self.tl_ratio = math.pow(self.amps_ratio, 2)
                self.total_tap_losses = self.tl_ratio * self.total_losses
                self.rated_top_oil = self.rated_top_oil * math.pow(self.tl_ratio, self.oil_exp)
                self.rated_hsr_to_tor = self.rated_hsr_to_tor * math.pow(self.tl_ratio, self.winding_exp)

            elif thermal_type == LoadingStandard.IEC60354:
                ltc_rated1_pos = self.ltc_rated_pos + 1
                ltc_rated_ratio = (self.total_losses - self.core_losses) / self.core_losses
                ltc_min_ratio = (
                    math.sqrt(self.amp_station(self.ltc_min_pos)) * self.total_losses - self.core_losses
                ) / self.core_losses
                ltc_max_ratio = (
                    math.sqrt(self.amp_station(self.ltc_max_pos)) * self.total_losses - self.core_losses
                ) / self.core_losses
                ltc_rated1_ratio = (
                    math.sqrt(self.amp_station(ltc_rated1_pos)) * self.total_losses - self.core_losses
                ) / self.core_losses

                m1 = (ltc_rated_ratio - ltc_min_ratio) / (self.ltc_rated_pos - self.ltc_min_pos)
                m2 = (ltc_max_ratio - ltc_rated1_ratio) / (self.ltc_max_pos - ltc_rated1_pos)

                if ltc_position > self.ltc_rated_pos:
                    self.loss_ratio = ltc_rated1_ratio + (ltc_position - ltc_rated1_pos) * m2
                elif ltc_position > self.ltc_min_pos and ltc_position < self.ltc_rated_pos:
                    self.loss_ratio = ltc_rated_ratio + (ltc_position - self.ltc_rated_pos) * m1

                self.tl_ratio = math.pow(self.amps_ratio, 2)
                self.total_tap_losses = self.tl_ratio * self.total_losses
                self.rated_hsr_to_tor = self.rated_hsr_to_tor * math.pow(self.tl_ratio, self.iec_winding_exp)
                self.rated_top_oil = self.rated_top_oil * math.pow(self.tl_ratio, self.iec_oil_exp)

            self.load_loss = self.total_tap_losses - self.core_losses
            self.wind_i2r_losses = 0.8 * self.load_loss
            self.wind_eddy_loss = 0.02 * self.load_loss
            self.wind_stray_losses = 0.18 * self.load_loss
        else:
            self.amps_ratio = 1
            self.tl_ratio = 1
        

        if self.rated_hsr_to_tor < 0:
            if self.winding_temp_base >= 65:
                self.rated_hsr_to_tor = 80 - self.top_oil_rise
            else:
                self.rated_hsr_to_tor = 65 - self.top_oil_rise


        # Adjusting losses to correct bases
        # rate_cor_factor is a factor of the highest nameplate rating to the base nameplate rating squared
        # The losses are typically tested at the base nameplate rating
        rate_cor_factor = math.pow(self.per_unit_base_kva / self.loss_base_kva, 2)



        # temp_cor_factor is a temperature related correction factor for resistance (typical value is 1.032)
        temp_cor_factor = (float(self.temp_factor) + float(self.rated_avg_wind)) / (float(self.temp_factor) + float(self.loss_temp_base))


        self.wind_i2r_losses = float(rate_cor_factor) * float(self.wind_i2r_losses) * temp_cor_factor
        self.wind_eddy_loss = float(rate_cor_factor) * float(self.wind_eddy_loss) / temp_cor_factor
        self.wind_stray_losses = float(self.wind_stray_losses) * float(rate_cor_factor) / temp_cor_factor

        # Since Per Unit Eddy Loss is typically input as zero, the following formula essentially is
        if self.wind_eddy_loss / self.wind_i2r_losses > self.per_unit_hs_eddy_loss:
            self.per_unit_hs_eddy_loss = self.wind_eddy_loss / self.wind_i2r_losses

        self.pwhs = ((float(self.rated_hot_spot) + float(self.temp_factor)) / (float(self.rated_avg_wind) + float(self.temp_factor))) * float(self.wind_i2r_losses)
        self.pehs = float(self.per_unit_hs_eddy_loss) * float(self.pwhs)
        
        # Since 5 minutes is a standard default input for winding time constant,
        # This loop simply sets dt to 1/2; dt is defined as the time increment for calculation
        while self.wind_time_cst / self.dt <= 9:
            self.dt = self.dt / 2

        # MwCw is winding mass times specific heat. Units are (Watts * Minutes / Degrees C)
        # This calculation is being made to estimate the mass of the windings, WWIND
        self.mw_cw = (float(self.wind_eddy_loss) + float(self.wind_i2r_losses)) * float(self.wind_time_cst) / (
            float(self.tested_rated_avg_wind) - float(self.rated_duct_avg_oil)
        )

        if self.tested_rated_avg_wind <= self.rated_duct_avg_oil:
            self.output_string += (
                f"Tested Average Winding Temperature : {self.tested_rated_avg_wind}°C cannot be lower or equal to "
                f"the Rated Duct Average Oil Temperature : {self.rated_duct_avg_oil}°C\n"
            )
            print(f"Tested Average Winding Temperature : {self.tested_rated_avg_wind}°C cannot be lower or equal to ")
            self.output_string += "possible cause of error : wrong Average Winding Rise \n"
            return

        # Calculates the total mass times specific heat of fluid, tank, and core

        self.mass_wind = self.mw_cw / self.heat_wind
        # self.mass_core = self.mass_core_coil - self.mass_wind


        # if self.mass_wind > self.mass_core_coil:
        #     self.output_string += (
        #         f"Mass of Windings: {self.mass_wind} cannot be greater than Mass of core and coil : {self.mass_core_coil}\n"
        #     )
        #     self.output_string += "possible cause of error : wrong EddyLoss or I2RLosses, or Winding Time Constant value. \n"
        #     return
        

        self.mass_fluid = self.gallons_of_fluid * 231 * self.fluid_density  # [W-min/lb]
        heat_tank = 3.51  # [W-min/lb]
        heat_core = 3.51  # [W-min/lb]
        self.mass_sum = (self.mass_tank * heat_tank) + (self.mass_core * heat_core) + (self.mass_fluid * self.heat_fluid)

        # Calculates the heat generated by core and the total losses whether an overexcitation occurs or not
        if self.over_excitation == 1:
            self.q_core = self.core_losses_over_ex * self.dt
            self.total_losses = self.wind_stray_losses + self.wind_i2r_losses + self.wind_eddy_loss + self.core_losses_over_ex
        else:
            self.q_core = self.core_losses * self.dt
            self.total_losses = self.wind_stray_losses + self.wind_i2r_losses + self.wind_eddy_loss + self.core_losses

        # Calculate the loss ratio and the top oil time constant (in minutes) for the IEEE-7 assessments
        self.iec_to_time_cst = self.mass_sum * self.rated_top_oil / (self.tl_ratio * self.total_losses)
        self.loss_ratio = self.load_loss / self.core_losses

        # print(f"mass_wind:{self.iec_to_time_cst} -{self.loss_ratio} ")


    def set_xfrm_dictionary(self, session_id: str, xfrm_id: str, xcool: Cooling) -> None:
        """Populate transformer parameters from a mapping of name -> value.

        Expects `poll_dictionary` to behave like a dict of string keys. Unknown
        keys are ignored; known ones are coerced to float/int/enum where
        appropriate. `xcool` is expected to expose attributes like LossBasekVA,
        LossTempBase, and loss components.
        """
        output_string = ""
        def _coerce(val: Any) -> Any:
            if isinstance(val, str):
                v = val.strip()
                if v == "":
                    return v
                try:
                    if "." in v or "e" in v.lower():
                        return float(v)
                    return int(v)
                except Exception:
                    return v
            return val

        key_map = {
            "IsTapChanging": "is_tap_changing",
            "LtcWinding": "ltc_winding",
            "LtcTapRange": "ltc_tap_range",
            "LtcTapSteps": "ltc_tap_step",
            "LtcRatedTapPos": "ltc_rated_pos",
            "HRatedAmps": "h_rated_amps",
            "XRatedAmps": "x_rated_amps",
            "TRatedAmps": "t_rated_amps",
            "HRatedMVA": "h_rated_mva",
            "XRatedMVA": "x_rated_mva",
            "TRatedMVA": "t_rated_mva",
            "HXRatedMVA": "hx_rated_mva",
            "HTRatedMVA": "ht_rated_mva",
            "XTRatedMVA": "xt_rated_mva",
            "HXLoadLoss": "hx_load_loss",
            "HTLoadLoss": "ht_load_loss",
            "XTLoadLoss": "xt_load_loss",
            "enp_ieee_ref": "enp_ieee_ref",
            "enp_iec_ref": "enp_iec_ref",
            "enp_paper_type": "enp_paper_type",
            "TransfoType": "transfo_type",
            # "DViscCst": "d_visc_cst",
            # "GViscCst": "g_visc_cst",
            "LoadCyclePeriod": "load_cycle_period",
            "NoOfCycleIntervals": "no_of_cycle_intervals",
        }
        with Session(p_engine) as p_session:
            rows = list(p_session.execute(select(datadictionaries)).mappings())
            poll_dictionary = {row["varname"]: row.get("value") for row in rows}

        for key, attr in key_map.items():
            if key not in poll_dictionary:
                continue
            val = _coerce(poll_dictionary[key])
            
            if attr == "enp_paper_type":
                try:
                    val = PaperTypes[val] if isinstance(val, str) else PaperTypes(int(val))
                except Exception:
                    self.logger.warning("Unknown paper type value %s; defaulting to KRAFT", val)
                    val = PaperTypes.KRAFT
            setattr(self, attr, val)

        print(f"ltc_tap_step:{self.ltc_tap_step}")
        print(f"ltc_tap_range:{self.ltc_tap_range}")
        print(f"ltc_winding:{self.ltc_winding}")
        print(f"ltc_rated_pos:{self.ltc_rated_pos}")
        print(f"ltc_winding:{self.ltc_winding}")
        print(f"h_rated_amps:{self.h_rated_amps}")
        print(f"x_rated_amps:{self.x_rated_amps}")
        print(f"t_rated_amps:{self.t_rated_amps}")
        print(f"h_rated_mva:{self.h_rated_mva}")
        print(f"x_rated_mva:{self.x_rated_mva}")
        print(f"t_rated_mva:{self.t_rated_mva}")
        print(f"hx_rated_mva:{self.hx_rated_mva}")
        print(f"ht_rated_mva:{self.ht_rated_mva}")
        print(f"xt_rated_mva:{self.xt_rated_mva}")
        print(f"hx_load_loss:{self.hx_load_loss}")
        print(f"ht_load_loss:{self.ht_load_loss}")
        print(f"xt_load_loss:{self.xt_load_loss}")
        print(f"enp_ieee_ref:{self.enp_ieee_ref}")
        print(f"enp_iec_ref:{self.enp_iec_ref}")
        print(f"enp_paper_type:{self.enp_paper_type}")
        print(f"transfo_type:{self.transfo_type}")
        print(f"load_cycle_period:{self.load_cycle_period}")
        print(f"no_of_cycle_intervals:{self.no_of_cycle_intervals}")

        # Derive LTC bounds
        self.ltc_min_pos = 1
        self.ltc_max_pos = self.ltc_tap_step + 1

        # Cooling and loss parameters from xcool object if present
        for attr in (
            "LossBasekVA",
            "LossTempBase",
            "WindI2RLosses",
            "WindStrayLosses",
            "WindEddyLoss",
            "Power",
            "AvgWindingRise",
            "HotSpotRise",
            "TopOilRise",
            "BottomOilRise",
            "XfrmerRating",
            "XfrmerCooling",
            "XfrmerCoolLevel",
            "PerUnitBasekVA",
        ):
            if hasattr(xcool, "LossBasekVA"): 
                self.loss_base_kva = _coerce(getattr(xcool, "LossBasekVA"))
            if hasattr(xcool, "LossTempBase"):
                self.loss_temp_base = _coerce(getattr(xcool, "LossTempBase"))
            if hasattr(xcool, "PerUnitBasekVA"):
                self.per_unit_base_kva = _coerce(getattr(xcool, "PerUnitBasekVA"))
            if hasattr(xcool, "WindI2RLosses"):
                self.wind_i2r_losses = _coerce(getattr(xcool, "WindI2RLosses"))
            if hasattr(xcool, "WindStrayLosses"):
                self.wind_stray_losses = _coerce(getattr(xcool, "WindStrayLosses"))
            if hasattr(xcool, "WindEddyLoss"):
                self.wind_eddy_loss = _coerce(getattr(xcool, "WindEddyLoss"))
            if hasattr(xcool, "AvgWindingRise"):
                self.avg_winding_rise = _coerce(getattr(xcool, "AvgWindingRise"))
            if hasattr(xcool, "HotSpotRise"):
                self.hot_spot_rise = _coerce(getattr(xcool, "HotSpotRise"))
            if hasattr(xcool, "TopOilRise"):
                self.top_oil_rise = _coerce(getattr(xcool, "TopOilRise"))
            if hasattr(xcool, "BottomOilRise"):
                self.bottom_oil_rise = _coerce(getattr(xcool, "BottomOilRise"))
            if hasattr(xcool, "XfrmerRating"):
                self.xfrmer_rating = _coerce(getattr(xcool, "XfrmerRating"))
            if hasattr(xcool, "XfrmerCooling"):
                self.xfrmer_cooling = _coerce(getattr(xcool, "XfrmerCooling"))
            if hasattr(xcool, "XfrmerCoolLevel"):
                self.xfrmer_cool_level = _coerce(getattr(xcool, "XfrmerCoolLevel"))
           
        print(f"loss_base_kva:{self.loss_base_kva}")
        print(f"avg_winding_rise:{self.avg_winding_rise}")
        print(f"hot_spot_rise:{self.hot_spot_rise}")
        print(f"top_oil_rise:{self.top_oil_rise}")
        print(f"bottom_oil_rise:{self.bottom_oil_rise}")
        print(f"xfrmer_rating:{self.xfrmer_rating}")
        print(f"xfrmer_cooling:{self.xfrmer_cooling}")
        print(f"xfrmer_cool_level:{self.xfrmer_cool_level}")

        print(f"wind_i2r_losses:{self.wind_i2r_losses}")
        print(f"wind_stray_losses:{self.wind_stray_losses}")
        print(f"wind_eddy_loss:{self.wind_eddy_loss}")  
        print(f"per_unit_base_kva:{self.per_unit_base_kva}")
        print(f"loss_temp_base:{self.loss_temp_base}")
                  
        self.avg_oil_rise  = (self.top_oil_rise + self.bottom_oil_rise) / 2
        if (math.fabs(self.avg_oil_rise - (self.top_oil_rise + self.bottom_oil_rise) / 2) > 2):
            output_string += f"Average Oil Rise: {self.avg_oil_rise} | {(self.top_oil_rise + self.bottom_oil_rise) / 2} cannot be less or no greater than (TopOilRise + BottomOilRise) / 2.\n"
        print(f"avg_oil_rise:{self.avg_oil_rise} -{(self.top_oil_rise + self.bottom_oil_rise) / 2}")

        # Reference temperatures
        if self.loss_base_kva <= 0:
            output_string += "Base Rating for Losses cannot be lower or equal to zero.\n"

        # Derived load loss when provided
        if hasattr(xcool, "WindI2RLosses") and hasattr(xcool, "WindStrayLosses") and hasattr(xcool, "WindEddyLoss"):
            power = _coerce(getattr(xcool, "Power", 0.0))
            self.load_loss = (
                _coerce(getattr(xcool, "WindI2RLosses"))
                + _coerce(getattr(xcool, "WindStrayLosses"))
                + _coerce(getattr(xcool, "WindEddyLoss"))
                - power
            )  
        
        if (math.fabs(self.load_loss - (self.wind_i2r_losses + self.wind_stray_losses + self.wind_eddy_loss - power)) > 2):
                    output_string += f"LoadLoss: {self.load_loss}  WindI2RLosses: {self.wind_i2r_losses} \
                    WindStrayLosses: {self.wind_stray_losses} WindEddyLoss: {self.wind_eddy_loss}" + \
                        "Load Loss cannot be less or no greater than the Sum(WindI2RLosses + WindStrayLosses + WindEddyLoss).\n"

        print(f"load_loss:{self.load_loss}")
        # Ambient and moisture parameters if present
        ambient_key_map = {
            "RatedAmbient"          : "rated_ambient",
            "WindingTempBase"       : "winding_temp_base",
            "CoreLosses"            : "core_losses",
            "PUMinMUL"              : "pu_min_mul",
            "PUMaxMUL"              : "pu_max_mul",
            "InsLifeExp"            : "life_time",
            "FluidType"             : "fluid_type",
            "MassCoreCoil"          : "mass_core_coil",
            "MassTank"              : "mass_tank",
            "GallonsOfFluid"        : "gallons_of_fluid",
            "WindingConductor"      : "winding_conductor",
            "PerUnitHSEddyLoss"     : "per_unit_hs_eddy_loss",
            "PerUnitHeighToHotSpot" : "per_unit_heigh_to_hot_spot",
            "OverExcitation"        : "over_excitation",
            "TimeOverExcitation"    : "time_over_excitation",
            # "MassFluid"             : "mass_fluid",
            "MassCore"              : "mass_core",
            "MassWind"              : "mass_wind",
            # "MassSum"               : "mass_sum",
            "FluidDensity"          : "fluid_density",
            "WindTimeCst"           : "wind_time_cst",
            "CoreLossesOverEx"      : "core_losses_over_ex",
            "PerImpedance"          : "per_impedance",
            "PerResistance"         : "per_resistance",
            "PerReactance"          : "per_reactance",
            "TimeStep"              : "dt",
        }
        for key, attr in ambient_key_map.items():
            if key in poll_dictionary:
                setattr(self, attr, _coerce(poll_dictionary[key]))

        print(f"rated_ambient:{self.rated_ambient}")
        print(f"winding_temp_base:{self.winding_temp_base}")
        print(f"core_losses:{self.core_losses}")
        print(f"mass_core_coil:{self.mass_core_coil}")
        print(f"mass_tank:{self.mass_tank}")
        print(f"gallons_of_fluid:{self.gallons_of_fluid}")
        print(f"winding_conductor:{self.winding_conductor}")
        print(f"life_time:{self.life_time}")
        print(f"wind_time_cst:{self.wind_time_cst}")
        print(f"per_unit_heigh_to_hot_spot:{self.per_unit_heigh_to_hot_spot}")
        if (self.rated_ambient < -40 or self.rated_ambient > 60):
            output_string += "Rated Ambient Temperature must be between -40ºC and 60ºC.\n"
        print(f"per_unit_hs_eddy_loss:{self.per_unit_hs_eddy_loss}")
        print(f"over_excitation:{self.over_excitation}")
        print(f"time_over_excitation:{self.time_over_excitation}")
        print(f"core_losses_over_ex:{self.core_losses_over_ex}")
        print(f"dt:{self.dt}")


        if (self.winding_temp_base != 65 and self.winding_temp_base  != 55):
                output_string += "The Rated Average Winding Rise can only be either 65ºC for thermally ugraded paper, or 55ºC for non thermally upgraded paper.\n"

        if (self.winding_conductor not in [1, 2]):
            output_string += "Unknown Winding Conductor Type Selection.\n"

        if (self.wind_time_cst < MIN_WIND_TIME_CST):
            output_string += "Winding time constant cannot be lower than 5 Minutes.\n"

        if (self.mass_core_coil <= 0):
            output_string += "Weight of Core and Coils cannot be lower or equal to zero.\n"
                   
        if (self.mass_tank <= 0):
            output_string += "Weight of Tank and Fittings cannot be lower or equal to zero.\n"

        if (self.fluid_type not in [1, 2, 3]):
            output_string += "Unknown FluidType Selection.\n"

        if (self.gallons_of_fluid <= 0):
            output_string += "Gallons of Fluid cannot be lower or equal to zero.\n"

        if (self.life_time <= 0):
            output_string += "Insulation Life Expectancy cannot be lower or equal to zero.\n"

        self.no_of_cycle_intervals = (self.load_cycle_period + 1) * 12

        # Moisture coefficients
        moisture_keys = {
            "LowOxygenParmKrafta0"  : "low_oxygen_parm_kraft_a0",
            "LowOxygenParmKrafta1"  : "low_oxygen_parm_kraft_a1",
            "LowOxygenParmKrafta2"  : "low_oxygen_parm_kraft_a2",
            "LowOxygenParmTUKa0"    : "low_oxygen_parm_tuk_a0",
            "LowOxygenParmTUKa1"    : "low_oxygen_parm_tuk_a1",
            "LowOxygenParmTUKa2"    : "low_oxygen_parm_tuk_a2",
            "MedOxygenParmKrafta0"  : "med_oxygen_parm_kraft_a0",
            "MedOxygenParmKrafta1"  : "med_oxygen_parm_kraft_a1",
            "MedOxygenParmKrafta2"  : "med_oxygen_parm_kraft_a2",
            "MedOxygenParmTUKa0"    : "med_oxygen_parm_tuk_a0",
            "MedOxygenParmTUKa1"    : "med_oxygen_parm_tuk_a1",
            "MedOxygenParmTUKa2"    : "med_oxygen_parm_tuk_a2",
            "HighOxygenParmKrafta0" : "high_oxygen_parm_kraft_a0",
            "HighOxygenParmKrafta1" : "high_oxygen_parm_kraft_a1",
            "HighOxygenParmKrafta2" : "high_oxygen_parm_kraft_a2",
            "HighOxygenParmTUKa0"   : "high_oxygen_parm_tuk_a0",
            "HighOxygenParmTUKa1"   : "high_oxygen_parm_tuk_a1",
            "HighOxygenParmTUKa2"   : "high_oxygen_parm_tuk_a2",
        }
        for key, attr in moisture_keys.items():
            if key in poll_dictionary:
                setattr(self, attr, _coerce(poll_dictionary[key]))

        # Derived LTC ampacity if available
        if "LtcCapacity" in poll_dictionary:
            self.ltc_capacity = _coerce(poll_dictionary["LtcCapacity"])

        poll_updates = {
            "LossBasekVA"     : str(self.loss_base_kva),
            "PerUnitBasekVA"  : str(self.per_unit_base_kva),
            "XfrmerRating"    : str(self.xfrmer_rating),
            "XfrmerCooling"   : self.xfrmer_cooling,
            "XfrmerCoolLevel" : str(self.xfrmer_cool_level),
            "LossTempBase"    : str(self.loss_temp_base),
            "WindI2RLosses"   : str(self.wind_i2r_losses),
            "WindStrayLosses" : str(self.wind_stray_losses),
            "WindEddyLoss"    : str(self.wind_eddy_loss),
            "LoadLoss"        : str(self.load_loss),
            "AvgWindingRise"  : str(self.avg_winding_rise),
            "HotSpotRise"     : str(self.hot_spot_rise),
            "TopOilRise"      : str(self.top_oil_rise),
            "BottomOilRise"   : str(self.bottom_oil_rise),
            "AvgOilRise"      : str(self.avg_oil_rise),
        }

        for var_name, value in poll_updates.items():
            if isinstance(poll_dictionary, dict) and var_name in poll_dictionary:
                poll_dictionary[var_name] = value
            elif hasattr(poll_dictionary, "__iter__"):
                for row in poll_dictionary:
                    if ("varname" in row and row["varname"] == var_name) or (
                        hasattr(row, "varname") and getattr(row, "varname") == var_name
                    ):
                        if "value" in row:
                            row["value"] = value
                        elif hasattr(row, "value"):
                            setattr(row, "value", value)
                        break


        # Session and unit identifiers (optional)
        self.session_id = session_id
        self.xfrm_id = xfrm_id
