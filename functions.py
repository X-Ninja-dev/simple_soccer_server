from classPlayer import Team, Player
from typing import Generator
import pandas as pd
import numpy as np
import random
import commentary as com
import match_data as data

# Event base rate
EVENT_RATE = 28         # base % chance of generating an event per minute

# bonus for each mentality type in %
MENTALITY_A3 = 25
MENTALITY_A2 = 15
MENTALITY_A1 = 10
MENTALITY_D1 = -15
MENTALITY_D2 = -30
MENTALITY_D3 = -45

SUCCESS_LONGSHOT = 17
SUCCESS_HEADER = 20         # base % chance for Header (attack_rating - defend_rating = 0)
SUCCESS_SHOT = 35
SUCCESS_ISOLATED = 65
SUCCESS_POST = 5
SUCCESS_POST_PENALTY = 10

SUCCESS_CHECK1 = 80

SUCCESS_PENALTY = 75        # base % chance for penalty (attack_rating - defend_rating = 0)
SUCCESS_CORNER = 50         # base % chance for a corner to lead into a Header (4 best headers from both data.players_report)
SUCCESS_FK = 10             # base % chance to score from a direct FK
BARRIER = 35
BLOCKED = 10
SAVE2CORNER = 25

SUCCESS_RATE = { "zone0" : {"to zone1": 77, "to zone2": 77, "to zone3": 61.6, "to zone4": 46.2}, \
    "zone1" : {"normal" : 60, "critical" : 20, "long shot" : 76.39}, \
    "zone2" : {"normal": 80, "longshot" : 76.39}, \
    "zone4" : {"normal" : 61.84, "critical" : 33.3}, \
    "cross" : {"early cross" : 69.94, "high cross": 81.17, "critical" : 46.38 }}

FOUL_RATE_no_event = 0.2            # base % chance of a foul per minute
CARD_RATE_no_event = 0.12           # card rate
YELLOW_RATE_no_event = 0.98         # chance of yellow if there is a card

FOUL_RATE = 0.12                     # base % chance of a foul
CARD_RATE_zone_1_2 = 0.25           # chance of card in zone 1
CARD_RATE_zone_3_4 = 0.75           # chance of card in zone 3 or 4
CARD_RATE_zone_5 = 1                # chance of card in zone 5
YELLOW_RATE = 0.98                  # chance of yellow if there is a card

RATING_DICT = {
    'Goal' : 1.5,
    'Miss' : -0.1,
    'Save' : 0.5,
    'Save Isolated' : 1,
    'On target' : 0.2,
    'Assist' : 1.25,

    'success1' : 0.25,
    'fail1' : -0.25,
    'success2' : 0.5,
    'fail2' : -0.5,

    'Cross Success' : 0.2,
    'Cross Fail' : -0.35,
    'Clear' : 0.6,

    'Goal conceived' : -0.75,
    'Yellow Card' : -0.25,
    'Second Yellow' : -0.5,
    'Red Card' : -1.25,
    'Penalty scored': 1,
    'Penalty conceived' : -0.5,
    'Penalty miss' : -1.25,
    'Penalty save'  : 1.25,
    'Commit penalty' : -0.4,

}


D = ['DC','DCL','DCR','DL','DR']
DM = ['DMC','DMCL','DMCR','DML','DMR']
M = ['MC','MCL','MCR','ML','MR']
AM = ['AMC','AMCL','AMCR','AML','AMR']
F = ['FCL','FCR','FC']

LEFT = ['DL','DML','ML','AML']
CENTER_L = ['DCL','DMCL','MCL','AMCL','FCL']
CENTER_R = ['DCR','DMCR','MCR','AMCR','FCR']
CENTER = ['DC','DMC','MC','AMC','FC']
RIGHT = ['DR','DMR','MR','AMR']


saving_stats = pd.read_csv('./saving_stats.csv')
saving_stas = saving_stats.set_index('type')

'''
DC	%	D L/R	%	DMC	%	DM L/R	%	MC	%	M L/R	%	AMC 	%	AM L/R	%	FC	%
Passing	20%	Passing	10%	Passing	20%	Passing	10%	Passing	30%	Passing	30%	Passing	30%	Passing	20%	Passing	30%
Technique		Technique	10%	Technique	10%	Technique	10%	Technique	30%	Technique	30%	Technique	30%	Technique	30%	Technique	50%
Tackle	40%	Tackle	20%	Tackle	25%	Tackle	20%	Tackle	10%	Tackle		Tackle		Tackle		Tackle	
Positioning	40%	Positioning	10%	Positioning	25%	Positioning	10%	Positioning	20%	Positioning	10%	Positioning	30%	Positioning	10%	Positioning	10%
Speed		Speed	25%	Speed		Speed	25%	Speed		Speed	15%	Speed		Speed	20%	Speed	
Stamina		Stamina	25%	Stamina	20%	Stamina	25%	Stamina	10%	Stamina	15%	Stamina	10%	Stamina	20%	Stamina	10%
'''

#ball_possession_table = pd.read_csv('/home/ruben/Documents/tradebotty/myfootballgame/input/ballpossession.csv')
#ball_possession_table = ball_possession_table.set_index('stat')

# initialize list elements
bp_data =   {'passing': [0.20,0.20,0.20,0.20,0.20,0.20,0.20,0.20,0.20,0.20,0.30,0.30,0.30,0.30,0.30,0.35,0.35,0.35,0.35,0.35,0.30,0.30,0.30],\
            'technique':[0,0,0,0.20,0.20,0.20,0.20,0.15,0.15,0.15,0.25,0.25,0.25,0.25,0.25,0.35,0.35,0.35,0.35,0.35,0.50,0.5,0.5],\
            'tackle':[0.40,0.40,0.40,0.20,0.20,0.20,0.20,0.35,0.35,0.35,0.10,0.10,0.10,0.10,0.10,0,0,0,0,0,0,0,0],\
            'positioning':[0.40,0.40,0.40,0.20,0.20,0.20,0.20,0.30,0.30,0.30,0.25,0.25,0.25,0.20,0.20,0.10,0.10,0.10,0.10,0.10,0.10,0.10,0.10],\
            'speed':[0,0,0,0.20,0.20,0.20,0.20,0,0,0,0.10,0.10,0.10,0.15,0.15,0.20,0.20,0.20,0.20,0.20,0.10,0.10,0.10]}

col = ['DCL','DC','DCR','DL','DR','DML','DMR','DMCL','DMC','DMCR','MCL','MC','MCR','ML','MR','AMCL','AMC','AMCR','AML','AMR','FCL','FC','FCR']
stats = ['passing','technique','tackle','positioning','speed']
# Create the pandas DataFrame with column name is provided explicitly
ball_possession_table = pd.DataFrame(bp_data)
ball_possession_table['positions'] = col
ball_possession_table.set_index('positions',inplace=True)


#data_zone1 = pd.read_csv('/home/ruben/Documents/tradebotty/myfootballgame/input/data_zone1.csv')    
#data_zone1 = data_zone1.set_index('event')

                # long shot / dribble / pass / through pass
actions_zone1 = { 'Short Pass': (0.4, 0.1, 0.45, 0.05),\
                'Direct': (0.1, 0.05, 0.05, 0.8),\
                'Wings' : (0, 0, 0, 0),\
                'Long Ball' : (0.4, 0.2, 0.2, 0.2)}

                # long shot / early cross / dribble / pass / through pass
actions_zone2 = { 'Short Pass': (0.35, 0.05, 0.10, 0.40, 0.10),\
                'Direct': (0.35, 0.10, 0.10, 0.10, 0.35),\
                'Wings' : (0.2 , 0.15, 0.25, 0.20, 0.20),\
                'Long Ball' : (0.10, 0.40, 0.20, 0.20, 0.1)}

actions_zone3 = {'actions_list':["High Cross", "Pass Shot", "Dribble Shot"],\
                    'weights': [0.85, 0.12, 0.3]}

actions_zone4 = { 'actions_list': ['Marked Shot','Dribble Shot','Pass Shot','Dribble Isolated'],\
                    'weights': [0.43, 0.43, 0.12, 0.2]}

actions_pre_longshot = { 'actions_list': ['Marked Long Shot','Dribble Long Shot','Pass Long Shot'],\
                    'weights': [0.4, 0.4, 0.2]}



########################################################################################################################
###                                   Utilities                                                                     ####
########################################################################################################################

def initialize_data(team_A, team_B):
    """Initializes all the require data for the report and player's report
    """
    data.team_A = team_A
    data.team_B = team_B

    zero_array = np.zeros(shape=(48,2))
    data.report = pd.DataFrame(zero_array)
    data.report.index = ['Formation','Strategy','Mentality','Rating','Ball Possession',\
        'Fouls','Fouls Zone0','Fouls Zone1','Fouls Zone2','Fouls Zone3','Fouls Zone4','Fouls Zone5','Yellow Card','Second Yellow','Red Card',\
        'Events','Check1 Success','Short Pass','Direct', 'Wings','Long Ball','Counter Attacks', \
        'Dribble','Pass','Through Pass','Cross',\
        'Long Shot','Goals from Long Shot','Header','Goals from Header','Shot','Goals from Shot','Isolated Shot','Goals from Isolated Shot', \
        'Penalty','Goals from Penalty','Free Kick','Goals from FK','Corner','Goals from Corner','Cross FK','Goals from Cross FK',\
        'Total Shots','Shots On Target','Shots per Event','Goals per Event','Goals per Shot','Goals'] 

    data.report.columns = [team_A.name, team_B.name]

    data.report.loc['Formation'] = ""
    data.report.at['Formation',data.team_A.name] = (getattr(data.team_A, 'formation_name'))
    data.report.at['Formation',data.team_B.name] = (getattr(data.team_B, 'formation_name'))

    data.report.loc['Rating'] = "72"

    for i in ['Strategy','Mentality']:
        data.report.loc[i] = ""
        data.report.at[i,data.team_A.name] = str(getattr(data.team_A, i.lower()))
        data.report.at[i,data.team_B.name] = str(getattr(data.team_B, i.lower()))

    full_lineup = {**data.team_A.lineup, **data.team_B.lineup}

    d = {'id': [*full_lineup]}
    data.players_report = pd.DataFrame(data=d)
    data.players_report['Player'] = data.players_report['id'].apply(lambda x: Player.get_player(x))    
    data.players_report['Team'] = data.players_report['Player'].apply(lambda x: x.team) 
    data.players_report['Position'] = data.players_report['id'].apply(lambda x: full_lineup[x])
    data.players_report['Energy'] = data.players_report['Player'].apply(lambda x: x.energy) 
    data.players_report['Status'] = 'on'         # status will indicate if the player is on the field. May be used to substitutions later on.S
    for stat in ['reflexes*','agility*','aerial*','oneonone*','passing*','handling*','command*','positioning*','stamina*','penalty*']:
        stat_name = stat.replace('*', '')
        data.players_report[stat] = data.players_report['Player'].apply(lambda x: getattr(x,stat_name) if isinstance(x, Player.Goalkeeper) else 0)
    for stat in ['finishing','longshot','speed','crossing','passing','technique','tackle','positioning','stamina','heading']:
        data.players_report[stat] = data.players_report['Player'].apply(lambda x: getattr(x,stat) if isinstance(x, Player.OutfieldPlayer) else 0)
    data.players_report['Foul'] = 0
    data.players_report['Yellow Card'] = 0
    data.players_report['Red Card'] = 0
    data.players_report['Clear'] = 0
    data.players_report['Block'] = 0
    data.players_report['Tackle'] = 0
    data.players_report['Interception'] = 0
    data.players_report['Pass Success'] = 0
    data.players_report['Pass Fail'] = 0
    data.players_report['Dribble Success'] = 0
    data.players_report['Dribble Fail'] = 0
    data.players_report['Through Pass Success'] = 0
    data.players_report['Through Pass Fail'] = 0
    data.players_report['Cross Success'] = 0
    data.players_report['Cross Fail'] = 0
    data.players_report['Long Shot'] = 0
    data.players_report['Shot'] = 0
    data.players_report['Header'] = 0
    data.players_report['Isolated Shot'] = 0
    data.players_report['Total Shots'] = 0
    data.players_report['Shots On Target'] = 0
    data.players_report['Save'] = 0
    data.players_report['Total Actions'] = 0
    data.players_report['Actions Success'] = 0
    data.players_report['Actions Fail'] = 0
    data.players_report['Assists'] = 0
    data.players_report['Goals'] = 0
    data.players_report['Rating'] = round(float(6),1)
    data.players_report = data.players_report.set_index('id')

    # check formations and store the bonus values in each team (team.formation)
    # this should be run everytime a managers make changes to the lineup or formation
    data.team_A.formation_bonus, data.team_B.formation_bonus = check_formation(data.team_A.lineup, data.team_B.lineup)

    
    data.event_report.drop(data.event_report.index, inplace=True)
    #event_report_columns = ['half','time','log','changes','foul0','zone0','zone1','zone2l','zone2r','zone3l','zone3r','zone4',\
    #    'finalization','foul','set piece','corner']
    #data.event_report = pd.DataFrame(np.zeros(shape=(0,len(event_report_columns))), columns=event_report_columns)


