from django.db import models

# Create your models here.
class datadictionaries(models.Model):
    varname     = models.TextField(blank=False, default='')
    value       = models.TextField(blank=True, default='')
    unit        = models.TextField(blank=True, default='')
    defaultv    = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    information = models.TextField(blank=True, default='')
    groupname   = models.TextField(blank=True, default='')
    class Meta:
        db_table = "datadictionaries"

# --------------------------------------------------------#
#  APPENDIX B CALIBRATION – PROBABILITY OF FAILURE        #
# --------------------------------------------------------#
class degradations(models.Model):
    varname    = models.TextField(blank=False, default='')  # - Asset Register Category
    alphamin   = models.FloatField(blank=False, default='')  # - Subsystems Component
    alphamax  = models.FloatField(blank=False, default='')  # - Observation type - Measured or Observed conditions 
    betamin  = models.FloatField(blank=False, default='')  # - Subsystems Component
    betamax     = models.FloatField(blank=False, default='')  # - Description
    sigmamin  = models.FloatField(blank=False, default='')  # - Condition input factor
    sigmamax  = models.FloatField(blank=False, default='')  # - Condition input collar 
    scoremin     = models.FloatField(blank=False, default='')  # - Condition input cap
    scoremax     = models.FloatField(blank=False, default='')  # - Condition input cap
    class Meta:
        db_table = "degradations"



class conditions(models.Model):
    eqpmt    = models.TextField(blank=False, default='')  # - Asset Register Category
    subcomp   = models.TextField(blank=False, default='')  # - Subsystems Component
    condtype  = models.TextField(blank=False, default='')  # - Observation type - Measured or Observed conditions 
    criteria  = models.TextField(blank=False, default='')  # - Subsystems Component
    descp     = models.TextField(blank=False, default='')  # - Description
    infactor  = models.TextField(blank=False, default='')  # - Condition input factor
    incollar  = models.TextField(blank=False, default='')  # - Condition input collar 
    incap     = models.TextField(blank=False, default='')  # - Condition input cap
    class Meta:
        db_table = "conditions"


class mconditions(models.Model):
    eqpmt    = models.TextField(blank=False, default='')  # - Asset Register Category
    subcomp   = models.TextField(blank=False, default='')  # - Subsystems Component
    condtype  = models.TextField(blank=False, default='')  # - Observation type - Measured or Observed conditions 
    criteria  = models.TextField(blank=False, default='')  # - Subsystems Component
    descp     = models.TextField(blank=False, default='')  # - Description
    infactor  = models.TextField(blank=False, default='')  # - Condition input factor
    incap     = models.TextField(blank=False, default='')  # - Condition input cap
    incollar  = models.TextField(blank=False, default='')  # - Condition input collar 
    class Meta:
        db_table = "mconditions"


class modifiers(models.Model):
    eqpmt    = models.TextField(blank=False, default='')  # - Asset Register Category
    low      = models.TextField(blank=False, default='')  # - Minimum
    high     = models.TextField(blank=False, default='')  # - Maximum
    score    = models.TextField(blank=False, default='')  # - Scor or Factor
    modtype  = models.TextField(blank=False, default='')  # - Type of modifiers
    class Meta:
        db_table = "modifiers"


class mmifactors(models.Model):
    eqpmt       = models.TextField(blank=False, default='') # Asset Register Category
    subcomp     = models.TextField(blank=False, default='') # Subsystems Component
    df1         = models.TextField(blank=False, default='') # Factor Divider 1
    df2         = models.TextField(blank=False, default='') # Factor Divider 2
    maxnofc     = models.TextField(blank=False, default='') # Max. No. of Combined Factors
    modtype     = models.TextField(blank=False, default='') # Max. No. of Combined Factors
    class Meta:
        db_table = "mmifactors"

