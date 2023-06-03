from pickle import FALSE
import pandas as pd
from typing import Type
from classPlayer import Team, Player
import match_data as data
import time

# loads the file with all the contextual commentaries

# Commented out by me..!
# comentary_table = pd.read_csv('./comentary.csv', sep = "*")
# print(f"COMMENTARY: {comentary_table}")
# opens the file to store the text output of the run
# f = open("output.txt", "w")

COMMENT_MUTE = True
COMMENT_DELAY = False

def comment(type: str, end: str, player1: str = None, player2: str=None, defender1: str=None, defender2: str=None, goalkeeper:str=None) -> None:
    print("COMMENT FUNCTION CALLED")
    if COMMENT_MUTE:
        return

    if COMMENT_DELAY:
        time.sleep(1)

        if end in ['goal','base','save','miss','save2corner','post']:
            time.sleep(0.5)

    # DEBUG
    print(f"type = {type}")
    print(f"end = {end}")
    print(f"DATA SET IN COMMENT: {comentary_table.loc[(comentary_table['type'] == type) & (comentary_table['end'] == end)]}")
    df = comentary_table.loc[(comentary_table['type'] == type) & (comentary_table['end'] == end)].sample()
    message = df['comentary'].values[0]
    exec(message)  

def comment_after_goal(team_A_name, team_B_name, player1: str):

    if COMMENT_MUTE:
        return

    if COMMENT_DELAY:
        time.sleep(1)

    if player1:
        #print(f"\n{player1} completes the HAT-TRICK!!!\n",file=f)    
        print("\n",player1,"completes the HAT-TRICK!!!\n")    

    #print("\n",team_A_name,int(data.report.at['Goals',team_A_name])," - ",team_B_name,int(data.report.at['Goals',team_B_name]),file=f)  
    print("\n",team_A_name,int(data.report.at['Goals',team_A_name])," - ",team_B_name,int(data.report.at['Goals',team_B_name]))  


def comment_team(event_type: str, zone: str, team: str, player1: str) -> None:
    """
    Prints the comment for the first check (1). 
    It will state the event type, the team's name, the player with the ball and the zone of the field.
    """

    if COMMENT_MUTE:
        return

    if zone == '1':
        area = 'middle'
    elif zone == '2l' or zone == '3l':
        area = 'left wing'
    elif zone == '2r' or zone == '3r':
        area = 'right wing'
    elif zone == '4':
        area = 'penalty area! Amazing pass from the defense!'

    #print("\n",t,"'",file=f)    
    print("\n",data.t,"'")    
    df = comentary_table.loc[(comentary_table['type'] == event_type) & (comentary_table['end'] == 'base')].sample()
    message = df['comentary'].values[0]
    exec(message)


def comment_foul(event_type: str ,end: str, defender1: str, player1: str=None):
    """
    Prints the comments for a foul and eventual card. Arguments are the names of players, type and end of the comment.
    """

    if COMMENT_MUTE:
        return

    if COMMENT_DELAY:
        time.sleep(1)

    if t >= 0:
        print("\n",data.t,"'",file=f)


    df = comentary_table.loc[(comentary_table['type'] == event_type) & (comentary_table['end'] == end)].sample()
    message = df['comentary'].values[0]
    exec(message)  


def comment_custom(context: str, extra_time: int=0, team_A_name: str='Team A', team_B_name: str='Team A') -> None:

    if COMMENT_MUTE:
        return

    if context == 'start':
        print(f"Welcome to the match between", team_A_name,"and", team_B_name,file=f)
        print(f"\nIt's a beautiful sunny afternoon here in the Arche International Stadium!\n",file=f)

        if COMMENT_DELAY:
            time.sleep(1)
        print("\nKICK_OFF!!\n")


    elif context == 'half-time':
        if COMMENT_DELAY:
            time.sleep(1)
        print("\n\n",data.t,"'",file=f)
        print("\nThe referee signals half time.\n\n",file=f)

    elif context == 'extra-time':
        if COMMENT_DELAY:
            time.sleep(1)
        print("\n",data.t,"'",file=f)
        print("\nThe referee is going to add more", int(extra_time), "minutes of stoppage time.\n",file=f)

    elif context == 'end':
       
        if COMMENT_DELAY:
            time.sleep(1)

        goals_A = int(data.report.at['Goals',team_A_name])
        goals_B = int(data.report.at['Goals',team_B_name])

        print("\n\n\nIt's the final whisle!",file=f)
        
        if COMMENT_DELAY:
            time.sleep(1)

        if goals_A > goals_B:
            print(f"\n",team_A_name, "wins!!!\n\n",file=f)

        elif goals_A < goals_B:
            print(f"\n",team_B_name, "wins!!!\n\n",file=f)

        else:
            print(f"\nIt's a draw.\n\n",file=f)   

        print(team_A_name,goals_A," - ",team_B_name,goals_B,file=f)

        mvp = data.match_table.loc[data.match_table['rating'].idxmax()].player

        print("\nMan of the Match: ",mvp.name, file=f)
        
        if COMMENT_DELAY:
            time.sleep(1)

        data.match_table['player'] = data.match_table['player'].apply(lambda x: x.name)  

        print("\n\n",data.match_table,file=f)
        print(data.report,file=f)


def comment_waste_attack(team_name: str) -> None:
    
    if COMMENT_MUTE:
        return
    
    print("\n",data.t,"'",file=f)
    print(team_name,"is not even trying to attack anymore, they just kick ball as far as possible.",file=f)
