import sc2reader
import glob
import os
import time

# Config
# Change this to match your in-game name
tracked_player = "kKo"
# Change this to your race
tracked_race = "Terran"
# Change this to your SC2 replay folder (Starcraft II/Accounts/1234567/12345-5-S1/Replays/Multiplayer/*
replay_folder = "C:/Users/walts/Documents/StarCraft II/Accounts/948824/2-S2-1-978970/Replays/Multiplayer/*"


# Variables
replay_path = "E:/Programming/GGParser/Nightshade LE (44).SC2Replay"
replay = sc2reader.load_replay(replay_path, load_level=4)


players = replay.players
player_1 = players[0]
player_2 = players[1]

zerg = "Zerg"
protoss = "Protoss"
terran = "Terran"

XvZ = [0, 0]
XvP = [0, 0]
XvT = [0, 0]

# Testing
print(player_1)
print(player_2)
print(replay.players)

# Parsing races
p1 = str(player_1)
p2 = str(player_2)


def get_latest_replay():
    global replay
    global replay_path
    replay_list = glob.glob(replay_folder)
    last_replay = max(replay_list, key=os.path.getctime)
    if replay_path != last_replay:
        print("Old replay was: " + replay_path)
        print("Newest replay is: " + last_replay)
        replay_path = last_replay
        replay = sc2reader.load_replay(replay_path, load_level=4)
        check_players()


def parse_winner(player, opponent):
    global replay
    winner = replay.winner
    opponent_string = str(opponent)
    if winner == player:
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
    map_scores = open("mapscore.txt", "r+")
    map_scores.write(tracked_race + " v " + zerg + ": " + str(XvZ[0]) + "-" + str(XvZ[1]))
    map_scores.write("\n")
    map_scores.write(tracked_race + " v " + protoss + ": " + str(XvP[0]) + "-" + str(XvP[1]))
    map_scores.write("\n")
    map_scores.write(tracked_race + " v " + terran + ": " + str(XvT[0]) + "-" + str(XvT[1]))
    map_scores.close()


def check_players():
    if p1.find(tracked_player) != -1 and p1.find(tracked_race) != 1:
        parse_winner(player_1, player_2)
    elif p2.find(tracked_player) != -1 and p2.find(tracked_race) != -1:
        parse_winner(player_2, player_1)
    else:
        print(("Tracked Player " + tracked_player) + "-" + tracked_race + " not found in the replay, skipping")


while True:
    time.sleep(2)
    get_latest_replay()