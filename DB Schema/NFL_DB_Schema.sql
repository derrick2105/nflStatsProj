-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema NFLStats1
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema NFLStats1
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `NFLStats1` DEFAULT CHARACTER SET utf8 ;
USE `NFLStats1` ;

-- -----------------------------------------------------
-- Table `NFLStats1`.`GameConditions`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`GameConditions` (
  `locationId` INT(10) UNSIGNED NOT NULL COMMENT '',
  `lowTemp` TINYINT(3) NOT NULL COMMENT '',
  `highTemp` TINYINT(3) NOT NULL COMMENT '',
  `isDome` TINYINT(1) NOT NULL COMMENT '',
  `forecast` VARCHAR(15) NOT NULL COMMENT '',
  `windSpeed` TINYINT(3) NOT NULL COMMENT '',
  `turf` VARCHAR(45) NOT NULL COMMENT '',
  PRIMARY KEY (`locationId`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`Teams`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`Teams` (
  `teamId` VARCHAR(3) NOT NULL COMMENT '',
  `name` VARCHAR(30) NOT NULL COMMENT '',
  PRIMARY KEY (`teamId`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`Season`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`Season` (
  `seasonID` INT(10) UNSIGNED NOT NULL COMMENT '',
  `week` TINYINT(4) NOT NULL COMMENT '',
  `year` YEAR NOT NULL COMMENT '',
  PRIMARY KEY (`seasonID`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`Games`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`Games` (
  `seasonID` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `homeTeam` VARCHAR(3) NOT NULL DEFAULT '' COMMENT '',
  `awayTeam` VARCHAR(3) NOT NULL DEFAULT '' COMMENT '',
  `locationId` INT(10) UNSIGNED NULL DEFAULT NULL COMMENT '',
  `gameTime` TIME NULL DEFAULT NULL COMMENT '',
  PRIMARY KEY (`seasonID`, `homeTeam`, `awayTeam`)  COMMENT '',
  INDEX `homeTeam` (`homeTeam` ASC)  COMMENT '',
  INDEX `awayTeam` (`awayTeam` ASC)  COMMENT '',
  INDEX `Games_ibfk_4` (`locationId` ASC)  COMMENT '',
  CONSTRAINT `Games_ibfk_4`
    FOREIGN KEY (`locationId`)
    REFERENCES `NFLStats1`.`GameConditions` (`locationId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_1`
    FOREIGN KEY (`homeTeam`)
    REFERENCES `NFLStats1`.`Teams` (`teamId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_2`
    FOREIGN KEY (`awayTeam`)
    REFERENCES `NFLStats1`.`Teams` (`teamId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `Games_ibfk_3`
    FOREIGN KEY (`seasonID`)
    REFERENCES `NFLStats1`.`Season` (`seasonID`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`Players`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`Players` (
  `playerId` INT(10) UNSIGNED NOT NULL COMMENT '',
  `firstName` VARCHAR(30) NOT NULL COMMENT '',
  `lastName` VARCHAR(30) NOT NULL COMMENT '',
  `position` VARCHAR(3) NOT NULL COMMENT '',
  PRIMARY KEY (`playerId`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`InjuryReport`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`InjuryReport` (
  `playerId` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `injurySeverity` VARCHAR(20) NOT NULL COMMENT '',
  PRIMARY KEY (`playerId`)  COMMENT '',
  CONSTRAINT `fk_InjuryReport_1`
    FOREIGN KEY (`playerId`)
    REFERENCES `NFLStats1`.`Players` (`playerId`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`PlayerStats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`PlayerStats` (
  `playerId` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `statId` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `seasonID` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `statValue` DECIMAL(11,0) NOT NULL DEFAULT '0' COMMENT '',
  PRIMARY KEY (`playerId`, `statId`, `seasonID`)  COMMENT '',
  INDEX `statId` (`statId` ASC)  COMMENT '',
  INDEX `seasonID` (`seasonID` ASC)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
DELAY_KEY_WRITE = 1;


-- -----------------------------------------------------
-- Table `NFLStats1`.`PlayerTeam`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`PlayerTeam` (
  `playerId` INT(10) UNSIGNED NULL DEFAULT NULL COMMENT '',
  `teamId` VARCHAR(3) NULL DEFAULT NULL COMMENT '',
  INDEX `playerId` (`playerId` ASC)  COMMENT '',
  INDEX `teamId` (`teamId` ASC)  COMMENT '',
  CONSTRAINT `PlayerTeam_ibfk_1`
    FOREIGN KEY (`playerId`)
    REFERENCES `NFLStats1`.`Players` (`playerId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `PlayerTeam_ibfk_2`
    FOREIGN KEY (`teamId`)
    REFERENCES `NFLStats1`.`Teams` (`teamId`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`Statistics`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`Statistics` (
  `statId` INT(10) UNSIGNED NOT NULL COMMENT '',
  `name` VARCHAR(50) NOT NULL COMMENT '',
  PRIMARY KEY (`statId`)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `NFLStats1`.`TeamLocations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `NFLStats1`.`TeamLocations` (
  `locationId` INT(10) UNSIGNED NOT NULL DEFAULT '0' COMMENT '',
  `teamId` VARCHAR(3) NOT NULL DEFAULT 'Nul' COMMENT '',
  `Stadium` VARCHAR(45) NOT NULL DEFAULT 'Null' COMMENT '',
  PRIMARY KEY (`locationId`)  COMMENT '',
  UNIQUE INDEX `Stadium_UNIQUE` (`Stadium` ASC)  COMMENT '',
  INDEX `fk_teamLocations_1_idx` (`teamId` ASC)  COMMENT '',
  CONSTRAINT `fk_teamLocations_1`
    FOREIGN KEY (`teamId`)
    REFERENCES `NFLStats1`.`Teams` (`teamId`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
