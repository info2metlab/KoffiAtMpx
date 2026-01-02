# Elena Damaan
# Chris Essonne
# Steven Greer

use yratings;
# make sure you have UTF-8 collaction for best .NET interoperability
# CREATE DATABASE quartznet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

DROP TABLE IF EXISTS Equipments;
DROP TABLE IF EXISTS Eqdictionaries;
DROP TABLE IF EXISTS Conditions;
DROP TABLE IF EXISTS Mconditions;
DROP TABLE IF EXISTS Modifiers;
DROP TABLE IF EXISTS MmiFactors;
DROP TABLE IF EXISTS VarDictionaries;
DROP TABLE IF EXISTS ObsConditions;
DROP TABLE IF EXISTS MeasConditions;
DROP TABLE IF EXISTS EventItems;


/*
 # --------------------------------------------------------#
 # EQUIPMENT DATA DICTIONARY                               #
 # --------------------------------------------------------# */

CREATE TABLE `Equipments` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) NULL,
        `Xfrmsite` VARCHAR(255) NULL,
        `Rating` VARCHAR(255) NULL,
        `Primsecv` VARCHAR(255) NULL,
        `Oilvolume` VARCHAR(255) NULL,
        `Maintnotes` TEXT NULL,
        `Loadpu` VARCHAR(255) NULL,
        `Instanote` TEXT NULL,
        `Inservice` VARCHAR(50) NULL,
        `Fluidtype` VARCHAR(100) NULL,
        `Solidtype` VARCHAR(100) NULL,
        `Factory` VARCHAR(255) NULL,
        `Eam` VARCHAR(255) NULL,
        `Lastdgacnd` VARCHAR(255) NULL,
        `Eqpmt` INT NULL,                -- maps to AssetCat enum (store as int)
        `Breath` VARCHAR(100) NULL,
        `Age` VARCHAR(50) NULL,
        `Vclass` VARCHAR(100) NULL,
        `Gpslatid` VARCHAR(100) NULL,
        `Gpslongid` VARCHAR(100) NULL,
        `Gpsaltid` VARCHAR(100) NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_Equipments_Eqsernum` (`Eqsernum`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `Eqdictionaries` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) NULL,
        `Varname` VARCHAR(255) NULL,
        `Value` TEXT NULL,
        `Unit` VARCHAR(100) NULL,
        `Defaultv` VARCHAR(255) NULL,
        `Description` TEXT NULL,
        `Information` TEXT NULL,
        `Groupname` VARCHAR(255) NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_Eqdictionaries_Eqsernum` (`Eqsernum`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
 

    /*
    # --------------------------------------------------------#
    # APPENDIX B CALIBRATION – PROBABILITY OF FAILURE         #
    # --------------------------------------------------------#
    */
    CREATE TABLE `Conditions` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqpmt` INT NULL,
        `Subcomp` INT NULL,
        `Condtype` INT NULL,
        `Criteria` INT NULL,
        `Descp` TEXT NULL,
        `Infactor` DOUBLE NULL,
        `Incollar` DOUBLE NULL,
        `Incap` DOUBLE NULL,
        PRIMARY KEY (`Id`),
        INDEX `IX_Conditions_Eqpmt` (`Eqpmt`),
        INDEX `IX_Conditions_Subcomp` (`Subcomp`),
        INDEX `IX_Conditions_Condtype` (`Condtype`),
        INDEX `IX_Conditions_Criteria` (`Criteria`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `Mconditions` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqpmt` INT NULL,
        `Subcomp` INT NULL,
        `Condtype` INT NULL,
        `Criteria` INT NULL,
        `Descp` TEXT NULL,
        `Infactor` DOUBLE NULL,
        `Incap` DOUBLE NULL,
        `Incollar` DOUBLE NULL,
        PRIMARY KEY (`Id`),
        INDEX `IX_Mconditions_Eqpmt` (`Eqpmt`),
        INDEX `IX_Mconditions_Subcomp` (`Subcomp`),
        INDEX `IX_Mconditions_Condtype` (`Condtype`),
        INDEX `IX_Mconditions_Criteria` (`Criteria`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE `Modifiers` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqpmt` INT NULL,
        `Low` DOUBLE NULL,
        `High` DOUBLE NULL,
        `Score` DOUBLE NULL,
        `Modtype` INT NULL,
        PRIMARY KEY (`Id`),
        INDEX `IX_Modifiers_Eqpmt` (`Eqpmt`),
        INDEX `IX_Modifiers_Modtype` (`Modtype`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE `MmiFactors` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqpmt` INT NULL,
        `Subcomp` INT NULL,
        `Df1` DOUBLE NULL,
        `Df2` DOUBLE NULL,
        `Maxnofc` INT NULL,
        `Modtype` INT NULL,
        PRIMARY KEY (`Id`),
        INDEX `IX_MmiFactors_Eqpmt` (`Eqpmt`),
        INDEX `IX_MmiFactors_Subcomp` (`Subcomp`),
        INDEX `IX_MmiFactors_Modtype` (`Modtype`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

   
    CREATE TABLE `VarDictionaries` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `VarName` VARCHAR(255) NOT NULL,
        `MinValue` VARCHAR(255) DEFAULT NULL,
        `MaxValue` VARCHAR(255) DEFAULT NULL,
        `Description` TEXT,
        `VarGroup` VARCHAR(255) DEFAULT NULL,
        `VarSubGroup` VARCHAR(255) DEFAULT NULL,
        `Unit` VARCHAR(100) DEFAULT NULL,
        `Eqpmt` INT DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_VarDictionaries_VarName` (`VarName`),
        KEY `IX_VarDictionaries_Eqpmt` (`Eqpmt`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `ObsConditions` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) DEFAULT NULL,
        `Sampdate` DATETIME(6) DEFAULT NULL,
        `h2ppm` DOUBLE DEFAULT NULL,
        `ch4ppm` DOUBLE DEFAULT NULL,
        `c2h6ppm` DOUBLE DEFAULT NULL,
        `c2h4ppm` DOUBLE DEFAULT NULL,
        `c2h2ppm` DOUBLE DEFAULT NULL,
        `coppm` DOUBLE DEFAULT NULL,
        `co2ppm` DOUBLE DEFAULT NULL,
        `c3h6ppm` DOUBLE DEFAULT NULL,
        `c3h8ppm` DOUBLE DEFAULT NULL,
        `n2ppm` DOUBLE DEFAULT NULL,
        `o2ppm` DOUBLE DEFAULT NULL,
        `tdcgppm` DOUBLE DEFAULT NULL,
        `tdgppm` DOUBLE DEFAULT NULL,
        `tcgppm` DOUBLE DEFAULT NULL,
        `oilTemp` DOUBLE DEFAULT NULL,
        `moisture` DOUBLE DEFAULT NULL,
        `genrate` DOUBLE DEFAULT NULL,
        `labnum` VARCHAR(255) DEFAULT NULL,
        `interft` DOUBLE DEFAULT NULL,
        `acidnum` DOUBLE DEFAULT NULL,
        `colornum` INT DEFAULT NULL,
        `visual` VARCHAR(255) DEFAULT NULL,
        `sediment` VARCHAR(255) DEFAULT NULL,
        `diebrkdwn` VARCHAR(255) DEFAULT NULL,
        `pwrfact25` VARCHAR(255) DEFAULT NULL,
        `pwrFact90` VARCHAR(255) DEFAULT NULL,
        `pwrFact100` VARCHAR(255) DEFAULT NULL,
        `oxidation` VARCHAR(255) DEFAULT NULL,
        `density` VARCHAR(255) DEFAULT NULL,
        `furans` VARCHAR(255) DEFAULT NULL,
        `keygas` VARCHAR(255) DEFAULT NULL,
        `sampid` VARCHAR(255) DEFAULT NULL,
        `ordernum` VARCHAR(255) DEFAULT NULL,
        `inspection` VARCHAR(255) DEFAULT NULL,
        `diagnosis` VARCHAR(255) DEFAULT NULL,
        `sampstate` VARCHAR(255) DEFAULT NULL,
        `samptype` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_ObsConditions_Eqsernum` (`Eqsernum`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    

    CREATE TABLE `MeasConditions` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `eqsernum` VARCHAR(255) DEFAULT NULL,
        `sampdate` DATETIME(6) DEFAULT NULL,
        `ambient` VARCHAR(255) DEFAULT NULL,
        `topoil` VARCHAR(255) DEFAULT NULL,
        `hotspotx` VARCHAR(255) DEFAULT NULL,
        `hotspoty` VARCHAR(255) DEFAULT NULL,
        `hotspotz` VARCHAR(255) DEFAULT NULL,
        `puloadx` VARCHAR(255) DEFAULT NULL,
        `puloady` VARCHAR(255) DEFAULT NULL,
        `puloadz` VARCHAR(255) DEFAULT NULL,
        `oiltemp` VARCHAR(255) DEFAULT NULL,
        `moisture` VARCHAR(255) DEFAULT NULL,
        `puloadc1` VARCHAR(255) DEFAULT NULL,
        `puloadc2` VARCHAR(255) DEFAULT NULL,
        `fanspeedc1` VARCHAR(255) DEFAULT NULL,
        `fanspeedc2` VARCHAR(255) DEFAULT NULL,
        `oilflow` VARCHAR(255) DEFAULT NULL,
        `oilpressure` VARCHAR(255) DEFAULT NULL,
        `fannoise` VARCHAR(255) DEFAULT NULL,
        `airflow` VARCHAR(255) DEFAULT NULL,
        `pumpload` VARCHAR(255) DEFAULT NULL,
        `h2ppm` VARCHAR(255) DEFAULT NULL,
        `ch4ppm` VARCHAR(255) DEFAULT NULL,
        `c2h6ppm` VARCHAR(255) DEFAULT NULL,
        `c2h4ppm` VARCHAR(255) DEFAULT NULL,
        `c2h2ppm` VARCHAR(255) DEFAULT NULL,
        `coppm` VARCHAR(255) DEFAULT NULL,
        `co2ppm` VARCHAR(255) DEFAULT NULL,
        `c3h6ppm` VARCHAR(255) DEFAULT NULL,
        `c3h8ppm` VARCHAR(255) DEFAULT NULL,
        `n2ppm` VARCHAR(255) DEFAULT NULL,
        `o2ppm` VARCHAR(255) DEFAULT NULL,
        `tdcgppm` VARCHAR(255) DEFAULT NULL,
        `tdgppm` VARCHAR(255) DEFAULT NULL,
        `tcgppm` VARCHAR(255) DEFAULT NULL,
        `ambientroc` VARCHAR(255) DEFAULT NULL,
        `topoilroc` VARCHAR(255) DEFAULT NULL,
        `hotspotxroc` VARCHAR(255) DEFAULT NULL,
        `hotspotyroc` VARCHAR(255) DEFAULT NULL,
        `hotspotzroc` VARCHAR(255) DEFAULT NULL,
        `puloadxroc` VARCHAR(255) DEFAULT NULL,
        `puloadyroc` VARCHAR(255) DEFAULT NULL,
        `puloadzroc` VARCHAR(255) DEFAULT NULL,
        `oiltemproc` VARCHAR(255) DEFAULT NULL,
        `moistureroc` VARCHAR(255) DEFAULT NULL,
        `puloadc1roc` VARCHAR(255) DEFAULT NULL,
        `puloadc2roc` VARCHAR(255) DEFAULT NULL,
        `fanspeedc1roc` VARCHAR(255) DEFAULT NULL,
        `fanspeedc2roc` VARCHAR(255) DEFAULT NULL,
        `oilflowroc` VARCHAR(255) DEFAULT NULL,
        `oilpressureroc` VARCHAR(255) DEFAULT NULL,
        `fannoiseroc` VARCHAR(255) DEFAULT NULL,
        `airflowroc` VARCHAR(255) DEFAULT NULL,
        `pumploadroc` VARCHAR(255) DEFAULT NULL,
        `h2ppmroc` VARCHAR(255) DEFAULT NULL,
        `ch4ppmroc` VARCHAR(255) DEFAULT NULL,
        `c2h6ppmroc` VARCHAR(255) DEFAULT NULL,
        `c2h4ppmroc` VARCHAR(255) DEFAULT NULL,
        `c2h2ppmroc` VARCHAR(255) DEFAULT NULL,
        `coppmroc` VARCHAR(255) DEFAULT NULL,
        `co2ppmroc` VARCHAR(255) DEFAULT NULL,
        `c3h6ppmroc` VARCHAR(255) DEFAULT NULL,
        `c3h8ppmroc` VARCHAR(255) DEFAULT NULL,
        `n2ppmroc` VARCHAR(255) DEFAULT NULL,
        `o2ppmroc` VARCHAR(255) DEFAULT NULL,
        `tdcgppmroc` VARCHAR(255) DEFAULT NULL,
        `tdgppmroc` VARCHAR(255) DEFAULT NULL,
        `tcgppmroc` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_MeasConditions_eqsernum` (`eqsernum`),
        KEY `IX_MeasConditions_sampdate` (`sampdate`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `EventItems` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) DEFAULT NULL,
        `EventDate` DATETIME(6) NOT NULL,
        `Payload` TEXT DEFAULT NULL,
        `SeverScale` INT NOT NULL DEFAULT 0,
        `Status` INT NOT NULL DEFAULT 0,
        PRIMARY KEY (`Id`),
        KEY `IX_EventItems_Eqsernum` (`Eqsernum`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `AlarmItems` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `IsActive` TINYINT(1) NOT NULL DEFAULT 0,
        `Eqsernum` VARCHAR(255) NULL,
        `Category` INT NULL,
        `Aseverity` INT NULL,
        `Score` VARCHAR(255) NULL,
        `AlarmName` VARCHAR(255) NULL,
        `LastSeen` VARCHAR(255) NULL,
        `FirstSeen` VARCHAR(255) NULL,
        `SeenCount` VARCHAR(255) NULL,
        `Source` VARCHAR(255) NULL,
        `Information` TEXT NULL,
        `Status` INT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_AlarmItems_Eqsernum` (`Eqsernum`),
        KEY `IX_AlarmItems_AlarmName` (`AlarmName`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE `alarmentries` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) DEFAULT NULL,
        `AlarmName` VARCHAR(255) DEFAULT NULL,
        `TTF` DOUBLE DEFAULT NULL,
        `Normal` DOUBLE DEFAULT NULL,
        `Caution` DOUBLE DEFAULT NULL,
        `Alert` DOUBLE DEFAULT NULL,
        `Alarm` DOUBLE DEFAULT NULL,
        `Emergency` DOUBLE DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_alarmentries_Eqsernum` (`Eqsernum`),
        KEY `IX_alarmentries_AlarmName` (`AlarmName`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `actionentries` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `AssetType` INT NULL,
        `Component` INT NULL,
        `AlarmType` INT NULL,
        `Statement` TEXT NULL,
        `Recommendations` TEXT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_actionentries_AssetType` (`AssetType`),
        KEY `IX_actionentries_Component` (`Component`),
        KEY `IX_actionentries_AlarmType` (`AlarmType`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    CREATE TABLE `RecommDictionary` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `AssetType` VARCHAR(255) DEFAULT NULL,
        `Component` VARCHAR(255) DEFAULT NULL,
        `AlarmType` VARCHAR(255) DEFAULT NULL,
        `Description` TEXT DEFAULT NULL,
        `Statement` JSON DEFAULT NULL,
        `Recommendations` JSON DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_RecommDictionary_AssetType` (`AssetType`),
        KEY `IX_RecommDictionary_Component` (`Component`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `alarmconfigs` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `Eqsernum` VARCHAR(255) DEFAULT NULL,
        `IsActive` TINYINT(1) NOT NULL DEFAULT 0,
        `AlarmName` VARCHAR(255) DEFAULT NULL,
        `ThreshType` VARCHAR(255) DEFAULT NULL,
        `CollectorType` VARCHAR(255) DEFAULT NULL,
        `TargetType` VARCHAR(255) DEFAULT NULL,
        `StatisticType` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_alarmconfigs_Eqsernum` (`Eqsernum`),
        KEY `IX_alarmconfigs_AlarmName` (`AlarmName`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

    // public class StateModel
    // {
    //     [Key]
    //     public int Id { get; set; }
    //     public bool ToSimulate { get; set; }
    //     public string AssetId { get; set; }
    //     public string StateName { get; set; }
    //     public string VarName { get; set; }
    //     public string Value { get; set; }
    //     public string Description { get; set; }
    //     public string Degradation { get; set; }
    //     public string scoreMin { get; set; }
    //     public string scoreMax { get; set; }
    //     public string alphaMin { get; set; }
    //     public string alphaMax { get; set; }
    //     public string betaMin { get; set; }
    //     public string betaMax { get; set; }
    //     public string sigmaMin { get; set; }
    //     public string sigmaMax { get; set; }
    //     public string GroupName { get; set; }
    // }

    

    // public class XfrmMap
    // {
    //     [Key]
    //     public int Id { get; set; }
    //     public string sessionId { get; set; }

    //     #region Added 4/30/2023
    //     public string Location { get; set; }
    //     public string Manufacturer { get; set; }
    //     public string Model { get; set; }
    //     public string Status { get; set; }
    //     #endregion
    //     public string XfrmID { get; set; }
    //     public string XType { get; set; }
    //     //public string XPhase { get; set; }
    //     public string Catgory { get; set; }
    //     public string VClass { get; set; }
    //     public string Rating1 { get; set; }
    //     public string Rating2 { get; set; }
    //     public string Rating3 { get; set; }
    //     public string Stage1 { get; set; }
    //     public string Stage2 { get; set; }
    //     public string Stage3 { get; set; }
    //     public string SolidInsulation { get; set; }
    //     public string LiquidInsulation { get; set; }
    //     //public string TankType { get; set; }
    //     public string Age { get; set; }
    //     public string GPSLatitude { get; set; }
    //     public string GPSLongitude { get; set; }
    //     public string GPSAltitude { get; set; }
    //     public string Voltage { get; set; }
    // }
    // ---------------------------
    // Asset Templates Structure
    // ---------------------------

    CREATE TABLE `LoadResults` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `cycle` INT NULL,
        `eqsernum` VARCHAR(255) NULL,
        `loadtype` VARCHAR(255) NULL,
        `sampdate` DATETIME(6) NULL,
        `uptopoil` VARCHAR(255) NULL,
        `uphotspot` VARCHAR(255) NULL,
        `upload` VARCHAR(255) NULL,
        `upbottom` VARCHAR(255) NULL,
        `uplife` VARCHAR(255) NULL,
        `ttptop` VARCHAR(255) NULL,
        `ttphot` VARCHAR(255) NULL,
        `ttpmva` VARCHAR(255) NULL,
        `margin` VARCHAR(255) NULL,
        `upsimu` INT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_LoadResults_eqsernum` (`eqsernum`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `LoadCurves` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `cycle` INT DEFAULT NULL,
        `eqsernum` VARCHAR(255) DEFAULT NULL,
        `loadtype` VARCHAR(255) DEFAULT NULL,
        `sampdate` DATETIME(6) DEFAULT NULL,
        `otime` VARCHAR(255) DEFAULT NULL,
        `opamb` VARCHAR(255) DEFAULT NULL,
        `obload` VARCHAR(255) DEFAULT NULL,
        `optopoil` VARCHAR(255) DEFAULT NULL,
        `ophotspot` VARCHAR(255) DEFAULT NULL,
        `opload` VARCHAR(255) DEFAULT NULL,
        `opbottom` VARCHAR(255) DEFAULT NULL,
        `oplife` VARCHAR(255) DEFAULT NULL,
        `margin` VARCHAR(255) DEFAULT NULL,
        `osimu` INT DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_LoadCurves_eqsernum` (`eqsernum`),
        KEY `IX_LoadCurves_sampdate` (`sampdate`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `LoadDistros` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `asset_id` VARCHAR(255) DEFAULT NULL,
        `opyear` VARCHAR(50) DEFAULT NULL,
        `load_type` VARCHAR(100) DEFAULT NULL,
        `margin` VARCHAR(100) DEFAULT NULL,
        `react_margin_min` VARCHAR(100) DEFAULT NULL,
        `margin_max` VARCHAR(100) DEFAULT NULL,
        `margin_std` VARCHAR(100) DEFAULT NULL,
        `uphotspot` VARCHAR(100) DEFAULT NULL,
        `uphotspot_min` VARCHAR(100) DEFAULT NULL,
        `uphotspot_max` VARCHAR(100) DEFAULT NULL,
        `uphotspot_std` VARCHAR(100) DEFAULT NULL,
        `uptopoil` VARCHAR(100) DEFAULT NULL,
        `uptopoil_min` VARCHAR(100) DEFAULT NULL,
        `uptopoil_max` VARCHAR(100) DEFAULT NULL,
        `uptopoil_std` VARCHAR(100) DEFAULT NULL,
        `upbottom` VARCHAR(100) DEFAULT NULL,
        `upbottom_min` VARCHAR(100) DEFAULT NULL,
        `upbottom_max` VARCHAR(100) DEFAULT NULL,
        `upbottom_std` VARCHAR(100) DEFAULT NULL,
        `uplife` VARCHAR(100) DEFAULT NULL,
        `uplife_min` VARCHAR(100) DEFAULT NULL,
        `uplife_max` VARCHAR(100) DEFAULT NULL,
        `uplife_std` VARCHAR(100) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_LoadDistros_asset_id` (`asset_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `LoadCbDistros` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `asset_id` VARCHAR(255) DEFAULT NULL,
        `opyear` VARCHAR(50) DEFAULT NULL,
        `load_type` VARCHAR(100) DEFAULT NULL,
        `score` VARCHAR(255) DEFAULT NULL,
        `score_min` VARCHAR(255) DEFAULT NULL,
        `score_max` VARCHAR(255) DEFAULT NULL,
        `score_std` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_LoadCbDistros_asset_id` (`asset_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `ThermalDistros` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `asset_id` VARCHAR(255) DEFAULT NULL,
        `opyear` VARCHAR(50) DEFAULT NULL,
        `load_type` VARCHAR(100) DEFAULT NULL,
        `th_time` VARCHAR(255) DEFAULT NULL,
        `opamb` VARCHAR(255) DEFAULT NULL,
        `obload` VARCHAR(255) DEFAULT NULL,
        `margin` VARCHAR(255) DEFAULT NULL,
        `margin_min` VARCHAR(255) DEFAULT NULL,
        `margin_max` VARCHAR(255) DEFAULT NULL,
        `margin_std` VARCHAR(255) DEFAULT NULL,
        `optopoil` VARCHAR(255) DEFAULT NULL,
        `optopoil_min` VARCHAR(255) DEFAULT NULL,
        `optopoil_max` VARCHAR(255) DEFAULT NULL,
        `optopoil_std` VARCHAR(255) DEFAULT NULL,
        `opbottom` VARCHAR(255) DEFAULT NULL,
        `opbottom_min` VARCHAR(255) DEFAULT NULL,
        `opbottom_max` VARCHAR(255) DEFAULT NULL,
        `opbottom_std` VARCHAR(255) DEFAULT NULL,
        `ophotspot` VARCHAR(255) DEFAULT NULL,
        `ophotspot_min` VARCHAR(255) DEFAULT NULL,
        `ophotspot_max` VARCHAR(255) DEFAULT NULL,
        `ophotspot_std` VARCHAR(255) DEFAULT NULL,
        `opload` VARCHAR(255) DEFAULT NULL,
        `opload_min` VARCHAR(255) DEFAULT NULL,
        `opload_max` VARCHAR(255) DEFAULT NULL,
        `opload_std` VARCHAR(255) DEFAULT NULL,
        `oplife` VARCHAR(255) DEFAULT NULL,
        `oplife_min` VARCHAR(255) DEFAULT NULL,
        `oplife_max` VARCHAR(255) DEFAULT NULL,
        `oplife_std` VARCHAR(255) DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_ThermalDistros_asset_id` (`asset_id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `loadingcases` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `xfrmId` VARCHAR(255) DEFAULT NULL,
        `sessionId` VARCHAR(255) DEFAULT NULL,
        `LoadType` VARCHAR(255) DEFAULT NULL,
        `HotSpotLimit` DOUBLE DEFAULT NULL,
        `TopOilLimit` DOUBLE DEFAULT NULL,
        `LoLLimit` DOUBLE DEFAULT NULL,
        `PULLimit` DOUBLE DEFAULT NULL,
        `BubblingLimit` DOUBLE DEFAULT NULL,
        `CoolPWLimit` DOUBLE DEFAULT NULL,
        `BeginOverTime` DOUBLE DEFAULT NULL,
        `EndOverTime` DOUBLE DEFAULT NULL,
        `InsLifeExp` DOUBLE DEFAULT NULL,
        `OxyContent` DOUBLE DEFAULT NULL,
        `MoisContent` DOUBLE DEFAULT NULL,
        `GasContent` DOUBLE DEFAULT NULL,
        `HSPressure` DOUBLE DEFAULT NULL,
        `LtcPosition` INT DEFAULT NULL,
        `LtcAmpacity` DOUBLE DEFAULT NULL,
        `OptimError` DOUBLE DEFAULT NULL,
        `ToSimulate` TINYINT(1) NOT NULL DEFAULT 0,
        `Scheduled` VARCHAR(255) DEFAULT NULL,
        `LPlan` VARCHAR(255) DEFAULT NULL,
        `JsonConditions` TEXT DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_loadingcases_xfrmId` (`xfrmId`),
        KEY `IX_loadingcases_sessionId` (`sessionId`),
        KEY `IX_loadingcases_LoadType` (`LoadType`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `LoadProfiles` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `IsSelected` TINYINT(1) NOT NULL DEFAULT 0,
        `xfrmId` VARCHAR(255) DEFAULT NULL,
        `sessionId` VARCHAR(255) DEFAULT NULL,
        `profileName` VARCHAR(255) DEFAULT NULL,
        `time` DOUBLE DEFAULT NULL,
        `sumamb` DOUBLE DEFAULT NULL,
        `sumpul` DOUBLE DEFAULT NULL,
        `sumcool` DOUBLE DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_LoadProfiles_xfrmId` (`xfrmId`),
        KEY `IX_LoadProfiles_sessionId` (`sessionId`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


    CREATE TABLE `Coolings` (
        `Id` INT NOT NULL AUTO_INCREMENT,
        `sessionId` VARCHAR(255) DEFAULT NULL,
        `xfrmId` VARCHAR(255) DEFAULT NULL,
        `Status` VARCHAR(255) DEFAULT NULL,
        `PerUnitBasekVA` DOUBLE DEFAULT NULL,
        `WindingTempBase` DOUBLE DEFAULT NULL,
        `AvgWindingRise` DOUBLE DEFAULT NULL,
        `HotSpotRise` DOUBLE DEFAULT NULL,
        `TopOilRise` DOUBLE DEFAULT NULL,
        `BottomOilRise` DOUBLE DEFAULT NULL,
        `AvgOilRise` DOUBLE DEFAULT NULL,
        `LossBasekVA` DOUBLE DEFAULT NULL,
        `LossTempBase` DOUBLE DEFAULT NULL,
        `WindI2RLosses` DOUBLE DEFAULT NULL,
        `WindEddyLoss` DOUBLE DEFAULT NULL,
        `WindStrayLosses` DOUBLE DEFAULT NULL,
        `XfrmerCoolLevel` DOUBLE DEFAULT NULL,
        `XfrmerCooling` VARCHAR(255) DEFAULT NULL,
        `XfrmerRating` DOUBLE DEFAULT NULL,
        `LoadLoss` DOUBLE DEFAULT NULL,
        `numCooler` INT DEFAULT NULL,
        `numFan` INT DEFAULT NULL,
        `numRadiator` INT DEFAULT NULL,
        `numPumps` INT DEFAULT NULL,
        `HRatedAmps` DOUBLE DEFAULT NULL,
        `XRatedAmps` DOUBLE DEFAULT NULL,
        `TRatedAmps` DOUBLE DEFAULT NULL,
        `Power` DOUBLE DEFAULT NULL,
        PRIMARY KEY (`Id`),
        KEY `IX_Coolings_sessionId` (`sessionId`),
        KEY `IX_Coolings_xfrmId` (`xfrmId`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



        public void ImportTemplateDictionaryFromJson(string jsonFilePath)
        {
            if (string.IsNullOrEmpty(jsonFilePath) || !File.Exists(jsonFilePath))
                throw new FileNotFoundException("JSON file not found.", jsonFilePath);

            var json = File.ReadAllText(jsonFilePath);
            var entries = System.Text.Json.JsonSerializer.Deserialize<List<Eqdictionary>>(json);
            if (entries == null || entries.Count == 0)
                return;

            foreach (var entry in entries)
            {
                Database.ExecuteSqlRaw(
                    "INSERT INTO Eqdictionaries (Eqsernum, Varname, Value, Unit, Defaultv, Description, Information, Groupname) " +
                    "VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})",
                    entry.Eqsernum ?? "Template",
                    entry.Varname,
                    entry.Value,
                    entry.Unit,
                    entry.Defaultv,
                    entry.Description,
                    entry.Information,
                    entry.Groupname
                );
            }
        }

        public List<MmiFactor> GetMmiFactors(AssetCat eqpmt, Modes Modtype)
        {
            return MmiFactors.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == Modtype).ToList();
        }

        public List<Mcondition> GetMeasCIFactors(CondState Criteria, AssetCond Condtype)
        {
            return Mconditions.Where(p => p.Criteria == Criteria).Where(p => p.Condtype == Condtype).ToList();
        }

        public List<Condition> GetObsCIFactors(CondState Criteria, AssetCond Condtype)
        {
            return Conditions.Where(p => p.Criteria == Criteria).Where(p => p.Condtype == Condtype).ToList();
        }



        public void ImportMmiFactorsFromJson(string jsonFilePath)
        {
            var json = System.IO.File.ReadAllText(jsonFilePath);
            var mmiFactors = System.Text.Json.JsonSerializer.Deserialize<List<MmiFactorDto>>(json);
            foreach (var factor in mmiFactors)
            {
                int eqpmt = (int)Enum.Parse(typeof(AssetCat), factor.Eqpmt);
                int subcomp = (int)Enum.Parse(typeof(SubAsset), factor.Subcomp);
                int modtype = (int)Enum.Parse(typeof(Modes), factor.Modtype);

                Database.ExecuteSqlRaw(
                    "INSERT INTO MmiFactors (Eqpmt, Subcomp, Df1, Df2, Maxnofc, Modtype) VALUES ({0}, {1}, {2}, {3}, {4}, {5})",
                    eqpmt, subcomp, factor.Df1, factor.Df2, factor.Maxnofc, modtype
                );
            }
        }


        public void ImportMconditionsFromJson(string jsonFilePath, bool insertIgnore = true)
        {
            var json = System.IO.File.ReadAllText(jsonFilePath);
            var items = System.Text.Json.JsonSerializer.Deserialize<List<MconditionDto>>(
                json,
                new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            );

            if (items == null || items.Count == 0)
                return;

            using var tx = Database.BeginTransaction();
            try
            {
                var sql = insertIgnore
                    ? "INSERT IGNORE INTO Mconditions (Eqpmt, Subcomp, Condtype, Criteria, Descp, Infactor, Incap, Incollar) VALUES ({0},{1},{2},{3},{4},{5},{6},{7})"
                    : "INSERT INTO Mconditions (Eqpmt, Subcomp, Condtype, Criteria, Descp, Infactor, Incap, Incollar) VALUES ({0},{1},{2},{3},{4},{5},{6},{7})";

                foreach (var it in items)
                {
                    var eqpmt = ParseEnumFlexible<AssetCat>(it.Eqpmt, nameof(it.Eqpmt));
                    var subcomp = ParseEnumFlexible<SubAsset>(it.Subcomp, nameof(it.Subcomp));
                    var condtype = ParseEnumFlexible<AssetCond>(it.Condtype, nameof(it.Condtype));
                    var criteria = ParseEnumFlexible<CondState>(it.Criteria, nameof(it.Criteria));

                    Database.ExecuteSqlRaw(
                        sql,
                        (int)eqpmt,
                        (int)subcomp,
                        (int)condtype,
                        (int)criteria,
                        it.Descp ?? string.Empty,
                        it.Infactor,
                        it.Incap,
                        it.Incollar
                    );
                }

                tx.Commit();
            }
            catch
            {
                tx.Rollback();
                throw;
            }
        }



        public void ImportModifiersFromJson(string jsonFilePath, bool insertIgnore = true)
        {
              var json = System.IO.File.ReadAllText(jsonFilePath);
            var items = System.Text.Json.JsonSerializer.Deserialize<List<ModifierDto>>(
                json,
                new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            );

            if (items == null || items.Count == 0)
                return;

            using var tx = Database.BeginTransaction();
            try
            {
                var sql = insertIgnore
                    ? "INSERT IGNORE INTO Modifiers (Eqpmt, Low, High, Score, Modtype) VALUES ({0}, {1}, {2}, {3}, {4})"
                    : "INSERT INTO Modifiers (Eqpmt, Low, High, Score, Modtype) VALUES ({0}, {1}, {2}, {3}, {4})";

                foreach (var it in items)
                {
                    var eqpmt = ParseEnumFlexible<AssetCat>(it.Eqpmt, nameof(it.Eqpmt));
                    var modtype = ParseEnumFlexible<Modes>(it.Modtype, nameof(it.Modtype));

                    Database.ExecuteSqlRaw(
                        sql,
                        (int)eqpmt,
                        it.Low,
                        it.High,
                        it.Score,
                        (int)modtype
                    );
                }

                tx.Commit();
            }
            catch
            {
                tx.Rollback();
                throw;
            }
        }

        public void ImportObservedConditionsFromJson(string jsonFilePath, bool insertIgnore = true)
        {
            var json = System.IO.File.ReadAllText(jsonFilePath);
            var items = System.Text.Json.JsonSerializer.Deserialize<List<ConditionDto>>(
                json,
                new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            );

            if (items == null || items.Count == 0)
                return;

            using var tx = Database.BeginTransaction();
            try
            {
                var sql = insertIgnore
                    ? "INSERT IGNORE INTO Conditions (Eqpmt, Subcomp, Condtype, Criteria, Descp, Infactor, Incollar, Incap) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})"
                    : "INSERT INTO Conditions (Eqpmt, Subcomp, Condtype, Criteria, Descp, Infactor, Incollar, Incap) VALUES ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})";

                foreach (var cond in items)
                {
                    var eqpmt = ParseEnumFlexible<AssetCat>(cond.Eqpmt, nameof(cond.Eqpmt));
                    var subcomp = ParseEnumFlexible<SubAsset>(cond.Subcomp, nameof(cond.Subcomp));
                    var condtype = ParseEnumFlexible<AssetCond>(cond.Condtype, nameof(cond.Condtype));
                    var criteria = ParseEnumFlexible<CondState>(cond.Criteria, nameof(cond.Criteria));

                    Database.ExecuteSqlRaw(
                        sql,
                        eqpmt,
                        subcomp,
                        condtype,
                        criteria,
                        cond.Descp ?? string.Empty,
                        cond.Infactor,
                        cond.Incollar,
                        cond.Incap
                    );
                }

                tx.Commit();
            }
            catch
            {
                tx.Rollback();
                throw;
            }
        }

        public void SetEconomicVars()
        {

            /* # -----------------------------------------------------------#
               # B.5.10 HV Transformer (GM)                                 #
               # -----------------------------------------------------------# */

            var mmiFactorJsonFilePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "CNAIMv2", "Mmifactors.json");
            ImportMmiFactorsFromJson(mmiFactorJsonFilePath);

            /* # -----------------------------------------------------------#
               # B.5.11 HV Transformer (GM) (Main Transformer component)    #
               # -----------------------------------------------------------# */

            var observedConditionJsonFilePath = Path.Combine(Directory.GetCurrentDirectory(), "CNAIMv2", "ObservedConditions.json");
            ImportObservedConditionsFromJson(observedConditionJsonFilePath);

            /*
            # --------------------------------------------------------- #
            # B.6.10 HV Transformer (GM)                                #
            # B.6.11 EHV Transformer (GM) (Main Transformer Component   # 
            # B.6.13 132kV Transformer (GM) (Main Transformer Component)#  
            # B.6.14 132kV Transformer (GM) (Tapchanger component)      #                                                          #
            # --------------------------------------------------------- #
            */
            var mConditionJsonFilePath = Path.Combine(Directory.GetCurrentDirectory(), "CNAIMv2", "MeasuredConditions.json");
            ImportMconditionsFromJson(mConditionJsonFilePath);

            /*
            # -------------------------------------------------#
            # B.7 Oil Test Modifier                            #
            # -------------------------------------------------#
            */
            //# TABLE 203: MOISTURE CONDITION STATE CALIBRATION
            var modifierJsonFilePath = Path.Combine(Directory.GetCurrentDirectory(), "CNAIMv2", "Modifiers.json");
            ImportModifiersFromJson(modifierJsonFilePath);

        }

        public Dictionary<string, double> GetOilCondVars(AssetCat eqpmt, double moisture, double acidity, double bd_strength)
        {
            using var context = new ConditionContext();
            var acitype = Modes.ACIDITY;
            var bdtype = Modes.BD_STRENGTH;
            var moistype = Modes.MOISTURE;
            var acidity_value_list = context.Modifiers.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == acitype);
            var moisture_value_list = context.Modifiers.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == moistype);
            var bd_strength_list = context.Modifiers.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == bdtype);

            //Console.WriteLine("acidity_value_list", acidity_value_list);
            var acidity_score = acidity_value_list.Where(p => p.Low < acidity).Where(p => p.High >= acidity).FirstOrDefault().Score;
            var moisture_score = moisture_value_list.Where(p => p.Low < moisture).Where(p => p.High >= moisture).FirstOrDefault().Score;
            var bd_strength_score = bd_strength_list.Where(p => p.Low < bd_strength).Where(p => p.High >= bd_strength).FirstOrDefault().Score;

            var retval = new Dictionary<string, double>(){
                { "moisture_score", moisture_score}, {"acidity_score", acidity_score }, {"bd_strength_score", bd_strength_score }
            };
            return retval;
        }

        public Dictionary<string, double> GetOilCondCaps(AssetCat eqpmt, double condvalue)
        {
            using var context = new ConditionContext();
            var oil_cond_value = Modes.OIL_CONDITION_SCORE;
            var oil_test_collar = Modes.OIL_TEST_COLLAR;
            var cond_value_list = Modifiers.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == oil_cond_value);
            var collar_value_list = Modifiers.Where(p => p.Eqpmt == eqpmt).Where(p => p.Modtype == oil_test_collar);

            var oil_factor = cond_value_list.Where(p => p.Low < condvalue).Where(p => p.High >= condvalue).FirstOrDefault().Score;
            var oil_collar = collar_value_list.Where(p => p.Low < condvalue).Where(p => p.High >= condvalue).FirstOrDefault().Score;
            var retval = new Dictionary<string, double>(){
                { "oil_factor", oil_factor}, {"oil_collar", oil_collar }
            };
            return retval;
        }

        public Dictionary<string, double> GetDGAScores(AssetCat eqpmt, double hydrogen, double methane,
                                                            double ethylene, double acetylene, double ethane,
                                                            double hydrogen_pre, double methane_pre, double ethylene_pre,
                                                            double acetylene_pre, double ethane_pre)
        {
            var h2cond_value_list = Modifiers.Where(p => p.Modtype == Modes.HYDROGEN_CONDITION);

            var h2score = h2cond_value_list.Where(p => p.Low < hydrogen).Where(p => p.High >= hydrogen).FirstOrDefault().Score;
            var h2score_pre = h2cond_value_list.Where(p => p.Low < hydrogen_pre).Where(p => p.High >= hydrogen_pre).FirstOrDefault().Score;

            var ch4cond_value_list = Modifiers.Where(p => p.Modtype == Modes.METHANE_CONDITION);
            var ch4score = ch4cond_value_list.Where(p => p.Low < methane).Where(p => p.High >= methane).FirstOrDefault().Score;
            var ch4score_pre = ch4cond_value_list.Where(p => p.Low < methane_pre).Where(p => p.High >= methane_pre).FirstOrDefault().Score;

            var c2h2cond_value_list = Modifiers.Where(p => p.Modtype == Modes.ACETYLENE_CONDITION);
            var c2h2score = c2h2cond_value_list.Where(p => p.Low < acetylene).Where(p => p.High >= acetylene).FirstOrDefault().Score;
            var c2h2score_pre = c2h2cond_value_list.Where(p => p.Low < acetylene_pre).Where(p => p.High >= acetylene_pre).FirstOrDefault().Score;

            var c2h4cond_value_list = Modifiers.Where(p => p.Modtype == Modes.ETHYLENE_CONDITION);
            var c2h4score = c2h4cond_value_list.Where(p => p.Low < ethylene).Where(p => p.High >= ethylene).FirstOrDefault().Score;
            var c2h4score_pre = c2h4cond_value_list.Where(p => p.Low < ethylene_pre).Where(p => p.High >= ethylene_pre).FirstOrDefault().Score;

            var c2h6cond_value_list = Modifiers.Where(p => p.Modtype == Modes.ETHYLENE_CONDITION);
            var c2h6score = c2h6cond_value_list.Where(p => p.Low < ethane).Where(p => p.High >= ethane).FirstOrDefault().Score;
            var c2h6score_pre = c2h6cond_value_list.Where(p => p.Low < ethane_pre).Where(p => p.High >= ethane_pre).FirstOrDefault().Score;

            var retval = new Dictionary<string, double>(){
                { "hydrogen_score", h2score}, {"methane_score", ch4score }, {"acetylene_score", c2h2score}, {"ethylene_score", c2h4score },
                {"ethane_score", c2h6score }, { "hydrogen_pre_score", h2score_pre }, {"methane_pre_score", ch4score_pre},
                {"acetylene_pre_score", c2h2score_pre }, {"ethylene_pre_score", c2h4score_pre }, { "ethane_pre_score", c2h6score_pre}
            };
            return retval;
        }

        public double GetConditionScore(AssetCat eqpmt, Modes modtype, double condvalue)
        {
            var condition_value_list = Modifiers.Where(p => p.Modtype == modtype);
            var condition_score = condition_value_list.Where(p => p.Low < condvalue).Where(p => p.High >= condvalue).FirstOrDefault().Score;
            return condition_score;
        }

        public double GetRandomNumberInRange(double minNumber, double maxNumber)
        {
            return random.NextDouble() * (maxNumber - minNumber) + minNumber;
        }

        public void CreateVarDictionaries()
        {
            VarDictionaries.AddRange
                (
                    new VarDictionary { VarName = "ambient", VarGroup = "TEMPERATURE", VarSubGroup = "AVG", Description = "Ambient temperature", MinValue = "-15", MaxValue = "35", Unit = "ºC" },
                    new VarDictionary { VarName = "topoil", VarGroup = "TEMPERATURE", VarSubGroup = "AVG", Description = "Top oil temperature", MinValue = "-15", MaxValue = "35", Unit = "ºC" },
                    new VarDictionary { VarName = "hotspotx", VarGroup = "TEMPERATURE", MinValue = "80", MaxValue = "150", VarSubGroup = "AVG", Description = "X Winding Hot spot temperature", Unit = "ºC" },
                    new VarDictionary { VarName = "hotspoty", VarGroup = "TEMPERATURE", MinValue = "80", MaxValue = "150", VarSubGroup = "AVG", Description = "Y Winding Hot spot temperature", Unit = "ºC" },
                    new VarDictionary { VarName = "hotspotz", VarGroup = "TEMPERATURE", MinValue = "80", MaxValue = "150", VarSubGroup = "AVG", Description = "Z Winding Hot spot temperature", Unit = "ºC" },
                    new VarDictionary { VarName = "oiltemp", VarGroup = "TEMPERATURE", MinValue = "30", MaxValue = "150", VarSubGroup = "AVG", Description = "Liquid insulation temperature", Unit = "ºC" },

                    new VarDictionary { VarName = "puloadx", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "X Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },
                    new VarDictionary { VarName = "puloady", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "Y Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },
                    new VarDictionary { VarName = "puloadz", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "Z Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },
                    new VarDictionary { VarName = "puloadc1", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "Z Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },
                    new VarDictionary { VarName = "puloadc2", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "Z Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },
                    new VarDictionary { VarName = "pumpload", VarGroup = "LOAD", VarSubGroup = "AVG", Description = "Z Winding Hot p.u. load", MinValue = "0.5", MaxValue = "1.3", Unit = "p.u." },

                    new VarDictionary { VarName = "moisture", VarGroup = "MOISTURE", VarSubGroup = "AVG", Description = "Moisture content in oil", MinValue = "0.5", MaxValue = "5", Unit = "ppm" },
                    new VarDictionary { VarName = "fanspeedc1", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Moisture content in oil", MinValue = "150", MaxValue = "1500", Unit = "rpm" },
                    new VarDictionary { VarName = "fanspeedc2", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Moisture content in oil", MinValue = "150", MaxValue = "1500", Unit = "rpm" },
                    new VarDictionary { VarName = "oilflow", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Oil flow in cooling ducts", MinValue = "150", MaxValue = "1500", Unit = "ºC" },
                    new VarDictionary { VarName = "oilpressure", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Oil pressure in cooling ducts", MinValue = "150", MaxValue = "1500", Unit = "ºC" },
                    new VarDictionary { VarName = "fannoise", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Fan noise", MinValue = "20", MaxValue = "80", Unit = "dB" },
                    new VarDictionary { VarName = "airflow", VarGroup = "COOLING", VarSubGroup = "AVG", Description = "Fans Air flow", MinValue = "20", MaxValue = "80", Unit = "Bar" },

                    new VarDictionary { VarName = "h2ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Hydrogen (H2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "ch4ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Methane (CH4)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c2h6ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Ethane (C2H6)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c2h4ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Ethylen (C2H4)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c3h6ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Propane (C3H6)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c3h8ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "propylen (C3H8)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "coppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Carbon Monoxide (CO)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "co2ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Carbondioxide (CO2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "n2ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Nitrogen (N2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "o2ppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Oxygen (O2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tdcgppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Total dissolved combustible Gas", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tcgppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Total combustible gas", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tdgppm", VarGroup = "DISSOLVED GASSES", VarSubGroup = "AVG", Description = "Total dissolved gas", MinValue = "20", MaxValue = "1200", Unit = "ppm" },

                    // Rate of change (ROC)
                    new VarDictionary { VarName = "ambientroc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "Ambient temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "topoilroc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "Top oil temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "hotspotxroc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "X Winding Hot spot temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "hotspotyroc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "Y Winding Hot spot temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "hotspotzroc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "Z Winding Hot spot temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "oiltemproc", VarGroup = "TEMPERATURE", VarSubGroup = "ROC", Description = "Oil temp. rate of change", MinValue = "20", MaxValue = "1200", Unit = "ppm" },

                    new VarDictionary { VarName = "puloadxroc", VarGroup = "LOAD", VarSubGroup = "ROC", Description = "X Winding p.u. load rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "puloadyroc", VarGroup = "LOAD", VarSubGroup = "ROC", Description = "Y Winding p.u. load rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "puloadzroc", VarGroup = "LOAD", VarSubGroup = "ROC", Description = "Z Winding p.u. load rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "puloadc1roc", VarGroup = "LOAD", VarSubGroup = "ROC", Description = "Cooling Bank 1 p.u. load rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "puloadc2roc", VarGroup = "LOAD", VarSubGroup = "ROC", Description = "Cooling Bank 2 p.u. load rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },

                    new VarDictionary { VarName = "moistureroc", VarGroup = "MOISTURE", VarSubGroup = "ROC", Description = "Per-unit moisture rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "fanspeedc1roc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "fanspeedc2roc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "oilflowroc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },

                    new VarDictionary { VarName = "oilpressureroc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "fannoiseroc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "airflowroc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },
                    new VarDictionary { VarName = "pumploadroc", VarGroup = "COOLING", VarSubGroup = "ROC", Description = "Fan speed rate of change", MinValue = "0.0", MaxValue = "0.1", Unit = "ppm" },


                    new VarDictionary { VarName = "h2ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Hydrogen (H2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "ch4ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Methane (CH4)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c2h6ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Ethane (C2H6)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c2h4ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Ethylen (C2H4)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c3h6ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Propane (C3H6)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "c3h8ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "propylen (C3H8)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "coppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Carbon Monoxide (CO)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "co2ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Carbondioxide (CO2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "n2ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Nitrogen (N2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "o2ppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Oxygen (O2)", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tdcgppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Total dissolved combustible Gas", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tcgppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Total combustible gas roc", MinValue = "20", MaxValue = "1200", Unit = "ppm" },
                    new VarDictionary { VarName = "tdgppmroc", VarGroup = "DISSOLVED GASSES", VarSubGroup = "ROC", Description = "Total dissolved gas roc", MinValue = "20", MaxValue = "1200", Unit = "ppm" },

                    new VarDictionary { VarName = "simstatus", VarGroup = "SYSTEM", VarSubGroup = "INTEROP", Description = "Simulation start/stop status", MinValue = "0", MaxValue = "1", Unit = "-" }

            );
            SaveChanges();
        }

        public void LoadAlarmSettings()
        {
            string _recomJsonFilePath = "Recommendations.json";
            string json = File.ReadAllText(_recomJsonFilePath);
            List<RecommDictionary> recomms = JsonConvert.DeserializeObject<List<RecommDictionary>>(json);
            if (recomms != null)
            {
                foreach (var recom in recomms)
                {
                    Enum.TryParse(recom.AssetType, out AssetCat assetCat);
                    Enum.TryParse(recom.Component, out AssetCond assetCond);
                    Enum.TryParse(recom.AlarmType, out Severity severity);
                    Database.ExecuteSqlRaw("INSERT INTO `actionentries`(`AssetType`,`Component`,`AlarmType`,`Statement`,`Recommendations`) VALUES ({0}, {1}, {2}, {3}, {4});",
                                                                      assetCat, assetCond, severity, string.Join(", ", recom.Statement), string.Join(", ", recom.Recommendations));
                }
            }
        }

        public virtual void CreateXfrmMonitor(XfrmMap rxXfrm)
        {
            LoadingStandard ieclStds, ieee7lStds, ieeeGlStds;
            Enum.TryParse("IEC60354", out ieclStds);
            Enum.TryParse("IEEE7", out ieee7lStds);
            Enum.TryParse("IEEEG", out ieeeGlStds);

            switch (rxXfrm.LiquidInsulation)
            {
                case "MINERAL OIL": rxXfrm.LiquidInsulation = "1"; break;
                case "SILICONE": rxXfrm.LiquidInsulation = "2"; break;
                case "ESTER": rxXfrm.LiquidInsulation = "3"; break;
            }

            switch (rxXfrm.SolidInsulation)
            {
                case "UPGRADED-KRAFT": rxXfrm.SolidInsulation = "TUK"; break;
                case "NON-UPGRADED": rxXfrm.LiquidInsulation = "KRAFT"; break;
                case "ARAMID": rxXfrm.LiquidInsulation = "ARAMID"; break;
            }
            try
            {
                Database.ExecuteSqlRaw(
                        "INSERT into `XfrmMaps`(`sessionId`,`Location`,`Manufacturer`,`Model`,`Status`,`XfrmID`,`XType`,`Catgory`,`VClass`,`Rating1`,`Rating2`,`Rating3`,`Stage1`," +
                        "`Stage2`,`Stage3`,`SolidInsulation`,`LiquidInsulation`,`Age`,`GPSLatitude`,`GPSLongitude`,`GPSAltitude`,`Voltage`,`JsonCosts`) VALUES " +
                        "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}" +
                        ", {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22});", rxXfrm.sessionId, rxXfrm.Location, rxXfrm.Manufacturer, rxXfrm.Model, rxXfrm.Status, rxXfrm.XfrmID, rxXfrm.XType,
                        rxXfrm.Catgory, rxXfrm.VClass, rxXfrm.Rating1, rxXfrm.Rating2, rxXfrm.Rating3, rxXfrm.Stage1, rxXfrm.Stage2, rxXfrm.Stage3, rxXfrm.SolidInsulation,
                        rxXfrm.LiquidInsulation, rxXfrm.Age, rxXfrm.GPSLatitude, rxXfrm.GPSLongitude, rxXfrm.GPSAltitude, rxXfrm.Voltage, rxXfrm.JsonCosts);
                Database.ExecuteSqlRaw(
                        "INSERT INTO `loadingcases`(`xfrmId`,`sessionId`,`LoadType`,`HotSpotLimit`,`TopOilLimit`,`LoLLimit`,`PULLimit`,`BubblingLimit`,`CoolPWLimit`,`BeginOverTime`," +
                        "`EndOverTime`,`InsLifeExp`,`OxyContent`,`MoisContent`,`GasContent`,`HSPressure`,`LtcPosition`,`LtcAmpacity`,`OptimError`,`ToSimulate`,`Scheduled`,`LPlan`) VALUES" +
                        "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21});",
                            rxXfrm.XfrmID, Utility.PERIODIC_USER, "24h-Normal", 120, 105, 150, 1.0, 150, 0.1, 0, 1440, 65000, 10, 100, 0, 10, -1, 100, 0.1, true, "", "NLEL");
                Database.ExecuteSqlRaw(
                        "INSERT INTO `loadingcases`(`xfrmId`,`sessionId`,`LoadType`,`HotSpotLimit`,`TopOilLimit`,`LoLLimit`,`PULLimit`,`BubblingLimit`,`CoolPWLimit`,`BeginOverTime`," +
                        "`EndOverTime`,`InsLifeExp`,`OxyContent`,`MoisContent`,`GasContent`,`HSPressure`,`LtcPosition`,`LtcAmpacity`,`OptimError`,`ToSimulate`,`Scheduled`,`LPlan`) VALUES" +
                        "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21});",
                            rxXfrm.XfrmID, Utility.PERIODIC_USER, "24h-STEmergency", 140, 110, 350, 1.3, 150, 0.0, 600, 800, 65000, 10, 100, 0, 10, -1, 100, 0.1, true, "", "STE");
                Database.ExecuteSqlRaw(
                        "INSERT INTO `loadingcases`(`xfrmId`,`sessionId`,`LoadType`,`HotSpotLimit`,`TopOilLimit`,`LoLLimit`,`PULLimit`,`BubblingLimit`,`CoolPWLimit`,`BeginOverTime`," +
                        "`EndOverTime`,`InsLifeExp`,`OxyContent`,`MoisContent`,`GasContent`,`HSPressure`,`LtcPosition`,`LtcAmpacity`,`OptimError`,`ToSimulate`,`Scheduled`,`LPlan`) VALUES" +
                        "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21});",
                            rxXfrm.XfrmID, Utility.PERIODIC_USER, "24h-LTEmergency", 140, 110, 650, 1.2, 150, 0.0, 400, 1200, 65000, 10, 100, 0, 10, -1, 100, 0.1, true, "", "LTE");
                Database.ExecuteSqlRaw(
                        "INSERT into `LoadingStds`(`sessionId`, `xfrmId`, `IsSelected`, `pubName`, `pubTitle`,`pubDate`) VALUES ({0}, {1}, 0, {2}, 'IEC Loading Guide For Power Transformers',  '2000-04-07');" +
                        "INSERT into `LoadingStds`(`sessionId`, `xfrmId`, `IsSelected`, `pubName`, `pubTitle`,`pubDate`) VALUES ({0}, {1}, 0, {3}, 'IEEE Clause 7 Loading Guide For oil filled Transformers',  '2000-04-07');" +
                        "INSERT into `LoadingStds`(`sessionId`, `xfrmId`, `IsSelected`, `pubName`, `pubTitle`,`pubDate`) VALUES ({0}, {1}, 0, {4}, 'IEEE AnnexG Loading Guide For oil filled Transformers',  '2000-04-07');",
                        rxXfrm.sessionId, rxXfrm.XfrmID, ieclStds, ieee7lStds, ieeeGlStds);
                Database.ExecuteSqlRaw(
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TransfoType',		{2}, 		    '-',        'DISTRIBUTION, MEDIUM, or LARGE Power Transformer');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TransfoPhase',		'-', 		    '-',        'Number of Phases');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CustomerID',		{2},			'-',        'Customer Name');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'UnitID',			{1},			'-',        'Unit Identifier');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LoadCyclePeriod',	'24',			'Hour(s)',  'Load cycle period');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'Age',	            {3},			'Year(s)',  'Equipment Age');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LossBasekVA',		'28000',		'kVA',      'Base Rating for Losses');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LossTempBase',	    '85',			'Celsius',  'Temperature Base for Losses');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindI2RLosses',	    '95000',		'Watts',    'I2R Losses, (Pw)');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindEddyLoss',	    '12000',		'Watts',    'Winding Eddy Losses, (Pe)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindStrayLosses',	'5600',			'Watts',    'Stray Losses, (Ps)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CoreLosses',		'88000',		'Watts',    'Core Losses, (Pcr)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerUnitBasekVA',	'28000',		'kVA',      'One Per Unit Base for Load Cycle');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindingTempBase',	'65',			'Celsius',  'Rated Avg. Winding Rise (AWR)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'AvgWindingRise',	'43',			'K',        'Tested Avg. Winding Rise (ΔΘᴡ⁄ᴀ,ʀ)');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HotSpotRise',		'50',			'K',        'Hot Spot Rise (ΔΘн,ᴀ)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TopOilRise',		'42.3',			'K',        'Tested Top Oil Rise (ΔΘᴛᴏ,ʀ)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'BottomOilRise',	    '27.3',			'K',        'Bottom Oil Rise (ΔΘʙᴏ,ʀ)');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'AvgOilRise',		'34.8',			 'K',       'Avg Oil Rise (ΔΘᴀᴏ,ʀ)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'RatedAmbient',	    '30',			'Celsius',  'Rated Ambient (Θᴀ,ʀ)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindingConductor',  '2',			'-',        'Winding Conductor (1=Aluminum, 2=Copper)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerUnitHSEddyLoss', '1',			'-',        'Per Unit Eddy Loss at Winding Hot Spot');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'WindTimeCst',		'10',			'min',       'Winding Time Constant (tw)');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerUnitHeighToHotSpot', '1',		'-',        'Per Unit Winding Height to Hot Spot');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MassCoreCoil',		'417776',		'pounds',   'Weight of Core and Coils');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MassTank',			'155426',		'pounds',   'Weight of Tank and Fittings');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'FluidType',		    {7},			'-',        'Fluid Type (1=min. oil, 2=silicone, 3=HTHC)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'GallonsOfFluid',	'21423',		'US Gal',   'Gallons of Fluid');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XfrmerRating',		'28000',		'kVA',      'Nameplate Ratings');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XfrmerCooling',	    'ONAN',		'-',        'Cooling Modes');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XfrmerCoolLevel',	 '0',		'%',            'Cooling Capacities');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'OverExcitation',	 '0',		'-',            'Over Excitation (0=no, 1=yes)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TimeOverExcitation', '0',		'hours',        'Time When Over Excitation Occurs (hour)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CoreLossesOverEx',	 '0',		'Watts',        'Core Loss During Over Excitatio');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TimeStep',			 '0.5',		'mi',           'Time increment for calculation.');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LoadLoss',			 '112600',	'Watts',        'Load Losses ');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerImpedance',		 '8.920',	'-',            'Winding Impedance');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerResistance',	     '0.432',	'-',            'Winding Resistance');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PerReactance',		 '8.910',	'-',            'Winding Reactance');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CumLossOfLife',	     '0',		'%',            'Cumulative LoL');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'ThermalCounter',	 '25',		'-',            'Number of Rating Iterations');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PUMinMUL',			    '0.24',		            '[1]', 'Minimum Load Multiplier');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'VintUnit',			    {5},		'Years',    'Vintage of Unit in Years');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'RatingGroup',		    '230',		'kV',       'kV Rating Group');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HotSpotDepth',		    '3.6',		'inches',   'Depth of hotspot below oil');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HotSpotMois',		    '1.11',		'%',        'Hot Spot Moisture Content');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PUMaxMUL',			    '2.20',		'[1]',      'Maximum Load Multiplier');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LoadType',			    '24-Hour Normal ', '-', 'Loading Scenario Name, ex.(Normal, Contingency)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'InsLifeExp',		    '65000',	'Hour',	    'Insulation Life Expectancy');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HotSpotLimit',		    '120',		'Celsius',  'Hot Spot Temperature Limit');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TopOilLimit',			'105',		'Celsius',  'Top Oil Temperature Limit');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LoLLimit',			    '24',		'Hour',	    'Loss of Life Rate Per Cycle Limit');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PULLimit',			    '1',		'[1]',      'Load Limit, p.u of Maximum Nameplate Rating');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'BubblingLimit',		    '143',		'degC',         'Bubbling Temperature Limit');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'OptimError',			'0.1',		'%',        'Hot Spot Temperature Limit Tolerance');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'BeginOverTime',		    '0',		'Hour',     'Begin Overload Time');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'EndOverTime',			'24',		'Hour', 'End Overload Time');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'GasContent',			'10',		'%', 'Content of Gas in Oil');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MoisContent',			'1.93',		'%', 'Insulation Moisture content at Hot Spot');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HSPressure',			'828',		'Mm/Hg', 'Threshold Pressure at Hot Spot ');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'AvgInsMois',			'1.850',	'%', 'Average Insulation Mositure Content');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HotSpotMoMUL',		    '0.6',		'-', 'Hot Spot Moisture Multiplier');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'OptimalLoad',			'40.17',	'MVA', 'Optimal Load');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LoLRate',				'0.04',		'%', 'LoL Rate Per Cycle');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'ActualLoad',			'22.4',		'MVA', 'Actual Load');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'enpStandard',			'IEEEG',	'-', 'Dynamic Loading Flag (0=inactive, 1=active)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'NominalLoad',			'37.33',	'MVA', 'Nominal Load');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'perCoolerInServ',		'100',		'%', 'Percentage of Total Coolers in Operation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CoolingStatus',		    'ON',		'-', 'Transformer Cooling Status');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'ActualLoading',		'24-Hour Normal ','-', 'Selected Loading loading');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'ActualCooling',		'100',		'%',	 'Selected Cooling Level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'ActualAmbient',		'0',		'Celsius', 'Selected Ambient Temperature');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MaximumAmbient',		'40',		'Celsius', 'Maximum Ambient Temperature');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'PowerFactor',			'90',		'MW/MVA', 'Load Power Factor');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'xlassreporting',		'-',		'-', 'Rating report configuration');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'Reactivfactor',		'44',		'MW/MVA', 'Reactive Factor');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'CaseID',				'1',		'-', 'Case Identification');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'moisPressure',		'-',		'-', 'Oil Pressure');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'moisWoilFactor',		'16.97',	'-', 'Oil Specific coefficient Woil');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'moisBFactor',			'3777',		'-', 'Oil Specific coefficient B');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'qNormalLife',			'65000',	'Hours', 'Normal Insulation Life');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'enp_paper_type',		{6}, '-',	 'Type of Paper');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'enp_iec_ref',			'110',		'Celsius', 'Reference IEC Temperature');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'enp_ieee_ref',		    '110',		'Celsius', 'Reference IEEE Temperature');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'num_fans',		    '12',		'-', 'Total number of fans');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'num_pumps',		'6',		'-', 'Total number of pumps');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'num_radiators',	'6',		'-', 'Total number of Radiators');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'num_coolers',		'3',		'-', 'Number of coolers');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'power_per_fan',	'5000',		'-', 'Cooling Power per fa');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'power_per_pump',	'8000',		'-', 'Cooling Power per pump');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'power_per_radiator', '2500',	'-', 'Cooling Power per radiator');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'power_cooler',		'2500',		'-', 'Power per cooler');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'AmbientOffset',		'0',		'K', 'Ambient Temperature Offset');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HRatedAmps',		 '489.5',	'Amps',	 'Rated current in the primary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XRatedAmps',		 '955 ',	'Amps',	 'Rated current in the secondary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TRatedAmps',		 '1575',	'Amps',	 'Rated current in the tertiary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HRatedVolt',		'180',		'kV', 'Rated voltage in the primary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XRatedVolt',		'250',		'kV', 'Rated voltage in the secondary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TRatedVolt',		'300',		'kV', 'Rated voltage in the tertiary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HRatedMVA',			'-1',		'kVA', 'Rated apparent power in the primary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XRatedMVA',			'-1',		'kVA', 'Rated apparent power in the secondary winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'TRatedMVA',			'-1',		'kVA', 'Rated apparent power in the tertiary winding');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HXRatedMVA',		 '-1',		'kVA', 'Cross Rated apparent power in HX winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HTRatedMVA',		 '-1',		'kVA', 'Cross Rated apparent power in HT winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XTRatedMVA',		 '-1',		'kVA', 'Cross Rated apparent power in XT winding');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HXLoadLoss',		 '-1',		'Watts', 'Load Losses in HX cross-winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HTLoadLoss',		 '-1',		'Watts', 'Load Losses in HT cross-winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'XTLoadLoss',		 '-1',		'Watts', 'Load Losses in XT cross-winding');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'opm_hydro_pressure',	'101.325',	'kPa',	 'Hydraulic Pressure in the Tank');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'opm_gas_content',		'10',		'%',	 'Gas Content in Tank');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmKrafta0', '0.3467',	'-',	 'Low Oxygen Parameter a0 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmKrafta1', '0.7223',	'-',     'Low Oxygen Parameter a1 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmKrafta2', '1.1687',	'-',     'Low Oxygen Parameter a2 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmKrafta0', '1.5167',	'-',     'Medium Oxygen Parameter a0 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmKrafta1', '3.6835',	'-',     'Medium Oxygen Parameter a1 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmKrafta2', '1.3592',	'-',     'Medium Oxygen Parameter a2 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmKrafta0', '2.5345',	'-',     'High Oxygen Parameter a0 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmKrafta1', '6.4215',	'-',     'High Oxygen Parameter a1 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmKrafta2', '1.5036',	'-',     'High Oxygen Parameter a2 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmTUKa0',    '0.3467',	'-',     'Oxygen Parameter a0 for TUK material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmTUKa1',    '0.3467',	'-',     'Oxygen Parameter a1 for TUK material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LowOxygenParmTUKa2',    '0.3467',	'-',     'Oxygen Parameter a2 for TUK material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmTUKa0',    '1.5167',	'-',     'Medium Oxygen Parameter a0 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmTUKa1',    '3.6835',	'-',     'Medium Oxygen Parameter a1 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'MedOxygenParmTUKa2',    '1.3592',	'-',     'Medium Oxygen Parameter a2 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmTUKa0',   '2.5345',	'-',     'High Oxygen Parameter a0 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmTUKa1',   '6.4215',	'-',     'High Oxygen Parameter a1 for Kraft material in LoL Calculation');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'HighOxygenParmTUKa2',   '1.5036',	'-',     'High Oxygen Parameter a2 for Kraft material in LoL Calculation');" +
                        /****Core and Coil *******/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_c2h2ppm',		'10',	'ppm', 'Acetylen gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_c2h2ppm',		'15',	'ppm', 'Acetylen gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_c2h2ppm',		'5',	'ppm', 'Acetylen gas alert level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_c2h4ppm',		'1000',	'ppm',    'Ethylen gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_c2h4ppm',		'1000',	'ppm',    'Ethylen gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_c2h4ppm',		'900',	'ppm',    'Ethylen gas alert level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_c2h6ppm',		'800',	'ppm',    'Ethane gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_c2h6ppm',		'700',	'ppm',    'Ethane gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_c2h6ppm',		'200',	'ppm',    'Ethane gas alert level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_ch4ppm',		'100',	'ppm',    'Methane gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_ch4ppm',		'200',	'ppm',    'Methane gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_ch4ppm',		'100',	'ppm',    'Methane gas alert level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_coppm',		'1200',	'ppm',    'Carbon monoxide gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_coppm',		'1400',	'ppm',    'Carbon monoxide gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_coppm',		'1000',	'ppm',    'Carbon monoxide gas alert level');" +
                        //
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_co2ppm',		'1300',	'ppm',    'Carbon dioxide gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_co2ppm',		'1200',	'ppm',    'Carbon dioxide gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_co2ppm',		'600',	'ppm',    'Carbon dioxide gas alert level');" +
                        //
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_norm_h2ppm',		'1400',	'ppm',    'Hydrogen gas normal level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_low_h2ppm',		'700',	'ppm',    'Hydrogen gas warning level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_real_high_h2ppm',		'500',	'ppm',    'Hydrogen gas alert level');" +
                        /**** IEC Gas Limits ****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_c2h2ppm',		    '0',	'ppm',    'IEC Acetylen gas  level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_c2h4ppm',		    '0',	'ppm',    'IEC Ethylen gas level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_c2h6ppm',		    '0',	'ppm',    'IEC Ethane gas level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_c3h6ppm',		    '0',	'ppm',    'IEC propane rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_ch4ppm',		    '0',	'ppm',    'IEC methane rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_coppm',		    '0',	'ppm',    'IEC carbon monoxide rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_co2ppm',		'0',	'ppm',    'IEC carbon dioxide rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_h2ppm',		'0',	'ppm',    'IEC hydrogen dioxide rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_lviec_tdcgppm',	'0',	'ppm',    'IEC Total combustible gas rate of change level');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_dga_frequency',		'0',	'ppm',    'Dissolved gas in oil analysis Frequency ');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'unp_fluid_type',		'0',	'ppm',    'Liquid insulation type');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'lab_test_results',		'1',	'-',    'Latest lab test results');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcTapRange',		    '10',	    'kV',        'Load Tap Range [±]');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcTapSteps',	        '10',        '-',        'Number of Tap Steps');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcRatedOilRise',       '35',	     'deg',      'Contact temperature rise over oil at rated current(ΔΘc,ʀ)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcLocation',	        'INTEGRATED','-',        'Location of the LTC (INTEGRATED/SEPARATED)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcWinding',		    'HV',	     '-',        'Winding with the adjustable tap (HV/LV)');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcCapacity',		    '10',	     'MVA',      'Load Tap Changer switching capacity');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcRatedTapPos',	    '5',	     '-',        'Load Tap Changer Rated Position');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcMinPos',		    '10',	     '-',      'Minimun Tap Changer Position');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'LtcMaxPos',	    '5',	     '-',        'Maximun Tap Changer Position');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'IsTapChanging',		    '0',	     '-',      'Whether or Not Tap Changer gets Evaluated');" +
                        /*****/
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'IsBushing',	    '0',	     '-',        'Whether or Not Bushing gets Evaluated ');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'GPSLatitude',		{8},		'deg',      'GPS Latitude');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'GPSLongitude',	    {9},	    'deg',      'GPS Longitude');" +
                        "INSERT into `DataDictionaries`(`SessionId`, `XfrmId`, `VarName`, `Value`, `Unit`,`Description`) VALUES ({0}, {1}, 'GPSAltitude',	    {10},		'deg',      'GPS Altitude');",
                        rxXfrm.sessionId, rxXfrm.XfrmID, rxXfrm.XType, rxXfrm.Age, rxXfrm.XfrmID, rxXfrm.XType, rxXfrm.SolidInsulation, rxXfrm.LiquidInsulation, rxXfrm.GPSLatitude, rxXfrm.GPSLongitude, rxXfrm.GPSAltitude);
            }
            catch (Exception ex)
            {
                Console.WriteLine("An error occurred while inserting data into DataDictionaries: " + ex.Message);
            }
        }

        public void CreateDefaultAssetAlarms(XfrmMap rxXfrm, string almName)
        {
            var actions_list = ActionEntries.Select(p => p.Component).Distinct().ToList();
            try
            {
                foreach (AssetCond condition in actions_list)
                {
                    var alarmName = string.Concat(almName, "-", condition);
                    for (int i = 0; i <= 24; i++)
                    {
                        Database.ExecuteSqlRaw("INSERT INTO `alarmentries`(`Eqsernum`,`AlarmName`,`TTF`,`Normal`,`Caution`,`Alert`,`Alarm`,`Emergency`) VALUES" +
                                                                            "({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7});", rxXfrm.XfrmID, alarmName, 0, 3.0, 5.0, 6.5, 8.5, 10);
                    }

                    Database.ExecuteSqlRaw("INSERT INTO `alarmconfigs`(`Eqsernum`,`IsActive`, `AlarmName`,`ThreshType`,`CollectorType`,`TargetType`,`StatisticType`) VALUES" +
                                           "({0}, {1}, {2}, {3}, {4}, {5}, {6});", rxXfrm.XfrmID, true, alarmName, "STATIC", "5", ((int)condition).ToString(), "AVERAGE");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating default asset alarms: {ex.ToString()}");
            }
            ;
        }

        /*
        # -------------------------------------------------#
        # DATA DICTIONARY AND DIAGNOSTICS METHODS          #
        # -------------------------------------------------#
        */
        public void SetEqpmtVar(string EquipId, string Varname, string Value)
        {
            var equiVar = Eqdictionaries.Where(p => p.Eqsernum == EquipId).FirstOrDefault(p => p.Varname == Varname);
            if (equiVar != null) equiVar.Value = Value;
            SaveChanges();
        }

        public string GetEqpmtVar(string EquipId, string Varname)
        {
            var equiVar = Eqdictionaries.Where(p => p.Eqsernum == EquipId).FirstOrDefault(p => p.Varname == Varname);
            return equiVar.Value;
        }

        public List<Eqdictionary> GetVarsGrp(string EquipId, string grpid)
        {
            return Eqdictionaries.Where(p => p.Eqsernum == EquipId).Where(p => p.Groupname == grpid).ToList();
        }

        public List<Eqdictionary> SetVarsGrp(string EquipId, string grpid)
        {
            return Eqdictionaries.Where(p => p.Eqsernum == EquipId).Where(p => p.Groupname == grpid).ToList();
        }

        public virtual void SetDictionary(string XfrmID, string p_varName, string p_varValue)
        {
            Database.ExecuteSqlRaw("UPDATE `DataDictionaries` SET `Value` = {0} WHERE `XfrmID`={1} AND `VarName`={2}", p_varValue, XfrmID, p_varName);
        }

        public virtual void RemoveProfile(ProfileItem profileItem)
        {
            Database.ExecuteSqlRaw("DELETE from `LoadProfiles` Where `xfrmId`={0} AND `profileName`={1}", profileItem.xfrmID, profileItem.profileName);
        }

        public virtual void RemoveDistribution(string XfrmID, string profileName)
        {
            Database.ExecuteSqlRaw("DELETE from `Distributions` Where `xfrmId`={0} AND `profileName`={1}", XfrmID, profileName);
        }

        public virtual void RemoveScenarios(string XfrmID, string ScenarioName)
        {
            Database.ExecuteSqlRaw("DELETE from `LoadingCases` Where `xfrmId`={0} AND `LoadType`={1}", XfrmID, ScenarioName);
        }



        public virtual void CreateAssetScoring(ObservableCollection<AssetRegistry> PreviewTemplates)
        {
            int nb_steps = 10;
            foreach (var assetVars in PreviewTemplates)
            {
                Enum.TryParse(assetVars.RegCat, out Asset regcat);
                if (!ScoreConds.Any(p => p.asset == regcat))
                {
                    var lowHighs = new List<LowHigh>
                    {
                        new LowHigh{ maintAction = MaintAction.INSPECT_AND_TESTING, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.3, 0.35), High = Utility.GenerateRandomArray(nb_steps, 0.37, 0.4)
                        },
                        new LowHigh{
                            maintAction = MaintAction.CONDITION_MONITORING, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.45, 0.49), High = Utility.GenerateRandomArray(nb_steps, 0.5, 0.55)
                        },
                        new LowHigh{
                            maintAction = MaintAction.ROUTINE_SERVICING, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.3, 0.35), High = Utility.GenerateRandomArray(nb_steps, 0.4, 0.45)
                        },
                        new LowHigh{
                            maintAction = MaintAction.MINIMUM_REPAIR, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.465, 0.5), High = Utility.GenerateRandomArray(nb_steps, 0.52, 0.6)
                        },
                        new LowHigh{
                            maintAction = MaintAction.REFURBISHMENT, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.85, 0.9), High = Utility.GenerateRandomArray(nb_steps, 0.9, 0.94)
                        },
                        new LowHigh{
                            maintAction = MaintAction.EM_REPLACEMENT, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.9, 0.92), High = Utility.GenerateRandomArray(nb_steps, 0.95, 1.0)
                        },
                        new LowHigh{
                            maintAction = MaintAction.CM_REPLACEMENT, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.65, 0.7), High = Utility.GenerateRandomArray(nb_steps, 0.73, 0.74)
                        },
                        new LowHigh{
                            maintAction = MaintAction.PM_REPLACEMENT, TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.65, 0.7), High = Utility.GenerateRandomArray(nb_steps, 0.7, 0.73)
                        },
                        new LowHigh{
                            maintAction = MaintAction.DISPOSAL,  TimeTs = Enumerable.Range(0, nb_steps).ToArray(),
                            Low = Utility.GenerateRandomArray(nb_steps, 0.95, 0.97), High = Utility.GenerateRandomArray(nb_steps, 0.98, 1.0)
                        },
                    };

                    var jCosts = new Dictionary<string, double>
                    {
                        { MaintAction.INSPECT_AND_TESTING.ToString(), 0.01 },
                        { MaintAction.CONDITION_MONITORING.ToString(), 0.02 },
                        { MaintAction.ROUTINE_SERVICING.ToString(), 0.025 },
                        { MaintAction.MINIMUM_REPAIR.ToString(), 0.1 },
                        { MaintAction.REFURBISHMENT.ToString(), 0.1 },
                        { MaintAction.EM_REPLACEMENT.ToString(), 0.3 },
                        { MaintAction.CM_REPLACEMENT.ToString(), 0.2 },
                        { MaintAction.PM_REPLACEMENT.ToString(), 0.2 },
                        { MaintAction.DISPOSAL.ToString(), 0.45 }
                    };

                    ScoreConds.Add(new ScoreAndCond
                    {
                        asset = regcat,
                        JConditions = JsonConvert.SerializeObject(lowHighs),
                        JCosts = JsonConvert.SerializeObject(jCosts),
                    });
                    SaveChanges();
                }
            }
            

        }
        
        public virtual void CreateXfrmRiskTemplate(ObservableCollection<AssetRegistry> PreviewTemplates)
        {
            using var context = new LoadingContext();
            /*----------------------------------*/
            /*      TEMPLATE STATE MODELS       */
            /*----------------------------------*/
            foreach (var assetVars in PreviewTemplates)
            {
                List<Signal> assetSignals = JsonConvert.DeserializeObject<List<Signal>>(assetVars.Signals);
                foreach (var signal in assetSignals)
                {
                    StateModels.Add(new StateModel
                    {
                        ToSimulate = true,
                        AssetId = assetVars.RegCat,
                        StateName = "StateTemplate",
                        VarName = signal.varname,
                        Value = "[0.01, 9.9]",
                        Description = signal.description,
                        Degradation = "Wiener[0.1, 1.3]",
                        scoreMin = "0.01",
                        scoreMax = "9.9",
                        alphaMin = "0.1",
                        alphaMax = "1.2",
                        betaMin = "0.1",
                        betaMax = "1.2",
                        sigmaMin = "0.1",
                        sigmaMax = "1.2",
                        GroupName = signal.groupname
                    });
                }
            }

        }


