import random

# MySQL Config
class MySQLConfigs:
    host = 'localhost'
    username = 'root'
    password = 'p@ssw0rd123#'
    database  = 'linkedin_profiles'

# Mapping country to country code
class CountryCode:
    country = 'Malaysia'
    code = 'my'

# LinkedIn accounts for simulation 
class LinkedInAccount(object):
    account = [
                    {'key':'goodbyemylove2000@gmail.com', 'password':'ma~lai12!'},
                    {'key':'david.cook199@gmail.com', 'password':'ma~lai12!'},
                    {'key':'pauldavid284@gmail.com', 'password':'ma~lai12!'},
                    {'key':'idontwanttomissathing2000@gmail.com', 'password':'ma~lai12!'},
                    {'key':'nomad9x@gmail.com', 'password':'ma~lai12'},
                    {'key':'nomatterwhat284@gmail.com', 'password':'ma~lai12!'},
                    {'key':'ilovecoca2000@gmail.com', 'password':'ma~lai12!'},
                    {'key':'iamdane109@gmail.com', 'password':'ma~lai12!'},
                    {'key':'kevin.dane109@gmail.com', 'password':'ma~lai12!'},
             ]
    # get accounts
    def get(self):
        return self.account[ random.randint(0, len(self.account) - 1) ]

#if __name__ == '__main__':
#    acc = LinkedinAccount()
#    print acc.get()



