import logging
import math
import json
from typing import Any, Callable, Iterable, List, Optional
from HelpThermalSolver import *
from HelpSolverAnalytics import *

        # public readonly LoadingStd ThermalStd = new LoadingStd
        # {
        #     XfrmID = "DUMMY",
        #     sessionId = "MPX",
        #     pubDate = DateTime.Now.ToString(),
        #     pubName = LoadingStandard.IEEEG,
        #     pubTitle = "Dummy title"
        # }

class SolverService:

    def __init__(self, thermal_std: Optional[Any]) -> None:
        self.xfrm_analytics  = SolverAnalytics()
        self.xfrm_assessment = ThermalSolver(self.xfrm_analytics, is_real_time=False)
        self.thermal_std = thermal_std
        self.logger = logging.getLogger(__name__)


    def to_minutes(start_date: str, end_date: str) -> dict:
        """Return start/end expressed in minutes.

        Accepts either numeric strings (minutes) or HH:MM strings. If start and end
        are equal, returns 0 and 1440.
        """

        def _parse(value: str) -> float:
            if ":" in value:
                hours, minutes = value.split(":", 1)
                return 60.0 * float(hours) + float(minutes)
            return float(value)

        if end_date == start_date:
            return {"start": 0.0, "end": 1440.0}

        return {
            "start": _parse(start_date),
            "end": _parse(end_date),
        }

   
    def set_xfrm_dictionary(self, session_id: str, xfrm_id: str, coolvar: Any) -> None:

        if not hasattr(self.xfrm_analytics, "set_xfrm_dictionary"):
            return
        try:
            self.xfrm_analytics.set_xfrm_dictionary(session_id, xfrm_id, coolvar)
        except TypeError:
            self.logger.warning("Legacy signature without poll_dictionary")


    def solver_update_cooling(
        self,
        total_cooling_power: float,
        epsilon: float = 1e-3,
        get_cooling_mode: Optional[Callable[[float], str]] = None,
    ) -> None:
        """Update cooling-derived limits (rating, rises, losses) for the active stage.

        This is a Python port of the commented C# logic that scales losses and temperature
        rises based on available cooling power. It operates on the current loading context
        (`Coolings` collection) and the analytics' core loss reference.
        """

        ctx = self._new_loading_context()
        if ctx is None:
            self.logger.warning("No loading context available; skipping cooling update")
            return

        coolings = getattr(ctx, "Coolings", []) or []
        on_cooling = next((c for c in coolings if str(getattr(c, "Status", "")).strip().upper() == "ON"), None)
        if not on_cooling:
            self.logger.info("No active cooling stage marked ON; skipping cooling update")
            return

        core_losses = float(getattr(self.xfrm_analytics, "core_losses", 0.0))
        power = float(getattr(on_cooling, "Power", 0.0))
        current_level = float(getattr(on_cooling, "XfrmerCoolLevel", 0.0))
        degraded = float(getattr(on_cooling, "Degraded", 0.0))

        if total_cooling_power <= 0:
            self.logger.warning("Total cooling power must be positive; got %s", total_cooling_power)
            return

        percent_level = 100.0 * power / total_cooling_power
        if degraded > 0 or abs(round(percent_level, 1) - current_level) <= 1e-1:
            return

        xcool_ref = coolings[0] if coolings else None
        ref_load_loss = float(getattr(xcool_ref, "LoadLoss", 0.0)) if xcool_ref else 0.0

        load_loss = float(getattr(on_cooling, "LoadLoss", 0.0))
        total_losses = load_loss + core_losses
        setattr(on_cooling, "TotalLosses", total_losses)

        if ref_load_loss + core_losses <= 0:
            self.logger.warning("Reference load loss plus core losses is zero; cannot scale cooling")
            return

        power_ratio = math.sqrt(total_losses / (ref_load_loss + core_losses))

        # Scale nameplate rating with available cooling power
        xfrmer_rating = float(getattr(xcool_ref, "XfrmerRating", 0.0)) if xcool_ref else 0.0
        new_rating = xfrmer_rating * power_ratio
        setattr(on_cooling, "XfrmerRating", new_rating)
        new_level = 100.0 * power / total_cooling_power
        if power == 0.0 and getattr(on_cooling, "Id", None) == 2:
            new_level = epsilon
        elif power == 0.0 and getattr(on_cooling, "Id", None) == 3:
            new_level = 2 * epsilon
        setattr(on_cooling, "XfrmerCoolLevel", new_level)

        # Evaluate cooling mode if helper provided
        if get_cooling_mode:
            try:
                setattr(on_cooling, "XfrmerCooling", get_cooling_mode(power))
            except Exception as exc:  # pragma: no cover - defensive
                self.logger.warning("get_cooling_mode failed: %s", exc)

        # Scale rises using analytics exponents
        winding_exp = getattr(self.xfrm_analytics, "winding_exp", 1.0) or 1.0
        oil_exp = getattr(self.xfrm_analytics, "oil_exp", 1.0) or 1.0

        def _scale(attr: str, exp: float) -> None:
            base_val = float(getattr(xcool_ref, attr, 0.0)) if xcool_ref else 0.0
            setattr(on_cooling, attr, base_val * math.pow(power_ratio, exp))

        _scale("AvgWindingRise", winding_exp)
        _scale("HotSpotRise", winding_exp)
        _scale("TopOilRise", oil_exp)
        _scale("BottomOilRise", oil_exp)

        top_oil = float(getattr(on_cooling, "TopOilRise", 0.0))
        bottom_oil = float(getattr(on_cooling, "BottomOilRise", 0.0))
        setattr(on_cooling, "AvgOilRise", (top_oil + bottom_oil) / 2.0)

        setattr(on_cooling, "LossBasekVA", new_rating)
        setattr(on_cooling, "PerUnitBasekVA", new_rating)

    async def solve_dynamic_plate(self, mpc_args: mpcArgs) -> OptimumResults:
        amb_step = 10  # retained from original for parity
        _ = amb_step  # avoid unused warning
        worst_amb: List[float] = []  # placeholder list; original code never filled it
        del worst_amb

        thermal_optimum: List[Any] = []
        plate_optimum: List[Any] = []
        mpc_profile  = mpc_args.loadProfile #[self._to_profile(p) for p in getattr(mpc_args, "mpcProfile", [])]
        session_id   = mpc_args.sessionId
        xfrm_id      = mpc_args.xfrmId
        mpc_scenario = mpc_args.loadingCase
        mpc_power    = mpc_args.mpcPower
        pof_failure  = mpc_args.mpcPof
        rx_ambient   = 0.0
        
        with Session(p_engine) as p_session:
            xcool        = p_session.execute(select(coolings)).all()
            for coolvar in xcool:
                # if hasattr(coolvar, "Power"):
                #     setattr(coolvar, "Power", mpc_power)

                # def _to_plain(o: Any):
                #     if isinstance(o, dict):
                #         return o
                #     d = getattr(o, "__dict__", None)
                #     if isinstance(d, dict):
                #         return {k: v for k, v in d.items() if not k.startswith("_")}
                #     try:
                #         return dict(o)
                #     except Exception:
                #         return repr(o)

                # profiles = [_to_plain(obj) for obj in mpc_profile]
                # Print JSON-safe, readable representation of the profile
                # print("mpc_profile =>", json.dumps(profiles, default=str))

                self.set_xfrm_dictionary(session_id, xfrm_id, coolvar)
                output_str = getattr(self.xfrm_analytics, "output_string", "")
                print(f"output_str => {output_str}"   )
                self.logger.info(f"PARAMETERS CHECKED OUTCOME {output_str}")
                if not output_str:
                    thermal_plate, thermals = self.xfrm_assessment.perform_trans_rating(
                        mpc_scenario,
                        mpc_profile,
                        self.thermal_std,
                        coolvar,
                        rx_ambient,
                        pof_failure
                    )
                    print(f"thermal_plate => {thermal_plate}"   )
                    if thermals:
                        thermal_optimum.extend(thermals)
                    if thermal_plate:
                        plate_optimum.append(thermal_plate)
                else:
                    self.logger.info(f"LOADABILITY_LIMITS: Could not run eNameplate due to: {output_str}")

            self.logger.info("==============================================================")
            self.logger.info(f"Session ID: {session_id}")
            self.logger.info(f"Transformer ID: {xfrm_id}")
            self.logger.info("End of the real-time forecast")
            self.logger.info(f"Thermal Results: {thermal_optimum}")
            self.logger.info(f"NamePlate Results: {plate_optimum}")
            self.logger.info("==============================================================")
            optimus_results                    =   OptimumResults()
            optimus_results.xfrm_id            =   xfrm_id
            optimus_results.thermal_results    =   thermal_optimum
            optimus_results.name_plate_results =   plate_optimum
            return optimus_results

    async def solve_without_limits(self, mpc_args: mpcArgs) -> OptimumResults:
        thermal_optimum: List[Any] = []
        plate_optimum: List[Any] = []
        mpc_profile = [self._to_profile(p) for p in getattr(mpc_args, "mpcProfile", [])]
        session_id = getattr(mpc_args, "sessionId", "")
        xfrm_id = getattr(mpc_args, "xfrmId", "")

        mpc_scenario = getattr(mpc_args, "mpcScenario", None)
        mpc_power    = getattr(mpc_scenario, "CoolPWLimit", 0.0) if mpc_scenario else 0.0
        xcool        = self.p_session.execute(coolings).select().all()

        for coolvar in xcool:
            if getattr(coolvar, "Status", None) != "ON":
                continue
            if hasattr(coolvar, "Power"):
                setattr(coolvar, "Power", mpc_power)

            self.set_xfrm_dictionary(session_id, xfrm_id, coolvar)
            output_str = getattr(self.xfrm_analytics, "output_string", "")
            self.logger.info("WITHOUT_LIMITS:%s", output_str)

            if not output_str:
                self.logger.info("Load profile: %s", mpc_profile)
                self.logger.info("mpcScenario: %s", mpc_scenario)

                thermal_plate, thermals = self.xfrm_real_assessment.perform_real_rating(
                    mpc_scenario,
                    mpc_profile,
                    self.thermal_std,
                    coolvar,
                )
                if thermals:
                    thermal_optimum.extend(thermals)
                if thermal_plate:
                    plate_optimum.append(thermal_plate)
            else:
                self.logger.info("MPC_REFERENCES: Could not run eNameplate due to: %s", output_str)

        self.logger.info("==============================================================")
        self.logger.info("Session ID: %s", session_id)
        self.logger.info("Transformer ID: %s", xfrm_id)
        self.logger.info("End of the real-time forecast")
        self.logger.info("Thermal Results: %s", thermal_optimum)
        self.logger.info("NamePlate Results: %s", plate_optimum)
        self.logger.info("==============================================================")

        return OptimumResults(xfrm_id=xfrm_id, thermal_results=thermal_optimum, name_plate_results=plate_optimum)

    async def solve_mpc_references(self, mpc_args: mpcArgs, mpc_standards: List[Any]) -> OptimumResults:
        thermal_optimum: List[Any] = []
        plate_optimum: List[Any] = []
        mpc_profile = [self._to_profile(p) for p in getattr(mpc_args, "mpcProfile", [])]
        session_id = getattr(mpc_args, "sessionId", "")
        xfrm_id = getattr(mpc_args, "xfrmId", "")

        mpc_scenario = getattr(mpc_args, "mpcScenario", None)
        mpc_power    = getattr(mpc_scenario, "CoolPWLimit", 0.0) if mpc_scenario else 0.0
        xcool        = self.p_session.execute(coolings).select().all()

        ambient_offset = 0.0

        for coolvar in xcool:
            if getattr(coolvar, "Status", None) != "ON":
                continue
            if hasattr(coolvar, "Power"):
                setattr(coolvar, "Power", mpc_power)

            self.set_xfrm_dictionary(session_id, xfrm_id, coolvar)

            output_str = getattr(self.xfrm_analytics, "output_string", "")
            self.logger.info("MPC_REFERENCES:%s", output_str)
            if not output_str:
                if not self.xfrm_assessment:
                    self.logger.warning("xfrm_assessment is missing; cannot run PerformTransRating")
                    continue
                thermal_plate, thermals = self.xfrm_assessment.perform_trans_rating(
                    mpc_scenario,
                    mpc_profile,
                    mpc_standards,
                    coolvar,
                    ambient_offset,
                )
                if thermals:
                    thermal_optimum.extend(thermals)
                if thermal_plate:
                    plate_optimum.append(thermal_plate)
            else:
                self.logger.info("MPC_REFERENCES: Could not run eNameplate due to: %s", output_str)

        self.logger.info("Session ID: %s", session_id)
        self.logger.info("Transformer ID: %s", xfrm_id)
        self.logger.info("End of the MPC forecast")
        return OptimumResults(xfrm_id=xfrm_id, thermal_results=thermal_optimum, name_plate_results=plate_optimum)
   