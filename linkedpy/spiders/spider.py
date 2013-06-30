# encoding=utf-8
import re
import time
from datetime import datetime
import Queue
from threading import Thread
from database import Database

from scrapy import log
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule
from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.http import FormRequest
from linkedpy.items import URL, Profile, Experience, Education, Skill, Specialty, Website, Group, Interest, Honor
from linkedpy.configs import CountryCode, LinkedInAccount

# clean up URLs 
def clean_url(url):
    return re.sub(r'\?.+$', '', url)

# Base Class for requesting URLs and passing response to others 
class LinkedPySpider(BaseSpider):
    name = 'linkedin'
    q = Queue.Queue()
    db = Database()
    logged = False
    mode = 'init'
    login=False
    handle_httpstatus_list = ['403',]

    # Initialize spider and set mode
    def __init__(self, mode='init', login=False):
        if mode:
            self.mode = mode
        if login:
            self.login = True
            self.acc = LinkedInAccount()

        self.base_url = 'http://' + CountryCode.code + '.linkedin.com'
        self.allowed_domains = ['www.linkedin.com', CountryCode.code + '.linkedin.com']

        self.deny_re = r''
        for char in CountryCode.code:
            self.deny_re += r'[^' + char + r']+'
        self.deny_re = r'http://+' + self.deny_re + r'\.linkedin\.com'

    # First requests
    def start_requests(self):
        yield Request(self.base_url, callback=self.run_before_login, meta = {'dont_merge_cookies': True})
        if self.login:
            yield Request('https://www.linkedin.com/uas/login', dont_filter = True, callback=self.parse_login, errback=self.err_back)

    def run_before_login(self, response):
        if self.mode == 'init':
            self.my_parse(response)
        if not self.login:
            return self.run()

    # login simulation request 
    def parse_login(self, response):
        account = self.acc.get()
        print account
        request = FormRequest.from_response(response,
                formname = 'login',
                formdata={'session_key': account['key'], 'session_password': account['password']},
                callback=self.check_login, errback=self.err_back)
        yield request

    def err_back(self, response):
        log.msg("Login failed, Try another account!!!", level=log.ERROR)

        self.logged = False
        #return Request('https://www.linkedin.com/uas/login', dont_filter = True, callback=self.parse_login)
        
    # check if login successfully 
    def check_login(self, response):
        # check login succeed before going on
        if "logout" in response.body:
            log.msg("Login successful!!!", level=log.INFO)
            self.logged = True
            return self.run()

    # change country code into www
    def www_domain(self, url):
        pub_re = [r'/pub/[a-z\-]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+',
                  r'/in/[a-z0-9]+'
                 ]
        for pub in pub_re:
            if re.search(pub, url):
                    return url.replace(CountryCode.code, 'www', 1)
        return url

    def post_err_back(self, response):
        log.msg("430 Forbidden, Try another account!!!", level=log.ERROR)
        self.logged = False
        return self.run()
    
    # main loop for running request concurrently. Obtaining URLs from Database instance
    def run(self):
        flag = False
        while True:
            try:
                if not self.q.empty():
                        if self.login and not self.logged:
                            yield Request('https://www.linkedin.com/uas/login', dont_filter = True, callback=self.parse_login)
                            break
                        else:
                            url = self.q.get()
                            url = self.www_domain(url)
                            yield Request(url, dont_filter = False, callback=self.my_parse, errback=self.post_err_back)
                else:
                    flag = True

                if flag:
                    urls = self.db.feed(self.mode)
                    if urls == -1:
                        log.msg('No work available yet, Mission completed...', level=log.INFO)
                        break
                    else:
                        for url in urls:
                            self.q.put(url)
                        flag = False
                time.sleep(0.5)
            except (KeyboardInterrupt):
                break

    # Parsing new URLs and passing to extract html if needs
    def my_parse(self, response):

        log.msg('Parsing urls from %s' % response.url, level=log.INFO)

        # http://my.linkedin.com/directory/people/a.html
        lx1 = SgmlLinkExtractor(
                allow= '(' + self.base_url + ')?' + r'/directory/people/([a-z]|\@)\.html',
                deny=(self.deny_re),
              )
        # http://my.linkedin.com/directory/people/my/A1.html
        lx2 = SgmlLinkExtractor(
                allow= '('+ self.base_url + ')?' + r'/directory/people/my/[A-Z]\d+\.html',
                deny=(self.deny_re),
                )
        # http://my.linkedin.com/directory/people/my/ahamid-3.html
        # http://my.linkedin.com/directory/people/my/aan.html
        lx3 = SgmlLinkExtractor(
                allow= '(' + self.base_url + ')?' + r'/directory/people/my/[a-z]+(\-\d+)?\.html',
                deny=(self.deny_re),
                )
        # http://my.linkedin.com/pub/zarita-a-baharum/23/9a2/756
        lx4 = SgmlLinkExtractor(
                allow= '(' + self.base_url +')?' + r'/pub/[a-z\-]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+',
                deny=(self.deny_re),
                )
        # http://www.linkedin.com/in/levananh
        lx5 = SgmlLinkExtractor(
                allow= '(' + self.base_url + ')?' + r'/in/[a-z0-9]+$',
                deny=(self.deny_re),
                )

        try:
            l1 = lx1._extract_links(response.body, response.url, 'utf-8')
            l1 = lx1._process_links(l1)

            l2 = lx2._extract_links(response.body, response.url, 'utf-8')
            l2 = lx2._process_links(l2)

            l3 = lx3._extract_links(response.body, response.url, 'utf-8')
            l3 = lx3._process_links(l3)

            l4 = lx4._extract_links(response.body, response.url, 'utf-8')
            l4 = lx4._process_links(l4)

            l5 = lx5._extract_links(response.body, response.url, 'utf-8')
            l5 = lx5._process_links(l5)

            links = [URL(main_url = response.url, found_urls = l1[i].url) for i in range(len(l1))]
            links.extend([URL(main_url = response.url, found_urls = l2[i].url) for i in range(len(l2))])
            links.extend([URL(main_url = response.url, found_urls = l3[i].url) for i in range(len(l3))])
            links.extend([URL(main_url = response.url, found_urls = clean_url(l4[i].url)) for i in range(len(l4))])
            links.extend([URL(main_url = response.url, found_urls = clean_url(l5[i].url)) for i in range(len(l5))])
            s = 'http://' + CountryCode.code
            if s in response.url:
                links.append(URL(main_url = response.url, found_urls = '$'))

        except:
            pass

        pub_re = [r'/pub/[a-z\-]+/[a-z0-9]+/[a-z0-9]+/[a-z0-9]+',
                  r'/in/[a-z0-9]+'
                 ]
        for pub in pub_re:
            if re.search(pub, response.url):
                self.extract(response) # extract profiles
        
        self.db.insert_urls(links)

    # Extracting all information of public profiles on response
    def extract(self, response):
        log.msg('Extract comments from %s' % response.url, level=log.INFO)
        response.replace(url = response.url.replace('www', CountryCode.code, 1),body = response.body_as_unicode())
        hxs = HtmlXPathSelector(response)
        # profiles
        p = Profile()

        title = hxs.select('//p[@class="title"]/text()')
        if not title: 
            title = hxs.select('//p[@class="headline-title title"]/text()')
        if title:
            p['title'] = title.extract()[0].strip().replace('--', '')

        p['first_name'] = hxs.select('//span[@class="given-name"]/text()').extract()[0].strip()
        p['last_name'] = hxs.select('//span[@class="family-name"]/text()').extract()[0].strip()
        location = hxs.select('//span[@class="locality"]/a/text()').extract()
        if not location:
            location = hxs.select('//span[@class="locality"]/text()').extract()
        location = location[0].strip().split(',')
        country = ''
        if len(location) == 3:
            p['locality'] = location[0].strip()
            p['region'] = location[1].strip()
            country = location[2].strip()
        elif len(location) == 2:
            p['locality'] = location[0].strip()
            p['region'] = location[1].strip()
        elif len(location) == 1:
            p['locality'] = location[0].strip()

        if not country:
            p['country'] = CountryCode.country

        desc_short = hxs.select('//p[@class=" description summary"]/descendant-or-self::*/text()').extract()
        if desc_short:
            desc_short = '\n'.join(d.strip() for d in desc_short)
            desc_short = desc_short.replace('&amp;', '&') 
            desc_short = desc_short.replace('=&gt;', ' =>') 
            p['desc_short'] = desc_short

        profile_pic = hxs.select('//div[@class="photo-wrap-lg"]/a/img/@src').extract()
        if not profile_pic:
             profile_pic = hxs.select('//div[@id="profile-picture"]/img/@src').extract()
        if profile_pic:
            p['profile_pic'] = profile_pic[0].strip()

        num_connection = hxs.select('//div[@class="member-connections"]/strong/text()').extract()
        if not num_connection:
            num_connection = hxs.select('//dd[@class="overview-connections"]/p/strong/text()').extract()

        num_connection = num_connection[0].strip().replace('+', '')
        p['num_connection'] = num_connection

        recomandations = hxs.select('//dl[@id="overview"]/dd/p/strong/text()').extract()
        for num in recomandations:
            rec_num = int(num.replace('+', ''))
            if rec_num != int(num_connection):
                p['recomandations'] = rec_num

        department = hxs.select('//dd[@class="industry"]/a/text()').extract()
        if not department:
            department = hxs.select('//dd[@class="industry"]/text()').extract()

        if department:
            p['department'] = department[0].strip().replace('&amp;', '&')
        profile_url = hxs.select('//dl[@class="public-profile"]//dd/a/@href').extract()
        if profile_url:
            profile_url = profile_url[0].strip()
            if not re.search(r'http://' + CountryCode.code, profile_url, re.M):
                log.msg("Filted out: %s" % profile_url, level=log.DEBUG)
                return
        else:
            profile_url = response.url

        p['profile_url'] = profile_url.replace('www', CountryCode.code, 1)

        email = re.search(r'mailto\:(\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}\b)', response.body, re.M)
        if email:
            p['email'] = email.group(1)
        phone = re.search(r'<dt>Phone:</dt>\n<dd>\n<p>([\+0-9 ]+)<span', response.body, re.M)
        if phone:
            p['phone'] = phone.group(1)
        address = re.search(r'<dt>Address:</dt>\n<dd>\n<p>([a-zA-z ,]+)</p>', response.body, re.M)    
        if address:
            p['address'] = append.group(1)
        im = re.search(r'<dt>IM: </dt>\n<dd>\n<p>([\w \!()]+)</p>', response.body, re.M)    
        if im:
            p['im'] = im.group(1)
        birthday = re.search(r'<dt>Birthday:</dt>\n<dd>\n<p>(\w+ \d+, \d+)</p>', response.body, re.M)    
        if birthday:
            p['birthday'] = birthday.group(1)
        marital_status = re.search(r'<dt>Marital status:</dt>\n<dd>\n<p>(\w+)</p>', response.body, re.M)    
        if marital_status:
            p['marital_status'] = marital.group(1)


        twitter_username = re.search(r'http://twitter\.com/(\w+)', response.body, re.M)
        if not twitter_username:
            twitter_username = re.search(r'/redirect\?url=http%3A%2F%2Fwww%2Etwitter%2Ecom%2F(\w+)\&', response.body, re.M)
        if twitter_username:
            p['twitter_username'] = twitter_username.group(1)


        fb = ''
        linkedin = ''
        fbid = ''
        g_plus = ''
        quora = ''
        tagged = ''
        g = ''
        twit = ''
        typ = ''

        # education
        edu_list = []
        vcalendar = hxs.select('//div[@id="profile-education"]//div[@class="content vcalendar"]/div/div')
        for vcard in vcalendar:
            edu = Education()
            date_start = vcard.select('.//abbr[@class="dtstart"]/text()').extract()
            if date_start:
                edu['date_start'] = date_start[0].strip()
            date_end = vcard.select('.//abbr[@class="dtend"]/text()').extract()
            if date_end:
                edu['date_end'] = date_end[0].strip()
            degree = vcard.select('.//span[@class="degree"]/text()').extract()
            if degree:
                edu['degree'] = degree[0].strip().replace('&amp;', '&')
            organization = vcard.select('.//h3[@class="summary fn org"]/a/text()').extract()
            if not organization:
                organization = vcard.select('.//h3[@class="summary fn org"]/text()').extract()

            if organization:
                edu['organization'] = organization[0].strip().replace('&amp;', '&')

            edu_list.append(edu)

        p['education'] = edu_list

        # skills
        skills_list = []
        skills_table = hxs.select('//ol[@class="skills"]')
        if skills_table:
            skill_rows = skills_table.select('li[@class="competency show-bean  "]/span/a/text()').extract()
            for skills in skill_rows:
                skill = skills.split(',')
                for s in skill:
                    ski = Skill()
                    ski['skill'] = s.strip().replace('&amp;', '&')
                    skills_list.append(ski)
            skills_rows = skills_table.select('li[@class="competency show-bean  extra-skill"]/span/a/text()').extract()
            if skills:
                for skills in skill_rows:
                    skill = skills.split(',')
                    for s in skill:
                        ski = Skill()
                        ski['skill'] = s.strip().replace('&amp;', '&')
                        skills_list.append(ski)

        if not skills_list:
            skills = hxs.select('//ol[@class="skills-with-endorsements"]/li')
            if skills:
                for i in xrange(len(skills)):
                    ski = skills[i].select('.//span[@class="endorse-item-name-text"]/text()').extract()
                    no_endorsements = skills[i].select('.//span[@class="num-endorsements"]/text()').extract()
                    s = Skill()
                    s['skill'] = ski[0].strip().replace('&amp;', '&')
                    s['no_endorsements'] = no_endorsements[0]
                    if i == 0:
                        s['first_skill_ind'] = 1 
                    else:    
                        s['first_skill_ind'] = 0 

                    skills_list.append(s)
            skills = hxs.select('//ol[@class="skills-with-endorsements compact-view"]/li')
            if skills:
                for i in xrange(len(skills)):
                    ski = skills[i].select('.//span[@class="endorse-item-name-text"]/text()').extract()
                    no_endorsements = skills[i].select('.//span[@class="num-endorsements"]/text()').extract()
                    s = Skill()
                    s['skill'] = ski[0].strip().replace('&amp;', '&')
                    s['no_endorsements'] = no_endorsements[0]
                    s['first_skill_ind'] = 0 
                    skills_list.append(s)

        p['skills'] = skills_list

        # specialities
        specialities_list = []
        specialties = hxs.select('//div[@id="profile-specialties"]//p/text()').extract()
        if specialties:
            for s in specialties:
                spe = Specialty()
                s = s.strip()
                if s[0] == '-':
                    s = s[1:].strip().capitalize()
                spe['specialty'] = s.replace('&amp;', '&')
                specialities_list.append(spe)

        p['specialties'] = specialities_list

        # experience
        experience_list = []
        vcalendar = hxs.select('//div[@id="profile-experience"]//div[@class="content vcalendar"]/div/div/div')

        for vcard in vcalendar:
        #    print vcard.extract()
            title = vcard.select('.//span[@class="title"]/text()').extract()
            if not title:
                title = vcard.select('.//strong[@class="title"]/a/text()').extract()

            if title:
                exp = Experience()
                exp['title'] = title[0].strip()
                date_start = vcard.select('.//abbr[@class="dtstart"]/text()').extract()
                if date_start:
                    exp['date_start'] = date_start[0].strip()
                date_end = vcard.select('.//abbr[@class="dtend"]/text()').extract()
                if date_end:
                    exp['date_end'] = date_end[0].strip()

                description = vcard.select('.//p[@class=" description current-position"]/descendant-or-self::*/text()').extract()
                if not description:
                    description = vcard.select('.//p[@class=" description past-position"]/descendant-or-self::*/text()').extract()
                if description:
                    if isinstance(description, list):
                        description = '\n'.join(d.strip() for d in description)
                    else:
                        description = description[0].strip()

                    exp['description'] = description.replace('&amp;', '&')

                organization = vcard.select('.//span[@class="org summary"]/text()').extract()
                if not organization:
                    organization = vcard.select('.//h4/strong/a[@name="company"]/text()').extract()

                if organization:
                    exp['organization'] = organization[0].strip().replace('&amp;', '&')

                experience_list.append(exp)

        p['experience'] = experience_list

        # websites
        websites_list = []
        # http://www.linkedin.com/redir/redirect?url=http%3A%2F%2Fwww%2Ehpc%2Eco%2Ejp&urlhash=0AVF 
        # http://www.linkedin.com/redir/redirect?url=http%3A%2F%2Fcuongnv%2Ecom&urlhash=DRTZ
        websites = hxs.select('//li[@class="website"]/a')
        for w in websites:
            web = Website()
            website = 'http://www.linkedin.com' + w.select('.//@href').extract()[0]
            cate = w.select('.//text()').extract()[0].strip()

            web['website'] = website
            web['cate'] = cate
            websites_list.append(web)

        p['websites'] = websites_list    
        
        # interests
        interests_list = []
        interests = hxs.select('//dd[@class="interests"]/p/a/text()').extract()
        for interest in interests:
            inter = Interest()
            inter['interest'] = interest.strip()
            interests_list.append(inter)

        p['interests'] = interests_list    
            
        # groups    
        groups_list = []
        groups = hxs.select('//div[@class="group-data"]')
        for group in groups:
            g = Group()
            g['group_url'] = 'http://www.linkedin.com' + group.select('.//a/@href').extract()[0]
            g['organization'] = group.select('.//a/strong[@class="fn org"]/text()').extract()[0].strip().replace('&amp;', '&')
            groups_list.append(g)

        p['groups'] = groups_list    

        # honors
        honors_list = []
        honors = hxs.select('//dd[@class="honors"]/p/text()').extract()
        for honor in honors:
            h = Honor()
            h['honor'] = honor.strip()
            honors_list.append(h)

        p['honors'] = honors_list    

        #print p

        # choose mode
        if self.mode == 'update':
            self.db.update_profile(p)
        else:    
            self.db.insert_profile(p)