#---------------------------#
# Asset YRATINGS TABLES     #
#---------------------------#
class obsconditions(models.Model):
    sampdate    = models.DateTimeField(auto_now=True)
    h2ppm       = models.TextField(blank=False, default='')
    ch4ppm      = models.TextField(blank=False, default='')
    c2h6ppm     = models.TextField(blank=False, default='')
    c2h4ppm     = models.TextField(blank=False, default='')
    c2h2ppm     = models.TextField(blank=False, default='')
    coppm       = models.TextField(blank=False, default='')
    co2ppm      = models.TextField(blank=False, default='')
    c3h6ppm     = models.TextField(blank=False, default='')
    c3h8ppm     = models.TextField(blank=False, default='')
    n2ppm       = models.TextField(blank=False, default='')
    o2ppm       = models.TextField(blank=False, default='')
    tdcgppm     = models.TextField(blank=False, default='')
    tdgppm      = models.TextField(blank=False, default='')
    tcgppm      = models.TextField(blank=False, default='')
    oilTemp     = models.TextField(blank=False, default='')
    moisture    = models.TextField(blank=False, default='')
    genrate     = models.TextField(blank=False, default='')
    labnum      = models.TextField(blank=False, default='')
    interft     = models.TextField(blank=False, default='')
    acidnum     = models.TextField(blank=False, default='')
    colornum    = models.TextField(blank=False, default='')
    visual      = models.TextField(blank=False, default='')
    sediment    = models.TextField(blank=False, default='')
    diebrkdwn   = models.TextField(blank=False, default='')
    pwrfact25   = models.TextField(blank=False, default='')
    pwrFact90   = models.TextField(blank=False, default='')
    pwrFact100  = models.TextField(blank=False, default='')
    oxidation   = models.TextField(blank=False, default='')
    density     = models.TextField(blank=False, default='')
    furans      = models.TextField(blank=False, default='')
    keygas      = models.TextField(blank=False, default='')
    sampid      = models.TextField(blank=False, default='')
    ordernum    = models.TextField(blank=False, default='')
    inspection  = models.TextField(blank=False, default='')
    diagnosis   = models.TextField(blank=False, default='')
    sampstate   = models.TextField(blank=False, default='')
    samptype    = models.TextField(blank=False, default='')
    class Meta:
        db_table = "obsconditions"

class measconditions(models.Model): 
    sampdate        = models.DateTimeField(auto_now=True)
    ambient         = models.TextField(blank=True, default='')
    topoil          = models.TextField(blank=True, default='')
    hotspotx        = models.TextField(blank=True, default='')
    hotspoty        = models.TextField(blank=True, default='')
    hotspotz        = models.TextField(blank=True, default='')
    puloadx         = models.TextField(blank=True, default='')
    puloady         = models.TextField(blank=True, default='')
    puloadz         = models.TextField(blank=True, default='')
    oiltemp         = models.TextField(blank=True, default='')
    moisture        = models.TextField(blank=True, default='')
    puloadc1        = models.TextField(blank=True, default='')
    puloadc2        = models.TextField(blank=True, default='')
    fanspeedc1      = models.TextField(blank=True, default='')
    fanspeedc2      = models.TextField(blank=True, default='')
    oilflow         = models.TextField(blank=True, default='')
    oilpressure     = models.TextField(blank=True, default='')
    fannoise        = models.TextField(blank=True, default='')
    airflow         = models.TextField(blank=True, default='')
    pumpload        = models.TextField(blank=True, default='')
    h2ppm           = models.TextField(blank=True, default='')
    ch4ppm          = models.TextField(blank=True, default='')
    c2h6ppm         = models.TextField(blank=True, default='')
    c2h4ppm         = models.TextField(blank=True, default='')
    c2h2ppm         = models.TextField(blank=True, default='')
    coppm           = models.TextField(blank=True, default='')
    co2ppm          = models.TextField(blank=True, default='')
    c3h6ppm         = models.TextField(blank=True, default='')
    c3h8ppm         = models.TextField(blank=True, default='')
    n2ppm           = models.TextField(blank=True, default='')
    o2ppm           = models.TextField(blank=True, default='')
    tdcgppm         = models.TextField(blank=True, default='')
    tdgppm          = models.TextField(blank=True, default='')
    tcgppm          = models.TextField(blank=True, default='')
    # Rate of change (ROC)
    ambientroc      = models.TextField(blank=True, default='')
    topoilroc       = models.TextField(blank=True, default='')
    hotspotxroc     = models.TextField(blank=True, default='')
    hotspotyroc     = models.TextField(blank=True, default='')
    hotspotzroc     = models.TextField(blank=True, default='')
    puloadxroc      = models.TextField(blank=True, default='')
    puloadyroc      = models.TextField(blank=True, default='')
    puloadzroc      = models.TextField(blank=True, default='')
    oiltemproc      = models.TextField(blank=True, default='')
    moistureroc     = models.TextField(blank=True, default='')
    puloadc1roc     = models.TextField(blank=True, default='')
    puloadc2roc     = models.TextField(blank=True, default='')
    fanspeedc1roc   = models.TextField(blank=True, default='')
    fanspeedc2roc   = models.TextField(blank=True, default='')
    oilflowroc      = models.TextField(blank=True, default='')
    oilpressureroc  = models.TextField(blank=True, default='')
    fannoiseroc     = models.TextField(blank=True, default='')
    airflowroc      = models.TextField(blank=True, default='')
    pumploadroc     = models.TextField(blank=True, default='')
    h2ppmroc        = models.TextField(blank=True, default='')
    ch4ppmroc       = models.TextField(blank=True, default='')
    c2h6ppmroc      = models.TextField(blank=True, default='')
    c2h4ppmroc      = models.TextField(blank=True, default='')
    c2h2ppmroc      = models.TextField(blank=True, default='')
    coppmroc        = models.TextField(blank=True, default='')
    co2ppmroc       = models.TextField(blank=True, default='')
    c3h6ppmroc      = models.TextField(blank=True, default='')
    c3h8ppmroc      = models.TextField(blank=True, default='')
    n2ppmroc        = models.TextField(blank=True, default='')
    o2ppmroc        = models.TextField(blank=True, default='')
    tdcgppmroc      = models.TextField(blank=True, default='')
    tdgppmroc       = models.TextField(blank=True, default='')
    tcgppmroc       = models.TextField(blank=True, default='')
    class Meta:
        db_table = "measconditions"

