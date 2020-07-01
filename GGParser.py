import sc2reader
import os

from os.path import expanduser
import sys
import time
import threading
import subprocess

from sc2reader.utils import Length
from sys import platform


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

        if platform == "win32":
            try:
                self.replay_folder = f"{expanduser('~')}\\documents\\StarCraft II"
            except ValueError:
                print("Replay folder not found, are you sure Starcraft II is installed?")
        elif platform == "linux" or platform == "linux2":
            try:
                self.replay_folder = os.environ['SC2_REPLAYS']
            except KeyError:
                print("Replay folder not found, are you sure Starcraft II is installed?")
                self.replay_folder = input("Provide path to your SC2 replay folder. "
                                           "This is usually located under .wine \n")

        # Folder polling rate in seconds
        self.poll_rate = 5
        # Minimum length of a game
        self.min_length = Length(seconds=60)

        print("GGParser initialized")
        print("Tracking folder: " + self.replay_folder)
        print("Tracking player: " + self.tracked_player + " - " + self.tracked_race)
        print("Polling the folder every " + str(self.poll_rate) + " seconds")

        self.zerg = "Zerg"
        self.protoss = "Protoss"
        self.terran = "Terran"

        self.XvZ = Score()
        self.XvP = Score()
        self.XvT = Score()
        self.XvR = Score()

        # Variables
        self.replay_path = self.get_latest_replay_init()

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
        try:
            last_replay = max(replay_list, key=os.path.getctime)
            return last_replay
        except ValueError:
            print("No replays found")

    def get_latest_replay(self):
        replay_list = self.get_all_replays()
        try:
            latest_replay = max(replay_list, key=os.path.getctime)
            if self.replay_path != latest_replay:
                print("Old replay was: " + self.replay_path)
                print("Newest replay is: " + latest_replay)
                self.replay_path = latest_replay
                replay = sc2reader.load_replay(self.replay_path, load_level=4)
                if replay.real_length > self.min_length:
                    self.check_players(replay)
                else:
                    print("Found replay is too short, skipping")
        except ValueError:
            print("No replays found")

    def check_players(self, replay):
        print(replay.players)
        players = replay.players

        i = self.parse_enemy(players)
        if i != -1:
            self.parse_winner(replay, i)

    def parse_enemy(self, players):
        player_1 = players[0]
        player_2 = players[1]

        if player_1.name == self.tracked_player and player_1.pick_race == self.tracked_race:
            return player_2

        if player_2.name == self.tracked_player and player_2.pick_race == self.tracked_race:
            return player_1

        else:
            print(
                "Tracked Player " + self.tracked_player + "-" + self.tracked_race + " not found in the replay, skipping")
            return -1

    def parse_winner(self, replay, enemy):
        winner = replay.winner
        if winner.players[0].name != enemy.name:
            if enemy.pick_race == "Zerg":
                self.XvZ.wins += 1
            if enemy.pick_race == "Protoss":
                self.XvP.wins += 1
            if enemy.pick_race == "Terran":
                self.XvT.wins += 1
            if enemy.pick_race == "Random":
                self.XvR.wins += 1
        else:
            if enemy.pick_race == "Zerg":
                self.XvZ.loses += 1
            if enemy.pick_race == "Protoss":
                self.XvP.loses += 1
            if enemy.pick_race == "Terran":
                self.XvT.loses += 1
            if enemy.pick_race == "Random":
                self.XvR.loses += 1
        self.update_score()

    def update_score(self):
        try:
            print("Updating the file")
            map_scores = open("mapscore.txt", "r+")
            map_scores.write(self.tracked_race[0] + "v" + "Z" + ": " + str(self.XvZ.wins) + "-" + str(self.XvZ.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "P" + ": " + str(self.XvP.wins) + "-" + str(self.XvP.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "T" + ": " + str(self.XvT.wins) + "-" + str(self.XvT.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "R" + ": " + str(self.XvR.wins) + "-" + str(self.XvR.loses))
        #  map_scores.write("Debug, done!")
            map_scores.close()
        except FileNotFoundError:
            print("File not found, creating new one and updating")
            map_scores = open("mapscore.txt", "w")
            map_scores.write(self.tracked_race[0] + "v" + "Z" + ": " + str(self.XvZ.wins) + "-" + str(self.XvZ.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "P" + ": " + str(self.XvP.wins) + "-" + str(self.XvP.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "T" + ": " + str(self.XvT.wins) + "-" + str(self.XvT.loses))
            map_scores.write("\n")
            map_scores.write(self.tracked_race[0] + "v" + "R" + ": " + str(self.XvR.wins) + "-" + str(self.XvR.loses))
        map_scores.close()

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
                # self.get_all_replays_and_analyze()


if __name__ == "__main__":
    GGParser().poll_replays()
