# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


# Define URL Item 
class URL(Item):
    # define the fields for your item here like:
    main_url = Field()
    found_urls = Field()
    pass

# Define Profile Item 
class Profile(Item):
    profile_url = Field()
    title = Field()
    first_name = Field()
    last_name = Field()
    locality = Field()
    region = Field()
    country = Field()
    desc_short = Field()
    profile_pic = Field()
    num_connection = Field()
    email = Field()
    phone = Field()
    twitter_username = Field()
    department = Field()
    recomandations = Field()
    date = Field()
    fb = Field()
    linkedin = Field()
    fbid = Field()
    g_plus = Field()
    quora = Field()
    tagged = Field()
    education = Field()
    skills = Field()
    specialties = Field()
    experience = Field()
    websites = Field()
    interests = Field()
    groups = Field()
    honors = Field()
    address = Field()
    im = Field()
    birthday = Field()
    marital_status = Field()
    pass

class Education(Item):
    date_start = Field()
    date_end = Field()
    degree = Field()
    organization = Field()   

class Skill(Item):
    skill = Field()
    no_endorsements = Field()
    first_skill_ind = Field()

class Specialty(Item):
    specialty = Field()

class Experience(Item):
    title = Field()
    date_start = Field()
    date_end = Field()
    organization = Field()
    description = Field()
    
class Website(Item):
    website = Field()
    cate = Field()

class Interest(Item):
    interest = Field()

class Group(Item):
    group_url = Field()
    organization = Field()

class Honor(Item):
    honor = Field()