def check_formation(team_A_lineup: dict, team_B_lineup: dict) -> list:
    """
    Checks the formation of both teams and updates the respective bonus for defense, midfield and attack on the team bonus attribute (team.formation)
    """
    D = ['DC','DCL','DCR','DL','DR']
    DM = ['DMC','DMCL','DMCR','DML','DMR']
    M = ['MC','MCL','MCR','ML','MR']
    AM = ['AMC','AMCL','AMCR','AML','AMR']
    F = ['FC','FCL','FCR']

    formation_A = {}
    formation_B = {}

    # calculate defensive bonus based on number of defenders
    # DC, DL and DR count as 1 defender each, DMC, DML and DMR count as 1/2 defender each
    formation_A['def_bonus'] =  sum(1 for v in team_A_lineup.values() if v in D)
    formation_A['def_bonus'] +=  sum(1 for v in team_A_lineup.values() if v in DM) / 2
    formation_B['def_bonus'] =  sum(1 for v in team_B_lineup.values() if v in D)
    formation_B['def_bonus'] +=  sum(1 for v in team_B_lineup.values() if v in DM) / 2

    # if a team has less than 2 DC it will have an added penalty
    if sum(1 for v in team_A_lineup.values() if v in ['DC','DCL','DCR']) < 2:
        formation_A['def_bonus'] -= 1
    if sum(1 for v in team_B_lineup.values() if v in ['DC','DCL','DCR']) < 2:
        formation_B['def_bonus'] -= 1

    # calculate midfield bonus based on number of midfielders
    # MC, ML and MR count as 1 midefielder each, DMC, DML, DMR, AML, AMR and AMC count as 1/2 midfielder each
    formation_A['mid_bonus'] =  sum(1 for v in team_A_lineup.values() if v in M)
    formation_A['mid_bonus'] +=  sum(1 for v in team_A_lineup.values() if v in DM) / 2
    formation_A['mid_bonus'] +=  sum(1 for v in team_A_lineup.values() if v in AM) / 2
    formation_B['mid_bonus'] =  sum(1 for v in team_B_lineup.values() if v in M)
    formation_B['mid_bonus'] +=  sum(1 for v in team_B_lineup.values() if v in DM) / 2
    formation_B['mid_bonus'] +=  sum(1 for v in team_B_lineup.values() if v in AM) / 2

    # calculate attacking bonus based on number of attackers
    # each FC count as 1 attacker, AMC, AML and AMR count as 1/2 attacker each
    formation_A['att_bonus'] =  sum(1 for v in team_A_lineup.values() if v in F)
    formation_A['att_bonus'] +=  sum(1 for v in team_A_lineup.values() if v in AM) / 2
    formation_B['att_bonus'] =  sum(1 for v in team_B_lineup.values() if v in F)
    formation_B['att_bonus'] +=  sum(1 for v in team_B_lineup.values() if v in AM) / 2

    # set min and max values
    formation_A['def_bonus'] = (cap_this(formation_A['def_bonus'],2,5) - 4)
    formation_B['def_bonus'] = (cap_this(formation_B['def_bonus'],2,5) - 4)
    formation_A['mid_bonus'] = (cap_this(formation_A['mid_bonus'],3,5.5) - 4)
    formation_B['mid_bonus'] = (cap_this(formation_B['mid_bonus'],3,5.5) - 4)
    formation_A['att_bonus'] = (cap_this(formation_A['att_bonus'],0,3) - 2)
    formation_B['att_bonus'] = (cap_this(formation_B['att_bonus'],0,3) - 2)


    data.BONUS[data.team_A.name] = (formation_A['att_bonus'] - formation_B['def_bonus'])*0.5
    data.BONUS[data.team_A.name+' mid'] = (formation_A['mid_bonus'] - formation_B['mid_bonus'])*0.25
    data.BONUS[data.team_B.name+' mid'] = (formation_B['mid_bonus'] - formation_A['mid_bonus'])*0.25
    data.BONUS[data.team_B.name] = (formation_B['att_bonus'] - formation_A['def_bonus'])*0.5

    return formation_A, formation_B


# defines the function for duels (player1 stat vs player2 stat)
DIFF_FUNCTION = 'linear2'
    
def get_duel_rating(attack_rating, defense_rating):
    """Sets the function between attacking and defending rating.
    linear: each point increases the success rate by 1%
    linear_half: each point increases the success rate by 0.5%
    progressive: each point below 5 increases the success rate by 1%, then each point increases 0.5% the sucess rate

    Returns:
    --------
    diff: float
        How much does the difference in attacking and defensive rating weights on the final success rate of an event 
    """
    def linear1(attack_rating, defense_rating):
        return attack_rating - defense_rating

    def linear2(attack_rating, defense_rating):
        return (attack_rating - defense_rating)*1.5

    def linear_half(attack_rating, defense_rating):
        return (attack_rating - defense_rating)/2

    def progressive(attack_rating, defense_rating):
        diff = attack_rating - defense_rating
        if diff > 5:
            diff = 5 + (diff-5)/2
        return diff

    diff = locals()[DIFF_FUNCTION](attack_rating,defense_rating)  
    return diff


def ball_possession() -> float:
    """
    Calculates the ball possession percentage for each team based on the active player's stats and formation.
    """

    # temporary variables to help the calculus
    rating = 0
    ratingA = 0
    ratingB = 0
    counterA = 0
    counterB = 0
    ratingA_goalkeeper = 0
    ratingB_goalkeeper = 0

    full_lineup = {**data.team_A.lineup, **data.team_B.lineup}

    for key, value in full_lineup.items():

        player = Player.get_player(int(key))

        if full_lineup[key] != 'GK':

            rating = 0
            for stat in ['passing','technique','tackle','positioning','speed']:
                rating += getattr(player,stat)*ball_possession_table.at[value,stat]*energy_impact(player.stamina)

            if player.team == data.team_A.name:
                counterA += 1
                ratingA += rating

            else:
                assert player.team == data.team_B.name, f"Player's team is not B... we got: {player.team}"
                counterB += 1
                ratingB += rating

        else:

            assert full_lineup[key] == 'GK', f"Player's position is not 'GK'': {full_lineup[key]}"
            if player.team == data.team_A.name:
                ratingA_goalkeeper = get_player_stat(player, 'passing')
            else:
                assert player.team == data.team_B.name, f"Player's team is not B... we got: {player.team}"
                ratingB_goalkeeper = get_player_stat(player, 'passing')


    ratingA = (ratingA/10) * 0.96 + ratingA_goalkeeper * 0.04 
    ratingB = (ratingB/10) * 0.96 + ratingB_goalkeeper * 0.04
    
    ball_possession =  50 + (ratingA - ratingB) * 1

    #ball_possession += (data.team_A.formation_bonus['mid_bonus'] - 4) * 6
    #ball_possession -= (data.team_B.formation_bonus['mid_bonus'] - 4) * 6


   # home team gains 4% bonus
   # ball_possession += 4
    ball_possession = cap_this(ball_possession,25,75)

    return ball_possession / 100


def generator_time() -> Generator[int, None, None]:
    """
    Generator to advance time in steps of one minute.
    """
    num = 0
    while True:
        yield num
        num += 1 


def cap_this(value: float, min: float , max: float=min) -> float:
    """
    Ensures a given value is within a given min and max cap.
    """

    if value < min:
        value = min
    elif value > max:
        value = max

    return value


def update_event_report(t: int, label: list, value: str):
    pass


def update_energy(func_type: str, player_list: list=[]) -> None:
    """
    Handles all changes on player's energy: drain, recharge, refill. 
    The first argument is the name of the required function to call ('time_drain', 'halftime', 'refill', 'players list')
    """

    def energy_depletion_rate(stamina: float) -> float:
        """
        Calculates and returns the energy depletion per minute for a player with a given stamina attribute.
        """
        min_depletion = 4.5
        max_stamina = 80
        increment = 0.35
        energy_depletion = min_depletion + ((max_stamina - stamina)*increment)/5
        return energy_depletion/5

    # new upgraded mode
    def all() -> None:
        """
        Drains a small ammount of energy on all active players. It should be run every minute. Some positions burn energy faster.
        """
        full_lineup = {**data.team_A.lineup, **data.team_B.lineup}    
        
        for player_id in full_lineup:
            player = Player.get_player(player_id)
            depletion = energy_depletion_rate(player.stamina)
            if full_lineup[player_id] in ['DL','DR','DML','DMR']:
                depletion = depletion*1.04
            #elif full_lineup[player_id] in ['DL','DR','ML','MR']:
            #    depletion = depletion*0.95
            elif full_lineup[player_id] in ['DC','DCL','DCR','DMC','DMCL','DMCR','AMC','AMCL','AMCR','FC','FCR','FCL']:
                depletion = depletion*0.96
            elif full_lineup[player_id] == 'GK':
                depletion = depletion*0.6

            player.energy -= depletion

            if player.energy < 0 :
                player.energy = 0


    def halftime() -> None:
        """
        Recharges a small amount of the energy to all players in the field (to be used half time and before extra-time)

        Amount recharged: 20
        """
        full_lineup = {**data.team_A.lineup, **data.team_B.lineup}    
        
        for player_id in full_lineup:
            player = Player.get_player(player_id)
            player.energy += 20

            if player.energy > 100:
                player.energy = 100


    def refill() -> None:
        """
        Resets the energy of all players from both teams to 100. It should be run after every match.
        """
        for player_id in data.team_A.players:
            player = Player.get_player(player_id)
            player.energy = 100
        for player_id in data.team_B.players:        
            player = Player.get_player(player_id)
            player.energy = 100


    def update_energy_players(player_list: list):
        """
        Drains a small ammount of energy from the players in the given list. This should run every time a player participates in an action.
        """
        factor = 0.0
        for player in player_list:
        # the energy depleted will be a fraction of the normal energy depletion rate per minute
            player.energy -= energy_depletion_rate(player.stamina)*factor
            if player.energy < 0 :
                player.energy = 0


    # if there's a player_list, then update the energy on those players
    if player_list:
        update_energy_players(player_list)
    # else call the function given the arg str
    else:
        locals()[func_type]()


