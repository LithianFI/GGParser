import sc2reader
import glob
import os
import time

# Config
# Change this to match your in-game name
tracked_player = "Lithian"
# Change this to your race
tracked_race = "Protoss"
# Change this to your SC2 replay folder (Starcraft II/Accounts/1234567/12345-5-S1/Replays/Multiplayer/*
try:
    replay_folder = "C:/Users/walts/Documents/StarCraft II/Accounts/948824/2-S2-1-978970/Replays/Multiplayer/*"
except ValueError:
    print("You didn't setup your replay folder path")

# Folder polling rate in seconds
poll_rate = 5


def get_latest_replay():
    replay_list = glob.glob(replay_folder)
    last_replay = max(replay_list, key=os.path.getctime)
    return last_replay


# Variables
replay_path = get_latest_replay()
replay = sc2reader.load_replay(replay_path, load_level=4)

zerg = "Zerg"
protoss = "Protoss"
terran = "Terran"

opponent = "Null"

XvZ = [0, 0]
XvP = [0, 0]
XvT = [0, 0]


def get_latest_replay():
    global replay
    global replay_path
    replay_list = glob.glob(replay_folder)
    latest_replay = max(replay_list, key=os.path.getctime)
    if replay_path != latest_replay:
        print("Old replay was: " + replay_path)
        print("Newest replay is: " + latest_replay)
        replay_path = latest_replay
        replay = sc2reader.load_replay(replay_path, load_level=4)
        check_players()


def parse_winner(player, enemy):
    global replay
    winner = replay.winner
    winner_string = str(winner)
    opponent_string = str(enemy)
    if winner_string.find(player) != -1:
        if opponent_string.find(zerg) != -1:
            XvZ[0] += 1
        if opponent_string.find(protoss) != -1:
            XvP[0] += 1
        if opponent_string.find(terran) != -1:
            XvT[0] += 1
    else:
        if opponent_string.find(zerg) != -1:
            XvZ[1] += 1
        if opponent_string.find(protoss) != -1:
            XvP[1] += 1
        if opponent_string.find(terran) != -1:
            XvT[1] += 1
    update_score()


def update_score():
    try:
        map_scores = open("mapscore.txt", "r+")
        map_scores.write(tracked_race[0] + " v " + "Z" + ": " + str(XvZ[0]) + "-" + str(XvZ[1]))
        map_scores.write("\n")
        map_scores.write(tracked_race[0] + " v " + "P" + ": " + str(XvP[0]) + "-" + str(XvP[1]))
        map_scores.write("\n")
        map_scores.write(tracked_race[0] + " v " + "T" + ": " + str(XvT[0]) + "-" + str(XvT[1]))
        map_scores.close()
    except FileNotFoundError:
        map_scores = open("mapscore.txt", "w")
        map_scores.write(tracked_race[0] + " v " + "Z" + ": " + str(XvZ[0]) + "-" + str(XvZ[1]))
        map_scores.write("\n")
        map_scores.write(tracked_race[0] + " v " + "P" + ": " + str(XvP[0]) + "-" + str(XvP[1]))
        map_scores.write("\n")
        map_scores.write(tracked_race[0] + " v " + "T" + ": " + str(XvT[0]) + "-" + str(XvT[1]))
        map_scores.close()


def parse_players():
    global replay
    global opponent
    global tracked_player
    players = replay.players
    player_1 = players[0]
    player_2 = players[1]

    p1 = str(player_1)
    p2 = str(player_2)

    if p1.find(tracked_player) != -1:
        opponent = p2
    elif p2.find(tracked_player) != -1:
        opponent = p1
    else:
        print(("Tracked Player " + tracked_player) + "-" + tracked_race + " not found in the replay, skipping")


def check_players():
    global replay
    print(replay.players)
    parse_players()
    parse_winner(tracked_player, opponent)


print("GGParser initialized")
print("Tracking folder: " + replay_folder)
print("Tracking player: " + tracked_player + " - " + tracked_race)
print("Polling the folder every " + str(poll_rate) + " seconds")


def initialize_txt():
    try:
        map_scores = open("mapscore.txt", "r+")
        map_scores.close()
    except FileNotFoundError:
        map_scores = open("mapscore.txt", "w")
        map_scores.close()


initialize_txt()

while True:
    time.sleep(poll_rate)
    get_latest_replay()
