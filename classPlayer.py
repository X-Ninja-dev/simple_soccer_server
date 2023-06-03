import pandas as pd
import numpy as np

class Player:
    
    player_list = {}
    player_counter = 0
    number = None

    def __init__(self, id: int) -> None:
        self.name = ""
        self.mp4_url = []
        self.image = []
        self.age = 21
        self.matches = 0    # total number of matches
        self.rating = 0
        self.status = 'on'

    def __str__(self):
        return f"{self.name}"


    class OutfieldPlayer:

        def __init__ (self, id: int, name: str, level: float=62):

            self.name = name
            self.mp4_url = []
            self.image = []
            self.age = 21
            self.id = id
            self.finishing = level
            self.longshot = level
            self.speed = level
            self.crossing = level
            self.passing = level
            self.technique = level
            self.tackle = level
            self.positioning = level
            self.stamina = level
            self.heading = level

            self.team = None
            self.position = 'field'

            # energy defines how much energy tha player has during the match. 
            # It starts with the value of the player stamina and depletes during the match.
            # some positions see their energy drain faster.
            self.energy = 100

            self.corner = self.crossing*0.8 + self.technique*0.2
            self.freekick = self.longshot*0.7 + self.technique*0.3
            self.penalty = max(self.longshot,self.finishing)*0.8 + self.technique*0.2
            self.rating = (self.finishing + self.longshot + self.speed + self.technique + self.passing \
                            + self.crossing + self.tackle + self.positioning + self.heading + self.stamina) / 10

            Player.player_list.update({id : self})
            Player.player_counter += 1

        def __str__(self):
            return f"{self.name}"

    class Goalkeeper:
        
        def __init__(self, id: int, name: str, level: float=62):

            self.name = name
            self.mp4_url = []
            self.image = []
            self.age = 21
            self.id = id
            self.penalty = level
            self.stamina = level
            self.oneonone = level
            self.aerial = level
            self.passing = level
            self.handling = level
            self.command = level
            self.positioning = level
            self.reflexes = level
            self.agility = level

            self.energy = 100
            self.team = None
            self.position = 'GK'

            self.rating = (self.penalty + self.stamina + self.oneonone + self.aerial + self.passing \
                            + self.handling + self.command + self.positioning + self.reflexes + self.agility) / 10

            Player.player_list.update({id : self})   
            Player.player_counter += 1

        def __str__(self):
            return f"{self.name}"

    def get_player(player_id: int):
        # assert isinstance(player_id,int),f"Not an int: {player_id}"
        player = Player.player_list[player_id]
        
        return player


class Team:

    def __init__(self, name):
        
        self.name = name   

        # Strategies:
        # Balanced / Short Pass / Direct / Long Ball / Wings           
        self.strategy = "Balanced"
        
        # Mentalities:
        # All Out Defensive / Defensive / Slightly Defensive
        # Normal
        # All Out Attacking / Attacking / Slightly Attacking
        self.mentality = "Normal"
        
        self.formation = []
        self.formation_name = ""
        self.formation_bonus = {'def_bonus' : 0, 'mid_bonus' : 0, 'att_bonus' : 0}
        
        # Pressure:
        # Low -> stamina drains 20% slower / -5% ball possession / -25% against Short Pass / +25% against Long Balls
        # Normal
        # High -> stamina drains 20% faster, +5% ball possession / +25% against Short Pass / -25% against Long Balls
        self.pressure = "Normal"
        
        # Defensive line:
        # Low -> +25% against Direct / -25% against Wings
        # Normal
        # High -> -25% against Direct / +25% against Wings
        self.defesive_line = "Normal"

        self.players = []
        self.lineup = {}
        self.substitutes = []
        self.instructions = []
        self.number_of_players = 0

        self.goalkeeper = None

        self.freekick_taker = None
        self.corner_taker = None
        self.penalty_taker = None

    def add_player_to_lineup(self, player_id, position):

        if len(self.lineup) < 11:
            self.lineup.update({player_id : position})
            self.players.append(player_id)
            self.number_of_players += 1
            player = Player.get_player(player_id)
            if player.team == None:
                player.team = self.name
        else:
            print("Lineup is full")

    def add_player_to_subs(self, player_id):

        if len(self.lineup) < 12:
            self.substitutes.append(player_id)
            self.players.append(player_id)
            self.number_of_players += 1
            player = Player.get_player(player_id)
            if player.team == None:
                player.team = self.name
        else:
            print("Lineup is full")

    def remove_player_from_lineup(self, player_id):
        del self.lineup[player_id]

    def swap_position(self, player_id, new_position):
        self.lineup[player_id] = new_position

    def substitution(self, player_id_out, player_id_in, position):
        del self.lineup[player_id_out] 
        self.lineup[player_id_in] = position

    def swap_players(self, player_id_1, player_id_2):
        position_1 = self.lineup[player_id_1]
        position_2 = self.lineup[player_id_2] 
        self.lineup[player_id_1] = position_2
        self.lineup[player_id_2] = position_1
        
    def get_player(self, player_id):
        assert isinstance(player_id,int),f"Not an int"
        player = self.players[player_id]

    def __iter__(self):
        return iter(self._players)

    def __str__(self):
        out = [f"{self.name}"]
#        out.extend(str(player) for player in self)
        return "\n".join(out)
    




