import logging
import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, List, Optional

from .XUtility import *





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
        self.dt = 0.0
        self.top_oil_rise = 0.0
        self.hot_spot_rise = 0.0
        self.avg_oil_rise = 0.0
        self.avg_winding_rise = 0.0
        self.bottom_oil_rise = 0.0
        self.duct_oil_rise = 0.0
        self.tested_avg_winding_rise = 0.0
        self.rated_delta_do_bo = 0.0
        self.rated_duct_avg_oil = 0.0
        self.rated_ambient = 0.0
        self.rated_avg_oil = 0.0
        self.rated_hot_spot = 0.0
        self.rated_duct_oil_at_hs = 0.0
        self.rated_avg_wind = 0.0
        self.rated_hsr_to_tor = 0.0
        self.tested_rated_avg_wind = 0.0
        self.rated_bottom_oil = 0.0
        self.rated_top_oil = 0.0
        self.rated_top_duct_oil = 0.0
        self.rated_tap_bottom_oil = 0.0
        self.rated_tap_top_oil = 0.0
        self.tested_rated_tap_avg_wind = 0.0
        self.rated_tap_avg_wind = 0.0
        self.rated_tap_hot_spot = 0.0
        self.rated_tap_delta_do_bo = 0.0
        self.rated_tap_hsr_to_tor = 0.0
        self.rated_to_time_cst = 0.0

        # Cooling mode and time constants
        self.i3e_cooling = ""
        self.wind_time_cst = 0.0
        self.to_time_cst = 0.0
        self.d_visc_cst = 0.0
        self.g_visc_cst = 0.0

        # Nameplate and tap settings
        self.xfrmer_rating = 0.0
        self.xfrmer_cooling = ""
        self.xfrmer_cool_level = 0.0
        self.transfo_type: str = ""
        self.h_rated_amps = 0.0
        self.x_rated_amps = 0.0
        self.t_rated_amps = 0.0
        self.h_rated_volt = 0.0
        self.x_rated_volt = 0.0
        self.t_rated_volt = 0.0
        self.h_rated_mva = 0.0
        self.x_rated_mva = 0.0
        self.t_rated_mva = 0.0
        self.hx_rated_mva = 0.0
        self.ht_rated_mva = 0.0
        self.xt_rated_mva = 0.0
        self.h_rated_t_losses = 0.0
        self.x_rated_t_losses = 0.0
        self.t_rated_t_losses = 0.0
        self.h_tap_amps = 0.0
        self.x_tap_amps = 0.0
        self.t_tap_amps = 0.0
        self.hx_load_loss = 0.0
        self.ht_load_loss = 0.0
        self.xt_load_loss = 0.0
        self.ltc_tap_range = 0.0
        self.ltc_tap_step = 1
        self.ltc_rated_pos = 0
        self.ltc_min_pos = 0
        self.ltc_max_pos = 0
        self.ltc_capacity = 0.0
        self.mva_capacity = 0.0
        self.is_tap_changing = 0
        self.ltc_winding = Winding.HV

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
            "XfrmID",
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

    def set_xfrm_dictionary(self, session_id: str, xfrm_id: str, xcool: Any) -> None:
        """Populate transformer parameters from a mapping of name -> value.

        Expects `poll_dictionary` to behave like a dict of string keys. Unknown
        keys are ignored; known ones are coerced to float/int/enum where
        appropriate. `xcool` is expected to expose attributes like LossBasekVA,
        LossTempBase, and loss components.
        """

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
            "DViscCst": "d_visc_cst",
            "GViscCst": "g_visc_cst",
            "LoadCyclePeriod": "load_cycle_period",
            "NoOfCycleIntervals": "no_of_cycle_intervals",
        }
        with Session(p_engine) as p_session:
            poll_dictionary = p_session.execute(select(datadictionaries).where(datadictionaries.c.groupname == "nameplate")).mappings()


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
            if hasattr(xcool, attr):
                setattr(self, attr.lower(), _coerce(getattr(xcool, attr)))
                    
            self.avg_oil_rise  = (self.top_oil_rise + self.bottom_oil_rise) / 2
            if (math.abs(self.avg_oil_rise - (self.top_oil_rise + self.bottom_oil_rise) / 2) > 2):
                output_string += f"Average Oil Rise: {self.avg_oil_rise} | {(self.top_oil_rise + self.bottom_oil_rise) / 2} cannot be less or no greater than (TopOilRise + BottomOilRise) / 2.\n"


        # Reference temperatures
        if hasattr(xcool, "LossBasekVA"):
            self.loss_base_kva = _coerce(getattr(xcool, "LossBasekVA"))
            if self.loss_base_kva <= 0:
                output_string += "Base Rating for Losses cannot be lower or equal to zero.\n"

        if hasattr(xcool, "LossTempBase"):
            self.loss_temp_base = _coerce(getattr(xcool, "LossTempBase"))

        # Per-unit base values
        if hasattr(xcool, "PerUnitBasekVA"):
            self.per_unit_base_kva = _coerce(getattr(xcool, "PerUnitBasekVA"))

        # Derived load loss when provided
        if hasattr(xcool, "WindI2RLosses") and hasattr(xcool, "WindStrayLosses") and hasattr(xcool, "WindEddyLoss"):
            power = _coerce(getattr(xcool, "Power", 0.0))
            self.load_loss = (
                _coerce(getattr(xcool, "WindI2RLosses"))
                + _coerce(getattr(xcool, "WindStrayLosses"))
                + _coerce(getattr(xcool, "WindEddyLoss"))
                - power
            )                             
            if (math.abs(self.load_loss - (self.wind_i2r_losses + self.wind_stray_losses + self.wind_eddy_loss - power)) > 2):
                        output_string += f"LoadLoss: {self.load_loss}  WindI2RLosses: {self.wind_i2r_losses} \
                        WindStrayLosses: {self.wind_stray_losses} WindEddyLoss: {self.wind_eddy_loss}" + \
                            "Load Loss cannot be less or no greater than the Sum(WindI2RLosses + WindStrayLosses + WindEddyLoss).\n"


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
            "MassFluid"             : "mass_fluid",
            "MassCore"              : "mass_core",
            "MassWind"              : "mass_wind",
            "MassSum"               : "mass_sum",
            "FluidDensity"          : "fluid_density",
            "WindTimeCst"           : "wind_time_cst",
            "CoreLossesOverEx"      : "core_losses_over_ex",
            "PerImpedance"          : "per_impedance",
            "PerResistance"         : "per_resistance",
            "PerReactance"          : "per_reactance",
            "DT"                    : "dt",
            "LifeTime"              : "life_time",

        }
        for key, attr in ambient_key_map.items():
            if key in poll_dictionary:
                setattr(self, attr, _coerce(poll_dictionary[key]))

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
                    if ("VarName" in row and row["VarName"] == var_name) or (
                        hasattr(row, "VarName") and getattr(row, "VarName") == var_name
                    ):
                        if "Value" in row:
                            row["Value"] = value
                        elif hasattr(row, "Value"):
                            setattr(row, "Value", value)
                        break


        # Session and unit identifiers (optional)
        self.session_id = session_id
        self.xfrm_id = xfrm_id


