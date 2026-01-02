import shutil
from audioop import avgpp
from datetime import datetime
from enum import Enum
import math
import os
import threading
import numpy as np
import pandas as pd
import sqlalchemy as db
from sqlalchemy.orm import Session
from sqlalchemy import select
import time
import arrow

import requests
from urllib.error import HTTPError
import logging
import logging.handlers
logger = logging.getLogger('uNamePlate')
logger.setLevel(logging.INFO)

syslog_handler = logging.handlers.SysLogHandler(address=('localhost', 514))
logger.addHandler(syslog_handler)



# DATABASE PARAMETERS
os.environ["DB_HOST"]           = 'localhost'
# os.environ["DB_MAINTENANCE"]    = 'maintenance'
# os.environ["DB_ASSET_REPO"]     = 'assetrepo'
os.environ["DB_ASSET_RATING"]   = 'mpxdb'
os.environ["DB_PORT"]           = '3306'
os.environ["DB_USER"]           = 'root'
os.environ["DB_PASSW"]          = 'loadinghub'

# maintenance_string  = f"mysql://{os.environ['DB_USER']}:{os.environ['DB_PASSW']}@{os.environ['DB_HOST']}:{int(os.environ['DB_PORT'])}/{os.environ['DB_MAINTENANCE']}"
# asset_repo_string   = f"mysql://{os.environ['DB_USER']}:{os.environ['DB_PASSW']}@{os.environ['DB_HOST']}:{int(os.environ['DB_PORT'])}/{os.environ['DB_ASSET_REPO']}"
rating_string       = f"mysql://{os.environ['DB_USER']}:{os.environ['DB_PASSW']}@{os.environ['DB_HOST']}:{int(os.environ['DB_PORT'])}/{os.environ['DB_ASSET_RATING']}"

# Get the current file's directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Go up two levels and build an absolute path to the load data CSV
two_levels_up = os.path.abspath(os.path.join(current_directory, "..", ".."))
LOAD_DATA_FILE = os.path.normpath(os.path.join(two_levels_up, "mpxWeb/CNAIMv2", "24hNormal.csv"))


MIN_SCORE = 0.5
MAX_SCORE = 10.0
LOADCYCLE = 25
PERIODIC_USER = "QR_USER"

CH_HORIZON              = 75
ORX_HORIZON             = 25
MAX_LEARNING_SCORE      = 1.0
ALPHA                   = 0.5
NUM_LEARNING_EPISODES   = 626
DISCOUNT_RATE           = 0.1

CoolingModes = ["ONAN", "ONAF", "ODAF", "ODWF", "OFWF", "OFAF", "OFAN", "OA", "FOA", "FA"]
Voltages = ["<110kV (Class1)", "110kV-220kV (Class2)", ">220kV (Class3)"]
Liquids = ["MINERAL OIL", "ESTER", "SILICONE", "DRY-AIR"]
Solids = ["UPGRADED-KRAFT", "NON-UPGRADED", "UPGRADED-ARAMID"]
AssetTypes = ["DISTRIBUTION", "POWER", "AUTO", "INSTRUMENT", "REGULATOR", "RECTIFIER"]
AssetCat = ["HV TRANSFORMER", "EHV TRANSFORMER", "AUTO", "INSTRUMENT", "REGULATOR", "RECTIFIER"]
TankTypes = ["FREE-BREATHING", "SEALED TANK"]
PevOptions = ["Uncontrolled Charging (UC)", "Controlled charging (CC)"]
xType = ["FREE-BREATHING", "SEALED TANK"]
XfmerPhases = ["1-PHASE", "3-PHASE"]
XWindings = ["HV", "LV", "TV"]
LtcLocation = ["INTEGRATED", "SEPARATED"]
ScanCollector = ["HOURLY", "DAILY", "WEEKLY"]
Statistics = ["AVERAGE", "STD", "25th-PERCENTILE", "50th-PERCENTILE"]
ThreshList = ["STATIC", "ANOMALY"]


class Severity(Enum):
        NORMAL = 0
        CAUTION = 1
        ALERT = 2
        ALARM = 3
        EMERGENCY = 4

class EvtStatus(Enum):
        PENDING = 0
        ACKNOWLEDGED = 1
        RESOLVED = 2
        DISMISSED = 3
        INFO = 4


class MaintenanceCost:
    asset_id            = ""
    score               = 0.0
    inspection_cost     = 0.0
    testing_cost        = 0.0
    pm_replacement_cost = 0.0        # PM_REPLACEMENT
    minimum_repair_cost = 0.0        # MINIMUM_REPAIR
    disposal_cost       = 0.0        # DISPOSAL
    refurbishment_cost  = 0.0        # UPGRADE
    cm_replacement_cost = 0.0        # CM_REPLACEMENT  
    monitoring_cost     = 0.0       # MONITORING      
    repair_factor       = 0.0       # REPAIR_FACTOR 
    em_replacement_cost = 0.0       # Emergency repair cost 
    
    # Degradation model parameters
    a                   = 0.2, # component['a']
    b                   = 1.2 # component['b']
    sigma               = 0.2 # component['sigma'] 