def energy_impact(energy: float) -> float:
    """
    Given a player's energy, it returns a multiplier that will impacts the all the player's stats.
    Low energy can impact a player's stats by a maximum of 20% (multiplier = 0.8).
    """
    max_energy_level1 = 45
    min_energy_level1 = 20

    max_energy_level2 = 20
    min_energy_level2 = 0
    
    a_level2 = 0.8
    b_level2 = 0.9

    a_level1 = 0.9
    b_level1 = 1
    result = 0

    if energy < min_energy_level1:
        result = a_level2 + (energy-min_energy_level2)*(b_level2-a_level2)/(max_energy_level2-min_energy_level2)

    elif energy < max_energy_level1:
        result = a_level1 + (energy-min_energy_level1)*(b_level1-a_level1)/(max_energy_level1-min_energy_level1)

    else:
        result = 1

    if result > b_level1:
        result = b_level1
    elif result < a_level2:
        result = a_level2

    return result


def update_rating(player_id: int, action: str) -> None:
    """
    Updates the rating of a player based on a given action.

    Parameters:
    ----------.
    player_id: int
        the id of the player
    action: str
        the action the player commited
    """
    data.players_report.at[player_id,'Rating'] += RATING_DICT[action]
    data.players_report.at[player_id,'Rating'] = cap_this(data.players_report.at[player_id,'Rating'],1,10)


def update_rating_v2(attacker_id: int, defender_id: int, success_rate: float, success: bool) -> None:
    """
    Updates the rating of a player based on the success rate if his action

    Parameters
    ----------
    attacker_id : int 
    defender_id : int
    success_rate : float 
        if success_rate < 0 -> attacker lost the duel
    """
    if success:
        factor = 1-(success_rate/100)

    else:   
        factor = -success_rate/100

    multiplier = 1

    data.players_report.at[attacker_id,'Rating'] += multiplier * factor
    data.players_report.at[defender_id,'Rating'] -= multiplier * factor
    data.players_report.at[attacker_id,'Rating'] = cap_this(data.players_report.at[attacker_id,'Rating'],1,10)
    data.players_report.at[defender_id,'Rating'] = cap_this(data.players_report.at[defender_id,'Rating'],1,10)



def get_player_stat(player: Player, stat: str) -> float:
    """
    Returns the player's stat after applying the effect of energy (if it's below a threshold)
    """
    return getattr(player,stat)*energy_impact(player.energy)



# generate events based on base rate and data.players_report' mentality
# returns True or False
def event_exist() -> bool:

    # initiates bonus and multiplier counter
    bonus = 0
    multiplier = 1

    mentality_team_A = data.team_A.mentality
    mentality_team_B = data.team_B.mentality

    # team A mentality
    if mentality_team_A == "All Out Attacking": # all out attacking
        bonus += MENTALITY_A3
    elif mentality_team_A == "Attacking": # attacking
        bonus += MENTALITY_A2   
    elif mentality_team_A == "Slightly Attacking": # slightly attacking
        bonus += MENTALITY_A1
    elif mentality_team_A == "Slightly Defensive": # slightly defensive
        bonus += MENTALITY_D1
    elif mentality_team_A == "Defensive": # defensive
        bonus += MENTALITY_D2
    elif mentality_team_A == "All Out Defensive": # all out defensive
        bonus += MENTALITY_D3
    
    # team B mentality
    if mentality_team_B == "All Out Attacking": # all out attacking
        bonus += MENTALITY_A3
    if mentality_team_B == "Attacking": # attacking
        bonus += MENTALITY_A2   
    if mentality_team_B == "Slightly Attacking": # slightly attacking
        bonus += MENTALITY_A1
    if mentality_team_B == "Slightly Defensive": # slightly defending
        bonus += MENTALITY_D1
    if mentality_team_B == "Defensive": # deffending
        bonus += MENTALITY_D2
    if mentality_team_B == "All Out Defensive": # all out deffending
        bonus += MENTALITY_D3

    # hard cap of -60%, in case both teams are playing All Out Defensive
    if bonus < -60:
        bonus = -60

    # the multiplier will be applied diretcly on the base event rate 
    multiplier = (100+bonus)/100

    # initiates event
    event = False
    # returns True if event was generated or False if not
    if random.random()*100 < EVENT_RATE*multiplier:
        event = True

    return event


# sets the Event Type, based on the strategy of the team
# team = 'A' or 'B'
def get_event_type(strategy: str) -> str:
    """ Sets the event type based on the attacking team's strategy
    Strategies: Balanced, Short Pass, Direct, Wings, Long Ball
    """
    # initiates event_type
    event_type = ""

    # generate random percentage
    r = random.random()*100

    sampleList = ["Short Pass", "Direct", "Wings", "Long Ball"]
    weights_balanced = [0.25,0.25,0.25,0.25] 
    weights_shortpass = [0.64,0.12,0.12,0.12] 
    weights_direct = [0.12,0.64,0.12,0.12] 
    weights_wings = [0.12,0.12,0.61,0.12] 
    weights_longball = [0.12,0.12,0.12,0.64] 

    # define and return the event type based on the strategy of the team
    if strategy == "Balanced":
        event_type = random.choices(sampleList, weights_balanced)[0]

    elif strategy == "Short Pass":
        event_type = random.choices(sampleList, weights_shortpass)[0]

    if strategy == "Direct":
        event_type = random.choices(sampleList, weights_direct)[0]

    if strategy == "Wings":
        event_type = random.choices(sampleList, weights_wings)[0]
 
    if strategy == "Long Ball":
        event_type = random.choices(sampleList, weights_longball)[0]

    return event_type


def get_top_headers(team_lineup: dict, n: int=1, taker_id: int=None) -> tuple:
    """Get the top n headers from a team

    Parameters:
    -----------
    team_lineup: dict
    n: int
    taker_id: int
    
    Returns:
    --------
    player_list: list
    average: float
    """
    player_dict = {}
    player_list = []
    stored_value = 101
    playerid_to_remove = None
    average = 0

    for player_id in team_lineup: 

        # if the player iteration is the taker or the gk, skip
        if player_id == taker_id or team_lineup[player_id] == 'GK':
            continue

        player = Player.get_player(player_id)
        if len(player_dict) < n:
            player_dict[player_id] = {'player': player, 'heading':player.heading}
            if stored_value > player.heading:
                stored_value = player.heading
                playerid_to_remove = player_id

        else: 
            if player.heading > player_dict[playerid_to_remove]['heading']:                        
                del player_dict[playerid_to_remove]
                player_dict[player_id] = {'player': player, 'heading':player.heading}
                stored_value = player.heading  
                playerid_to_remove = player_id

                for playerid_stored in player_dict:
                    if stored_value > player_dict[playerid_stored]['heading']:
                        stored_value = player_dict[playerid_stored]['heading']
                        playerid_to_remove = playerid_stored

    for key in player_dict:
        average += player_dict[key]['heading']
        player_list.append(player_dict[key]['player'])
    
    average = average / n

    return (player_list, average)


def remove_player_from_lineup(player: Player):

    if isinstance(player, Player.Goalkeeper):
        print("Can't remove Goalkeeper")

    else:
        if player.team == data.team_A.name:
            del data.team_A.lineup[player.id]
        elif player.team == data.team_B.name:
            del data.team_B.lineup[player.id]
    data.players_report.at[player.id,'Status'] = 'sent off'


########################################################################################################################
###                                   Fouls and Cards                                                               ####
########################################################################################################################


def check_card(card_rate,yellow_rate) -> str:
    """Check if a foul will lead to card (yellow or red)
    
    Parameters
    ----------
    card_rate : float
        The probability of getting a card
    yelow_rate : floar
        The probability of getting a yellow card if there's a card

    Returns
    -------
    card: str
        card is in ['Yellow Card', 'Red Card', 'None']
    """

    r = random.random()
    card = None
    # if card
    if r < (card_rate):
        # if yellow card
        if r < (card_rate * yellow_rate):
            card = 'Yellow Card'
        # if red card
        else:
            card = 'Red Card' 

    return card    

def check_foul(defender: Player, zone: str='0') -> str:
    """Check if there is a foul and respective card.

    TODO this function should first pick a player based on how aggressive he is (likeliness to commit foul and get card)
    and then see if there's foul and card based on foul rate and card rate of the player himself.
    foul_rate = foul_rate * 1+(defender.aggressiveness)
    card_rate = card_rate * 1+(defender.aggressiveness)

    Parameters
    ----------
    defender : Player
        The player that might make a foul
    zone : float
        The zone where the action is taking place. Default value refers to zone 0 (no event)

    Returns
    -------
    outcome : str = None or 'Foul' or 'Yellow Card' or 'Second Yellow', or 'Red Card'
    """
    
    outcome = None
    foul_rate = FOUL_RATE                       # base % chance of a foul
    yellow_rate = YELLOW_RATE                   # chance of yellow if there is a card
    card_rate = CARD_RATE_zone_1_2

    if zone == '0':
        foul_rate = FOUL_RATE_no_event                     # base % chance of a foul per minute
        card_rate = CARD_RATE_no_event                   # card rate
        yellow_rate = YELLOW_RATE_no_event                  # chance of yellow if there is a card
    elif '2' in zone:
        zone = '2'
    elif '3' in zone:
        zone = '3'
    if zone in ['3','4']:
        card_rate = CARD_RATE_zone_3_4
    elif zone == '5':
        card_rate = CARD_RATE_zone_5           

    r = random.random()
    # if foul
    if r < foul_rate:
        data.players_report.at[defender.id,'Foul'] += 1
        data.players_report.at[defender.id,'Total Actions'] += 1
        data.report.at['Fouls',defender.team] += 1
        data.report.at['Fouls Zone'+zone,defender.team] += 1
        outcome = 'Foul'
        card = check_card(card_rate, yellow_rate)

        if card:

            if card == 'Yellow Card':
                
                pardon = 0.75
                # if the player already has a yellow there's a {pardon} chance to not see the second yellow
                if data.players_report.loc[defender.id,'Yellow Card'] == 1 and random.random() < pardon and zone not in ['4','5']:
                    return outcome
                
            data.players_report.loc[defender.id,card] += 1
            data.report.at[card,defender.team] += 1
            update_rating(defender.id,card) 

            if data.players_report.loc[defender.id,'Yellow Card'] == 2:
                card = 'Second Yellow' 
                data.players_report.loc[defender.id,'Red Card'] += 1
                data.report.at[card,defender.team] += 1
                update_rating(defender.id,'Second Yellow')      

            #if card == 'Second Yellow' or card == 'Red Card':
                #remove_player_from_lineup(defender) 

            outcome = card

    return outcome         


########################################################################################################################
###                                   Get Players                                                                   ####
########################################################################################################################



# get a random player from a given team
# returns the player id (which is the index of the dataframe data.players_report)
def get_random_player(team_lineup: dict) -> Player:
    """
    Returns a random player from a given lineup, excluding the Goalkeeper
    """
    player_id = random.choice([key for key, value in team_lineup.items() if (value != 'GK')])
    
    return Player.get_player(player_id)


