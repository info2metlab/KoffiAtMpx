import json
import logging
import threading
from pathlib import Path

from .models import (
    actionentries,
    conditions,
    datadictionaries,
    loadingcases,
    coolings,
    mconditions,
    mmifactors,
    modifiers,
    vardictionaries,
)
from mpxWeb import models


_logger = logging.getLogger(__name__)
_once_lock = threading.Lock()
_once_flag = False

base_dir = Path(__file__).resolve().parent / "CNAIMv2"

def import_template_dictionary_from_json(
    json_file_path: str, default_eqsernum: str = "Template", ignore_conflicts: bool = True
) -> int:
    """Load equipment dictionary rows from JSON into the eqdictionaries table."""
    path = Path(json_file_path)
    if not path.exists():
        _logger.warning("Template dictionary file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            entries = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse template dictionary JSON %s: %s", path, exc)
        return 0

    if not isinstance(entries, list) or not entries:
        return 0

    rows = []
    for entry in entries:
        rows.append(
            datadictionaries(
                varname=str(entry.get("Varname", "")),
                value=str(entry.get("Value", "")),
                unit=str(entry.get("Unit", "")),
                defaultv=str(entry.get("Defaultv", "")),
                description=str(entry.get("Description", "")),
                information=str(entry.get("Information", "")),
                groupname=str(entry.get("Groupname", "")),
            )
        )

    datadictionaries.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)

def import_mmi_factors_from_json(json_file_path: str) -> int:
    """
    Load MMI factor rows from a JSON file into the mmifactors table.
    Returns the number of rows queued for insert.
    """
    path = Path(json_file_path)
    if not path.exists():
        _logger.warning("MMI factors file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            mmi_factors = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse MMI factors JSON %s: %s", path, exc)
        return 0

    if not mmi_factors:
        return 0

    rows = []
    for factor in mmi_factors:
        rows.append(
            mmifactors(
                eqpmt=str(factor.get("Eqpmt", "")),
                subcomp=str(factor.get("Subcomp", "")),
                df1=str(factor.get("Df1", "")),
                df2=str(factor.get("Df2", "")),
                maxnofc=str(factor.get("Maxnofc", "")),
                modtype=str(factor.get("Modtype", "")),
            )
        )

    mmifactors.objects.bulk_create(rows, ignore_conflicts=True)
    return len(rows)

def import_mconditions_from_json(json_file_path: str, ignore_conflicts: bool = True) -> int:
    """Load measured condition rows from JSON into the mconditions table."""
    path = Path(json_file_path)
    if not path.exists():
        _logger.warning("Measured conditions file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            items = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse measured conditions JSON %s: %s", path, exc)
        return 0

    if not items:
        return 0

    rows = []
    for it in items:
        rows.append(
            mconditions(
                eqpmt=str(it.get("Eqpmt", "")),
                subcomp=str(it.get("Subcomp", "")),
                condtype=str(it.get("Condtype", "")),
                criteria=str(it.get("Criteria", "")),
                descp=str(it.get("Descp", "")),
                infactor=str(it.get("Infactor", "")),
                incap=str(it.get("Incap", "")),
                incollar=str(it.get("Incollar", "")),
            )
        )

    mconditions.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)

def import_modifiers_from_json(json_file_path: str, ignore_conflicts: bool = True) -> int:
    """Load modifier rows from JSON into the modifiers table."""
    path = Path(json_file_path)
    if not path.exists():
        _logger.warning("Modifiers file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            items = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse modifiers JSON %s: %s", path, exc)
        return 0

    if not items:
        return 0

    rows = []
    for it in items:
        rows.append(
            modifiers(
                eqpmt=str(it.get("Eqpmt", "")),
                low=str(it.get("Low", "")),
                high=str(it.get("High", "")),
                score=str(it.get("Score", "")),
                modtype=str(it.get("Modtype", "")),
            )
        )

    modifiers.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)

