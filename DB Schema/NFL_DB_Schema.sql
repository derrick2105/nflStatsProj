--
-- Table structure for table `ByeWeeks`
--
DROP TABLE IF EXISTS `ByeWeeks`;

CREATE TABLE `ByeWeeks` (
  `seasonId` int(10) unsigned NOT NULL,
  `teamId` varchar(3) NOT NULL,
  PRIMARY KEY (`seasonId`,`teamId`),
  KEY `fk_ByeWeeks_2_idx` (`teamId`),
  CONSTRAINT `fk_ByeWeeks_1` FOREIGN KEY (`seasonId`) REFERENCES `Season` (`seasonID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ByeWeeks_2` FOREIGN KEY (`teamId`) REFERENCES `Teams` (`teamId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `GameConditions`
--
DROP TABLE IF EXISTS `GameConditions`;

CREATE TABLE `GameConditions` (
  `gameId` int(10) unsigned NOT NULL DEFAULT '0',
  `locationId` int(10) unsigned NOT NULL,
  `lowTemp` int(10) NOT NULL,
  `highTemp` int(10) NOT NULL,
  `isDome` int(10) NOT NULL,
  `forecast` varchar(15) DEFAULT NULL,
  `windSpeed` int(10) DEFAULT NULL,
  `turf` varchar(45) NOT NULL,
  PRIMARY KEY (`gameId`,`locationId`),
  KEY `fk_GameConditions_2_idx` (`locationId`),
  KEY `fk_GameConditions_3_idx` (`turf`),
  CONSTRAINT `fk_GameConditions_1` FOREIGN KEY (`gameId`) REFERENCES `Season` (`seasonID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_GameConditions_2` FOREIGN KEY (`locationId`) REFERENCES `TeamLocations` (`locationId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_GameConditions_3` FOREIGN KEY (`turf`) REFERENCES `TurfTypes` (`turf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `Games`
--
DROP TABLE IF EXISTS `Games`;

CREATE TABLE `Games` (
  `seasonID` int(10) unsigned NOT NULL,
  `homeTeam` varchar(3) NOT NULL DEFAULT '',
  `awayTeam` varchar(3) NOT NULL DEFAULT '',
  `locationId` int(10) unsigned DEFAULT NULL,
  `gameTime` time DEFAULT NULL,
  PRIMARY KEY (`seasonID`,`homeTeam`,`awayTeam`),
  KEY `homeTeam` (`homeTeam`),
  KEY `awayTeam` (`awayTeam`),
  KEY `Games_ibfk_4` (`locationId`),
  CONSTRAINT `Games_ibfk_1` FOREIGN KEY (`homeTeam`) REFERENCES `Teams` (`teamId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_2` FOREIGN KEY (`awayTeam`) REFERENCES `Teams` (`teamId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_3` FOREIGN KEY (`seasonID`) REFERENCES `Season` (`seasonID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_4` FOREIGN KEY (`locationId`) REFERENCES `TeamLocations` (`locationId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `InjuryReport`
--
DROP TABLE IF EXISTS `InjuryReport`;

CREATE TABLE `InjuryReport` (
  `playerId` int(10) unsigned NOT NULL DEFAULT '0',
  `injurySeverity` varchar(20) NOT NULL,
  PRIMARY KEY (`playerId`),
  CONSTRAINT `fk_InjuryReport_1` FOREIGN KEY (`playerId`) REFERENCES `Players` (`playerId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `PlayerStats`
--
DROP TABLE IF EXISTS `PlayerStats`;

CREATE TABLE `PlayerStats` (
  `playerId` int(10) unsigned NOT NULL DEFAULT '0',
  `statId` int(10) unsigned NOT NULL DEFAULT '0',
  `seasonID` int(10) unsigned NOT NULL DEFAULT '0',
  `statValue` decimal(5,2) NOT NULL DEFAULT '0.00',
  PRIMARY KEY (`playerId`,`statId`,`seasonID`),
  KEY `fk_PlayerStats_2` (`statId`),
  KEY `fk_PlayerStats_3` (`seasonID`),
  CONSTRAINT `fk_PlayerStats_1` FOREIGN KEY (`playerId`) REFERENCES `Players` (`playerId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_PlayerStats_2` FOREIGN KEY (`statId`) REFERENCES `Statistics` (`statId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_PlayerStats_3` FOREIGN KEY (`seasonID`) REFERENCES `Season` (`seasonID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 DELAY_KEY_WRITE=1;

--
-- Table structure for table `PlayerTeam`
--
DROP TABLE IF EXISTS `PlayerTeam`;

CREATE TABLE `PlayerTeam` (
  `playerId` int(10) unsigned NOT NULL DEFAULT '0',
  `teamId` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`playerId`),
  CONSTRAINT `fk_PlayerTeam_1` FOREIGN KEY (`playerId`) REFERENCES `Players` (`playerId`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `Players`
--
DROP TABLE IF EXISTS `Players`;

CREATE TABLE `Players` (
  `playerId` int(10) unsigned NOT NULL,
  `firstName` varchar(30) NOT NULL,
  `lastName` varchar(30) NOT NULL,
  `position` varchar(3) NOT NULL,
  PRIMARY KEY (`playerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `Season`
--
DROP TABLE IF EXISTS `Season`;

CREATE TABLE `Season` (
  `seasonID` int(10) unsigned NOT NULL,
  `week` tinyint(4) NOT NULL,
  `seasonYear` year(4) NOT NULL,
  PRIMARY KEY (`seasonID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `Statistics`
--
DROP TABLE IF EXISTS `Statistics`;

CREATE TABLE `Statistics` (
  `statId` int(10) unsigned NOT NULL,
  `stat_name` varchar(50) NOT NULL,
  PRIMARY KEY (`statId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `TeamLocations`
--
DROP TABLE IF EXISTS `TeamLocations`;

CREATE TABLE `TeamLocations` (
  `locationId` int(10) unsigned NOT NULL,
  `teamId` varchar(3) NOT NULL,
  `Stadium` varchar(45) NOT NULL DEFAULT 'Null',
  `turf` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`locationId`,`teamId`,`Stadium`),
  KEY `fk_teamLocations_1_idx` (`teamId`),
  KEY `fk_TeamLocations_2_idx` (`turf`),
  CONSTRAINT `fk_TeamLocations_1` FOREIGN KEY (`teamId`) REFERENCES `Teams` (`teamId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_TeamLocations_2` FOREIGN KEY (`turf`) REFERENCES `TurfTypes` (`turf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `Teams`
--
DROP TABLE IF EXISTS `Teams`;

CREATE TABLE `Teams` (
  `teamId` varchar(3) NOT NULL,
  `name` varchar(30) NOT NULL,
  `teamNumber` int(3) unsigned NOT NULL,
  PRIMARY KEY (`teamId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `TurfTypes`
--
DROP TABLE IF EXISTS `TurfTypes`;

CREATE TABLE `TurfTypes` (
  `turfId` int(11) NOT NULL AUTO_INCREMENT,
  `turf` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`turfId`),
  KEY `index2` (`turf`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;