def get_random_player_from_positionslist(team_lineup: dict, positions: list, positions_b: list=None, player1_id: int=None, rate: float=0.9) -> Player:

    player = None
    player_sample = []

    if positions_b == None:
        positions_b = positions + ['MC','MCL','MCR','DMC','DMCL','DMCR','AMC','AMCL','AMCR']

    if random.random() < rate:
        player_sample = [key for key, value in team_lineup.items() if (value in positions) and key != player1_id]

    else:
        player_sample = [key for key, value in team_lineup.items() if (value in positions_b) and key != player1_id]

    if not player_sample:
        player_sample = [key for key, value in team_lineup.items() if ((key != player1_id) and (value != 'GK'))]

    player = Player.get_player(random.choice(player_sample))

    return player

# get the defender marking a specific zone
# returns the player (object Player)
def get_defender(team_lineup: dict, zone: str, player1_id: int=None) -> Player:
    global D,DM,M,AM,F,LEFT,CENTER_L,CENTER,CENTER_R,RIGHT

    r = random.random()
    player_sample = []

    if zone == '1':

        if r < 0.4:
            player_sample = [key for key, value in team_lineup.items() if ('DMC' in value) and key != player1_id]
        
        elif r < 0.8:
            player_sample = [key for key, value in team_lineup.items() if ('MC' in value) and key != player1_id]
  
        else:
            player_sample = [key for key, value in team_lineup.items() if ('DC' in value) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (DM+M+AM)) and key != player1_id]
       
    elif zone == '2l':
        
        if r < 0.6:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMR','MR']) and key != player1_id]

        elif r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['MCR','MC','DMC','DMCR','DR','AMR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in RIGHT) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if value in (list(set(DM+M).intersection(CENTER+CENTER_R+RIGHT))+['DR']) and key != player1_id]
         
    elif zone == '2r':
        
        if r < 0.6:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DML','ML']) and key != player1_id]

        elif r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['MCL','MC','DMC','DMCL','DL','AML']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in RIGHT) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if value in (list(set(DM+M).intersection(CENTER+CENTER_L+LEFT))+['DL']) and key != player1_id]
         
    elif zone == '3l':
        
        if r < 0.75:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMR']) and key != player1_id]
        
        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['MR','DMCR','DMC']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DCR','MC','MCR','MR','DMCR','DMC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in set(D+DM+M).intersection(RIGHT+CENTER_R)) and key != player1_id]

    elif zone == '3r':
        
        if r < 0.75:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DL','DML']) and key != player1_id]
        
        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['ML','DMCL','DMC']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DCL','MC','MCL','DMCL','ML','DMCL','DMC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in set(D+DM+M).intersection(LEFT+CENTER_L)) and key != player1_id]

    elif zone == '4':
        
        if r < 0.5:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL','DCR']) and key != player1_id]
        
        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DCMl','DMCR','DC','DCL','DCR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in (D+DM+M)) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (D+DM+M)) and key != player1_id]


    elif zone == '5':
        
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL','DCR']) and key != player1_id]
        
        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DCMl','DMCR','DC','DCL','DCR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in (D+DM+M)) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (D+DM+M)) and key != player1_id]

    elif zone == 'Cross':
        
        if r < 0.75:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL','DCR']) and key != player1_id]
        
        elif r < 0.95:
            player_sample = [key for key, value in team_lineup.items() if (value in ['GK','DC','DCL','DCR','DMC','DCMl','DMCR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['GK','MC','MCL','MCR','DL','DML','DR','DMR',]) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (D+DM+'GK')) and key != player1_id]

    if not player_sample:
        player_sample = [key for key, value in team_lineup.items() if (value not in ['GK']) and key != player1_id]

    player = Player.get_player(random.choice(player_sample))

    return player

# get the defender marking a specific zone
# returns the player (object Player)
def get_attacker(team_lineup: dict, zone: str, player1_id = None) -> Player:


    r = random.random()
#    df = data.players_report.loc[ (data.players_report['team'] == opposite_team.name) & (data.players_report['status'] == 'on') & (data.players_report['position'] != 'GK') & (data.players_report['position'] != 'FC')].sample()
    player_sample = []

    if zone == '1':

        if r < 0.5:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMC','AMCR','AMCL']) and key != player1_id]
        
        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMC','AMCR','AMCL','MC','MCL','MCR']) and key != player1_id]
            
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['FC','FCL','FCR','MR','ML','DMC','DMCL','DMCR','AML','AMR']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (F+AM+M+DM)) and key != player1_id]

    elif zone == '2l':
        
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AML','ML']) and key != player1_id]

        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DL','DML','AMCL']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DL','DML','AMCL','MCL','FCL','MC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (list(set(CENTER_L+CENTER).intersection(F+AM+M))+LEFT)) and key != player1_id]                  

    elif zone == '2r':
        
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMR','MR']) and key != player1_id]

        elif r < 0.9:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMR','AMCR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMR','AMCR','MCR','FCR','MC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (list(set(CENTER_R+CENTER).intersection(F+AM+M))+RIGHT)) and key != player1_id]                  

    elif zone == '3l':
        
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AML','ML']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DL','DML','AMCL','FCL','MCL','MC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (list(set(CENTER_L+CENTER).intersection(F+AM+M))+LEFT)) and key != player1_id]                  

    elif zone == '3r':
        
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMR','MR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMR','AMCR','FCR','MCR','MC']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (list(set(CENTER_R+CENTER).intersection(F+AM+M))+RIGHT)) and key != player1_id]                  

    elif zone == '4':
        
        if r < 0.75:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMC','FC','AMCL','AMCR','FCL','FCR']) and key != player1_id] 
        
        elif r < 0.95:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMR','AML','MC','MCL','MCR']) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['ML','MR','DMR','DML','DL','DR']) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (F+AM+M+['DL','DR','DML','DMR'])) and key != player1_id]

    elif zone == '5':
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in F) and key != player1_id] 
        
        elif r < 0.95:
            player_sample = [key for key, value in team_lineup.items() if (value in F+AM) and key != player1_id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in [M]) and key != player1_id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in (F+AM+M+['DL','DR','DML','DMR'])) and key != player1_id]

    if not player_sample:
        player_sample = [key for key, value in team_lineup.items() if (value != 'GK') and key != player1_id] 

    player = Player.get_player(random.choice(player_sample))

    return player

# get the defender that should be marking a given attacker
# returns the player (object Player)
def get_direct_marker(attacker, defender):

    player_position = ""
    team_lineup = {}
    if defender.team == data.team_A.name:
        team_lineup = data.team_A.lineup
        player_position = data.team_B.lineup[attacker.id]

    elif defender.team == data.team_B.name:
        team_lineup = data.team_B.lineup
        player_position = data.team_A.lineup[attacker.id]

    else:
        print("ERROR: team_name not identified")

    player_sample = []

    r = random.random()
#    df = data.players_report.loc[ (data.players_report['team'] == opposite_team.name) & (data.players_report['status'] == 'on') & (data.players_report['position'] != 'GK') & (data.players_report['position'] != 'FC')].sample()

    if player_position == "AML": 
        if r < 0.8:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMR','MR']) and key != defender.id]

        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['AMR','DR','DMR','MR','MCR,DMCR']) and key != defender.id]

        if not player_sample:
            player_sample = [key for key, value in team_lineup.items() if (value in set(D+DM+M).intersection(CENTER_R+RIGHT)) and key != defender.id]

    if player_position == "AMCL": 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['MCR','DMCR']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR','DMC','MR','DR','DMR']) and key != defender.id]

    if player_position == "AMCR": 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['MCL','DMCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL','DMC','ML','DL','DML']) and key != defender.id]

    elif player_position == "AMR": 
        
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DL','DML']) and key != defender.id]
        
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR','DMC','DMCR','ML']) and key != defender.id]

    elif player_position == "AMC": 
        
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCL','DMCR']) and key != defender.id]
            
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL','DCR','MC','MCL','MCR']) and key != defender.id]

    elif player_position == "FC": 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR','DCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCL','DMCR']) and key != defender.id]


    elif player_position == "FCL": 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCR','DR']) and key != defender.id]

    elif player_position == "FCR": 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCL','DL']) and key != defender.id]

               
    elif player_position == "MC": 
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCL','DMCR','MC','MCR','MCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR','DCL']) and key != defender.id]

    elif player_position == "MCL": 
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCR','MC','MCR']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCR']) and key != defender.id]

    elif player_position == "MCR": 
        if r < 0.7:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMC','DMCL','MC','MCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DC','DCL']) and key != defender.id]

    if player_position in ['DML', 'DL']: 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DMR','MR','DMCR']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DR','DMC','MCR','MC']) and key != defender.id]
    if player_position in ['DMR', 'DR']: 
        if r < 0.85:
            player_sample = [key for key, value in team_lineup.items() if (value in ['DML','ML','DMCL']) and key != defender.id]
        else:
            player_sample = [key for key, value in team_lineup.items() if (value in ['Dl','DMC','MCL','MC']) and key != defender.id]

    if not player_sample:
        player_sample = [key for key, value in team_lineup.items() if (value not in ['GK','FC','FCL','FCR']) and key != defender.id]

    player = Player.get_player(random.choice(player_sample))

    return player

# get the zone to where the ball goes based on the event type
def get_zone(event_type: str) -> str:

    zone = "0"
    r = random.random()

    zone_rate = {"Short Pass" : [85,15,0,0],\
                "Direct" : [75,15,0,0],\
                "Wings" : [0,100,0,0],\
                "Long Ball" : [60,30,5,5]}

    assert event_type in ["Short Pass", "Direct", "Wings", "Long Ball"], f"event type is not recognizable"

    weights = zone_rate[event_type]
    zone = random.choices(['1','2','3','4'],weights)[0]

    if zone == '2':
        zone = random.choices(['2l','2r'])[0]

    elif zone == '3':
        zone = random.choices(['3l','3r'])[0]

    return zone

########################################################################################################################
###                                   Duels                                                                         ####
########################################################################################################################

def duel_shortpass(attacker1: Player, attacker2: Player, defender1: Player, defender2: Player) -> float:

    passing_att = ( get_player_stat(attacker1,'passing') + get_player_stat(attacker2,'passing') )/2
    technique_att = ( get_player_stat(attacker1,'technique') + get_player_stat(attacker2,'technique') )/2
    positioning_def = ( get_player_stat(defender1,'positioning') + get_player_stat(defender2,'positioning') )/2
    tackle_def = ( get_player_stat(defender1,'tackle') + get_player_stat(defender2,'tackle') )/2

    attack_rating = passing_att*0.5 + technique_att*0.5
    defense_rating = positioning_def*0.5 + tackle_def*0.5

    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_direct(attacker1: Player, attacker2: Player, defender1: Player, defender2: Player) -> float:

    passing_att = get_player_stat(attacker1,'passing')
    speed_att = get_player_stat(attacker2,'speed')
    technique_att = get_player_stat(attacker2,'technique')

    speed_def = get_player_stat(defender2,'speed')
    positioning_def = get_player_stat(defender1,'positioning')*0.5 + get_player_stat(defender2,'positioning')*0.5

    attack_rating = passing_att*0.4 + speed_att*0.4 + technique_att*0.2
    defense_rating = speed_def*0.6 + positioning_def*0.4

    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_wings(attacker1: Player, attacker2: Player, defender1: Player, defender2: Player) -> float:

    speed_att = ( get_player_stat(attacker1,'speed') + get_player_stat(attacker2,'speed') )/2
    technique_att = ( get_player_stat(attacker1,'technique') + get_player_stat(attacker2,'technique') )/2
    speed_def = ( get_player_stat(defender1,'speed') + get_player_stat(defender2,'speed') )/2
    tackle_def = ( get_player_stat(defender1,'tackle') + get_player_stat(defender2,'tackle') )/2

    attack_rating = technique_att*0.5 + speed_att*0.5
    defense_rating = speed_def*0.5 + tackle_def*0.5

    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)

    return diff