# --------------------------------#
# Database Tables                 #
# --------------------------------#
metadata            = db.MetaData()

# m_engine            = db.create_engine(maintenance_string,
#                                        pool_pre_ping=True,  # checks if connection is alive before using
#                                        pool_recycle=3600)   # recycles connections to avoid timeout
                        
# r_engine            = db.create_engine(asset_repo_string, pool_pre_ping=True, pool_recycle=3600)
p_engine            = db.create_engine(rating_string, pool_pre_ping=True, pool_recycle=3600)

# healthresults        = db.Table("healthresults", metadata, autoload_with=p_engine)
# xfrmmaps             = db.Table("xfrmmaps", metadata, autoload_with=p_engine)
vardictionaries      = db.Table("vardictionaries", metadata, autoload_with=p_engine)
measconditions      = db.Table("measconditions", metadata, autoload_with=p_engine)

loadcurves           = db.Table("loadcurves", metadata, autoload_with=p_engine)
loadresults          = db.Table("loadresults", metadata, autoload_with=p_engine)
loaddistros          = db.Table("loaddistros", metadata, autoload_with=p_engine)
thermaldistros       = db.Table("thermaldistros", metadata, autoload_with=p_engine)

loadprofiles         = db.Table("loadprofiles", metadata, autoload_with=p_engine)

# labresults           = db.Table("labresults", metadata, autoload_with=p_engine)
datadictionaries     = db.Table("datadictionaries", metadata, autoload_with=p_engine)
loadcbdistros        = db.Table("loadcbdistros", metadata, autoload_with=p_engine)
degradations          = db.Table("degradations", metadata, autoload_with=p_engine)

# dgaresults           = db.Table("dgaresults", metadata, autoload_with=p_engine)
# nameplates           = db.Table("nameplates", metadata, autoload_with=p_engine)
coolings             = db.Table("coolings", metadata, autoload_with=p_engine)
loadingcases         = db.Table("loadingcases", metadata, autoload_with=p_engine)

alarmitems           = db.Table("alarmitems", metadata, autoload_with=p_engine)
alarmconfigs         = db.Table("alarmconfigs", metadata, autoload_with=p_engine)
alarmentries         = db.Table("alarmentries", metadata, autoload_with=p_engine)
actionentries        = db.Table("actionentries", metadata, autoload_with=p_engine)

modifiers            = db.Table("modifiers", metadata, autoload_with=p_engine)
mmifactors           = db.Table("mmifactors",  metadata, autoload_with=p_engine)
mconditions          = db.Table("mconditions", metadata, autoload_with=p_engine)
conditions           = db.Table("conditions",  metadata, autoload_with=p_engine)


# SimulationPath = "../XReliability"
DATE_FMT = '%m/%d/%Y %I:%M:%S %p'

format2 = '%Y-%m-%d %H:%M:%S %p'
# Format date in ISO 8601 (international standard)
iso_format = '%Y-%m-%dT%H:%M:%S'

def parse_dt(val: str) -> datetime:
    try:
        return datetime.strptime(val, DATE_FMT)
    except (TypeError, ValueError) as ex:
        logger.error("Failed to parse datetime '%s' with format '%s': %s", val, DATE_FMT, ex)
        raise

FLEET_LABELS = ["VERY GOOD", "GOOD", "FAIR", "BAD", "POOR", "VERY POOR"]
ALARM_LABELS = ["CAUTION", "ALERT", "ALARM", "EMERGENCY"]
NUMBER_DGA_SCORES = 11

black       = (0, 0, 0)
green       = (0, 255, 0)
ligthgreen  = (0, 0, 0)
yellow      = (255, 255, 0)
orange      = (255, 128, 0)
red         = (255, 0, 0)
brown       = (58, 31, 4)
white       = (255, 255, 255)
grey        = (128, 128, 128)


