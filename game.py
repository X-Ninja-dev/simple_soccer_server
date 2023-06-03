'''
      ZONES     FINALIZATION        OPTIONS 

        1       Long Shot       -   Pass to 4     | Dribble   | Through Pass 
        2       Early Cross     -   Pass to 3     | Dribble   | Through Pass | Cut Inside (Long Shot)
        3       High Cross      -   Low Cross     | Dribble (Shot)
        4       Shot            -   Pass to Shot  
        5       Isolated Shot
                                ________                                
 ______________________________|________|______________________________
|             |           |                  |           |             |
|             |           |__________________|           |             |
|             |                    5                     |             |      
|      3l     |                                          |     3r      |     
|             |         4          4          4          |             |     
|             |__________________________________________|             |                                          
|                                                                      |   
|      2l                          1                           2r      |    
|                                                                      |    
|                                                                      |    
|                                                                      |    
|                                  0                                   |  


'''


import argparse
from decimal import ROUND_DOWN
import os
import json
import pandas as pd
import numpy as np
import random
from classPlayer import Team, Player
import functions as func
import commentary as com
import match_data as data
import time
import copy


from pathlib import Path


# runs the game
def run(home_team, away_team, comments = True, thread_number = 0):

    start_time = time.perf_counter()

    # create a copy of the teams to avoid changing the origial arguments (they are passed as reference)
    data.team_A = copy.deepcopy(home_team)
    data.team_B = copy.deepcopy(away_team)

    # enables/disables mute mode
    # comments = False
    if not comments:
        com.COMMENT_MUTE = True
    
    # initialize the report and match tables
    func.initialize_data(data.team_A,data.team_B)

    # initiates time at 0
    advance_time = func.generator_time()
    data.t = next(advance_time)

    # overall ball possession counter - sums ball possession each minute to be divided by total minutes at the end of the match    
    bp_overall = 0

    # set time and triggers for half time and stoppage time
    total_time = 90
    stoppage_time_trigger = True
    half = 1
    half_time_stoppage_time = random.randint(0,3)
    bp_counter_time = 0

    while data.t < total_time:
        
        report_index = len(data.event_report)
        data.event_report.loc[len(data.event_report),'time'] = data.t
        data.event_report.at[report_index,'half'] = half
        set_piece = None
        foul = None

        if com.COMMENT_DELAY:
            time.sleep(1)

        # stoppage time
        # at minute 88 the total time of match will increase by 1 min for each goal and an additional random number between 2 and 5
        if data.t > 88 and stoppage_time_trigger:
                
            extra_time = data.report.loc['Goals'].sum() + random.randint(2,5)
            if extra_time > 8:
                extra_time = 8
            total_time += extra_time
            stoppage_time_trigger = False
            data.event_report.at[report_index,'log'] = {"stoppage-time" : extra_time}

        elif data.t > 44+half_time_stoppage_time and half == 1:
            half = 2   
            data.t = 45
            data.event_report.at[report_index,'log'] = "hal-time"
            func.update_energy('halftime')
            continue        


        '''
        Whenever there are changes in the lineup, formation or mentality, a cycle should run and update what changed
        # check formations and store the bonus values in each team (team.formation)
        # this should be run everytime a managers make changes to the lineup or formation
        team_A.formation_bonus, team_B.formation_bonus = func.check_formation(team_A.lineup, team_B.lineup)
        update both teams' lineup
        update both teams' formation and formation bonus
        '''

        # check ball possession (and count it for the overall statistics)
        bp = func.ball_possession()
        bp_overall += bp
        bp_counter_time += 1
        # updates (drains) the energy of all players in the field
        func.update_energy('all')

        # sets which team is attacking based on Ball Possession
        if random.random() < bp:
            team = data.team_A
            opposite_team = data.team_B
        else:
            team = data.team_B
            opposite_team = data.team_A
        
        '''
        For now, a foul may be commited by the team without ball possession. 
        This should be changed so the team with higher aggressiveness is more likely to commit a foul.
        A team aggressiveness could be defined by the sum of the aggressiveness of its players.
        
        Or... if a foul is commited then the player is selected based on its aggressiveness from all players 
        regardless of the team (maybe exclude gk).
        This would ensure the fouls will be commited by more aggressive players and not dependent on the team or ball possession.
        However, if the foul is commited by the team that have the ball and will now attack, it would be weird... 
        This solution would require that time is advanced.
        '''
        outcome = None
        zone = '0'
        ##############################################################
        # check for foul outside checks
        defender = func.get_random_player(opposite_team.lineup)
        foul = func.check_foul(defender)
        if foul: 
            data.event_report.at[report_index,'foul0'] = {'outcome' : foul, 'defender': defender.id}

        ##############################################################
        # check if event is generated
        if not func.event_exist():
            data.t = next(advance_time)
            continue

        # if the attacking team is playing All Out Defense, the event may be wasted immediately (50% chance)
        if team.mentality == 'All Out Defensive' and random.random() < 0.5:
            data.event_report.at[report_index,'zone0'] = {'event' : 'wasted'}
            data.t = next(advance_time)
            continue

        # get event type and zone where the ball is
        event_type = func.get_event_type(team.strategy)          

        ####################################################################################
        ###                              Check 1                                         ###
        ####################################################################################
        (assister,attacker1,defender1,zone,success_rate,success) = func.zone0_check(data.BONUS[team.name+' mid'],team.lineup,opposite_team.lineup,event_type)
        attacker2 = attacker1

        func.update_rating_v2(assister.id,defender1.id,success_rate,success)
        data.event_report.at[report_index,'zone0'] = \
            {'event': event_type, 'player1': assister.id, 'player2': attacker1.id,'defender': defender1.id,\
            'new zone': zone, 'success rate': success_rate, 'success': success}

        if not success:
            data.t = next(advance_time)
            continue

        # counts the event success in the record
        data.report.at['Check1 Success',team.name] += 1
             
        ####################################################################################
        ###                         Check Zone 1 or 2                                    ###
        ####################################################################################

        success = True
        action = None

        if zone in ['1','2l','2r']:
            foul = func.check_foul(defender1,zone)

            if not foul:
                if zone == '1':
                    (action,attacker2,attacker3,defender2,new_zone,success_rate,success) = func.zone1_check(event_type,attacker1,defender1)     
                else:
                    (action,attacker2,attacker3,defender2,new_zone,success_rate,success) = func.zone2_check(zone,event_type,attacker1,defender1) 

                if attacker3 != attacker2:
                    assister = attacker2
                else:
                    assister = None
                
                data.event_report.at[report_index,'zone'+zone] = \
                {'action': action, 'player1': attacker2.id, 'player2': attacker3.id,'defender': defender2.id,\
                'new zone': new_zone, 'success rate': success_rate, 'success': success}

                func.update_rating_v2(attacker1.id,defender2.id,success_rate,success)
                attacker1 = attacker3
                if defender1 == defender2:
                    defender2 = func.get_defender(opposite_team.lineup,zone,defender1.id)
                defender1 = defender2
                zone = new_zone

        if not success:
            data.t = next(advance_time)
            continue
      

        ####################################################################################
        ###                         Check Zone 3 or 4                                    ###
        ####################################################################################

        if zone in ['3l','3r','4']:
            foul = func.check_foul(defender1,zone) 

            if not foul:
                if zone == '4':
                    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) = func.zone4_check(attacker1,defender1)
                else:
                    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) = func.zone3_check(attacker1,defender1) 

                if attacker1 != attacker2:
                    assister = attacker1

                data.event_report.at[report_index,'zone'+zone] = \
                {'action': action, 'player1': attacker1.id, 'player2': attacker2.id,'defender': defender2.id,\
                'new zone': new_zone, 'success rate': success_rate, 'success': success}

                attacker1 = attacker2
                func.update_rating_v2(attacker1.id,defender2.id,success_rate,success)
                if defender1 == defender2:
                    defender2 = func.get_defender(opposite_team.lineup,zone,defender1.id)
                defender1 = defender2
                zone = new_zone

        if not success:
            data.t = next(advance_time)
            continue

        if zone == '5':
            foul = func.check_foul(defender1,zone) 

        ####################################################################################
        ###                           Set Pieces                                         ###
        ####################################################################################

        if foul:
            set_piece = func.check_set_pieces(zone, defender1.id)
            data.event_report.at[report_index,'foul'] = \
            {'zone': zone, 'outcome': foul, 'defender': defender1.id, 'player': attacker1.id}

            if set_piece:

                data.t = next(advance_time)
                report_index = len(data.event_report)
                data.event_report.loc[len(data.event_report),'time'] = data.t
                data.event_report.at[report_index,'half'] = half

                if set_piece == 'Cross FK':

                    (outcome, assister, attacker1, defender) = func.run_corner(team,opposite_team.goalkeeper,'Cross FK')
                    if outcome == 'wasted':
                        data.event_report.at[report_index,'set piece'] = \
                        {'set piece': set_piece, 'taker': assister.id, 'attacker': None,\
                        'defender': None, 'goalkeeper': opposite_team.goalkeeper, 'outcome': outcome}

                    else:
                        data.event_report.at[report_index,'set piece'] = \
                        {'set piece': set_piece, 'taker': assister.id, 'attacker': attacker1.id,\
                        'defender': defender.id, 'goalkeeper': opposite_team.goalkeeper, 'outcome': outcome}

                else:
                    
                    if set_piece == 'Free Kick':
                        (outcome, attacker1) = func.run_freekick(team,opposite_team.goalkeeper)
                        assister = None

                    elif set_piece == 'Penalty':
                        (outcome, attacker1) = func.run_penalty(team,opposite_team.goalkeeper)
                        assister = None

                    data.event_report.at[report_index,'set piece'] = \
                    {'set piece': set_piece, 'taker': attacker1.id, 'goalkeeper': opposite_team.goalkeeper, 'outcome': outcome}


            else:
                data.t = next(advance_time)
                continue

        else:
            if zone == '5':
                zone = 'Isolated Shot'

            outcome = func.check_shot(zone,attacker1,opposite_team.goalkeeper)

            data.event_report.at[report_index,'finalization'] = \
            {'finalization': zone, 'player': attacker1.id,'goalkeeper': opposite_team.goalkeeper}

        if outcome in ['Corner','Save2corner','Blocked2corner']:
            if not set_piece:
                report_index = len(data.event_report)
                data.event_report.loc[len(data.event_report),'time'] = data.t
                data.event_report.at[report_index,'half'] = half
            j = 1
            while outcome in ['Corner','Save2corner','Blocked2corner']:
                (outcome, assister, attacker, defender) = func.run_corner(team,opposite_team.goalkeeper)
                j+=1
                if outcome in ['Corner','Save2corner','Blocked2corner'] and j >3:
                    outcome = None
                    set_piece = None
                    data.t = next(advance_time)  
                    continue

        if outcome == 'Goal':    

            hattrick = False
            if data.players_report.at[attacker1.id,'Goals'] == 3:
                func.update_rating(attacker1.id,'success1')
                hattrick = attacker2.name

            if assister and assister != attacker1:
                func.update_rating(assister.id,'Assist')
                data.players_report.at[assister.id,'Assists'] += 1 

        set_piece = None
        data.t = next(advance_time)

 

    bp_team_A = round((100*bp_overall)/bp_counter_time)
    data.report.at['Ball Possession',data.team_A.name] = bp_team_A
    data.report.at['Ball Possession',data.team_B.name] = 100 - bp_team_A

    if data.report.at['Total Shots',data.team_A.name] > 0 and data.report.at['Events',data.team_B.name] > 0:
        data.report.at['Goals per Shot',data.team_A.name] = round(data.report.at['Goals',data.team_A.name] / data.report.at['Total Shots',data.team_A.name],4)
        data.report.at['Shots per Event',data.team_A.name] = round(data.report.at['Total Shots',data.team_A.name] / data.report.at['Events',data.team_B.name],4)

    if data.report.at['Total Shots',data.team_B.name] > 0 and data.report.at['Events',data.team_B.name] > 0:
        data.report.at['Goals per Shot',data.team_B.name] = round(data.report.at['Goals',data.team_B.name] / data.report.at['Total Shots',data.team_B.name],4)
        data.report.at['Shots per Event',data.team_B.name] = round(data.report.at['Total Shots',data.team_B.name] / data.report.at['Events',data.team_B.name],4)


    if data.report.at['Events',data.team_A.name] > 0:
        data.report.at['Goals per Event',data.team_A.name] = round(data.report.at['Goals',data.team_A.name] / data.report.at['Events',data.team_A.name],2)
    if data.report.at['Events',data.team_B.name] > 0:
        data.report.at['Goals per Event',data.team_B.name] = round(data.report.at['Goals',data.team_B.name] / data.report.at['Events',data.team_B.name],2)

    data.players_report['Energy'] = round(data.players_report['Player'].apply(lambda x: x.energy),2)
    data.players_report['Rating'] = round(data.players_report['Rating'],2)

    func.update_energy('refill')

    data.report.columns=['Team A','Team B']
    
    #PATH = '/home/ruben/Documents/tradebotty/myfootballgame/output/testing/'


    exe_time = (time.perf_counter() - start_time)
    #print("%s seconds" % exe_time)
    #print(int(exe_time/60),"'",round(((exe_time/60)-np.floor(exe_time/60))*60),"''")
    #print("\n")


    return data.report, data.players_report