class eventitems(models.Model): 
    eventdate       = models.DateTimeField(auto_now=True)
    payload         = models.TextField(blank=True, default='')
    severscale      = models.TextField(blank=True, default='')
    status          = models.TextField(blank=True, default='')
    class Meta:
        db_table = "eventitems"

class alarmitems(models.Model): 
    isactive        = models.TextField(blank=True, default='')
    category        = models.TextField(blank=True, default='')
    aseverity       = models.TextField(blank=True, default='')
    score           = models.TextField(blank=True, default='')
    alarmname       = models.TextField(blank=True, default='')
    lastseen        = models.TextField(blank=True, default='')
    firstseen       = models.TextField(blank=True, default='')
    seenCount       = models.TextField(blank=True, default='')
    source          = models.TextField(blank=True, default='')
    information     = models.TextField(blank=True, default='')
    status          = models.TextField(blank=True, default='')
    class Meta:
        db_table = "alarmitems"

class alarmentries(models.Model): 
    alarmname       = models.TextField(blank=True, default='')
    ttf             = models.TextField(blank=True, default='')
    normal          = models.TextField(blank=True, default='')
    caution         = models.TextField(blank=True, default='')
    alert           = models.TextField(blank=True, default='')
    alarm           = models.TextField(blank=True, default='')
    emergency       = models.TextField(blank=True, default='')
    class Meta:
        db_table = "alarmentries"

class actionentries(models.Model): 
    assettype       = models.TextField(blank=True, default='')
    component       = models.TextField(blank=True, default='')
    alarmtype       = models.TextField(blank=True, default='')
    description     = models.TextField(blank=True, default='')
    class Meta:
        db_table = "actionentries"

class alarmconfigs(models.Model): 
    isactive        = models.TextField(blank=True, default='')
    alarmname       = models.TextField(blank=True, default='')
    threshtype      = models.TextField(blank=True, default='')
    collectortype   = models.TextField(blank=True, default='')
    targettype      = models.TextField(blank=True, default='')
    statistictype   = models.TextField(blank=True, default='')
    class Meta:
        db_table = "alarmconfigs"

    
class vardictionaries(models.Model): 
    varname         = models.TextField(blank=True, default='')
    minvalue        = models.TextField(blank=True, default='')
    maxvalue        = models.TextField(blank=True, default='') 
    description     = models.TextField(blank=True, default='')
    vargroup        = models.TextField(blank=True, default='')
    varsubgroup     = models.TextField(blank=True, default='')
    unit            = models.TextField(blank=True, default='')
    eqpmt           = models.TextField(blank=True, default='')
    class Meta:
        db_table = "vardictionaries"

class loadprofiles(models.Model):
    IsSelected      = models.BooleanField(null=False)
    profileName     = models.TextField(null=True, blank=True)
    time            = models.TextField(null=True, blank=True)
    sumamb          = models.FloatField(null=False)
    sumpul          = models.FloatField(null=False)
    sumcool         = models.FloatField(null=False)
    class Meta:
        db_table = "loadprofiles"

