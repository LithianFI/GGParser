import sc2reader
import glob
import os
import time

from os.path import expanduser


import sys
import time
import threading


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


class Score:
    def __init__(self):
        self.wins = 0
        self.loses = 0


class GGParser:

    def __init__(self):
        self.initialize_txt()

        # Config
        # Tracked Player
        name = input("Type the player name you want to track \n")
        self.tracked_player = name
        # Tracked Race
        race = input("Type the race you want to track (Zerg, Protoss, Terran) \n")
        self.tracked_race = race

        try:
            self.replay_folder = f"{expanduser('~')}\\documents\\StarCraft II"
        except ValueError:
            print("Replay folder not found, are you sure Starcraft II is installed?")

        # Folder polling rate in seconds
        self.poll_rate = 5

        print("GGParser initialized")
        print("Tracking folder: " + self.replay_folder)
        print("Tracking player: " + self.tracked_player + " - " + self.tracked_race)
        print("Polling the folder every " + str(self.poll_rate) + " seconds")

        self.zerg = "Zerg"
        self.protoss = "Protoss"
        self.terran = "Terran"

        self.opponent = "null"

        self.XvZ = Score()
        self.XvP = Score()
        self.XvT = Score()

        # Variables
        self.replay_path = self.get_latest_replay_init()
        self.replay = sc2reader.load_replay(self.replay_path, load_level=4)

    def get_all_replays(self):
        replay_list = []
        for root, dirs, files in os.walk(self.replay_folder, topdown=False):
            for name in files:
                if name.endswith(".SC2Replay"):
                    file_path = os.path.join(root, name)
                    replay_list.append(file_path)
        return replay_list

    def get_latest_replay_init(self):
        replay_list = self.get_all_replays()
        last_replay = max(replay_list, key=os.path.getctime)
        return last_replay

    def get_latest_replay(self):
        replay_list = self.get_all_replays()
        latest_replay = max(replay_list, key=os.path.getctime)
        if self.replay_path != latest_replay:
            print("Old replay was: " + self.replay_path)
            print("Newest replay is: " + latest_replay)
            self.replay_path = latest_replay
            self.replay = sc2reader.load_replay(self.replay_path, load_level=4)
            self.check_players()

    def parse_winner(self, player, enemy):
        winner = self.replay.winner
        winner_string = str(winner)
        opponent_string = str(enemy)
        if winner_string:
            if opponent_string.find(self.zerg) != -1:
                self.XvZ.wins += 1
            if opponent_string.find(self.protoss) != -1:
                self.XvP.wins += 1
            if opponent_string.find(self.terran) != -1:
                self.XvT.wins += 1
        else:
            if opponent_string.find(self.zerg) != -1:
                self.XvZ.loses += 1
            if opponent_string.find(self.protoss) != -1:
                self.XvP.loses += 1
            if opponent_string.find(self.terran) != -1:
                self.XvT.loses += 1
        self.update_score()

    def update_score(self):
        try:
            print("Updating the file")
            map_scores = open("mapscore.txt", "r+")
            map_scores.write(self.tracked_race[0] + " v " + "Z" + ": " + str(self.XvZ.wins) + "-" + str(self.XvZ.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + " v " + "P" + ": " + str(self.XvP.wins) + "-" + str(self.XvP.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + " v " + "T" + ": " + str(self.XvT.wins) + "-" + str(self.XvT.loses))
            map_scores.close()
        except FileNotFoundError:
            print("File not found, creating new one and updating")
            map_scores = open("mapscore.txt", "w")
            map_scores.write(self.tracked_race[0] + " v " + "Z" + ": " + str(self.XvZ.wins) + "-" + str(self.XvZ.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + " v " + "P" + ": " + str(self.XvP.wins) + "-" + str(self.XvP.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + " v " + "T" + ": " + str(self.XvT.wins) + "-" + str(self.XvT.loses))
            map_scores.close()

    def parse_players(self):
        players = self.replay.players
        player_1 = players[0]
        player_2 = players[1]

        p1 = str(player_1)
        p2 = str(player_2)

        if p1.find(self.tracked_player) != -1:
            self.opponent = p2
            return 1
        elif p2.find(self.tracked_player) != -1:
            self.opponent = p1
            return 1
        else:
            print(("Tracked Player " + self.tracked_player) + "-" + self.tracked_race + " not found in the replay, skipping")
            return 0

    def check_players(self):
        print(self.replay.players)
        i = self.parse_players()
        if i == 1:
            self.parse_winner(self.tracked_player, self.opponent)


    @staticmethod
    def initialize_txt():
        try:
            map_scores = open("mapscore.txt", "r+")
            map_scores.close()
        except FileNotFoundError:
            map_scores = open("mapscore.txt", "w")
            map_scores.close()

    def poll_replays(self):
        while True:
            with Spinner():
                time.sleep(self.poll_rate)
                self.get_latest_replay()


if __name__ == "__main__":
    GGParser().poll_replays()