def duel_longball(attacker1: Player, attacker2: Player, defender2: Player) -> float:
    passing_att = get_player_stat(attacker1,'passing')
    heading_att = get_player_stat(attacker2,'heading')
    heading_def = get_player_stat(defender2,'heading')
    positioning_def = get_player_stat(defender2,'positioning')

    attack_rating = passing_att*0.4 + heading_att*0.6
    defense_rating = heading_def*0.75 + positioning_def*0.25

    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    
    return diff

def duel_pre_longshot(attacker1: Player, defender1: Player) -> float: 
    attack_rating = get_player_stat(attacker1,'longshot')
    defense_rating = get_player_stat(defender1,'positioning')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_pre_shot(attacker1: Player, defender1: Player) -> float: 
    attack_rating = get_player_stat(attacker1,'finishing')
    defense_rating = get_player_stat(defender1,'positioning')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_pre_cross(attacker1: Player, defender1: Player) -> float: 
    attack_rating = get_player_stat(attacker1,'crossing')
    defense_rating = get_player_stat(defender1,'positioning')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_dribble(attacker1: Player, defender1: Player) -> float: 
    attack_rating = get_player_stat(attacker1,'technique')
    defense_rating = get_player_stat(defender1,'tackle')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_speed_dribble(attacker1: Player, defender1: Player) -> float:     
    attack_rating = (get_player_stat(attacker1,'technique') + get_player_stat(attacker1,'speed'))/2
    defense_rating = (get_player_stat(defender1,'tackle') + get_player_stat(defender1,'speed'))/2
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_pass(attacker1: Player, defender1: Player) -> float: 
    attack_rating = get_player_stat(attacker1,'passing')
    defense_rating = get_player_stat(defender1,'positioning')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_pass_onetwo(attacker1: Player, attacker2: Player, defender1: Player, defender2: Player) -> float: 
    attack_rating = (get_player_stat(attacker1,'passing')+get_player_stat(attacker2,'passing') \
        + get_player_stat(attacker1,'technique')+get_player_stat(attacker2,'technique'))/4
    defense_rating = (get_player_stat(defender1,'positioning') + get_player_stat(defender1,'tackle') \
        + get_player_stat(defender2,'positioning') + get_player_stat(defender2,'tackle'))/4    
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_throughpass(attacker1: Player, attacker2: Player, defender2: Player) -> float: 
    attack_rating = (get_player_stat(attacker1,'passing') + get_player_stat(attacker2,'speed'))/2
    defense_rating = (get_player_stat(defender2,'positioning') + get_player_stat(defender2,'speed'))/2
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_throughpass_goalkeeper(attacker1: Player, attacker2: Player, goalkeeper: Player.Goalkeeper) -> float: 
    attack_rating = (get_player_stat(attacker1,'passing')+get_player_stat(attacker2,'speed'))/2
    defense_rating = get_player_stat(goalkeeper,'oneonone')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_cross(attacker1: Player, defender1: Player, goalkeeper: Player.Goalkeeper) -> float: 
    attack_rating = get_player_stat(attacker1,'crossing')
    defense_rating = (get_player_stat(defender1,'heading') + get_player_stat(goalkeeper,'aerial'))/2
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_finalization_header(attacker: Player, goalkeeper: Player.Goalkeeper) -> float: 
    attack_rating = get_player_stat(attacker,'heading')
    defense_rating = (get_player_stat(goalkeeper,'aerial')*0.75 + get_player_stat(goalkeeper,'reflexes')*0.25 )
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff

def duel_finalization_longshot(attacker: Player, goalkeeper: Player.Goalkeeper) -> float:  
    attack_rating = get_player_stat(attacker,'longshot')
    defense_rating = get_player_stat(goalkeeper,'agility')*0.7 + get_player_stat(goalkeeper,'reflexes')*0.1 + get_player_stat(goalkeeper,'positioning')*0.2 
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff 
        
def duel_finalization_shot(attacker: Player, goalkeeper: Player.Goalkeeper) -> float: 
    attack_rating = get_player_stat(attacker,'finishing')
    defense_rating = get_player_stat(goalkeeper,'reflexes')*0.7 + get_player_stat(goalkeeper,'positioning')*0.3    
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff 

def duel_finalization_isolated(attacker: Player, goalkeeper: Player.Goalkeeper) -> float:  
    attack_rating =  get_player_stat(attacker,'finishing')*0.7 + get_player_stat(attacker,'technique')*0.3
    defense_rating = get_player_stat(goalkeeper,'oneonone')
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff 

def duel_freekick(taker: Player, goalkeeper: Player.Goalkeeper) -> float:
    taker_rating =  get_player_stat(taker,'finishing')*0.7 + get_player_stat(taker,'technique')*0.3
    save_rating = get_player_stat(goalkeeper,'agility')*0.5 + get_player_stat(goalkeeper,'command')*0.25 + get_player_stat(goalkeeper,'positioning')*0.25
    diff = get_duel_rating(taker_rating,save_rating)
    diff = cap_this(diff,-15,15)
    return diff 

def duel_penalty(taker: Player, goalkeeper: Player.Goalkeeper) -> float:
    taker_rating =  max(get_player_stat(taker,'longshot'),get_player_stat(taker,'finishing'))*0.7 + get_player_stat(taker,'technique')*0.3
    save_rating = get_player_stat(goalkeeper,'penalty')
    diff = get_duel_rating(taker_rating,save_rating)
    diff = cap_this(diff,-15,15)
    return diff 

def duel_corner(attack_rating: float, defense_rating: float, goalkeeper: Player.Goalkeeper, n: int) -> float:
    defense_rating = (defense_rating + (goalkeeper.aerial*0.5 + goalkeeper.aerial*0.5)) / (n+1)
    diff = get_duel_rating(attack_rating,defense_rating)
    diff = cap_this(diff,-15,15)
    return diff


########################################################################################################################
###                                   Checks                                                                        ####
########################################################################################################################

# set if check 1 is successful or failure
# it is set as a linear function of +1% for each 1 point difference in overall
# hard cap at +-20 points difference (+-20%)
# returns True or False
def zone0_check(bonus: float, team_lineup: dict, opposite_team_lineup: dict, event_type: str) -> tuple:
    """Run the entire check 1

    Parameters
    ----------
    team_lineup : dict
        The lineup of the attacking team
    opposite_team_lineup : dict
        The lineup of the defending team
    event_type: str
        The event type (Short Pass, Direct, Wings or Long Ball)

    Returns
    -------
    attacker_1,attacker_2,defender_2,zone,base_success_rate,success: tuple(Player, Player, Player, str, float, bool)
        zone can be None if the check failed
    """
    
    success_table = { '1' : 77.0, '2l' : 77.0, '2r' : 77, '3l': 61.6, '3r': 61.6, '4': 46.2}

    success = False
    defender_action = 'Tackle'
    zone = get_zone(event_type)
    base_success_rate = success_table[zone]

    short_pass_att = ['DC','DL','DR','MC','DMC','DML','DMR','ML','MR']
    short_pass_def = ['ML','MR','MC','AMC','AML','AMR','FC']
    direct_att = ['MC','DMC','DML','DMR','ML','MR']
    direct_def = ['AMC','AML','AMR','FC','MC']
    wings_left_att = ['DL','DML','ML','MC']
    wings_left_def = ['DMR','MR','AMR','MC']
    wings_right_att = ['DR','DMR','MR','MC']
    wings_right_def = ['DML','ML','AML','MC']
    long_ball_att1 = ['GK','DC','DL','DR','DMC','DML','DMR']
    long_ball_att2 = ['AML','AMR','FC','AMC','MC']

    positions_sample = {'Short Pass' : {1: short_pass_att, 2:  short_pass_def},\
                        'Direct': {1: direct_att, 2:  direct_def},\
                        'Wings l': {1: wings_left_att, 2:  wings_left_def},\
                        'Wings r': {1: wings_right_att, 2:  wings_right_def},\
                        'Long Ball': {1: long_ball_att1, 2:  long_ball_att2}
                        }

    if event_type == "Wings":
        if 'l' in zone:
            sub_zone = ' l'
        elif 'r' in zone:
            sub_zone = ' r'

        attacker_1 = get_random_player_from_positionslist(team_lineup,positions_sample[event_type+sub_zone][1])
        attacker_2 = get_attacker(team_lineup,zone,attacker_1.id)
        defender_1 = get_random_player_from_positionslist(opposite_team_lineup,positions_sample[event_type+sub_zone][2])
        defender_2 = get_defender(opposite_team_lineup,zone,defender_1.id)

        diff = duel_wings(attacker_1,attacker_2,defender_1,defender_2)

    elif event_type == "Long Ball":
        
        '''
        Managers should be able to pick a target man.
        The target man will be favoured when selecting a player to receive long balls or any kind of crosses (cross, indirect free kick or corner)

        As an alternative, this code should select the best header from the attack (AML/AMC/AMR/FC) as the target man.
        '''
        attacker_1 = get_random_player_from_positionslist(team_lineup,positions_sample[event_type][1])
        attacker_2 = get_random_player_from_positionslist(team_lineup,'FC',positions_sample[event_type][2],attacker_1)
        defender_2 = get_defender(opposite_team_lineup,zone)

        defender_action = 'Clear'

        diff = duel_longball(attacker_1,attacker_2,defender_2)

    else:

        attacker_1 = get_random_player_from_positionslist(team_lineup,positions_sample[event_type][1])
        attacker_2 = get_attacker(team_lineup,zone,attacker_1)
        defender_1 = get_random_player_from_positionslist(opposite_team_lineup,positions_sample[event_type][2])
        defender_2 = get_defender(opposite_team_lineup,zone,defender_1)
        
        defender_action = 'Interception'

        if event_type == "Short Pass":
            diff = duel_shortpass(attacker_1,attacker_2,defender_1,defender_2) 
        elif event_type == "Direct":
            diff = duel_direct(attacker_1, attacker_2, defender_1, defender_2)


    data.players_report.loc[attacker_1.id,'Total Actions'] += 1
    data.players_report.at[defender_2.id,'Total Actions'] += 1
    # counts the event type in the record
    data.report.at['Events',attacker_1.team] += 1
    data.report.at[event_type,attacker_1.team] += 1

    success_rate = (base_success_rate*(1+bonus)) + diff
    r = random.random()*100
    if r < success_rate:
        data.players_report.at[attacker_1.id,'Pass Success'] += 1
        data.players_report.at[attacker_1.id,'Actions Success'] += 1
        data.players_report.at[defender_2.id,'Actions Fail'] += 1
        data.report.at['Check1 Success',attacker_1.team]
    
        success = True

    else:
        data.players_report.at[attacker_1.id,'Pass Fail'] += 1
        data.players_report.at[attacker_1.id,'Actions Fail'] += 1
        data.players_report.at[defender_2.id,'Actions Success'] += 1
        data.players_report.at[defender_2.id,defender_action] += 1


    return (attacker_1,attacker_2,defender_2,zone,success_rate,success)

