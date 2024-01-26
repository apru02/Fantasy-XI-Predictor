import requests
from bs4 import BeautifulSoup
import pandas as pd

def compare_dates(date1,date2):
    d1 = date1.split('/')
    d2 = date2.split('/')
    if int(d1[2]) > int(d2[2]):
        return 1
    elif int(d1[2]) < int(d2[2]):
        return 0
    else:
        if int(d1[1]) > int(d2[1]):
            return 1
        elif int(d1[1]) < int(d2[1]):
            return 0
        else:
            if int(d1[0]) > int(d2[0]):
                return 1
            elif int(d1[0]) < int(d2[0]):
                return 0
            else:
                return 0

def getPlayerPerformanceIndex(player_id,date):
    avg = 0

    # Making a GET request 
    r = requests.get('http://www.howstat.com/cricket/Statistics/IPL/PlayerProgressBat.asp?PlayerID=' + player_id) 

    # Parsing the HTML 
    soup = BeautifulSoup(r.content, 'html.parser') 
    # b= soup.find('body')
    # bodytext = b.text.strip()
    # if 'No records available to display' in bodytext:
    #     return [0,0,0,0,0,0]
    # Getting the title tag 
    s = soup.find('table', class_='TableLined') 
    # Extracting all the <td> tags into a list
    l = s.find_all('tr')
    n = len(l)
    last_match_index = 0
    for i in range(3,n-1):
        date_of_match = l[i].find_all('td')[2].text.strip()
        if compare_dates(date_of_match,date):
            break
        else:
            last_match_index = i+1
    
    from_index = max(3,last_match_index-10)
    total_runs = 0
    inn = 0
    impact_innnings = 0
    played = 0
    last_good_innings = 0
    for i in range(from_index,last_match_index):
        t = l[i].find_all('td')
        runs = t[8].text.strip()  # Remove leading and trailing whitespace
        # Check for '*' at the end and remove it
        if runs.endswith('*') and 'DNB' not in runs:
            runs = runs[:-1]
        # Check for additional characters and remove them
            runs = runs.replace('\r\n', '').replace('\xa0', '').replace(',', '').strip()
            runs_scored = int(runs)
            balls_faced = int(t[9].text.strip())
            strike_rate = 0
            if balls_faced > 0:
                strike_rate = runs_scored / balls_faced * 100

            impact_innnings+= 1
            total_runs += runs_scored
            played += 1
            last_good_innings=0
        elif runs == '-' or 'DNB' in runs:
            continue
        else:
            runs = runs.replace('\r\n', '').replace('\xa0', '').replace(',', '').strip()
            runs_scored = int(runs)
            balls_faced = int(t[9].text.strip())
            strike_rate = 0
            if balls_faced > 0:
                strike_rate = runs_scored / balls_faced * 100
            if (runs_scored > 20 or (balls_faced > 10 and strike_rate > 140) or (balls_faced <=10 and balls_faced >= 4 and strike_rate >=150)): 
                impact_innnings+= 1
                last_good_innings = 0
            else:
                last_good_innings += 1
            inn += 1
            played += 1
            total_runs += runs_scored
    if inn == 0:
        avg = 0
    else:
        avg = total_runs / inn
    if played > 0:
        consistency = impact_innnings / played
    else:
        consistency = 0
    avg_before_last_match = 0
    strike_rate_before_last_match = 0
    runs_before_last_match = 0
    if last_match_index != 3:
        avg_before_last_match = l[last_match_index-1].find_all('td')[-2].text.strip()
        if (avg_before_last_match == '-' or len(avg_before_last_match) == 0):
            avg_before_last_match = 0
        else:
            avg_before_last_match = float(avg_before_last_match)
        strike_rate_before_last_match = l[last_match_index-1].find_all('td')[-1].text.strip()
        if (strike_rate_before_last_match != '-'):
            strike_rate_before_last_match = float(strike_rate_before_last_match)
        else:
            strike_rate_before_last_match = 0
        runs_before_last_match = l[last_match_index-1].find_all('td')[-3].text.strip()
        if (runs_before_last_match != '0'):
            runs_before_last_match = int(runs_before_last_match)
        else:
            runs_before_last_match = 0
    return [runs_before_last_match,avg,consistency,avg_before_last_match,strike_rate_before_last_match,last_good_innings]

print(getPlayerPerformanceIndex('4062','24/03/2019'))
def getBowlerPerformanceIndex(player_id,date):
    # Making a GET request 
    r = requests.get('http://www.howstat.com/cricket/Statistics/IPL/PlayerProgressBowl.asp?PlayerID=' + player_id) 
    # Parsing the HTML 
    soup = BeautifulSoup(r.content, 'html.parser') 
    # Getting the title tag 
    s = soup.find('table', class_='TableLined') 
    # Extracting all the <td> tags into a list
    l = s.find_all('tr')
    n = len(l)
    match_indices = []
    for i in range(3,n):
        date_of_match = l[i].find_all('td')[1].text.strip()
        figures = l[i].find_all('td')[5].text.strip()
        if len(date_of_match)>0 and "did not bowl" not in figures:
            if compare_dates(date,date_of_match):
                #print(len(match_indices)+1,date_of_match)
                match_indices.append(i)
            else:
                break
    start_index = max(0,len(match_indices)-10)
    wickets = 0
    runs_conceded = 0
    total_overs = 0
    consistency = 0
    last_good_innings = 0
    for i in range(start_index,len(match_indices)):
        figures = l[match_indices[i]].find_all('td')[7].text.strip()
        overs = l[match_indices[i]].find_all('td')[6].text.strip().split('.')
        over = int(overs[0]) + int(overs[1])/6
        total_overs += over
        fig = figures.split('/')
        wicket = int(fig[0])
        runs = int(fig[1])
        wickets += wicket
        runs_conceded += runs
        if((wicket <=1 and (runs/over) < 8) or (wicket > 1 and (runs/over) < 10) or (wicket > 3 and (runs/over) <= 11)):
            consistency += 1   
            last_good_innings = 0
        else:
            last_good_innings += 1
    career_average = 0
    # career_strike_rate = 0
    career_wickets = 0
    career_eco = 0
    recent_avg = 0
    recent_eco = 0
    
    if wickets > 0:
        recent_avg = runs_conceded/wickets
        recent_eco = runs_conceded/total_overs
    if len(match_indices) > 0:
        consistency = consistency/(len(match_indices)-start_index)
        if len(l[match_indices[-1]].find_all('td')[-1].text.strip()) > 0:
            career_average = float(l[match_indices[-1]].find_all('td')[-1].text.strip())
        # if len(l[match_indices[-1]].find_all('td')[-4].text.strip()) > 0:
        #     career_strike_rate = float(l[match_indices[-1]].find_all('td')[-4].text.strip())
        if len(l[match_indices[-1]].find_all('td')[-2].text.strip()) > 0:
            career_wickets = int(l[match_indices[-1]].find_all('td')[-2].text.strip())
        if len(l[match_indices[-1]].find_all('td')[-3].text.strip()) > 0:
            career_eco = float(l[match_indices[-1]].find_all('td')[-3].text.strip())
    return [consistency,recent_avg,recent_eco,career_average,career_wickets,career_eco,last_good_innings]
    

# print(getBowlerPerformanceIndex('3993','25/03/2023'))