# ------------------------------------------------------------
# Function: archive_best_models
# Purpose:
#   Create a dated snapshot (archive) of the current contents of
#   the BestKoffi directory inside BestKoffi/Arxiv.
# Behavior:
#   - Skips the existing Arxiv subfolder to avoid recursive growth.
#   - Creates destination folder: BestKoffi/Arxiv/archive_YYYYMMDD_HHMMSS
#   - Copies all other files/subfolders preserving metadata.
#   - Returns the full path of the created archive folder (or "" if source missing).
# Steps (pseudocode):
#   1. Verify source directory (best_models_dir) exists; warn + return "" if not.
#   2. Ensure archive root directory (arxiv_models_dir) exists.
#   3. Generate UTC timestamp string.
#   4. Build destination folder path using prefix + timestamp.
#   5. Copy tree from source to destination excluding 'Arxiv' subfolder.
#   6. Log success and return destination path.
#   7. Handle any exception: log error and return "".
# ------------------------------------------------------------
def archive_best_models(
    archive_root: str,
    source_root: str,
    prefix: str = "archive"
) -> str:
    if not os.path.isdir(source_root):
        logger.warning(f"Archive skipped: source directory not found -> {source_root}")
        return ""
    os.makedirs(archive_root, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(archive_root, f"{prefix}_{ts}")
    try:
        shutil.copytree(
            source_root,
            dest,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns('Arxiv')  # avoid nesting previous archives
        )
        logger.info(f"Archived best models from '{source_root}' to '{dest}'")
        return dest
    except Exception as e:
        logger.error(f"Archiving failed: {e}")
        return ""


class LoadProfile:
    sessionId   = ""
    IsSelected  = True
    xfrmId      = ""
    profileName = "PERIODIC"
    time        = ""
    sumamb      = ""
    sumpul      = ""
    sumcool     = ""

class LoadingCase:
    xfrmId          = "",
    sessionId       = PERIODIC_USER,
    LoadType        = '24-hNormal',
    HotSpotLimit    = '120',
    TopOilLimit     = '105',
    LoLLimit        = '0.037',
    PULLimit        = '1.0',
    BubblingLimit   = '150',
    CoolPWLimit     = '0',
    BeginOverTime   = '0',
    EndOverTime     = '24',
    InsLifeExp      = '65000',
    OxyContent      = '10',
    MoisContent     = '10',
    HSPressure      = '22'
    LtcPosition     = '-99'
    LtcAmpacity     = '5'
    OptimError      = '0.001'
    Scheduled        = True

class LoadResult:
    eqsernum    = '' 
    loadtype    = ''
    sampdate    = ''
    uptopoil    = '0'
    uphotspot   = '0'
    upload      = '0'  
    upbottom    = '0'
    uplife      = '0.0'
    ttptop      = '0.0'
    ttphot      = '0.0'
    ttpmva      = '0.0'
    upsimu      = ''
    cycle       = 0

class LoadCurve:
    eqsernum    = ''
    loadtype    = ''
    sampdate    = arrow.now().int_timestamp
    otime       = '0'
    opamb       = '0.0'
    obload      = '0.0'
    optopoil    = '0.0'
    ophotspot   = '0.0'
    opload      = '0.0 '
    opbottom    = '0.0'
    oplife      = '0.001'
    opage       =' 0'
    osimu       = ''
    cycle = 0

class LOADING(Enum):
    REFERENCE = 0
    MEASURED  = 1
    SEASONAL  = 2

# FAILURE_DATA_FILE = "C:\\Users\\sonia\\OneDrive\\Desktop\\XReliability\\failure_data.csv"
class SETPOINTS(Enum):
    TOPOIL_TEMPERATURE      =   0
    HOTSPOT_TEMPERATURE     =   1
    WINDING_TEMPERATURE     =   2
    PU_LOAD                 =   3

class MaintStrategy(Enum):
    REACTIVE        =   0
    PREVENTATIVE    =   1
    CONDITION_BASED =   2
    PREDICTIVE      =   3
    RELIABLE_RCM    =   4


class MaintAction(Enum):
    IDLE                    = 0      # No maintenance action
    INSPECT_AND_TESTING     = 1      # Scheduled Inspections: Regularly checking the asset to identify potential issues early.
    ROUTINE_SERVICING       = 2      # Tasks like lubrication, filter changes, cleaning, and recalibration to ensure smooth operation.
    CONDITION_MONITORING    = 3      # Condition Monitoring: Using sensors or diagnostic tools to track the health of the asset, such as checking temperature, vibration, or pressure.
                                     # Data Analysis: Leveraging historical data and trends to predict when parts are likely to fail.
                                     # Technology Integration: Using AI, machine learning, or IoT (Internet of Things) to automate monitoring and anticipate repair needs.
    MINIMUM_REPAIR          = 4      # Minor Repair: Fixing small issues before they escalate, such as replacing worn parts.
    UNAVAIL_FOR_SERVICE     = 5
    PM_REPLACEMENT          = 6      # preventive maintenance planned replacement
    CM_REPLACEMENT          = 7      # Breakdown Response: Addressing unexpected failures or malfunctions to restore functionality quickly.
    EM_REPLACEMENT          = 8      # emergency replacement when ran to failure
    REFURBISHMENT           = 9      # Upgrades or refurbishments to extend usability.Adding new components, software updates, or modern technologies to improve the asset's functionality.
    DISPOSAL                = 10     # Disposal: Retiring the asset from service when it is no longer cost-effective to maintain or repair.


FPF_CONDITION_GRADE = '''Condition is currently monitored visually by the Fleet Supervisor before budget. \
The visual inspection per the Fleet Performance Policy grades an excellent as 0; Good as 10; Fair as 25 and Poor as 40. \
The Asset Management Strategy translates the fleet score card to a 1-5 grading system as detailed in Table 5.3.3.\
It is important that a consistent and standard approach is used in reporting asset performance enabling effective decision support.'''

FPF_PROB_FAILURE = '''Without improved maintenance(preventive or condition-based) condition declines, leading to an increased Failure Probabilities. Case with CBM shows benefits of improved maintenance: fewer units with high failure probabilities in future years.'''
FPF_FAILURE_RATE = '''Without improved maintenance(preventive or condition-based) condition declines, leading to an increased Failure Probabilities. Case with CBM shows benefits of improved maintenance: fewer units with high failure probabilities in future years.'''
APPRAISAL_INTRO = '''An asset condition appraisal and reliability report is a document that evaluates the condition of an asset and its reliability. The report involves periodically monitoring assets and collecting data to determine their condition. This data can include the asset's location, condition, likelihood of failure, and more.'''


class MpcState:
    xfrmId     = ""
    sessionId  = ''
    otime      = " "
    inlet      = " "
    outlet     = " "
    topoil     = " "
    hotspot    = " "
    puload     = " "
    fpower     = " "
    ppower     = " "
    nfans      = " "        # active fans
    npumps     = " "      

class action:
    Cw          = 0.0
    Cp          = 0.0
    n_pumps     = 0
    n_fans      = 0



class timetofail:
    def __init__(self):
       self.Eqsernum    = ""
       self.TTF   = '0',
       self.Score = '0'


class LoadType(Enum):
    NLEL = 0
    PLBN = 1
    STE = 2
    LTE = 3



class LoadingStandard(Enum):
    IEEEG   = 0
    IEEE7   = 1
    IEC     = 2

class ReportType(Enum):
    LOAD_REPORT = 0
    FLEET_REPORT = 1
    MAIN_PLAN_REPORT = 2
    DGA_REPORT = 3
    TRANSFORMER_E_NAMEPLATE = 4,
    APPRAISAL_REPORT= 5


class VClass(Enum):
    V_CLASS_MORE_230_KV = 0
    V_CLASS_69KV_230_KV = 1
    V_CLASS_138KV_230_KV = 2
    V_CLASS_69KV_138_KV = 3
    V_CLASS_LESS_69_KV = 4

class DegCmd(Enum):
    PREVIEW = 0
    SURVIVAL = 1,
    DEGRADATION = 2,

class DevStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1

class Risk(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2

class AccessType(Enum):
    TYPE_A = 0
    TYPE_B = 1
    TYPE_C = 2

class AssetCat(Enum):
    HV_TRANSFORMER          = 0
    EHV_TRANSFORMER         = 1
    UHV_TRANSFORMER         = 2
    ALL_TRANSFORMER         = 4
    LV_TRANSFORMER          = 5

    LV_SWITCHGEAR           = 6
    HV_SWITCHGEAR           = 7
    EHV_SWITCHGEAR          = 8
    UHV_SWITCHGEAR          = 9

    CIRCUIT_BREAKER         = 10
    RECTIFIERS              = 11
    SHUNT_REACTORS          = 12
            
    GENERATOR_TRANSFORMERS  = 13
    SUBSTATION_TRANSFORMERS = 14
    BUSHINGS = 15
    
    
class Asset(Enum):
    
    # HV_TRANSFORMER
    HV_6p6_11kV_TRANSFORMER     = 0
    HV_20kV_TRANSFORMER         = 1
    # EHV_TRANSFORMER
    HV_33kV_TRANSFORMER         = 2
    HV_66kV_TRANSFORMER         = 3

    # UHV_TRANSFORMER
    HV_132kV_TRANSFORMER        = 4

    # LV_SWITCHGEARS_AND_OTHER
    LV_BOARD_WM                 = 5
    LV_BOARD_XTYPE_WM           = 6
    LV_BOARD_CB                 = 7
    LV_PILLAR_ID                = 8
    LV_PILLAR_OD_SUBSTATION     = 9
    LV_PILLAR_OD_NOT_SUBSTATION = 10

    # HV_SWITCHGEARS_GM_PRIMARY
    HV_6p6_11kV_CB_GM_PRIMARY   = 11
    HV_20kV_CB_GM_PRIMARY       = 12

    # HV_SWITCHGEARS_GM_DISTRIBUTION
    HV_6p6_11kV_CB_GM_SECONDARY = 13
    HV_6p6_11kV_RMU             = 14
    HV_6p6_11kV_XTYPE_RMU       = 15
    HV_6p6_11kV_SWITCH_GM       = 16
    HV_20kV_CB_GM_SECONDARY     = 17
    HV_20kV_RMU                 = 18
    HV_20kV_SWITCH_GM           = 19

    # EHV_SWITCHGEARS_GM
    HV_33kV_CB_AIS_ID           = 20
    HV_33kV_CB_AIS_OD           = 21
    HV_33kV_CB_GIS_ID           = 22
    HV_33kV_CB_GIS_OD           = 23
    HV_33kV_RMU                 = 24
    HV_33kV_SWITCH_GM           = 25

    HV_66kV_CB_AIS_ID           = 26
    HV_66kV_CB_AIS_OD           = 27
    HV_66kV_CB_GIS_ID           = 28
    HV_66kV_CB_GIS_OD           = 29

    # UHV SWITCHGEARS_GM
    HV_132kV_CB_AIB_ID          = 30
    HV_132kV_CB_AIB_OD          = 31
    HV_132kV_CB_GIB_ID          = 32
    HV_132kV_CB_GIB_OD          = 33
        
    # LV_OHL_SUPPORT
    LV_POLES                    = 34

    # HV_OHL_SUPPORT_POLES
    HV_6p6_11kV_POLES           = 35
    HV_20kV_POLES               = 36

    # EHV_OHL_SUPPORT_POLES
    HV_33kV_POLES               = 37
    HV_66kV_POLES               = 38

    # EHV_OHL_SUPPORT_TOWER
    HV_33kV_TOWER               = 39
    HV_66kV_TOWER               = 40
    
    # UHV_OHL_SUPPORT_TOWER
    HV_132kV_TOWER              = 41

    # LV_UGB
    LV_UGB                      = 42

    # EHV_UG_CABLE (GAS INSULATED, NON PRESSURIZED, OIL)
    HV_33kV_UG_CABLE_GAS        = 43
    HV_66kV_UG_CABLE_GAS        = 44

    HV_33kV_UG_CABLE_NP         = 45
    HV_66kV_UG_CABLE_NP         = 46

    HV_33kV_UG_CABLE_OIL        = 47
    HV_66kV_UG_CABLE_OIL        = 48

    # UHV_UG_CABLE (GAS INSULATED, NON PRESSURIZED, OIL)
    HV_132kV_UG_CABLE_GAS       = 49
    HV_132kV_UG_CABLE_NP        = 50
    HV_132kV_UG_CABLE_OIL       = 51



class Env(Enum):        
    INDOOR = 0
    OUTDOOR = 1

class SubAsset(Enum):  
    MAIN_TANK = 0
    COOLER_RADIATOR = 1
    ALL_TRANSFORMER = 2
    CABLE_BOX = 3
    TAP_CHANGER = 4

class AssetCond(Enum):  
    INTERNAL_CONDITION          = 0
    EXTERNAL_CONDITON           = 1
    DRIVE_MECHANISM             = 2
    PARTIAL_DISCHARGE           = 3
    SELECTOR_DIVERTER_CONTACTS  = 4
    SELECTOR_DIVERTER_BRAIDS    = 5
    TEMPERATURE_READINGS        = 6
    CABLE_BOX_CONDITION         = 7
    KIOSK_CONDITION             = 8
    BUSHINGS_CONDITION          = 9
    COOLERS_RADIATOR_CONDITION  = 10
    MAIN_TANK_CONDITION         = 11
    THERMAL_CONDITION           = 12
    OIL_CONDITION               = 13
    PAPER_CONDITION             = 14
    TAP_CHANGER                 = 15
    GLOBAL                      = 16

class CondState(Enum):  
    DEFAULT                         = 0
    LOW                             = 1
    MEDIUM                          = 2
    HIGH_NOT_CONFIRMED              = 3
    HIGH_CONFIRMED                  = 4
    NORMAL                          = 5
    MODERATELY_HIGH                 = 6
    VERY_HIGH                       = 7
    SUBSTANTIAL_DETERIORATION       = 8
    SOME_DETERIORATION              = 9
    SUPERFICIAL_MINOR_DETERIORATION = 10
    NO_DETERIORATION                = 11
    SLIGHT_DETERIORATION            = 12
        
class Modes(Enum):  
    MOISTURE                    = 0
    ACIDITY                     = 1
    BD_STRENGTH                 = 2
    OIL_CONDITION_SCORE         = 3
    OIL_TEST_COLLAR             = 4
    HYDROGEN_CONDITION          = 5
    METHANE_CONDITION           = 6
    ETHYLENE_CONDITION          = 7
    ETHANE_CONDITION            = 8
    ACETYLENE_CONDITION         = 9
    DGA_TEST_FACTOR             = 10
    FFA_TEST_FACTOR             = 11
    HEALTH_SCORE_MODIFIER       = 12
    OBSERVED_CONDTION_MODIFIER  = 13
    MEASURED_CONDTION_MODIFIER  = 14


class YesNoTap(Enum):
    NO_TAP  = 0
    WITH_TAP = 1

class Security(Enum):
    NON_SECURED = 0
    SECURED = 1

class SolidInsulation(Enum):
    THERMALY_UPGRADED_PAPER = 0
    NORMAL_KRAFT_PAPER = 1

    
class TemperatureTypes(Enum):
    TOP_OIL = 0
    HOT_SPOT = 1
    BOT_OIL = 2
    BUBBLING =3

class RoCLimitsTypes(Enum):   
        G1 = 0,
        G2 = 1

class DGARateOfChangeFactors:
    def __init__(self):
        self.G1 = 0
        self.G2 = 0


class LevelType(Enum):
    NORMAL = 0
    CAUTION = 1
    WARNING = 2

class GasesTypes(Enum):
    C2H2 = 0
    C2H4 = 1
    C2H6 = 2
    C3H6 = 3
    CH4 = 4
    CO = 5
    CO2 = 6
    H2 = 7
    O2 = 8
    N2 = 9
    TDCG = 10
    
class CIWeighFactors(Enum):
    DGA_WF              = 0
    HST_WF              = 1
    TOP_WF              = 2
    BUBB_WF             = 3
    BOARD_BP_WF         = 4
    OIL_BP_WF           = 5
    LOAD_WF             = 6
    BUSHING_WF          = 7
    LOL_WF              = 8
    TAP_WF              = 9
    OIL_QUALITY_WF      = 10
    SERVICE_AGE_WF      = 11
    HST_INSUL_AGE_WF    = 12
    CORE_MEGGER_WF      = 13
    WINDING_INSUL_WF    = 14
    INSUL_DP_WF         = 15
    OIL_FURAN_WF        = 16
    MOIS_IN_OIL_WF      = 17
    MOIS_IN_PAPER_WF    = 18
    LTC_WF              = 19
    HVBUSHING_ONLINE_WF = 20
    HVBUSHING_OFFLINE_WF = 21
    PD_WF                = 22

class RoCLimitsTypes(Enum):
        G1 = 0
        G2 = 1

class Severity(Enum):
    NORMAL      = 0
    CAUTION     = 1
    ALERT       = 2
    ALARM       = 3
    EMERGENCY   = 4
    BLACKOUT    = 5

class EvtStatus(Enum):
    PENDING = 0
    ACKNOWLEDGED = 1
    RESOLVED = 2
    DISMISSED = 3
    INFO = 4

class GridEdge(Enum):
    PRIMARY = 0
    SECONDARY = 1
    TERTIARY = 2
        
class TCValue:
     def __init__(self): 
          self.tcCondition = 0
          self.tcGasType = GasesTypes()
          self.ppmValue = 0.0


# ------------------------ #
# Deserialization object   #   
# ------------------------ #
def gaussErrorFunction(x):
    err = 0.0;
    t = (1 / (1 + 0.5 * math.fabs(x)))
    tau = t * math.exp(-math.pow(x,2) - 1.26551223 + 1.00002368 * t + 0.37409196 * math.pow(t,2) + 0.09678418 * math.pow(t,3)
                                - 0.18628806 * math.pow(t, 4) + 0.27886807 * math.pow(t, 5) - 1.13520398 * math.pow(t, 6)
                                + 1.48851587 * math.pow(t, 7) - 0.82215223 * math.pow(t, 8) + 0.17087277 * math.pow(t, 9))
    if (x >= 0):
        err = 1 - tau
    else:
        err = tau - 1
    return err

def altspace(start, step, count, endpoint=False):
   stop = start + (step*count)
   return np.linspace(start, stop, count, endpoint=endpoint)

class RepeatEvery(threading.Thread):
    def __init__(self, interval, func, *args, **kwargs):
        threading.Thread.__init__(self)
        self.interval = interval  # seconds between calls
        self.func = func          # function to call
        self.args = args          # optional positional argument(s) for call
        self.kwargs = kwargs      # optional keyword argument(s) for call
        self.runable = True
        self.cycle = 0

    def run(self):
        while self.runable:
            self.func(*self.args, **self.kwargs)
            time.sleep(self.interval)
            # self.cycle = self.cycle + 1

    def stop(self):
        self.runable = False

    # def get_cycle(self):
    #     return self.cycle

def get_load_references (equipId, mode):
    ref_state = []
    try:
        mode = 'REFERENCE'
        response = requests.post(os.environ["API_URL"] + '/getloadcurve', data={'equipId':equipId, 'mode':mode}, verify=False)                         
        df = pd.DataFrame(response.json())
        print("=========== Ref state ==========") 
        print(df)
        if df.__len__():   
            df['opamb'] = df['opamb'].astype('float')
            df['optopoil'] = df['optopoil'].astype('float')
            df['ophotspot'] = df['ophotspot'].astype('float')
            df['opload'] = df['opload'].astype('float')
            df['opbottom'] = df['opbottom'].astype('float')
            df['obload'] = df['obload'].astype('float')
            ref_state  = pd.DataFrame(df, columns=['sampdate', 'opamb', 'optopoil','ophotspot','opload', 'obload', 'opbottom'])

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
        
    return ref_state

def create_random_step_curve(length=20, steps=2):  
    step_size = length // steps  
    curve = []  

    for step in range(steps):  
        value = np.random.uniform(0, 1)  
        curve.extend([value] * step_size)  

    # Adjust for any remaining samples due to integer division  
    remaining = length - len(curve)  
    if remaining > 0:  
        curve.extend([np.random.uniform(0, 1)] * remaining)  
    return curve 

def get_real_data(equipId, num_sample):
    x_state = []
    try:
            response = requests.post(os.environ["API_URL"]  + '/getsmpbyId', data={'equipId':equipId, 'num_sample':num_sample}, verify=False)   
            samples = response.json()                 
            x_state = np.array([pd.to_numeric(samples['ambient']), pd.to_numeric(samples['bottomoil']),  pd.to_numeric(samples['topoil']), 
                          max(pd.to_numeric(samples['hotspotx']), pd.to_numeric(samples['hotspoty']), pd.to_numeric(samples['hotspotz'])), 
                          max(pd.to_numeric(samples['puloadx']), pd.to_numeric(samples['puloady']),  pd.to_numeric(samples['puloadz']))])
            return x_state

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

def get_cooling_config(equipId):

    try:
        response = requests.post(os.environ["API_URL"] + '/getcoolingconfig', data={'equipId':equipId})                         

        # NUM_FANS            = response["num_fans"]         
        # NUM_PUMPS           = response["num_pumps"]          
        # FAN_POWERS          = response["fan_powers"] 
        # PUMP_POWERS         = response["pump_powers"] 
        # FAN_EFFICIENCY      = response["fan_efficiency"]
        # PUMP_EFFICIENCY     = response["pump_efficiency"]
        # FAN_SPEED           = response["fan_speed"]
        # PUMP_SPEED          = response["pump_speed"]
        # FAN_TYPE            = response["fan_type"]
        # PUMP_TYPE           = response["pump_type"]
        # FAN_MODE            = response["fan_mode"]
        # PUMP_MODE           = response["pump_mode"]

        return response.json()
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

# Generate a random sinusoidal series of 25 floats between 18�C and 29�C  
def generate_sinusoidal_series(min_val, max_val, start_val, end_val):  
  x = np.linspace(start_val, end_val, 25)  # Generate 25 points between start_val and end_val  
  sinusoidal = np.sin(x)  # Generate sinusoidal values  
  scaled = (sinusoidal - np.min(sinusoidal)) / (np.max(sinusoidal) - np.min(sinusoidal))  # Normalize to [0, 1]  
  scaled = scaled * (max_val - min_val) + min_val  # Scale to [min_val, max_val]  
  return scaled


    # -------------------------------------------------#
    # TABLE 218: REFERENCE FINANCIAL COST OF FAILURE   #
    # -------------------------------------------------#
    
def get_oil_condition_vars(eqpmt, moisture, acidity, bd_strength):
        """Return oil condition scores for moisture, acidity, and breakdown strength."""
        try:
            with Session(p_engine) as session:
                def fetch_score(modtype, value):
                    row = session.execute(
                        select(modifiers.c.score)
                        .where(modifiers.c.eqpmt == eqpmt)
                        .where(modifiers.c.modtype == modtype)
                        .where(modifiers.c.low < value)
                        .where(modifiers.c.high >= value)
                    ).first()
                    return float(row[0]) if row else None

                return {
                    "moisture_score": fetch_score(Modes.MOISTURE.name, moisture),
                    "acidity_score": fetch_score(Modes.ACIDITY.name, acidity),
                    "bd_strength_score": fetch_score(Modes.BD_STRENGTH.name, bd_strength),
                }
        except Exception as exc:
            logger.error("Error in get_oil_condition_vars: %s", exc)
            return None

def get_oil_condition_caps(eqpmt, condvalue):
        """Return oil condition factor and collar scores for a measured value."""
        try:
            with Session(p_engine) as session:
                def fetch_score(modtype):
                    row = session.execute(
                        select(modifiers.c.score)
                        .where(modifiers.c.eqpmt == eqpmt)
                        .where(modifiers.c.modtype == modtype)
                        .where(modifiers.c.low < condvalue)
                        .where(modifiers.c.high >= condvalue)
                    ).first()
                    return float(row[0]) if row else None

                return {
                    "oil_factor": fetch_score(Modes.OIL_CONDITION_SCORE.name),
                    "oil_collar": fetch_score(Modes.OIL_TEST_COLLAR.name),
                }
        except Exception as exc:
            logger.error("Error in get_oil_condition_caps: %s", exc)
            return None
    
def get_dga_attributes(eqpmt):
        """Return default DGA attribute scores (placeholder until sourced from data)."""
        return {
            "dga_test_score": 0.2,
            "dga_test_score_pre": 0.4,
        }
       
def get_dga_scores(
        eqpmt,
        hydrogen,
        methane,
        ethylene,
        acetylene,
        ethane,
        hydrogen_pre,
        methane_pre,
        ethylene_pre,
        acetylene_pre,
        ethane_pre,
    ):
        """Return DGA scores and pre-scores for the provided gas measurements."""

        def _score_for(modtype, value):
            try:
                with Session(p_engine) as session:
                    row = session.execute(
                        select(modifiers)
                        .where(modifiers.c.eqpmt == eqpmt)
                        .where(modifiers.c.modtype == modtype)
                        .where(modifiers.c.low < value)
                        .where(modifiers.c.high >= value)
                    ).mappings().first()
                    return float(row["score"]) if row and "score" in row else None
            except Exception as exc:
                logger.error("Error fetching DGA score for %s: %s", modtype, exc)
                return None

        return {
            "hydrogen_score": _score_for(Modes.HYDROGEN_CONDITION.name, hydrogen),
            "methane_score": _score_for(Modes.METHANE_CONDITION.name, methane),
            "acetylene_score": _score_for(Modes.ACETYLENE_CONDITION.name, acetylene),
            "ethylene_score": _score_for(Modes.ETHYLENE_CONDITION.name, ethylene),
            "ethane_score": _score_for(Modes.ETHANE_CONDITION.name, ethane),
            "hydrogen_pre_score": _score_for(Modes.HYDROGEN_CONDITION.name, hydrogen_pre),
            "methane_pre_score": _score_for(Modes.METHANE_CONDITION.name, methane_pre),
            "acetylene_pre_score": _score_for(Modes.ACETYLENE_CONDITION.name, acetylene_pre),
            "ethylene_pre_score": _score_for(Modes.ETHYLENE_CONDITION.name, ethylene_pre),
            "ethane_pre_score": _score_for(Modes.ETHANE_CONDITION.name, ethane_pre),
        }

def get_condition_score(eqpmt, modtype, condvalue):
        """Return condition score rows for a given equipment, modifier type, and value."""
        try:
            with Session(p_engine) as session:
                result = session.execute(
                    select(modifiers)
                    .where(modifiers.c.eqpmt == eqpmt)
                    .where(modifiers.c.modtype == modtype)
                    .where(modifiers.c.low < condvalue)
                    .where(modifiers.c.high >= condvalue)
                ).mappings()
                return list(result)
        except Exception as exc:
            logger.error("Error in get_condition_score: %s", exc)
            return []

def get_mmi_factors(eqpmt, modtype):
        """Return MMI factors filtered by equipment and mode."""
        try:
            with Session(p_engine) as session:
                result = session.execute(
                    select(mmifactors)
                    .where(mmifactors.c.eqpmt == eqpmt)
                    .where(mmifactors.c.modtype == modtype)
                ).mappings()
                return list(result)
        except Exception as exc:
            logger.error("Error in get_mmi_factors: %s", exc)
            return []

def get_meas_ci_factors(eqpmt, criteria, condtype):
        """Return measured condition input factors for the given criteria and condition type."""
        try:
            with Session(p_engine) as session:
                result = session.execute(
                    select(mconditions)
                    .where(mconditions.c.eqpmt == eqpmt)
                    .where(mconditions.c.criteria == criteria)
                    .where(mconditions.c.condtype == condtype)
                ).mappings()
                return list(result)
        except Exception as exc:
            logger.error("Error in get_meas_ci_factors: %s", exc)
            return []

def get_obs_ci_factors(eqpmt, criteria, condtype):
        """Return observed condition input factors for the given criteria and condition type."""
        try:
            with Session(p_engine) as session:
                result = session.execute(
                    select(conditions)
                    .where(conditions.c.eqpmt == eqpmt)
                    .where(conditions.c.criteria == criteria)
                    .where(conditions.c.condtype == condtype)
                ).mappings()
                return list(result)
        except Exception as exc:
            logger.error("Error in get_obs_ci_factors: %s", exc)
            return []