# giving an event type, it returns the subsequent action for check1
def get_action_zone1(event_type):
    """Get the action selected on zone 1 based on the event type

    Parameters
    ----------
    event_tye : str
        event type is in ['Short Pass', 'Direct', 'Wings' or 'Long Ball']

    Returns
    -------
    action: str
        action is in ['Long Shot', 'Dribble', 'Pass', 'Through Pass']
    """

    sample_list = ["Long Shot", "Dribble", "Pass", "Through Pass"]
    action = random.choices(sample_list,actions_zone1[event_type])[0]

    return action

# giving an event type, it returns the subsequent action for check2
def get_action_zone2(event_type):
    """Get the action selected on zone 2 based on the event type

    Parameters
    ----------
    event_tye : str
        event type is in ['Short Pass', 'Direct', 'Wings' or 'Long Ball']

    Returns
    -------
    action: str
        action is in ['Cut Inside', 'Early Cross', 'Dribble', 'Pass', 'Through Pass']
    """

    sample_list = ['Cut Inside', 'Early Cross', 'Dribble', 'Pass', 'Through Pass']
    action = random.choices(sample_list,actions_zone2[event_type])[0]

    return action


# giving an event type, it returns the subsequent option for check2
# return option
def get_action_zone3():
    """Get the action selected on zone 3

    Returns
    -------
    action: str
        action is in ["High Cross", "Pass Shot", "Dribble Shot"]
    """
    action = random.choices(actions_zone3['actions_list'],actions_zone3['weights'])[0]
    return action

def get_action_zone4():
    """Get the action selected on zone 4

    Returns
    -------
    action: str
        action is in [""Marked Shot","Dribble Shot","Pass Shot","Dribble Isolated"]
    """
    action = random.choices(actions_zone4['actions_list'],actions_zone4['weights'])[0]
    return action

def pre_long_shot(attacker1: Player, defender1: Player) -> tuple:
    """Checks actions before a Long Shot

    Parameters:
    -----------
    attacker1: Player
    defender1: Player

    Returns:
    --------
    action, attacker1, attacker2, defender2, diff, success : tuple(str,Player,Player,Player,float,bool):
    """

    base_sucess_rate = SUCCESS_RATE['zone1']['long shot']
    success = False
    attacker2 = attacker1
    defender2 = defender1
    diff = 0

    action = random.choices(actions_pre_longshot['actions_list'],actions_pre_longshot['weights'])[0]

    if action == 'Marked Long Shot':
        diff = duel_pre_longshot(attacker1,defender1)

    elif action == 'Dribble Long Shot':
        diff = duel_dribble(attacker1,defender1)

    elif action == 'Pass Long Shot':
        if attacker1.team == data.team_A.name:
            team_lineup = data.team_A.lineup
            opposite_team_lineup = data.team_B.lineup
        elif attacker1.team == data.team_B.name:
            team_lineup = data.team_B.lineup
            opposite_team_lineup = data.team_A.lineup
       
        attacker2 = get_attacker(team_lineup,'5',attacker1)
        defender2 = get_defender(opposite_team_lineup,'4',defender1)
        diff = duel_pass(attacker1,defender2)

    return (action, attacker1, attacker2, defender2, diff, success)

def cross(type,attacker1,defender1):

    assert type in ['Early Cross', 'High Cross', 'Low Cross'], f'Invalid cross type'

    if attacker1.team == data.team_A.name:
        team_lineup = data.team_A.lineup
        opposite_team_lineup = data.team_B.lineup
        goalkeeper_id = data.team_B.goalkeeper
        
    elif attacker1.team == data.team_B.name:
        team_lineup = data.team_B.lineup
        opposite_team_lineup = data.team_A.lineup
        goalkeeper_id = data.team_A.goalkeeper

    assert attacker1.team == data.team_A.name or attacker1.team == data.team_B.name, f"payer's team not recognizable"
    
    goalkeeper = Player.get_player(goalkeeper_id)

    base_sucess_rate = 71
    attacker2 = attacker1
    success = False
    defender2 = get_defender(opposite_team_lineup,'4',defender1.id)
    diff = 0
    new_zone = 'Header'

    if type == 'Low Cross':
        diff = duel_pass(attacker1,defender2)
        new_zone = 'Shot'

    else:
        diff = duel_cross(attacker1,defender2,goalkeeper)
        if type == 'Early Cross':
            base_sucess_rate = 67  

    if random.random()*100 < base_sucess_rate + diff:
        success = True
        attacker2 = get_attacker(team_lineup,'5',attacker1.id)
        update_rating(attacker1.id,'success1')
        com.comment(type,'success',player1=attacker1.name,defender1=defender1.name)
        #update_rating(defender2.id,'fail1')
        #data.players_report.at[defender2.id,'Actions'] += 1

    else:            

        r = random.random()*100
        if r > get_player_stat(attacker1,'crossing') + 10:
            com.comment('Cross','wasted',player1=attacker1.name,defender1=defender2.name)
            update_rating(attacker1.id,'fail2')

        else:

            if r < 15 and  type != 'Low Cross':
                com.comment(type,'GK',player1=attacker1.name,defender1=defender1.name,goalkeeper=goalkeeper.name)
                update_rating(goalkeeper.id,'success1')
                data.players_report.at[goalkeeper.id,'Actions'] += 1

            else:
                com.comment(type,'fail',player1=attacker1.name,defender1=defender2.name)
                update_rating(defender2.id,'success2')
                data.players_report.at[defender2.id,'Actions'] += 1

    data.players_report.at[attacker1.id,'Actions'] += 1

    return success, attacker2, defender2, new_zone

# check outcome of any type of finalization
# returns outcome (blocked / miss / post / save / goal)
def check_shot(type,attacker,goalkeeper_id):

    # initializes the outcome and adds the type of shot to the report dataframe
    outcome = False
    diff = 0
    on_target = 50

    bonus = data.BONUS[attacker.team]

    goalkeeper = Player.get_player(goalkeeper_id)
    data.report.at[type,attacker.team] += 1
    data.players_report.at[attacker.id,'Total Actions'] += 1
    data.report.at['Total Shots',attacker.team] += 1
    data.players_report.at[attacker.id,'Total Shots'] += 1
    data.players_report.at[attacker.id,type] += 1


    if type == 'Header':
        goal_rate = SUCCESS_HEADER
        on_target = 40
        blocked = 5
        # heading vs aerial (0.75) + reflexes (0.25)
        diff = duel_finalization_header(attacker,goalkeeper)
        # if heading > 65 the rate of on-target shot increases by 0.5% for each point above 70
        if attacker.heading > 65:
            on_target += (attacker.heading - 65) * 0.5
        
    if type == 'Long Shot':
        goal_rate = SUCCESS_LONGSHOT
        on_target = 40
        blocked = 15
        # long shot vs agility (0.7) + reflexes (0.1) + positioning (0,2)
        diff = duel_finalization_longshot(attacker,goalkeeper)
        # if longshot > 65 the rate of on-target shot increases by 0.5% for each point above 70
        if attacker.longshot > 65:
            on_target += (attacker.longshot - 65) * 0.5

    if type == 'Shot':
        goal_rate = SUCCESS_SHOT
        on_target = 50
        blocked = 5
        # finishing vs reflexes (0.7) + positioning (0.3)
        diff = duel_finalization_shot(attacker,goalkeeper)

        # if finishing > 65 the rate of on-target shot increases by 0.5% for each point above 70
        if attacker.finishing > 65:
            on_target += (attacker.finishing - 65) * 0.5

    if type == 'Isolated Shot':
        goal_rate = SUCCESS_ISOLATED
        on_target = 50
        blocked = 0
        # finishing(0.7) + technique (0.3) vs one-on-one (1)
        diff = duel_finalization_isolated(attacker, goalkeeper)

        # if finishing > 65 the rate of on-target shot increases by 0.5% for each point above 70
        if attacker.finishing > 65:
            on_target += (attacker.finishing - 65) * 0.5

 
    # if goal
    success_rate = (goal_rate*(1+bonus)) + diff
    if random.random()*100  < success_rate:
        outcome = "Goal"
        data.report.at['Goals from '+type ,attacker.team] += 1
        data.report.at['Goals',attacker.team] += 1
        data.report.at['Shots On Target',attacker.team] += 1
        data.players_report.at[attacker.id,'Goals'] += 1
        data.players_report.at[attacker.id,'Shots On Target'] += 1
        data.players_report.at[attacker.id,'Actions Success'] += 1
        update_rating(attacker.id,'Goal')
        update_rating(goalkeeper.id,'Goal conceived')
        data.players_report.at[goalkeeper.id,'Actions Fail'] += 1
        data.players_report.at[goalkeeper.id,'Total Actions'] += 1


    # if not goal
    else:
        r = random.random()*100
        # on target and save
        if r < on_target:
            outcome = "Save"
            data.report.at['Shots On Target',attacker.team] += 1
            data.players_report.at[attacker.id,'Shots On Target'] += 1
            data.players_report.at[attacker.id,'Actions Success'] += 1
            update_rating(goalkeeper.id,'Save')
            if type == 'Isolated Shot':
                update_rating(goalkeeper.id,'Save Isolated')   
                update_rating(attacker.id,'fail1')
            data.players_report.at[goalkeeper.id,'Actions Success'] += 1
            data.players_report.at[goalkeeper.id,'Total Actions'] += 1
            data.players_report.at[goalkeeper_id,'Save'] += 1
            update_energy('players list',[goalkeeper])

            if random.random()*100 > 40 + get_player_stat(goalkeeper,'handling')*0.5:
                outcome = 'Save2corner'

        # blocked and maybe corner
        elif r < on_target + blocked:
            outcome = "Blocked"

            data.players_report.at[attacker.id,'Actions Fail'] += 1

            if random.random()*100 > SAVE2CORNER:
                outcome = 'Blocked2corner'

        # miss or post
        else:

            data.players_report.at[attacker.id,'Actions Fail'] += 1

            update_rating(attacker.id,'Miss')
            if type == 'Isolated Shot':
                update_rating(attacker.id,'fail2')

            outcome = "Miss"

            if random.random()*100 < SUCCESS_POST:
                outcome == "Post"

    return outcome


