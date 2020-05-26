import sc2reader

# Variables
replay = sc2reader.load_replay('Nightshade LE (44).SC2Replay', load_level=4)

tracked_player = "kKo"
tracked_race = "Terran"

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
    lines = map_scores.readlines()
    i = 0
    for x in lines:
        if x.find(zerg) != -1:
            x.replace(x, tracked_race + " v " + zerg + ": " + str(XvZ[0]) + "-" + str(XvZ[1]))
        if x.find(protoss) != -1:
            x.replace(x, tracked_race + " v " + protoss + ": " + str(XvP[0]) + "-" + str(XvP[1]))
        if x.find(terran) != -1:
            x.replace(x, tracked_race + " v " + terran + ": " + str(XvT[0]) + "-" + str(XvT[1]))
        i += 1
    for line in lines:
        map_scores.write(line)
    map_scores.close()


# Actual parser
while True:
    if p1.find(tracked_player) != -1 and p1.find(tracked_race) != 1:
        parse_winner(player_1, player_2)
    elif p2.find(tracked_player) != -1 and p2.find(tracked_race) != -1:
        parse_winner(player_2, player_1)
    else:
        print(("Tracked Player " + tracked_player) + "-" + tracked_race + " not found in the replay, skipping")
