import requests
from bs4 import BeautifulSoup
import pandas as pd
from string import ascii_lowercase
import re
import time
from random import randint
import pickle
import csv
import sys
import os

url_search = "https://www.cpso.on.ca/Public-Information-Services/Find-a-Doctor?search=general"
abs_file_path = os.path.abspath(__file__)
file_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(file_dir)

headers_search = {
    "Host": "www.cpso.on.ca",
    "User-Agent": "Adam Kowalczewski, Service Canada, adam.kowalczewski@servicecanada.gc.ca",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.cpso.on.ca/Public-Information-Services/Find-a-Doctor?search=general",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "Cookie": "CMSPreferredCulture=en-CA; _ga=GA1.3.788028045.1540596057; _gid=GA1.3.1509832542.1540596057; CMSCsrfCookie=PB+DjsX3FE9SCgAk3jGZzc65Ld6NEaE755HpaDB9; ASP.NET_SessionId=pek14izhwnw4u0curdgkxygh; _gat_UA-36725164-1=1",
    "Upgrade-Insecure-Requests": "1"
}

manScript = "%3b%3bAjaxControlToolkit%2c+Version%3d4.1.60919.0%2c+Culture%3dneutral%2c+PublicKeyToken%3d28f01b0e84b6d53e%3aen-CA%3aee051b62-9cd6-49a5-87bb-93c07bc43d63%3a475a4ef5%3aeffe2a26%3a7e63a579"
manScript = manScript.replace( "%3b", ";" )
manScript = manScript.replace( "%2c", "," )
manScript = manScript.replace( "%3d", "=" )
manScript = manScript.replace( "%3a", ":" )
manScript = manScript.replace( "en-CA", "en-US")

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status[0:40].ljust(40)))
    sys.stdout.flush()

def count_doc_by_city_lastname( city_code, char ):
    with requests.Session() as s:

        r = s.get(url_search)
        soup = BeautifulSoup(r.content, 'html.parser')

        payload = {
            "__CMSCsrfToken": soup.find("input", id="__CMSCsrfToken")['value'],
            "__VIEWSTATE": soup.find("input", id="__VIEWSTATE")['value'],
            "__VIEWSTATEGENERATOR": soup.find("input", id="__VIEWSTATEGENERATOR")['value'],
            "lng": 'en-CA',
            "manScript_HiddenField": manScript,
            "searchType":"general",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$advancedState":"closed",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ConcernsState":"closed",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddCity": city_code,
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$txtLastName": char,
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$grpGender":"+",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$grpDocType":"rdoDocTypeAll",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddHospitalName":"-1",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$ddLanguage":"08",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkActiveDoctors":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPracticeRestrictions":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPendingHearings":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkPastHearings":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkHospitalNotices":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkConcerns":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$chkNotices":"on",
            "p$lt$ctl04$pageplaceholder$p$lt$ctl02$AllDoctorsSearch$btnSubmit1":"Submit"
        }

        # get doctor search result count
        time.sleep(randint(1,3))
        r = s.post(url_search, data = payload)
        soup = BeautifulSoup(r.content, 'html.parser')
        target = soup.find('div', class_ = "doctor-search-count").strong.text
        return int(re.search( "\d+", target ).group())

# for the big cities in Ontario (more than 1,000 doctors each)
cities = {
    "1127": "Brampton",
    "1425": "Hamilton",
    "1561": "London",
    "1630": "Mississauga",
    "1711": "Ottawa",
    "1977": "Toronto"
 }

#cities = { "2067": "Windsor" }
start_time = time.time()

for city_code, city in cities.items():
    city_idx = []
    char_idx = []
    count = []

    for char_1 in ascii_lowercase:
        char = char_1

        try:
            n_dr = count_doc_by_city_lastname( city_code, char )
            print( f"{city}-{char}: found {n_dr}")

        except:
            print( f"{city}-{char}: none found")
            count.append( 'NA' )
            continue

        # if n results for one letter are below threshold, stop
        if n_dr < 1000:
            city_idx.append(city)
            char_idx.append(char)
            count.append( n_dr )
            continue

        # otherwise move to two letters
        for char_2 in ascii_lowercase:
            char = char_1 + char_2

            try:
                n_dr = count_doc_by_city_lastname( city_code, char )
                print( f"{city}-{char}: found {n_dr}")
            except:
                count.append( 'NA' )
                print( f"{city}-{char}: none found")
                continue

            city_idx.append(city)
            char_idx.append(char)
            count.append( n_dr )

    result = pd.DataFrame({
        "city_name": city_idx,
        "char_idx": char_idx,
        "count": count })

    result.to_csv( f'{project_dir}/data/n_city_lname2_{city}.csv', index = False )

elapsed_time = time.time() - start_time
print( '-' * 10 )
print(time.strftime("-- time elapsed for scrape: %H:%M:%S -- ", time.gmtime(elapsed_time)))