if __name__ == '__main__':

    # Initialize the Parser
    parser = argparse.ArgumentParser(description ='Run a match.')
    
    # Adding Arguments
    parser.add_argument('-c', action = 'store_true', help = 'enable comments (default = mute)')    
    parser.add_argument('-path', type = str, help = 'path to the folders with the team files (json)',default = '')
    args = parser.parse_args()


    # read the dir home_team and away_team
    # read the json player files (class str) into dicts and create a player object with the respective attribute values
  
    path = args.path
    teams = os.listdir(path)
    print(f"TEAMS: {teams}")
    with open(path + teams[0]) as json_file:
        json_team_A = json.load(json_file)

    with open(path + teams[1]) as json_file:
        json_team_B = json.load(json_file)

    team_A = Team(json_team_A["settings"]["name"])
    team_B = Team(json_team_B["settings"]["name"])

    for key, value in json_team_A["settings"].items():
        setattr(team_A,key,value)    
    for key, value in json_team_B["settings"].items():
        setattr(team_B,key,value)  

    for player in json_team_A["players"]:
        if player["position"] == 'GK':
            new_player = Player.Goalkeeper(player["id"],player["name"])
            team_A.goalkeeper = new_player.id
        else:
            new_player = Player.OutfieldPlayer(player["id"],player["name"])

        for key, value in player.items():
            setattr(new_player,key,value)
        
        new_player.team = team_A.name
        team_A.lineup[new_player.id] = player["position"]

    for player in json_team_B["players"]:
        if player["position"] == 'GK':
            new_player = Player.Goalkeeper(player["id"],player["name"])
            team_B.goalkeeper = new_player.id
        else:
            new_player = Player.OutfieldPlayer(player["id"],player["name"])

        for key, value in player.items():
            setattr(new_player,key,value)
        
        new_player.team = team_B.name
        team_B.lineup[new_player.id] = player["position"]
    
    
    new_dict = {}
    for key in team_A.lineup.keys():
        new_dict[int(key)] = team_A.lineup[key]
    team_A.lineup = new_dict

    new_dict = {}
    for key in team_B.lineup.keys():
        new_dict[int(key)] = team_B.lineup[key]
    team_B.lineup = new_dict

    report, match_table = run(team_A, team_B, args.c)


    # print(f"match_table: {match_table}")
    # print(report)
    result = report.to_json()
    result = json.loads(result)
    with open(f"{path}report.json", "w") as f:
        json.dump(result, f)