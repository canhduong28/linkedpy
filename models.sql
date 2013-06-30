SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `linkedin_profiles` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
USE `linkedin_profiles` ;

-- -----------------------------------------------------
-- Table `linkedin_profiles`.`crawled_urls`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`crawled_urls` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `url` VARCHAR(250) NOT NULL ,
  PRIMARY KEY (`sno`) ,
  UNIQUE INDEX `url` (`url` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`crawler_urls`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`crawler_urls` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `main_url` VARCHAR(250) NOT NULL ,
  `found_urls` VARCHAR(250) CHARACTER SET 'utf8' COLLATE 'utf8_unicode_ci' NULL DEFAULT NULL ,
  `date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ,
  `stat` ENUM('C','W') NOT NULL DEFAULT 'W' ,
  PRIMARY KEY (`sno`) ,
  INDEX `main_url` (`main_url` ASC) ,
  INDEX `found_urls` (`found_urls` ASC) ,
  INDEX `stat` (`stat` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_education`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_education` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT(10) NOT NULL ,
  `date_start` DATE NULL ,
  `date_end` DATE NULL ,
  `degree` VARCHAR(250) NULL ,
  `organization` VARCHAR(250) NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) ,
  INDEX `degree` (`degree` ASC) ,
  INDEX `organization` (`organization` ASC) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_unicode_ci;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_experience`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_experience` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT(10) NOT NULL ,
  `title` VARCHAR(250) NULL DEFAULT NULL ,
  `date_start` DATE NULL DEFAULT NULL ,
  `date_end` DATE NULL DEFAULT NULL ,
  `organization` VARCHAR(250) NULL DEFAULT NULL ,
  `description` TEXT NULL DEFAULT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) ,
  INDEX `title` (`title` ASC) ,
  INDEX `organization` (`organization` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_profiles`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_profiles` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `crawled_urls_sno` INT(10) NOT NULL ,
  `profile_url` VARCHAR(200) NOT NULL ,
  `first_name` VARCHAR(250) NOT NULL ,
  `last_name` VARCHAR(250) NOT NULL ,
  `num_connection` VARCHAR(10) NOT NULL ,
  `country` VARCHAR(250) NOT NULL ,
  `title` VARCHAR(250) NULL ,
  `department` VARCHAR(250) NULL ,
  `locality` VARCHAR(250) NULL ,
  `region` VARCHAR(250) NULL ,
  `desc_short` TEXT NULL ,
  `profile_pic` VARCHAR(250) NULL DEFAULT NULL ,
  `recommendations` VARCHAR(10) NULL DEFAULT NULL ,
  `twitter_username` VARCHAR(250) NULL DEFAULT NULL ,
  `email` VARCHAR(250) NULL DEFAULT NULL ,
  `phone` VARCHAR(100) NULL DEFAULT NULL ,
  `address` VARCHAR(250) NULL ,
  `birthday` YEAR NULL ,
  `im` VARCHAR(250) NULL ,
  `marital_status` VARCHAR(45) NULL ,
  `profile_id` VARCHAR(200) NULL DEFAULT NULL ,
  `fb` VARCHAR(250) BINARY NOT NULL DEFAULT '0' ,
  `linkedin` VARCHAR(250) NULL DEFAULT NULL ,
  `fbid` INT(10) NOT NULL DEFAULT '0' ,
  `g+` VARCHAR(250) NULL DEFAULT NULL ,
  `quora` VARCHAR(250) NULL DEFAULT NULL ,
  `tagged` VARCHAR(250) NULL DEFAULT NULL ,
  `g` INT(10) NOT NULL DEFAULT '0' ,
  `twit` INT(10) NOT NULL DEFAULT '0' ,
  `typ` ENUM('LI','FB','G+','T') NOT NULL DEFAULT 'LI' ,
  `created` DATETIME NULL ,
  `updated` DATETIME NULL DEFAULT NULL ,
  INDEX `title` (`title` ASC) ,
  INDEX `first_name` (`first_name` ASC) ,
  INDEX `last_name` (`last_name` ASC) ,
  INDEX `locality` (`locality` ASC) ,
  INDEX `region` (`region` ASC) ,
  INDEX `country` (`country` ASC) ,
  INDEX `department` (`department` ASC) ,
  INDEX `fbid` (`fb` ASC, `g` ASC, `twit` ASC) ,
  PRIMARY KEY (`sno`, `twit`) ,
  UNIQUE INDEX `crawled_urls_sno_UNIQUE` (`crawled_urls_sno` ASC) ,
  UNIQUE INDEX `profile_url` (`profile_url` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_skills`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_skills` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT(10) NOT NULL ,
  `skill` VARCHAR(250) NOT NULL ,
  `no_endorsements` INT NULL ,
  `first_skill_ind` TINYINT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) ,
  INDEX `skill` (`skill` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_specialities`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_specialities` (
  `sno` INT(10) NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT(10) NOT NULL ,
  `specialty` VARCHAR(450) NOT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) ,
  INDEX `specialty` (`specialty` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_websites`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_websites` (
  `sno` INT NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT NOT NULL ,
  `website` VARCHAR(350) NOT NULL ,
  `cate` VARCHAR(45) NOT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_interests`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_interests` (
  `sno` INT NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT NOT NULL ,
  `interest` VARCHAR(250) NOT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_groups`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_groups` (
  `sno` INT NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT NOT NULL ,
  `group_url` VARCHAR(250) NOT NULL ,
  `organization` VARCHAR(250) NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) )
ENGINE = MyISAM;


-- -----------------------------------------------------
-- Table `linkedin_profiles`.`linkedin_honors`
-- -----------------------------------------------------
CREATE  TABLE IF NOT EXISTS `linkedin_profiles`.`linkedin_honors` (
  `sno` INT NOT NULL AUTO_INCREMENT ,
  `profile_sno` INT NOT NULL ,
  `honor` VARCHAR(300) NOT NULL ,
  PRIMARY KEY (`sno`) ,
  INDEX `profile_sno` (`profile_sno` ASC) )
ENGINE = MyISAM;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
