import json
import os
import pandas as pd
from get_player_id import get_player_id

def add_spacebetweenConsecutiveCapitalLetterIfNotAlreadyPresent(player_name):    
    new_name = ""
    for i in range(len(player_name)):
        if i == 0:
            new_name += player_name[i]
        elif player_name[i].isupper() and player_name[i-1].isupper():
            new_name += " " + player_name[i]
        else:
            new_name += player_name[i]
    return new_name


def generate_scorecard(match_id):
    score_card = {}
    df = pd.read_csv('player_id1.csv')
    dict = {}
    for i in range(len(df.index)):
        dict[df.iloc[i,0]] = df.iloc[i,1]

    with open(os.path.join('ipl_json', str(match_id) + '.json')) as f:
        data = json.load(f)
    # open player_id.csv file
    
    match_date = data['info']['dates'][0]
    officials = []
    for role in data['info']['officials']:
        for person in data['info']['officials'][role]:
            officials.append(person)
    for player in data['info']['registry']['people']:
        # print(player)
        if player in officials:
            continue
        player_id = 0
        search_name = add_spacebetweenConsecutiveCapitalLetterIfNotAlreadyPresent(player)
        if search_name in dict:
            player_id = dict[search_name]
            print(player_id," was found in the csv file")
        else:
            player_id = get_player_id(player)
            print(player_id," was not found in the csv file")
            dict[search_name] = player_id
        score_card[player] = {'player_id': player_id, 'match_date': match_date, 'notout': 0, 'runs': 0, 'balls': 0, 'fours': 0, 'sixes': 0, 'wickets': 0, 'deliveries': 0,
                              'maidens': 0, 'runs_conceded': 0, 'catches': 0, 'stumps': 0, 'runouts': 0, 'points': 0,'Average Form':0,'Consistency':0,'Average':0,'Strike Rate':0,'Total Runs':0,'Last Bat Innings':0,
                              'Bowling_Consistency':0,'Recent_Bowling_Avg':0,'Recent_Eco':0,'Career_Bowling_Avg':0,'Career_Wickets':0,'Career_Eco':0,'Last_Bowl_Innings':0}

    for team in data['info']['players']:
        for player in data['info']['players'][team]:
            # print(player)
            score_card[player]['points'] += 4

    for innings in data['innings']:
        for overs in innings['overs']:
            total_runs_in_over = 0
            for delivery in overs['deliveries']:
                batter = delivery['batter']
                bowler = delivery['bowler']
                runs = delivery['runs']['batter']
                total_runs_in_over += runs
                if ('extras' in delivery):
                    if ('wides' in delivery['extras']):
                        score_card[bowler]['runs_conceded'] += delivery['extras']['wides']
                        total_runs_in_over += delivery['extras']['wides']
                    if ('noballs' in delivery['extras']):
                        score_card[bowler]['runs_conceded'] += delivery['extras']['noballs']
                        score_card[batter]['balls'] += 1
                        total_runs_in_over += delivery['extras']['noballs']
                    if ('legbyes' in delivery['extras']):
                        score_card[batter]['balls'] += 1
                        score_card[bowler]['deliveries'] += 1
                    if ('byes' in delivery['extras']):
                        score_card[batter]['balls'] += 1
                        score_card[bowler]['deliveries'] += 1
                else:
                    score_card[batter]['balls'] += 1
                    score_card[bowler]['deliveries'] += 1
                score_card[batter]['runs'] += runs
                score_card[bowler]['runs_conceded'] += runs
                if (runs == 4):
                    score_card[batter]['fours'] += 1
                elif (runs == 6):
                    score_card[batter]['sixes'] += 1
                score_card[batter]['notout'] = 1
                if ('wickets' in delivery):
                    wickets = delivery['wickets'][0]
                    player_out = wickets['player_out']
                    score_card[player_out]['notout'] = 0

                    if (wickets['kind'] != 'run out'):
                        score_card[bowler]['wickets'] += 1
                    else:
                        if 'fielders' in wickets:
                            for fielder in wickets['fielders']:
                                score_card[fielder['name']]['runouts'] += 1
                    if (wickets['kind'] == 'caught'):
                        # print(wickets['fielders'][0]["name"])
                        score_card[wickets['fielders']
                                   [0]["name"]]['catches'] += 1
                    elif (wickets['kind'] == 'stumped'):
                        score_card[wickets['fielders']
                                   [0]["name"]]['stumps'] += 1

            if (total_runs_in_over == 0):
                score_card[bowler]['maidens'] += 1
    # points analysis
    for player in score_card:
        if (score_card[player]['balls'] > 0):
            score_card[player]['points'] += score_card[player]['runs']
            score_card[player]['points'] += score_card[player]['fours']
            score_card[player]['points'] += score_card[player]['sixes']*2
            if (score_card[player]['runs'] > 50):
                score_card[player]['points'] += 8
            if (score_card[player]['runs'] > 100):
                score_card[player]['points'] += 16
            if (score_card[player]['runs'] == 0):
                score_card[player]['points'] -= 2
            if (score_card[player]['balls'] > 10):
                strike_rate = score_card[player]['runs'] / \
                    score_card[player]['balls'] * 100
                if (strike_rate < 50):
                    score_card[player]['points'] -= 6
                elif (strike_rate < 60 and strike_rate >= 50):
                    score_card[player]['points'] -= 4
                elif (strike_rate < 70 and strike_rate >= 60):
                    score_card[player]['points'] -= 2
        if (score_card[player]['deliveries'] > 0):
            score_card[player]['points'] += score_card[player]['wickets']*25
            score_card[player]['points'] += score_card[player]['maidens']*8
            if (score_card[player]['wickets'] >= 4):
                score_card[player]['points'] += 8
            if (score_card[player]['wickets'] >= 5):
                score_card[player]['points'] += 16

            economy = (score_card[player]['runs_conceded'] /
                       score_card[player]['deliveries']) * 6
            if (economy < 6 and economy >= 5):
                score_card[player]['points'] += 2
            elif (economy < 5):
                score_card[player]['points'] += 4
        score_card[player]['points'] += score_card[player]['catches']*8
        score_card[player]['points'] += score_card[player]['stumps']*12
        score_card[player]['points'] += score_card[player]['runouts']*12

    df = pd.DataFrame.from_dict(score_card, orient='index')
    df = df[['player_id','match_date','notout', 'runs', 'balls', 'fours', 'sixes', 'wickets', 'deliveries',
            'maidens', 'runs_conceded', 'catches', 'stumps', 'runouts', 'points','Average Form','Consistency',
            'Average','Strike Rate','Total Runs','Last Bat Innings','Bowling_Consistency','Recent_Bowling_Avg','Recent_Eco','Career_Bowling_Avg','Career_Wickets','Career_Eco','Last_Bowl_Innings']]
    df = df.sort_values(by=['points'], ascending=False)
    cutoff = df.iloc[10, 14]
    #add a new column to df "dreamTeam" and initialize it with 0 ,set 1 if qualifies cutoff
    df['dreamTeam'] = 0
    df.loc[df['points'] >= cutoff, 'dreamTeam'] = 1
    print(df)
    df.to_csv('my_data.csv', mode='a', header=False)
    df1 = pd.DataFrame(list(dict.items()), columns=['player_name', 'player_id'])
    df1.to_csv('player_id1.csv', index=False)


#print(add_spacebetweenConsecutiveCapitalLetterIfNotAlreadyPresent('BB McCullum'))
generate_scorecard(1175356)