class loadingcases(models.Model):
    LoadType        = models.TextField(null=True, blank=True)
    LtcPosition     = models.IntegerField(null=False)
    HotSpotLimit    = models.FloatField(null=False)
    TopOilLimit     = models.FloatField(null=False)
    LoLLimit        = models.FloatField(null=False)
    PULLimit        = models.FloatField(null=False)
    BubblingLimit   = models.FloatField(null=False)
    CoolPWLimit     = models.FloatField(null=False)
    BeginOverTime   = models.FloatField(null=False)
    EndOverTime     = models.FloatField(null=False)
    InsLifeExp      = models.FloatField(null=False)
    OxyContent      = models.FloatField(null=False)
    MoisContent     = models.FloatField(null=False)
    GasContent      = models.FloatField(null=False)
    HSPressure      = models.FloatField(null=False)
    LtcAmpacity     = models.FloatField(null=False)
    OptimError      = models.FloatField(null=False)
    Scheduled       = models.BooleanField(null=False)
    LPlan           = models.TextField(blank=True, default='STE')
    class Meta:
        db_table = "loadingcases"

class coolings(models.Model):
    Status              = models.TextField(blank=False, default='')
    XfrmerCooling       = models.TextField(blank=False, default='')
    numCooler           = models.IntegerField(null=False)
    numFan              = models.IntegerField(null=False)
    numRadiator         = models.IntegerField(null=False)
    numPumps            = models.IntegerField(null=False)
    PerUnitBasekVA      = models.FloatField(null=False)
    WindingTempBase     = models.FloatField(null=False)
    AvgWindingRise      = models.FloatField(null=False)
    HotSpotRise         = models.FloatField(null=False)
    TopOilRise          = models.FloatField(null=False)
    BottomOilRise       = models.FloatField(null=False)
    AvgOilRise          = models.FloatField(null=False)
    LossBasekVA         = models.FloatField(null=False)
    LossTempBase        = models.FloatField(null=False)
    WindI2RLosses       = models.FloatField(null=False)
    WindEddyLoss        = models.FloatField(null=False)
    WindStrayLosses     = models.FloatField(null=False)
    XfrmerCoolLevel     = models.FloatField(null=False)
    XfrmerRating        = models.FloatField(null=False)
    LoadLoss            = models.FloatField(null=False)
    HRatedAmps          = models.FloatField(null=False)
    XRatedAmps          = models.FloatField(null=False)
    TRatedAmps          = models.FloatField(null=False)
    Power               = models.FloatField(null=False)

    class Meta:
        db_table = "coolings"


class loadresults(models.Model):
    cycle       = models.IntegerField(null=True, blank=True)
    loadtype    = models.TextField(blank=True, default='')
    sampdate    = models.DateTimeField(null=True, blank=True)
    uptopoil    = models.TextField(blank=True, default='')  
    uphotspot   = models.TextField(blank=True, default='')
    upload      = models.TextField(blank=True, default='')
    upbottom    = models.TextField(blank=True, default='')
    uplife      = models.TextField(blank=True, default='')
    ttptop      = models.TextField(blank=True, default='')
    ttphot      = models.TextField(blank=True, default='')
    ttpmva      = models.TextField(blank=True, default='')
    margin      = models.TextField(blank=True, default='')    
    class Meta:
        db_table = "loadresults"


class loadcurves(models.Model):
    Id         = models.AutoField(primary_key=True)
    cycle      = models.IntegerField(null=True, blank=True)
    loadtype   = models.CharField(max_length=255, null=True, blank=True)
    sampdate   = models.DateTimeField(null=True, blank=True)
    otime      = models.CharField(max_length=255, null=True, blank=True)
    opamb      = models.CharField(max_length=255, null=True, blank=True)
    obload     = models.CharField(max_length=255, null=True, blank=True)
    optopoil   = models.CharField(max_length=255, null=True, blank=True)
    ophotspot  = models.CharField(max_length=255, null=True, blank=True)
    opload     = models.CharField(max_length=255, null=True, blank=True)
    opbottom   = models.CharField(max_length=255, null=True, blank=True)
    oplife     = models.CharField(max_length=255, null=True, blank=True)
    margin     = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "loadcurves"



