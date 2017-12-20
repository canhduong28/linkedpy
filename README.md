linkedpy
========

Scrapy spider to crawl LinkedIn public data

LinkedIn Crawler

Configuration Guide
===================
There are some configurations might be defined before starting to run LinkedIn Crawler.

(After importing models.sql into MySQL Database)

linkedpy//configs.py

    MySQLConfigs:
        - parameters for connecting to MySQL Database

    CountryCode:
        - parameters for mapping country's name and country code

    LinkedInAccount:
        - class for storing some valid LinkedIn accounts
            (currently, it contains three accounts)

        - Running with logging in a long time, those accounts might be forbidden a mount of time. To continue, It needs to add one ore valid account(s).

        (Do not remove forbidden accounts. they will be valid after times, so they are still useful on another running time.)


Usage Guide
=============

* The working directory is now linkedin_crawler

Syntax: scrapy crawl linkedin

There are two parameters might be added to custom execution

 -a mode=update => Running in update mode

 -a login=True  => Running with logging in requirement
    (For short syntax: T can be instead of True)

    * Both of them are added concurrently


Examples
=============

1. Running normally without logging in and update

        scrapy crawl linkedin

2. Running with update mode

        scrapy crawl linkedin -a mode=update

3. Running with with logging in requirement

        scrapy crawl linkedin -a login=True
    or
        scrapy crawl linkedin -a login=T

4. Running with with both logging in requirement and update

        scrapy crawl linkedin -a mode=update -a login=True
    or
        scrapy crawl linkedin -a mode=update -a login=T

!!! Be careful with whitespaces

To stop running: press Ctrl + C twice

Written by Canh Duong 2012 (contact: canhdn91@gmail.com)