# run all the checks for when the ball in is zone 1
def zone1_check(event_type, attacker1: Player, defender1: Player) -> tuple[str,Player,Player,Player,str,float,bool]:
    """Check the zone 1 duel

    Parameters
    ----------
    attacker1 : Player
    defender1: Player

    Returns
    -------
    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) : tuple(str,Player,Player,Player,str,float,bool)
    """

    success = False
    base_success_rate = 60
    critical_success_rate = 20
    longshot_success_rate = 76.39
    bonus = 0
    attacker2 = attacker1
    defender2 = defender1
    diff = 0
    weights_no_critical = {'Through Pass': 0.88, 'Pass': 0.97, 'Dribble': 0.97}

    new_zone = '4'

    action = get_action_zone1(event_type)
    sub_action = action
    defender_action = 'Tackle'


    if action == 'Long Shot':
        #bonus = data.BONUS[attacker1.team]
        base_success_rate = longshot_success_rate
        (action, attacker1, attacker2, defender2, diff, success) = pre_long_shot(attacker1,defender1)
        if 'Marked' in action:
            sub_action = None
            defender_action = 'Block'
        elif 'Dribble' in action:
            sub_action = 'Dribble'
        elif 'Pass' in action:
            sub_action = 'Pass'
            defender_action = 'Interception'

        new_zone = 'Long Shot'

    else:
        if random.random() > weights_no_critical[action]:
            base_success_rate = critical_success_rate
            new_zone = '5'
    
        if action == 'Dribble':
            diff = duel_dribble(attacker1,defender1)

        else:

            sub_action = action
            defender_action = 'Interception'

            if attacker1.team == data.team_A.name:
                team_lineup = data.team_A.lineup
                opposite_team_lineup = data.team_B.lineup
            else:
                team_lineup = data.team_B.lineup
                opposite_team_lineup = data.team_A.lineup  
        
            assert attacker1.team == data.team_A.name or attacker1.team == data.team_B.name, f"Player's team unidentified... {attacker1.team}"

            attacker2 = get_attacker(team_lineup,new_zone,attacker1.id)

            if action == 'Through Pass':
                defender2 = get_defender(opposite_team_lineup,new_zone,defender1.id)

                if defender2.position == 'GK':
                    

                    goalkeeper_id = list(opposite_team_lineup.keys())[list(opposite_team_lineup.values()).index('GK')]
                    goalkeeper = Player.get_player(goalkeeper_id)

                    diff = duel_throughpass_goalkeeper(attacker1,attacker2,goalkeeper)
                else:
                    diff = duel_throughpass(attacker1,attacker2,defender2)

            elif action == 'Pass':
                defender2 = get_defender(opposite_team_lineup,'4',defender1.id)

                if random.random() < 0.25:
                    sub_action = 'One-Two'
                    temp = attacker1
                    attacker1 = attacker2
                    attacker2 = temp
                    diff = duel_pass_onetwo(attacker1,attacker2,defender1,defender2)

                else:
                    diff = duel_pass(attacker1,defender2)


    data.players_report.at[defender2.id,'Total Actions'] += 1
    data.players_report.at[attacker1.id,'Total Actions'] += 1

    success_rate = (base_success_rate*(1+bonus)) + diff
    if random.random()*100 < success_rate:
        success = True
        # DEBUG: uncommented this line. changed "option" to "action"
        com.comment(action,'success',player1=attacker1.name,player2=attacker2.name,defender1=defender1.name,defender2=defender2.name)
        # com.comment(option,'success',player1=attacker1.name,player2=attacker2.name,defender1=defender1.name,defender2=defender2.name)

        if sub_action == 'One-Two':
            data.players_report.at[attacker1.id,'Actions Success'] += 1
            data.players_report.at[attacker1.id,'Pass Success'] += 1
            action = 'One-Two'

        elif sub_action:
            data.players_report.at[attacker1.id,sub_action+' Success'] += 1

        data.players_report.at[defender2.id,'Actions Fail'] += 1

    else:

        if sub_action == 'One-Two':
            data.players_report.at[attacker1.id,'Actions Fail'] += 1
            data.players_report.at[attacker1.id,'Pass Fail'] += 1
            action = 'One-Two'

        elif sub_action:
            data.players_report.at[attacker1.id,sub_action+' Fail'] += 1

        data.players_report.at[defender2.id,'Actions Success'] += 1
        data.players_report.at[defender2.id,defender_action] += 1

    return (action,attacker1,attacker2,defender2,new_zone,success_rate,success)


def zone2_check(zone,event_type, attacker1: Player, defender1: Player) -> tuple[str,Player,Player,Player,str,float,bool]:
    """Check the zone 2 duel

    Parameters
    ----------
    attacker1 : Player
    defender1: Player

    Returns
    -------
    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) : tuple[str,Player,Player,Player,str,float,bool]
    """

    if zone == '2l':
        new_zone = '3l'
    elif zone == '2r':
        new_zone = '3r'

    success = False
    base_success_rate = 80
    longshot_success_rate = 76.39
    early_cross_success_rate = 64.94
    bonus = 0
    attacker2 = attacker1
    defender2 = defender1
    diff = 0

    action = get_action_zone2(event_type)
    sub_action = action
    defender_action = 'Tackle'

    if action == 'Cut Inside':
        #bonus = data.BONUS[attacker1.team]
        base_success_rate = longshot_success_rate
        (action, attacker1, attacker2, defender2, diff, success) = pre_long_shot(attacker1,defender1)
        if 'Marked' in action:
            sub_action = None
            defender_action = 'Block'
        elif 'Dribble' in action:
            sub_action = 'Dribble'
        elif 'Pass' in action:
            sub_action = 'Pass'
            defender_action = 'Interception'

        new_zone = 'Long Shot'

    if action == 'Early Cross':
        #bonus = data.BONUS[attacker1.team]
        base_success_rate = early_cross_success_rate
        diff = duel_pre_cross(attacker1,defender1)
        sub_action = 'Cross'
        defender_action = 'Block'

    elif action == 'Dribble':
        diff = duel_speed_dribble(attacker1,defender1)

    else:
        defender_action = 'Interception'

        if attacker1.team == data.team_A.name:
            team_lineup = data.team_A.lineup
            opposite_team_lineup = data.team_B.lineup
        else:
            team_lineup = data.team_B.lineup
            opposite_team_lineup = data.team_A.lineup 

        assert attacker1.team == data.team_A.name or attacker1.team == data.team_B.name, f"Player's team unidentified... {attacker1.team}"

        attacker2 = get_attacker(team_lineup,new_zone,attacker1.id)
        defender2 = get_defender(opposite_team_lineup,new_zone,defender1.id)

        if action == 'Through Pass':
            diff = duel_throughpass(attacker1,attacker2,defender2)

        elif action == 'Pass':

            if random.random() < 0.25:
                sub_action = 'One-Two'
                temp = attacker1
                attacker1 = attacker2
                attacker2 = temp
                diff = duel_pass_onetwo(attacker1,attacker2,defender1,defender2)

            else:
                diff = duel_pass(attacker1,defender2)


    data.players_report.at[defender2.id,'Total Actions'] += 1
    data.players_report.at[attacker1.id,'Total Actions'] += 1

    success_rate = (base_success_rate*(1+bonus)) + diff
    if random.random()*100 < success_rate:
        success = True
        #com.comment(option,'success',player1=attacker1.name,player2=attacker2.name,defender1=defender1.name,defender2=defender2.name)

        if sub_action == 'One-Two':
            data.players_report.at[attacker1.id,'Actions Success'] += 1
            data.players_report.at[attacker1.id,'Pass Success'] += 1
            action = 'One-Two'

        elif sub_action:
            data.players_report.at[attacker1.id,sub_action+' Success'] += 1

        data.players_report.at[defender2.id,'Actions Fail'] += 1

    else:

        if sub_action == 'One-Two':
            data.players_report.at[attacker1.id,'Actions Fail'] += 1
            data.players_report.at[attacker1.id,'Pass Fail'] += 1
            action = 'One-Two'

        elif sub_action:
            data.players_report.at[attacker1.id,sub_action+' Fail'] += 1

        data.players_report.at[defender2.id,'Actions Success'] += 1
        data.players_report.at[defender2.id,defender_action] += 1

    return (action,attacker1,attacker2,defender2,new_zone,success_rate,success)


def zone3_check(attacker1: Player, defender1: Player) -> tuple[str,Player,Player,Player,str,float,bool]:
    """Check the zone 3 duel

    Parameters
    ----------
    attacker1 : Player
    defender1: Player

    Returns
    -------
    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) : tuple(str,Player,Player,Player,str,float,bool)
    """
    success = False
    base_success_rate = 81.17
    critical_success_rate = 46.38
    bonus = data.BONUS[attacker1.team]
    attacker2 = attacker1
    defender2 = defender1
    diff = 0
    new_zone = 'Header'
    action = get_action_zone3()
    sub_action = None
    defender_action = 'Clear'

    if action == 'Dribble Shot':
        base_success_rate = critical_success_rate
        diff = duel_dribble(attacker2,defender2)
        sub_action = 'Dribble'
        defender_action = 'Tackle'

    else:
        if attacker1.team == data.team_A.name:
            team_lineup = data.team_A.lineup
            opposite_team_lineup = data.team_B.lineup
            goalkeeper_id = data.team_B.goalkeeper
        else:
            team_lineup = data.team_B.lineup
            opposite_team_lineup = data.team_A.lineup
            goalkeeper_id = data.team_A.goalkeeper

        attacker2 = get_attacker(team_lineup,'5')
        defender2 = get_defender(opposite_team_lineup,'cross',defender1)
        
        if action == 'High Cross':
            sub_action = 'Cross'
            goalkeeper = Player.get_player(goalkeeper_id)
            diff = duel_cross(attacker1,defender2,goalkeeper)

            if random.random() < 0.15:
                defender2 = goalkeeper

        if action == 'Pass Shot':
            base_success_rate = critical_success_rate
            sub_action = 'Pass'
            diff = duel_pass(attacker1,defender2)
            defender_action = 'Interception'


    data.players_report.at[defender2.id,'Total Actions'] += 1
    data.players_report.at[attacker1.id,'Total Actions'] += 1

    success_rate = (base_success_rate*(1+bonus)) + diff
    if random.random()*100 < success_rate:
        success = True
        if sub_action: data.players_report.at[attacker1.id,sub_action+' Success'] += 1
        data.players_report.at[attacker1.id,'Actions Success'] += 1
        data.players_report.at[defender2.id,'Actions Fail'] += 1

    else:
        if sub_action: data.players_report.at[attacker1.id,sub_action+' Fail'] += 1
        data.players_report.at[defender2.id,defender_action] += 1
        data.players_report.at[attacker1.id,'Actions Fail'] += 1
        data.players_report.at[defender2.id,'Actions Success'] += 1

    return (action,attacker1,attacker2,defender2,new_zone,success_rate,success)


def zone4_check(attacker1: Player, defender1: Player) -> tuple[str,Player,Player,Player,str,float,bool]:
    """Check the zone 4 duel

    Parameters
    ----------
    attacker1 : Player
    defender1: Player

    Returns
    -------
    (action,attacker1,attacker2,defender2,new_zone,success_rate,success) : tuple(str,Player,Player,Player,str,float,bool)
    """

    success = False
    base_success_rate = 61.84
    dribble_success_rate = 33.3
    bonus = 0
    #bonus = data.BONUS[attacker1.team]
    attacker2 = attacker1
    defender2 = defender1
    diff = 0
    new_zone = 'Shot'

    action = get_action_zone4()
    sub_action = None
    defender_action = 'Tackle'

    if action == 'Marked Shot':
        diff = duel_pre_shot(attacker1,defender1)
        defender_action = 'Block'

    elif action == 'Dribble Shot':
        diff = duel_dribble(attacker1,defender1)
        sub_action = 'Dribble'

    elif action == 'Dribble Isolated':
        base_success_rate = dribble_success_rate
        diff = duel_speed_dribble(attacker1,defender1)
        new_zone = '5'
        sub_action = 'Dribble'

    elif action == 'Pass Shot':

        defender_action = 'Interception'
        sub_action = 'Pass'

        if attacker1.team == data.team_A.name:
            team_lineup = data.team_A.lineup
        else:
            team_lineup = data.team_B.lineup

        attacker2 = get_attacker(team_lineup,'5')
        defender2 = get_direct_marker(attacker2,defender1)
        diff = duel_pass(attacker1,defender2)


    data.players_report.at[defender2.id,'Total Actions'] += 1
    data.players_report.at[attacker1.id,'Total Actions'] += 1

    success_rate = (base_success_rate*(1+bonus)) + diff
    if random.random()*100 < success_rate:
        success = True
        if sub_action: data.players_report.at[attacker1.id,sub_action+' Success'] += 1
        data.players_report.at[attacker1.id,'Actions Success'] += 1
        data.players_report.at[defender2.id,'Actions Fail'] += 1

    else:
        if sub_action: data.players_report.at[attacker1.id,sub_action+' Fail'] += 1
        data.players_report.at[defender2.id,defender_action] += 1
        data.players_report.at[attacker1.id,'Actions Fail'] += 1
        data.players_report.at[defender2.id,'Actions Success'] += 1

    return (action,attacker1,attacker2,defender2,new_zone,success_rate,success)