class loaddistros(models.Model):
    Id               = models.AutoField(primary_key=True)
    opyear           = models.CharField(max_length=50, null=True, blank=True)
    load_type        = models.CharField(max_length=100, null=True, blank=True)

    upload           = models.CharField(max_length=100, null=True, blank=True)
    upload_min       = models.CharField(max_length=100, null=True, blank=True)
    upload_max       = models.CharField(max_length=100, null=True, blank=True)
    upload_std       = models.CharField(max_length=100, null=True, blank=True)

    margin           = models.CharField(max_length=100, null=True, blank=True)
    margin_min       = models.CharField(max_length=100, null=True, blank=True)
    margin_max       = models.CharField(max_length=100, null=True, blank=True)
    margin_std       = models.CharField(max_length=100, null=True, blank=True)

    upbottom         = models.CharField(max_length=100, null=True, blank=True)
    upbottom_min     = models.CharField(max_length=100, null=True, blank=True)
    upbottom_max     = models.CharField(max_length=100, null=True, blank=True)
    upbottom_std     = models.CharField(max_length=100, null=True, blank=True)

    uptopoil         = models.CharField(max_length=100, null=True, blank=True)
    uptopoil_min     = models.CharField(max_length=100, null=True, blank=True)
    uptopoil_max     = models.CharField(max_length=100, null=True, blank=True)
    uptopoil_std     = models.CharField(max_length=100, null=True, blank=True)

    uphotspot        = models.CharField(max_length=100, null=True, blank=True)
    uphotspot_min    = models.CharField(max_length=100, null=True, blank=True)
    uphotspot_max    = models.CharField(max_length=100, null=True, blank=True)
    uphotspot_std    = models.CharField(max_length=100, null=True, blank=True)

    uplife           = models.CharField(max_length=100, null=True, blank=True)
    uplife_min       = models.CharField(max_length=100, null=True, blank=True)
    uplife_max       = models.CharField(max_length=100, null=True, blank=True)
    uplife_std       = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = "loaddistros"

class setpoints(models.Model):
    Id                = models.AutoField(primary_key=True)
    sw_type           = models.CharField(max_length=100, null=True, blank=True)
    upper_curve       = models.CharField(max_length=100, null=True, blank=True)
    lower_curve       = models.CharField(max_length=100, null=True, blank=True)
    period            = models.CharField(max_length=100, null=True, blank=True)
    coolpwr           = models.CharField(max_length=100, null=True, blank=True)
    status            = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = "setpoints"


class loadcbdistros(models.Model):
    Id               = models.AutoField(primary_key=True)
    opyear           = models.CharField(max_length=50, null=True, blank=True)
    load_type        = models.CharField(max_length=100, null=True, blank=True)
    score            = models.CharField(max_length=255, null=True, blank=True)
    score_min        = models.CharField(max_length=255, null=True, blank=True)
    score_max        = models.CharField(max_length=255, null=True, blank=True)
    score_std        = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "loadcbdistros"



class thermaldistros(models.Model):
    Id               = models.AutoField(primary_key=True)
    opyear           = models.CharField(max_length=50, null=True, blank=True)
    load_type        = models.CharField(max_length=100, null=True, blank=True)
    th_time          = models.CharField(max_length=255, null=True, blank=True)
    opamb            = models.CharField(max_length=255, null=True, blank=True)
    obload           = models.CharField(max_length=255, null=True, blank=True)
    margin           = models.CharField(max_length=255, null=True, blank=True)
    margin_min       = models.CharField(max_length=255, null=True, blank=True)
    margin_max       = models.CharField(max_length=255, null=True, blank=True)
    margin_std       = models.CharField(max_length=255, null=True, blank=True)
    optopoil         = models.CharField(max_length=255, null=True, blank=True)
    optopoil_min     = models.CharField(max_length=255, null=True, blank=True)
    optopoil_max     = models.CharField(max_length=255, null=True, blank=True)
    optopoil_std     = models.CharField(max_length=255, null=True, blank=True)
    opbottom         = models.CharField(max_length=255, null=True, blank=True)
    opbottom_min     = models.CharField(max_length=255, null=True, blank=True)
    opbottom_max     = models.CharField(max_length=255, null=True, blank=True)
    opbottom_std     = models.CharField(max_length=255, null=True, blank=True)
    ophotspot        = models.CharField(max_length=255, null=True, blank=True)
    ophotspot_min    = models.CharField(max_length=255, null=True, blank=True)
    ophotspot_max    = models.CharField(max_length=255, null=True, blank=True)
    ophotspot_std    = models.CharField(max_length=255, null=True, blank=True)
    opload           = models.CharField(max_length=255, null=True, blank=True)
    opload_min       = models.CharField(max_length=255, null=True, blank=True)
    opload_max       = models.CharField(max_length=255, null=True, blank=True)
    opload_std       = models.CharField(max_length=255, null=True, blank=True)
    oplife           = models.CharField(max_length=255, null=True, blank=True)
    oplife_min       = models.CharField(max_length=255, null=True, blank=True)
    oplife_max       = models.CharField(max_length=255, null=True, blank=True)
    oplife_std       = models.CharField(max_length=255, null=True, blank=True)
    class Meta:
        db_table = "thermaldistros"

        
