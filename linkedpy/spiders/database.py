#!/usr/bin/python
import sys
import re
import MySQLdb
import MySQLdb.cursors

try:
   import queue
except ImportError:
   import Queue as queue
import random
from datetime import datetime
from scrapy import log
import time
from linkedpy.configs import MySQLConfigs
from linkedpy.items import Profile, URL

# class to communicate with MySQL database
class Database(object):

    def __init__(self):
       self.conn = None
       self.offset  = 0

    # settting a connection to MySQL database
    def connect(self):
       try:
           self.conn = MySQLdb.connect(
                  host=MySQLConfigs.host,
                  user=MySQLConfigs.username,
                  passwd=MySQLConfigs.password,
                  db=MySQLConfigs.database,
                  cursorclass=MySQLdb.cursors.DictCursor,
                  charset='utf8',
                  use_unicode=True
                  )
       except MySQLdb.Error, e:
           print "Error %d: %s" % (e.args[0], e.args[1])
           sys.exit()

    # Obtaining cursor and reconnect if needs
    def cursor(self):
       try:
           self.conn.ping(True)
           return self.conn.cursor()
       except (AttributeError, MySQLdb.OperationalError):
           # raise MySQLdb.Error
           self.connect()
           return self.conn.cursor()

    # Selecting available URLs to request
    def feed(self, mode):
       random = True 
       urls = []
       if mode == 'update':
           status = 'C' # visited URLs need to be updated
       else:
           status = 'W' # unvisited URLs  
       limit = 20
       cursor = self.cursor()
       while True:
           if random:
               cursor.execute('select found_urls from crawler_urls use index(stat) where stat = %s order by rand() limit %s , %s', (status, self.offset, limit))
           else:
               cursor.execute('select found_urls from crawler_urls use index(stat) where stat = %s limit %s , %s', (status, self.offset, limit))

           rows = cursor.fetchall()
           if rows:
               urls = [row['found_urls'] for row in rows]
               self.offset += len(urls)
               return urls
           else:
               # Check having available URLs
               cursor.execute('select count(*) as quantity from crawler_urls use index(stat) where stat = %s', (status))
               rows = cursor.fetchone()
               if rows['quantity'] == 0:
                   return -1
               else:
                   self.offset = 0
                   continue

    # Inserting new URLs and update status of visited URLs on crawler_urls
    def insert_urls(self, items):
        cursor = self.cursor()
        for item in items:
            if item['found_urls'] == '$':
                cursor.execute("update crawler_urls use index(found_urls) set stat = 'C' where found_urls = %s limit 1", (item['main_url'], ))
                cursor.execute('commit')
            else:    
                cursor.execute("select sno, stat from crawler_urls use index(found_urls) where found_urls = %s limit 1", (item['found_urls'], ))
                result = cursor.fetchone()

                if not result: # existed in crawler_urls
                    cursor.execute("insert into crawler_urls (main_url, found_urls) values (%s, %s)", (item['main_url'], item['found_urls']))
                    log.msg(" - [W] %s" % item['found_urls'], level=log.DEBUG)
        cursor.execute('commit')

    # Converting string to datetime
    def string_to_date(self, data):
        # July 2005
        # 2010
        try:
            data = data.replace('Julai', 'July', 1)
            if data:
                if re.search(r'[a-z]+', data):
                    return datetime.strptime(data.encode('ascii', 'ignore'),"%B %Y")
                else:
                    return datetime.strptime(data.encode('ascii', 'ignore'),"%Y")
            else:
                return data
        except:
            return None

    # Inserting profiles into linkedin_profiles 
    def insert_profile(self, item):
        cursor = self.cursor()

        # udpate crawled_url
        cursor.execute('select sno from crawled_urls use index(url) where url = %s limit 1', (item['profile_url']))
        result = cursor.fetchone()
        if result:
            crawled_urls_sno = result['sno']
        else:
            cursor.execute("insert into crawled_urls (url) values (%s)", (item['profile_url']))
            log.msg(" - [P] %s" % item['profile_url'], level=log.DEBUG)
            crawled_urls_sno = cursor.lastrowid

        cursor.execute('select sno from linkedin_profiles use index(profile_url) where profile_url = %s limit 1', (item['profile_url']))
        result = cursor.fetchone()
        if not result:

            cursor.execute(\
                    "insert into linkedin_profiles (crawled_urls_sno, profile_url, title, first_name, last_name, locality, region,\
                    country, desc_short, profile_pic, num_connection, email, phone, twitter_username, department, recommendations,\
                    im, address, birthday, marital_status, created)\
                    values (%s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)",
                    (
                        crawled_urls_sno, item.get('profile_url'), item.get('title'),
                        item.get('first_name'), item.get('last_name'), item.get('locality'),
                        item.get('region'), item.get('country'), item.get('desc_short'),
                        item.get('profile_pic'), item.get('num_connection'), item.get('email'),
                        item.get('phone'), item.get('twitter_username'), item.get('department'),
                        item.get('recomandations'),
                        item.get('im'), item.get('address'), item.get('birthday'),
                        item.get('marital_status'),
                        datetime.now() 
                    )
                )

            profile_sno = cursor.lastrowid

            # education
            for edu in item['education']:
                cursor.execute(\
                        'insert into linkedin_education (profile_sno, date_start, date_end, degree, organization)\
                        values (%s,%s,%s,%s,%s)',
                        (
                            profile_sno, self.string_to_date(edu.get('date_start')), self.string_to_date(edu.get('date_end')),
                            edu.get('degree'), edu.get('organization')
                        )
                    )

            # experience
            for exp in item['experience']:
                cursor.execute(\
                        'insert into linkedin_experience (profile_sno, date_start, date_end, title, organization, description)\
                        values (%s,%s,%s,%s,%s, %s)',
                        (
                            profile_sno, self.string_to_date(exp.get('date_start')), self.string_to_date(exp.get('date_end')),
                            exp.get('title'), exp.get('organization'), exp.get('description')
                        )
                    )
            # skills
            for ski in item['skills']:
                cursor.execute(\
                        'insert into linkedin_skills (profile_sno, skill, no_endorsements, first_skill_ind)\
                        values (%s,%s, %s, %s)',
                        (
                            profile_sno,
                            ski.get('skill'),
                            ski.get('no_endorsements'),
                            ski.get('first_skill_ind'),
                        )
                    )
            # specialties
            for spe in item['specialties']:
                cursor.execute(\
                        'insert into linkedin_specialities (profile_sno, specialty)\
                        values (%s,%s)',
                        (
                            profile_sno,
                            spe.get('specialty', None)
                        )
                    )

            # websites
            for w in item['websites']:
                cursor.execute(\
                        'insert into linkedin_websites (profile_sno, website, cate)\
                        values (%s, %s, %s)',
                        (
                            profile_sno,
                            w.get('website'),
                            w.get('cate')
                        )
                    )
            # interests
            for w in item['interests']:
                cursor.execute(\
                        'insert into linkedin_interests (profile_sno, interest)\
                        values (%s,%s)',
                        (
                            profile_sno,
                            w.get('interest')
                        )
                    )
            # groups
            for w in item['groups']:
                cursor.execute(\
                        'insert into linkedin_groups (profile_sno, group_url, organization)\
                        values (%s,%s,%s)',
                        (
                            profile_sno,
                            w.get('group_url'),
                            w.get('organization')
                        )
                    )
            # honors
            for w in item['honors']:
                cursor.execute(\
                        'insert into linkedin_honors (profile_sno, honor)\
                        values (%s,%s)',
                        (
                            profile_sno,
                            w.get('honor'),
                        )
                    )
            cursor.execute('commit')
            log.msg(" - [Added] profile: %s" % item['profile_url'], level=log.INFO)

        # update crawled_urls
        cursor.execute(\
                'update crawler_urls use index(found_urls) set stat= %s where found_urls = %s limit 1',
                ('C', item['profile_url'])
        )
        log.msg(" - [W->C] %s" % item['profile_url'], level=log.DEBUG)

    # update profiles on linkedin_profiles
    def update_profile(self, item):
        #print item
        cursor = self.cursor()

        cursor.execute('select sno from linkedin_profiles use index(profile_url) where profile_url = %s limit 1', (item['profile_url']))
        result = cursor.fetchone()
        if not result:
            #print "insert mode"
            return self.insert_profile(item)
        profile_sno = result['sno']
        # Updating
        sql = 'update linkedin_profiles set '
        for key in item.keys():
            if isinstance(item[key], list):
                continue
            sql += '%s = "%s", ' %( key, item[key])
        #sql = sql[:len(sql) -2]

        sql += ' updated = "%s"' % datetime.now() 
        
        sql += ' where sno = %s limit 1' % profile_sno
        MySQLdb.escape_string(sql)

        cursor.execute(sql)
        cursor.execute('commit')

        # education
        cursor.execute('delete from linkedin_education where profile_sno = %s', profile_sno)
        for edu in item['education']:
            cursor.execute(\
                    'insert into linkedin_education (profile_sno, date_start, date_end, degree, organization)\
                    values (%s,%s,%s,%s,%s)',
                    (
                        profile_sno, self.string_to_date(edu.get('date_start')), self.string_to_date(edu.get('date_end')),
                        edu.get('degree'), edu.get('organization')
                    )
                )

        # experience
        cursor.execute('delete from linkedin_experience where profile_sno = %s', profile_sno)
        for exp in item['experience']:
            cursor.execute(\
                    'insert into linkedin_experience (profile_sno, date_start, date_end, title, organization, description)\
                    values (%s,%s,%s,%s,%s, %s)',
                    (
                        profile_sno, self.string_to_date(exp.get('date_start')), self.string_to_date(exp.get('date_end')),
                        exp.get('title'), exp.get('organization'), exp.get('description')
                    )
                )
        # skills
        cursor.execute('delete from linkedin_skills where profile_sno = %s', profile_sno)
        for ski in item['skills']:
            cursor.execute(\
                    'insert into linkedin_skills (profile_sno, skill, no_endorsements, first_skill_ind)\
                    values (%s,%s, %s, %s)',
                    (
                        profile_sno,
                        ski.get('skill'),
                        ski.get('no_endorsements'),
                        ski.get('first_skill_ind'),
                    )
                )
        # specialties
        cursor.execute('delete from linkedin_specialities where profile_sno = %s', profile_sno)
        for spe in item['specialties']:
            cursor.execute(\
                    'insert into linkedin_specialities (profile_sno, specialty)\
                    values (%s,%s)',
                    (
                        profile_sno,
                        spe.get('specialty', None)
                    )
                )
        # websites
        cursor.execute('delete from linkedin_websites where profile_sno = %s', profile_sno)
        for w in item['websites']:
            cursor.execute(\
                    'insert into linkedin_websites (profile_sno, website, cate)\
                    values (%s,%s, %s)',
                    (
                        profile_sno,
                        w.get('website'),
                        w.get('cate')
                    )
                )
        # interests
        cursor.execute('delete from linkedin_interests where profile_sno = %s', profile_sno)
        for w in item['interests']:
            cursor.execute(\
                    'insert into linkedin_interests (profile_sno, interest)\
                    values (%s,%s)',
                    (
                        profile_sno,
                        w.get('interest')
                    )
                )
        # groups
        cursor.execute('delete from linkedin_groups where profile_sno = %s', profile_sno)
        for w in item['groups']:
            cursor.execute(\
                    'insert into linkedin_groups (profile_sno, group_url, organization)\
                    values (%s,%s,%s)',
                    (
                        profile_sno,
                        w.get('group_url'),
                        w.get('organization')
                    )
                )
        # honors
        cursor.execute('delete from linkedin_honors where profile_sno = %s', profile_sno)
        for w in item['honors']:
            cursor.execute(\
                    'insert into linkedin_honors (profile_sno, honor)\
                    values (%s,%s)',
                    (
                        profile_sno,
                        w.get('honor'),
                    )
                )

        cursor.execute('commit')           
        log.msg(" - [Updated] profile: %s" % item['profile_url'], level=log.INFO)

        log.msg(" - [Updated] crawled_urls: %s" % item['profile_url'], level=log.DEBUG)