########################################################################################################################
###                                   Set Pieces                                                                    ####
########################################################################################################################


# check Free Kick
# arguments: attacking team
# returns outcome (blocked / miss / post / save / goal)
def run_freekick(team: Team, goalkeeper_id: int) -> tuple[str, int]:

    on_target = 35
    outcome = None
    
    fk_taker_id = random.choice([key for key, value in team.lineup.items() if value != 'GK'])

    fk_taker = Player.get_player(fk_taker_id)
    goalkeeper = Player.get_player(goalkeeper_id)

    # get the goalkeeper from the data.players_report table
    data.players_report.at[fk_taker.id,'Long Shot'] += 1
    data.report.at['Free Kick',fk_taker.team] += 1
    data.report.at['Total Shots',fk_taker.team] += 1
    data.players_report.at[fk_taker.id,'Total Actions'] += 1
    data.players_report.at[fk_taker.id,'Total Shots'] += 1


    # taker: 70% longshot + 30% technique
    # goalkeeper: 50% agility + 25% command + 25% positioning
    diff = duel_freekick(fk_taker,goalkeeper)

    # if goal
    if random.random()*100 < (SUCCESS_FK + diff):
        outcome = "Goal"
        data.report.at['Goals from FK',fk_taker.team] += 1
        data.report.at['Goals',fk_taker.team] += 1
        data.report.at['Shots On Target',fk_taker.team] += 1
        data.players_report.at[fk_taker_id,'Shots On Target'] += 1
        data.players_report.at[goalkeeper_id,'Total Actions'] += 1
        data.players_report.at[goalkeeper_id,'Actions Fail'] += 1
        data.players_report.at[fk_taker_id,'Actions Success'] += 1
        data.players_report.at[fk_taker_id,'Goals'] += 1
        update_rating(fk_taker_id, 'Goal')
        update_rating(goalkeeper_id, 'Goal conceived')

    else:

        # if on-target then it's a save
        if random.random()*100 < on_target:
            outcome = "Save"
            data.report.at['Shots On Target',fk_taker.team] += 1
            update_rating(goalkeeper_id, 'Save')
            data.players_report.at[goalkeeper_id,'Actions Success'] += 1
            data.players_report.at[goalkeeper_id,'Save'] += 1
            data.players_report.at[goalkeeper_id,'Total Actions'] += 1

        # if off target can be blocked by barrier, miss or post
        else:

            data.players_report.at[fk_taker_id,'Actions Fail'] += 1

            if random.random()*100 < BARRIER:
                outcome = 'Blocked'

            else:
                outcome = "Miss"
                if random.random()*100 < SUCCESS_POST_PENALTY:
                    outcome = "Post"

    return (outcome, fk_taker)

# check Free Kick
# arguments: attacking team
# returns outcome (blocked / miss / post / save / goal)
def run_penalty(team: Team, goalkeeper_id: int) -> tuple[str, int]:


    penalty_taker_id = random.choice([key for key, value in team.lineup.items() if (value != 'GK')])

    on_target = 90
    outcome = None

    penalty_taker = Player.get_player(penalty_taker_id)
    goalkeeper = Player.get_player(goalkeeper_id)
     
    data.players_report.at[penalty_taker.id,'Total Shots'] += 1
    data.players_report.at[penalty_taker.id,'Total Actions'] += 1
    data.players_report.at[goalkeeper.id,'Total Actions'] += 1
    data.report.at['Penalty',penalty_taker.team] += 1
    data.report.at['Total Shots',penalty_taker.team] += 1

    # taker: 70% longshot + 30% technique
    # goalkeeper: 50% agility + 25% command + 25% positioning
    diff = duel_penalty(penalty_taker,goalkeeper) 

    # if goal
    if random.random()*100 < (SUCCESS_FK + diff):
        outcome = "Goal"
        data.report.at['Goals',penalty_taker.team] += 1
        data.report.at['Goals from Penalty',penalty_taker.team] += 1
        data.report.at['Shots On Target',penalty_taker.team] += 1
        data.players_report.at[penalty_taker.id,'Goals'] += 1
        data.players_report.at[penalty_taker.id,'Actions Success'] += 1
        data.players_report.at[goalkeeper.id,'Actions Fail'] += 1
        update_rating(penalty_taker.id,'Penalty scored')
        update_rating(goalkeeper.id,'Penalty conceived')

    else:
        data.players_report.at[penalty_taker.id,'Actions Fail'] += 1
        update_rating(penalty_taker.id,'Penalty miss')

        # if on-target then it's a save
        if random.random()*100 < on_target:
            outcome = "Save"
            data.report.at['Shots On Target',penalty_taker.team] += 1
            data.players_report.at[goalkeeper.id,'Actions Success'] += 1
            data.players_report.at[goalkeeper_id,'Save'] += 1
            update_rating(goalkeeper.id,'Penalty save')

        # if off target can be blocked by barrier, miss or post
        else:
            outcome = "Miss"
            if random.random()*100 < SUCCESS_POST_PENALTY:
                outcome = "Post"

    return (outcome, penalty_taker)

# check corner
# arguments: attacking team
# returns outcome (wasted / cleared / blocked / corner / miss / post / save / goal)
# Cross FK are similar to corners, only the name and the context in which are generated is different 
# team == 'A' or 'B'
def run_corner(team: Team, goalkeeper_id: int, context: str = 'Corner'):
    """Runs a Corner or Cross FK
    
    Parameters:
    -----------
    team: Team
    goalkeeper_id: int
    context: str

    Returns:
    --------
    outcome: str
    taker: Player
    attacker: Player (or None)
    defender: Player (or None)
    """


    taker_id = random.choice([key for key, value in team.lineup.items() if (value != 'GK')])

    taker = Player.get_player(taker_id)
    goalkeeper = Player.get_player(goalkeeper_id)
    attacker = None
    defender = None
    on_target = 40
    
    # sets which team is which using 'A' or 'B' to simplify calls
    if team.name == data.team_A:
        opposite_team = data.team_B
    else:
        opposite_team = data.team_A

    # commentary    
    outcome = None
    data.players_report.at[taker.id,'Total Actions'] += 1

    data.report.at[context,team.name] += 1

    # check if corner is wasted
    # the higher the crossing skill, the lower the chance of wasting the corner 
    if random.random()*100 > taker.corner + 5:
        outcome = 'wasted'
        update_rating(taker.id,'fail2')
        data.players_report.at[taker.id,'Actions Fail'] += 1
        data.players_report.at[taker.id,'Cross Fail'] += 1

    else:
        n = 4
        (attackers,attack_rating) = get_top_headers(team.lineup,n,taker.id)
        (defenders, defense_rating) = get_top_headers(opposite_team.lineup,n)  
        diff = duel_corner(attack_rating,defense_rating,goalkeeper,n)

        attacker = random.choice(attackers)
        defender = random.choice(defenders)
        
        data.players_report.loc[attacker.id,'Total Actions'] += 1
        data.players_report.loc[defender.id,'Total Actions'] += 1

        # runs an aerial duel between 3 attackers and 3 defenders + goalkeeper
        # if success there will be an header
        if random.random()*100 < (SUCCESS_CORNER + diff):

            # randomly select one of the best attacking headers
            data.players_report.at[taker.id,'Cross Success'] += 1            
            data.players_report.at[taker.id,'Actions Success'] += 1
            data.players_report.at[attacker.id,'Actions Success'] += 1
            data.players_report.at[attacker.id,'Total Shots'] += 1
            data.players_report.loc[attacker.id,'Header'] += 1
            data.players_report.loc[defender.id,'Actions Fail'] += 1
            data.report.at["Total Shots",team.name] += 1
            data.report.at['Header',team.name] += 1
            update_rating(taker.id,'success1')
            update_rating(attacker.id,'success1')
            update_rating(defender.id,'fail1')

            diff = duel_finalization_header(attacker,goalkeeper)

            # if goal
            if random.random()*100 < (SUCCESS_HEADER + diff):
                outcome = "Goal"
                data.players_report.loc[attacker.id,'Shots On Target'] += 1
                data.players_report.loc[attacker.id,'Goals'] += 1
                data.report.at['Goals',team.name] += 1
                data.report.at['Goals from Header',team.name] += 1
                data.report.at['Shots On Target',team.name] += 1
                data.report.at['Goals from '+context,team.name] += 1
                update_rating(attacker.id,'Goal')
                update_rating(goalkeeper.id,'Goal conceived')
                update_rating(defender.id,'fail1')
                data.players_report.at[goalkeeper.id,'Actions Fail'] += 1
                data.players_report.at[goalkeeper.id,'Total Actions'] += 1

            # if not goal
            else:
                r = random.random()*100
                # on target and save
                if r < on_target:
                    outcome = "Save"
                    data.players_report.loc[attacker.id,'Shots On Target'] += 1
                    update_rating(goalkeeper.id,'Save')
                    data.players_report.at[goalkeeper.id,'Actions Success'] += 1
                    data.players_report.at[goalkeeper.id,'Total Actions'] += 1
                    data.players_report.at[goalkeeper.id,'Save'] += 1

                    if random.random()*100 > 40 + get_player_stat(goalkeeper,'handling')*0.5:
                        outcome = 'save2corner'

                else:

                    # blocked and maybe corner
                    if r < on_target + BLOCKED:
                        outcome = "Blocked"
                        update_rating(defender.id,'success1')
                        data.players_report.loc[defender.id,'Block'] += 1 
                        data.players_report.loc[defender.id,'Actions Success'] += 1 

                        if random.random()*100 > SAVE2CORNER:
                            outcome = 'Blocked2Corner'

                    # miss or post
                    else:                    
                        outcome = "Miss"
                        update_rating(attacker.id,'Miss')

                        if random.random()*100 < SUCCESS_POST:
                            outcome == "Post"
                        
        else: 
            data.players_report.at[taker.id,'Cross Fail'] += 1
            outcome = "Cleared"
            if random.random() < 0.15:
                defender = goalkeeper
                outcome = "Cleared by GK"                                          
            update_rating(defender.id,'success2')
            data.players_report.loc[defender.id,'Total Actions'] += 1 
            data.players_report.loc[defender.id,'Actions Success'] += 1 
            data.players_report.loc[defender.id,'Clear'] += 1                                            


    return (outcome, taker, attacker, defender)


def check_set_pieces(zone: str, defender_id: int) -> str:
    """Checks if there will be a set pice.

    Parameters:
    -----------
    zone: str
    defender_id: int

    Returns:
    --------
    set_pieces: str
    """

    assert zone in ['1','2r','2l','3l','3r','4','5'], f"Invalid Zone: {zone}"

    set_piece = None
    r = random.random()
    if zone == '1' or (zone == '4' and r < 0.5):
        set_piece = 'Free Kick'
    elif zone == '5' or (zone == '4' and r >= 0.5):
        set_piece = 'Penalty'
        update_rating(defender_id,'Commit penalty')
    elif zone in ['3l','3r'] or (zone in ['2l','2r'] and r < 0.5):
        set_piece = 'Cross FK'

    return set_piece


