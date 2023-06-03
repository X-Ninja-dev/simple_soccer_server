from classPlayer import Team, Player
from typing import Generator
from typing import Type
import pandas as pd
import random
import commentary as com
import numpy as np

team_A = []
team_B = []
instructions_team_A = []
instructions_team_B = []
t = 0
BONUS = {}

zero_array = np.zeros(shape=(48,2))
report = pd.DataFrame(zero_array)
report.index = ['Formation','Strategy','Mentality','Rating','Ball Possession',\
    'Fouls','Fouls Zone0','Fouls Zone1','Fouls Zone2','Fouls Zone3','Fouls Zone4','Fouls Zone5','Yellow Card','Second Yellow','Red Card',\
    'Events','Check1 Success','Short Pass','Direct', 'Wings','Long Ball','Counter Attacks', \
    'Dribble','Pass','Through Pass','Cross',\
    'Long Shot','Goals from Long Shot','Header','Goals from Header','Shot','Goals from Shot','Isolated Shot','Goals from Isolated Shot', \
    'Penalty','Goals from Penalty','Free Kick','Goals from FK','Corner','Goals from Corner','Cross FK','Goals from Cross FK',\
    'Total Shots','Shots On Target','Shots per Event','Goals per Event','Goals per Shot','Goals'] 

f443d = ['GK','DL','DR','DCl','DCr','DMC','MCl','MCr','AML','AMR','FC']
f433a = ['GK','DL','DR','DCl','DCr','MCl','MCr','AMC','AML','AMR','FC']
f433 = ['GK','DL','DR','DCl','DCr','MCl','MCr','MC','AML','AMR','FC']
f442 = ['GK','DL','DR','DCl','DCr','MCl','MCr','ML','MR','FCl','FCr']
f451= ['GK','DL','DR','DCl','DCr','DMC','MCl','MCr','ML','MR','FC']
f352 = ['GK','DML','DMR','DCl','DC','DCr','MCl','MCr','AMC','FCl','FCr']

#table_columns=['id','Player','Team','Position','Energy','Status','Foul','Yellow Card','Red Card','Clear','Block','Tackle',\
#'Interception','Pass Success','Pass Fail','Dribble Success','Dribble Fail','Through Pass Success','Through Pass Fail',\
#'Cross Success','Cross Fail','Long Shot','Shot','Header','Isolated Shot','Total Shots','Shots On Target',\
#'Total Actions','Actions Success','Actions Fail','Save','Assists','Goals','Rating']


players_report = pd.DataFrame()

#players_report = pd.DataFrame(np.zeros(shape=(22,34)), columns = table_columns)
#players_report = players_report.set_index('id')
#print(players_report)


# event_report will save all events and respective detais
event_report_columns = ['half','time','log','changes','foul0','zone0','zone1','zone2l','zone2r','zone3l','zone3r','zone4','finalization','foul','set piece','corner']

event_report = pd.DataFrame(columns=event_report_columns)