def import_observed_conditions_from_json(json_file_path: str, ignore_conflicts: bool = True) -> int:
    """Load observed condition rows from JSON into the conditions table."""
    path = Path(json_file_path)
    if not path.exists():
        _logger.warning("Observed conditions file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            items = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse observed conditions JSON %s: %s", path, exc)
        return 0

    if not items:
        return 0

    rows = []
    for cond in items:
        rows.append(
            conditions(
                eqpmt=str(cond.get("Eqpmt", "")),
                subcomp=str(cond.get("Subcomp", "")),
                condtype=str(cond.get("Condtype", "")),
                criteria=str(cond.get("Criteria", "")),
                descp=str(cond.get("Descp", "")),
                infactor=str(cond.get("Infactor", "")),
                incollar=str(cond.get("Incollar", "")),
                incap=str(cond.get("Incap", "")),
            )
        )

    conditions.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)

def import_var_dictionaries(eqpmt: str = "", ignore_conflicts: bool = True) -> int:
    """Seed the vardictionaries table with static variable definitions."""
    definitions = [
        {"varname": "ambient", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "Ambient temperature", "minvalue": "-15", "maxvalue": "35", "unit": "C"},
        {"varname": "topoil", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "Top oil temperature", "minvalue": "-15", "maxvalue": "35", "unit": "C"},
        {"varname": "hotspotx", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "X Winding Hot spot temperature", "minvalue": "80", "maxvalue": "150", "unit": "C"},
        {"varname": "hotspoty", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "Y Winding Hot spot temperature", "minvalue": "80", "maxvalue": "150", "unit": "C"},
        {"varname": "hotspotz", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "Z Winding Hot spot temperature", "minvalue": "80", "maxvalue": "150", "unit": "C"},
        {"varname": "oiltemp", "vargroup": "TEMPERATURE", "varsubgroup": "AVG", "description": "Liquid insulation temperature", "minvalue": "30", "maxvalue": "150", "unit": "C"},
        {"varname": "puloadx", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "X Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "puloady", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "Y Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "puloadz", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "Z Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "puloadc1", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "Z Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "puloadc2", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "Z Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "pumpload", "vargroup": "LOAD", "varsubgroup": "AVG", "description": "Z Winding Hot p.u. load", "minvalue": "0.5", "maxvalue": "1.3", "unit": "p.u."},
        {"varname": "moisture", "vargroup": "MOISTURE", "varsubgroup": "AVG", "description": "Moisture content in oil", "minvalue": "0.5", "maxvalue": "5", "unit": "ppm"},
        {"varname": "fanspeedc1", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Moisture content in oil", "minvalue": "150", "maxvalue": "1500", "unit": "rpm"},
        {"varname": "fanspeedc2", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Moisture content in oil", "minvalue": "150", "maxvalue": "1500", "unit": "rpm"},
        {"varname": "oilflow", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Oil flow in cooling ducts", "minvalue": "150", "maxvalue": "1500", "unit": "C"},
        {"varname": "oilpressure", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Oil pressure in cooling ducts", "minvalue": "150", "maxvalue": "1500", "unit": "C"},
        {"varname": "fannoise", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Fan noise", "minvalue": "20", "maxvalue": "80", "unit": "dB"},
        {"varname": "airflow", "vargroup": "COOLING", "varsubgroup": "AVG", "description": "Fans Air flow", "minvalue": "20", "maxvalue": "80", "unit": "Bar"},
        {"varname": "h2ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Hydrogen (H2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "ch4ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Methane (CH4)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c2h6ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Ethane (C2H6)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c2h4ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Ethylen (C2H4)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c3h6ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Propane (C3H6)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c3h8ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "propylen (C3H8)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "coppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Carbon Monoxide (CO)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "co2ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Carbondioxide (CO2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "n2ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Nitrogen (N2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "o2ppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Oxygen (O2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tdcgppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Total dissolved combustible Gas", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tcgppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Total combustible gas", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tdgppm", "vargroup": "DISSOLVED GASSES", "varsubgroup": "AVG", "description": "Total dissolved gas", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "ambientroc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "Ambient temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "topoilroc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "Top oil temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "hotspotxroc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "X Winding Hot spot temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "hotspotyroc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "Y Winding Hot spot temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "hotspotzroc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "Z Winding Hot spot temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "oiltemproc", "vargroup": "TEMPERATURE", "varsubgroup": "ROC", "description": "Oil temp. rate of change", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "puloadxroc", "vargroup": "LOAD", "varsubgroup": "ROC", "description": "X Winding p.u. load rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "puloadyroc", "vargroup": "LOAD", "varsubgroup": "ROC", "description": "Y Winding p.u. load rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "puloadzroc", "vargroup": "LOAD", "varsubgroup": "ROC", "description": "Z Winding p.u. load rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "puloadc1roc", "vargroup": "LOAD", "varsubgroup": "ROC", "description": "Cooling Bank 1 p.u. load rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "puloadc2roc", "vargroup": "LOAD", "varsubgroup": "ROC", "description": "Cooling Bank 2 p.u. load rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "moistureroc", "vargroup": "MOISTURE", "varsubgroup": "ROC", "description": "Per-unit moisture rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "fanspeedc1roc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "fanspeedc2roc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "oilflowroc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "oilpressureroc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "fannoiseroc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "airflowroc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "pumploadroc", "vargroup": "COOLING", "varsubgroup": "ROC", "description": "Fan speed rate of change", "minvalue": "0.0", "maxvalue": "0.1", "unit": "ppm"},
        {"varname": "h2ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Hydrogen (H2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "ch4ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Methane (CH4)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c2h6ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Ethane (C2H6)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c2h4ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Ethylen (C2H4)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c3h6ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Propane (C3H6)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "c3h8ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "propylen (C3H8)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "coppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Carbon Monoxide (CO)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "co2ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Carbondioxide (CO2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "n2ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Nitrogen (N2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "o2ppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Oxygen (O2)", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tdcgppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Total dissolved combustible Gas", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tcgppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Total combustible gas roc", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "tdgppmroc", "vargroup": "DISSOLVED GASSES", "varsubgroup": "ROC", "description": "Total dissolved gas roc", "minvalue": "20", "maxvalue": "1200", "unit": "ppm"},
        {"varname": "simstatus", "vargroup": "SYSTEM", "varsubgroup": "INTEROP", "description": "Simulation start/stop status", "minvalue": "0", "maxvalue": "1", "unit": "-"},
    ]

    rows = [
        vardictionaries(
            varname=item["varname"],
            vargroup=item["vargroup"],
            varsubgroup=item["varsubgroup"],
            description=item["description"],
            minvalue=item["minvalue"],
            maxvalue=item["maxvalue"],
            unit=item["unit"],
            eqpmt=eqpmt,
        )
        for item in definitions
    ]

    vardictionaries.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)

def import_alarm_settings(json_path: str | Path = "Recommendations.json", ignore_conflicts: bool = True) -> int:
    """Load alarm recommendations into the actionentries table."""
    path = Path(json_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    if not path.exists():
        _logger.warning("Recommendations file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse recommendations JSON %s: %s", path, exc)
        return 0

    if not isinstance(data, list):
        _logger.error("Recommendations payload must be a list of objects")
        return 0

    entries = []
    for item in data:
        asset_type = item.get("AssetType") or item.get("assettype") or ""
        component = item.get("Component") or item.get("component") or ""
        alarm_type = item.get("AlarmType") or item.get("alarmtype") or ""

        statements = item.get("Statement") or []
        recommendations = item.get("Recommendations") or []

        if isinstance(statements, list):
            statements_txt = ", ".join(str(s) for s in statements)
        else:
            statements_txt = str(statements)

        if isinstance(recommendations, list):
            recommendations_txt = ", ".join(str(r) for r in recommendations)
        else:
            recommendations_txt = str(recommendations)

        desc_parts = []
        if statements_txt:
            desc_parts.append(f"Statement: {statements_txt}")
        if recommendations_txt:
            desc_parts.append(f"Recommendations: {recommendations_txt}")
        description = " | ".join(desc_parts)

        entries.append(
            actionentries(
                assettype=str(asset_type),
                component=str(component),
                alarmtype=str(alarm_type),
                description=description,
            )
        )

    if not entries:
        return 0

    actionentries.objects.bulk_create(entries, ignore_conflicts=ignore_conflicts)
    return len(entries)


def import_degradations_from_json(json_path: str | Path = "Degradations.json", ignore_conflicts: bool = True) -> int:
    """Load degradation data into the degradation table."""
    path = Path(json_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    if not path.exists():
        _logger.warning("Degradations file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse degradation JSON %s: %s", path, exc)
        return 0

    if not isinstance(data, list):
        _logger.error("Degradation payload must be a list of objects")
        return 0

    rows = []
    for item in data:
        rows.append(
            models.degradations(
                varname=str(item.get("varname", "")),
                alphamin=float(item.get("alphamin", 0) or 0),
                alphamax=float(item.get("alphamax", 0) or 0),
                betamin=float(item.get("betamin", 0) or 0),
                betamax=float(item.get("betamax", 0) or 0),
                sigmamin=float(item.get("sigmamin", 0) or 0),
                sigmamax=float(item.get("sigmamax", 0) or 0),
                scoremin=float(item.get("scoremin", 0) or 0),
                scoremax=float(item.get("scoremax", 0) or 0),
                # DegradationType=str(item.get("DegradationType", "")),
                # AgeingRate=float(item.get("AgeingRate", 0) or 0),
                # NormalLife=float(item.get("NormalLife", 0) or 0),
                # MaxLife=float(item.get("MaxLife", 0) or 0),
            )
        )

    if not rows:
        return 0

    models.degradations.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)


def import_loading_cases(json_path: str | Path = "LoadingCases.json", ignore_conflicts: bool = True) -> int:
    """Load loading case definitions into the loadingcases table."""
    path = Path(json_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    if not path.exists():
        _logger.warning("Loading cases file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse loading cases JSON %s: %s", path, exc)
        return 0

    if not isinstance(data, list):
        _logger.error("Loading cases payload must be a list of objects")
        return 0

    rows = []
    for item in data:
        rows.append(
            loadingcases(
                LoadType=str(item.get("LoadType", "")),
                LtcPosition=int(item.get("LtcPosition", -1) or -1),
                HotSpotLimit=float(item.get("HotSpotLimit", 0) or 0),
                TopOilLimit=float(item.get("TopOilLimit", 0) or 0),
                LoLLimit=float(item.get("LoLLimit", 0) or 0),
                PULLimit=float(item.get("PULLimit", 0) or 0),
                BubblingLimit=float(item.get("BubblingLimit", 0) or 0),
                CoolPWLimit=float(item.get("CoolPWLimit", 0) or 0),
                BeginOverTime=float(item.get("BeginOverTime", 0) or 0),
                EndOverTime=float(item.get("EndOverTime", 0) or 0),
                InsLifeExp=float(item.get("InsLifeExp", 0) or 0),
                OxyContent=float(item.get("OxyContent", 0) or 0),
                MoisContent=float(item.get("MoisContent", 0) or 0),
                GasContent=float(item.get("GasContent", 0) or 0),
                HSPressure=float(item.get("HSPressure", 0) or 0),
                LtcAmpacity=float(item.get("LtcAmpacity", 0) or 0),
                OptimError=float(item.get("OptimError", 0) or 0),
                Scheduled       = bool(item.get("Scheduled", "")),
                LPlan           = str(item.get("LPlan", "NLEL"))
            )
        )

    if not rows:
        return 0

    loadingcases.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)


def import_nameplate_data(json_path: str | Path = "NamePlate.json", ignore_conflicts: bool = True) -> int:
    """Load nameplate cooling data into the coolings table."""
    path = Path(json_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parent / path

    if not path.exists():
        _logger.warning("Nameplate data file not found: %s", path)
        return 0

    try:
        with path.open("r", encoding="utf-8") as fp:
            data = json.load(fp)
    except json.JSONDecodeError as exc:
        _logger.error("Failed to parse nameplate data JSON %s: %s", path, exc)
        return 0

    if not isinstance(data, list):
        _logger.error("Nameplate data payload must be a list of objects")
        return 0

    rows = []
    for item in data:
        rows.append(
            coolings(
                Status=str(item.get("Status", "")),
                XfrmerCooling=str(item.get("XfrmerCooling", "")),
                numCooler=int(item.get("numCooler", 0) or 0),
                numFan=int(item.get("numFan", 0) or 0),
                numRadiator=int(item.get("numRadiator", 0) or 0),
                numPumps=int(item.get("numPumps", 0) or 0),
                PerUnitBasekVA=float(item.get("PerUnitBasekVA", 0) or 0),
                WindingTempBase=float(item.get("WindingTempBase", 0) or 0),
                AvgWindingRise=float(item.get("AvgWindingRise", 0) or 0),
                HotSpotRise=float(item.get("HotSpotRise", 0) or 0),
                TopOilRise=float(item.get("TopOilRise", 0) or 0),
                BottomOilRise=float(item.get("BottomOilRise", 0) or 0),
                AvgOilRise=float(item.get("AvgOilRise", 0) or 0),
                LossBasekVA=float(item.get("LossBasekVA", 0) or 0),
                LossTempBase=float(item.get("LossTempBase", 0) or 0),
                WindI2RLosses=float(item.get("WindI2RLosses", 0) or 0),
                WindEddyLoss=float(item.get("WindEddyLoss", 0) or 0),
                WindStrayLosses=float(item.get("WindStrayLosses", 0) or 0),
                XfrmerCoolLevel=float(item.get("XfrmerCoolLevel", 0) or 0),
                XfrmerRating=float(item.get("XfrmerRating", 0) or 0),
                LoadLoss=float(item.get("LoadLoss", 0) or 0),
                HRatedAmps=float(item.get("HRatedAmps", 0) or 0),
                XRatedAmps=float(item.get("XRatedAmps", 0) or 0),
                TRatedAmps=float(item.get("TRatedAmps", 0) or 0),
                Power=float(item.get("Power", 0) or 0),
            )
        )

    if not rows:
        return 0

    coolings.objects.bulk_create(rows, ignore_conflicts=ignore_conflicts)
    return len(rows)


def set_mpx_static_vars(base_dir: str | Path | None = None) -> dict:
    """
    Load CNAIM economic calibration data from JSON files into the database.
    Returns counts per dataset loaded.
    """
    base_path = Path(base_dir) if base_dir else Path.cwd() / "CNAIMv2"
    import_var_dictionaries(ignore_conflicts=True)
    counts = {
        "coolings": import_nameplate_data(base_path / "NamePlate.json"),
        "loadingcases": import_loading_cases(base_path / "LoadingCases.json"),
        "template": import_template_dictionary_from_json(base_path / "TemplateDictionary.json"),
        "mmi": import_mmi_factors_from_json(base_path / "MmiFactors.json"),
        "observed": import_observed_conditions_from_json(base_path / "ObservedConditions.json"),
        "measured": import_mconditions_from_json(base_path / "MeasuredConditions.json"),
        "modifiers": import_modifiers_from_json(base_path / "Modifiers.json"),
        "degradations": import_degradations_from_json(base_path / "Degradations.json"),

    }

    _logger.info(
        "MPX initial vars loaded (coolings=%s loadingcases=%s template=%s mmi=%s observed=%s measured=%s modifiers=%s, degradations=%s)",
        counts["coolings"],
        counts["loadingcases"],
        counts["template"],
        counts["mmi"],
        counts["observed"],
        counts["measured"],
        counts["modifiers"],
        counts["degradations"],
    )
    return counts


def initialize_app():
    global _once_flag
    if _once_flag:
        return
    with _once_lock:
        if _once_flag:
            return
        _perform_init()
        _once_flag = True


def _perform_init():
    # Place startup initialization logic here; keep minimal to avoid slowing boot
    set_mpx_static_vars(base_dir=base_dir)
    _logger.info("mpxWeb initialization complete")

