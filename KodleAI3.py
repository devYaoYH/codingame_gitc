import sys
import math
import random

###################
# Debugging Flags #
###################
MSG_CONTENT = ""
MSG_MAXLEN = 42
MSG_RATE = 12
MSG_RANDIDX = -1
MSG_DELAY = MSG_MAXLEN
MSG_START = 0
MSG_END = MSG_MAXLEN
MSG_OUTPUT = True
SHOW_RESOLUTION = False
SHOW_ENEMY_ATTACKS = False

#########################
# Hitchhiker's Guide :O #
#########################
HITCHHIKER_GALAXY_QUOTES = ['Many were increasingly of the opinion that they\xe2\x80\x99d all made a big mistake in coming down from the trees in the first place. And some said that even the trees had been a bad move, and that no one should ever have left the oceans.', '\xe2\x80\x9cMy doctor says that I have a malformed public-duty gland and a natural deficiency in moral fibre,\xe2\x80\x9d Ford muttered to himself, \xe2\x80\x9cand that I am therefore excused from saving Universes.\xe2\x80\x9d', 'Isn\xe2\x80\x99t it enough to see that a garden is beautiful without having to believe that there are fairies at the bottom of it too?', 'A common mistake that people make when trying to design something completely foolproof is to underestimate the ingenuity of complete fools.', 'Curiously enough, the only thing that went through the mind of the bowl of petunias as it fell was Oh no, not again. Many people have speculated that if we knew exactly why the bowl of petunias had thought that we would know a lot more about the nature of the Universe than we do now.', 'The reason why it was published in the form of a micro sub meson electronic component is that if it were printed in normal book form, an interstellar hitchhiker would require several inconveniently large buildings to carry it around in.', '\xe2\x80\x9cForty-two,\xe2\x80\x9d said Deep Thought, with infinite majesty and calm.', 'Not unnaturally, many elevators imbued with intelligence and precognition became terribly frustrated with the mindless business of going up and down, up and down, experimented briefly with the notion of going sideways, as a sort of existential protest, demanded participation in the decision-making process and finally took to squatting in basements sulking.', 'Make it totally clear that this gun has a right end and a wrong end. Make it totally clear to anyone standing at the wrong end that things are going badly for them. If that means sticking all sort of spikes and prongs and blackened bits all over it then so be it. This is not a gun for hanging over the fireplace or sticking in the umbrella stand, it is a gun for going out and making people miserable with.', 'In the end, it was the Sunday afternoons he couldn\xe2\x80\x99t cope with, and that terrible listlessness that starts to set in about 2:55, when you know you\xe2\x80\x99ve taken all the baths that you can usefully take that day, that however hard you stare at any given paragraph in the newspaper you will never actually read it, or use the revolutionary new pruning technique it describes, and that as you stare at the clock the hands will move relentlessly on to four o\xe2\x80\x99clock, and you will enter the long dark teatime of the soul.', 'He gazed keenly into the distance and looked as if he would quite like the wind to blow his hair back dramatically at that point, but the wind was busy fooling around with some leaves a little way off.', 'He hoped and prayed that there wasn\xe2\x80\x99t an afterlife. Then he realized there was a contradiction involved here and merely hoped that there wasn\xe2\x80\x99t an afterlife.', '\xe2\x80\x9cIt seemed to me,\xe2\x80\x9d said Wonko the Sane, \xe2\x80\x9cthat any civilization that had so far lost its head as to need to include a set of detailed instructions for use in a packet of toothpicks, was no longer a civilization in which I could live and stay sane.\xe2\x80\x9d', '\xe2\x80\x9cNothing travels faster than the speed of light with the possible exception of bad news, which obeys its own special laws.\xe2\x80\x9d', 'Protect me from knowing what I don\xe2\x80\x99t need to know. Protect me from even knowing that there are things to know that I don\xe2\x80\x99t know. Protect me from knowing that I decided not to know about the things that I decided not to know about. Amen.', 'All you really need to know for the moment is that the universe is a lot more complicated than you might think, even if you start from a position of thinking it\xe2\x80\x99s pretty damn complicated in the first place.', 'In the beginning the Universe was created. This has made a lot of people very angry and been widely regarded as a bad move.', 'Don\xe2\x80\x99t Panic.', 'Don\xe2\x80\x99t Panic.']

#######################
# Behavioural Toggles #
#######################
SIMULATE_ENEMY = True

########################
# Behavioural Controls #
########################
MAP_RUSH_SIZE = 13
BOMB_SCORE_THRESHOLD = 0.57
BOMB_SCORE_THRESHOLD_LARGE = 1.03
MAX_LINK_DISTANCE = 7
ENEMY_MAX_LINK = 5

# Game Statics
MAX_INT = 65535
FACTORY_UPGRADE_COST = 10
BOMB_PRODUCTION_COOLDOWN = 5

# Target Scoring Constants
PRODUCTION_MULTIPLIER = 10
BOMB_TROOP_THRESHOLD = 25

# Movement Constants
TROOP_OFFENSIVE = 1.00 # Sends this % of troops against superior enemies
TROOP_DEFENSIVE = 1.00 # Sends this % of troops to reinforce friendly targets
TROOP_OFFENSIVE_MULTIPLIER = 1.17
TROOP_EXCESS_NEUTRAL = 1
TROOP_EXCESS_ENEMY = 1
ENEMY_OFFENSIVE = 1.53 # How offensive is the enemy
ENEMY_DEFENSIVE = 1.00 # How defensive is the enemy
ENEMY_EXCESS_NEUTRAL = 1
ENEMY_EXCESS_ENEMY = 1

# Game Variables
NUM_FACTORIES = 0
GAME_TURNS = 0
INITIAL_FACTORY = -1
INITIAL_FACTORY_ENEMY = -1
FRONTLINE_FACTORY = -1
FRONTLINE_DISTANCE = MAX_INT
CYBORGS_OWN = 0
CYBORGS_ENEMY = 0
num_bombs = 2

# Map Variables
adjList = [] # Adjacency List ordered by shortest distance
adjMatrix = [] # Adjacency Matrix
factoryInfo = [] # Information regarding each factory
troopInfo = [] # Packets for each troop movement
bombInfo = [] # Packets for each bomb movement

# Floyd-Warshall APSP matrix with backtracking
floydWarMatrix = [] # Store shortest distance
floydWarPath = [] # Stores complete path to objective
floydWarNext = [] #TODO: Optimization --> Stores next target?

# Simulation for next n turns
SIMUL_TURNS = 21
simulFac = [] # Simulated Factories for attack options

# Actions
turnMoves = [] # Commands for current turn
turnBombs = [] # Commands to send bombs
turnIncs = [] # Commands to upgrade factories
turnOne = True # Selector for initialization turn events

# Helper Functions
def readMaxAvailTroops(simulStates):
    # if (simulStates[0].production == 0): # Non-production factory
    #     return (simulStates[0].troops, 0)
    turn = 0
    ttt = MAX_INT
    availTroops = MAX_INT
    # Decide whether factory has been overrun
    if (simulStates[-1].owner == -1): # Overrun by enemy
        enProducedTroops = 0
        enProduction = simulStates[-1].production
        enFinalTroops = simulStates[-1].troops
        for i in range(2, len(simulStates)):
            if (simulStates[-i].owner == -1):
                if (simulStates[-i].cooldown <=0):
                    enProducedTroops += enProduction
                ttt = len(simulStates)-i
            else:
                break
        availTroops = enFinalTroops - enProducedTroops
        availTroops = -availTroops
    else:
        for state in simulStates:
            curTroops = state.troops if (state.owner == 1) else -state.troops
            if (curTroops < availTroops and ((turn < ttt) if availTroops < 0 else True)):
                availTroops = curTroops
                ttt = turn
            turn += 1
    return (availTroops, ttt)

def readMaxEnemyTroops(simulStates):
    # if (simulStates[0].production == 0): # Non-production factory
    #     return (simulStates[0].troops, 0)
    turn = 0
    ttt = MAX_INT
    availTroops = MAX_INT
    # Decide whether factory has been overrun
    if (simulStates[-1].owner == 1): # Overrun by enemy
        enProducedTroops = 0
        enProduction = simulStates[-1].production
        enFinalTroops = simulStates[-1].troops
        for i in range(2, len(simulStates)):
            if (simulStates[-i].owner == -1):
                enProducedTroops += enProduction
                ttt = len(simulStates)-i
            else:
                break
        availTroops = enFinalTroops - enProducedTroops
        availTroops = -availTroops
    else:
        for state in simulStates:
            curTroops = state.troops if (state.owner == -1) else -state.troops
            if (curTroops < availTroops and ((turn < ttt) if availTroops < 0 else True)):
                availTroops = curTroops
                ttt = turn
            turn += 1
    return (availTroops, ttt)

# Decision Making
def scoreTarget(tgtID, curID):
    distanceMultiplier = (float)(1.0/max(1,(adjMatrix[curID][tgtID]**2)))
    score = 0
    score += 7 if factoryInfo[tgtID].troops < factoryInfo[curID].troops else 0
    score += factoryInfo[tgtID].production*PRODUCTION_MULTIPLIER*distanceMultiplier # Rewards production
    score -= max(5, factoryInfo[tgtID].troops*0.5)*distanceMultiplier # Penalizes troops
    # print("{0} Score: {1}".format(tgtID, score), file=sys.stderr)
    return score

def scoreRedistribution(tgtID, curID, closestEnemyDistance):
    score = closestEnemyDistance
    # distanceMultiplier = (float)(1.0/max(1,closestEnemyDistance)**2)
    # score = 0
    # score += 7 if factoryInfo[tgtID].troops < factoryInfo[curID].troops else 0
    # score += factoryInfo[tgtID].production*PRODUCTION_MULTIPLIER*distanceMultiplier # Rewards production
    # score -= max(5, factoryInfo[tgtID].troops*0.5)*distanceMultiplier # Penalizes troops
    # print("{0} Score: {1}".format(tgtID, score), file=sys.stderr)
    return score

def scoreBomb(tgtID, curID, resolutions):
    if (tgtID == curID):
        return 0
    targetStates = resolutions[tgtID]
    ttt = adjMatrix[curID][tgtID]+1
    tttState = targetStates[ttt]
    distanceMultiplier = (float)(1.0/max(1,(ttt**2)))
    # print("Dist Mult: {0} | ttt: {1}".format(distanceMultiplier, ttt), file=sys.stderr)
    score = 0
    score += tttState.production*PRODUCTION_MULTIPLIER*distanceMultiplier # Rewards production
    # print("Production score: {0}".format(score), file=sys.stderr)
    score += max(10, tttState.troops)*distanceMultiplier # Rewards troops
    # print("{0} Score: {1}".format(tgtID, score), file=sys.stderr)
    return score
        
def should_bomb(tgtID, curID, resolutions):
    # print("Testing target Factory {0}:".format(tgtID), file=sys.stderr)
    if (tgtID == curID):
        return False
    targetStates = resolutions[tgtID]
    ttt = adjMatrix[curID][tgtID]+1
    tttState = targetStates[ttt]
    # print("Ttt state: Owner->{0} | Troops->{1} | Production->{2}".format(tttState.owner, tttState.troops, tttState.production), file=sys.stderr)
    if (tttState.owner != -1):
        return False
    if (num_bombs < 1):
        return False
    if (tttState.troops > BOMB_TROOP_THRESHOLD):
        return True
    if (tttState.production > 2):
        return True
    return False

def should_reinforce(facID):
    if (factoryInfo[facID].owner != 1):
        return False
    if (factoryInfo[facID].troops < 1):
        return False
    if (factoryInfo[facID].production < 3):
        return False
    return True

def needed_upgradeTroops(curFac, tgtFac, resolutions):
    ttt = floydWarMatrix[curFac.ID][tgtFac.ID]+1
    arrivalState = resolutions[tgtFac.ID][ttt]
    if (arrivalState.owner == -1 and arrivalState.troops > 0):
        return -1
    if (arrivalState.production < 3):
        requestTroops = FACTORY_UPGRADE_COST - (arrivalState.troops if arrivalState.owner == 1 else -arrivalState.troops)
        if (requestTroops > 0):
            return requestTroops
    return -1

def needed_reinforcements(ttt, availTroops, resolution):
    arrivalState = resolution[ttt]
    print("State: Owner->{0} | Troops->{1}".format(arrivalState.owner, arrivalState.troops), file=sys.stderr)
    if (arrivalState.production < 1): #TODO: Do not reinforce no production factories?
        return -1
    #TODO: Will be in time to reinforce?
    requestTroopsTup = readMaxAvailTroops(resolution)
    requestTroops = requestTroopsTup[0] # Reads how many troops needed
    requestTurn = requestTroopsTup[1] # Reads when it is needed
    print("Requested troops: {0} by turn: {1}".format(requestTroops, requestTurn), file=sys.stderr)
    if (requestTroops < 0):
        return min(availTroops, -requestTroops)
    return -1

def simulateEnemySmart(enemyFac, resolutions):
    # Storing enemy movements
    actions = []

    # Simulate enemy attacks
    if (enemyFac.troops < 1):
        return actions
    curTroops = min(enemyFac.troops, readMaxEnemyTroops(resolutions[enemyFac.ID])[0])
    if (SHOW_ENEMY_ATTACKS):
        print("Simulating enemy attacks from Factory {0}|Current Troops: {1}".format(enemyFac.ID, curTroops), file=sys.stderr)

    validTargets = []
    for adj in range(NUM_FACTORIES):
        ignore = False
        targetFac = factoryInfo[adj]
        # Filters targets and add some to valid target list
        if (targetFac.owner == -1):
            ignore = True # Ignore 'own' factories
        else:
            if (targetFac.production == 0):
                ignore = True # Ignores factories that do not give production
        # Adds valid targets
        if (ignore):
            continue
        else:
            validTargets.append(targetFac)

    # Naive case: no cyborgs!
    for targetFac in validTargets:
        if (curTroops < 1):
            return actions
        if (targetFac.troops == 0 and targetFac.owner == 0):
            actions.append(MOVE([enemyFac.ID, targetFac.ID, 1]))
            curTroops -= 1

    # Weighs targets
    weightedTargets = []
    for targetFac in validTargets:
        weightedTargets.append((targetFac, scoreTarget(targetFac.ID, enemyFac.ID)))
    weightedTargets = sorted(weightedTargets, key=lambda x: x[1], reverse=True)

    # Attacks targets in weighted order
    for targetTup in weightedTargets:
        if (curTroops < 1):
            return actions
        targetFac = targetTup[0]
        targetStates = resolutions[targetFac.ID]
        ttt = adjMatrix[enemyFac.ID][targetFac.ID]+1
        # Do not simulate enemy movements beyond immediacy
        if (ttt > ENEMY_MAX_LINK):
            continue
        tttState = targetStates[ttt]
        if (SHOW_ENEMY_ATTACKS):
            print("Enemy attacking: {0}".format(targetFac.ID), file=sys.stderr)
        targetAttack = False
        targetTroops = 0
        # Determines how many troops to send
        if (tttState.owner == 0):
            targetTroops = int((tttState.troops+ENEMY_EXCESS_NEUTRAL)*ENEMY_OFFENSIVE)
            if (targetTroops <= curTroops):
                targetAttack = True
        elif (tttState.owner == 1):
            targetTroops = int((tttState.troops+ENEMY_EXCESS_ENEMY)*ENEMY_OFFENSIVE)
            if (targetTroops <= curTroops):
                targetAttack = True
            else:
                targetTroops = curTroops
                targetAttack = True
        # Issues attack command if available
        if (targetAttack):
            originID = enemyFac.ID
            targetID = targetFac.ID
            closestIntermediate = floydWarPath[enemyFac.ID][targetFac.ID][0]
            if (closestIntermediate != -1):
                targetID = closestIntermediate
            actions.append(MOVE([originID, targetID, targetTroops]))
            if (SHOW_ENEMY_ATTACKS):
                print(actions[-1].printCmd(), file=sys.stderr)
            curTroops -= targetTroops
    return actions

# Classes
class FactoryMsg(object):

    def __init__(self, entityID, args):
        self.ID = entityID
        self.owner = args[0]
        self.troops = args[1]
        self.production = args[2]
        self.cooldown = args[3]

    def updateOwnership(self):
        if (self.troops < 0):
            self.owner *= -1
            self.troops = abs(self.troops)

class TroopMsg(object):

    def __init__(self, entityID, args):
        self.ID = entityID
        self.owner = args[0]
        self.origin = args[1]
        self.target = args[2]
        self.size = args[3]
        self.ttt = args[4]

    def isEnemy(self):
        return (self.owner == -1)

class BombMsg(object):

    def __init__(self, entityID, args):
        self.ID = entityID
        self.owner = args[0]
        self.origin = args[1]
        self.target = args[2]
        self.ttt = args[3]

    def isEnemy(self):
        return (self.owner == -1)

class Action(object):

    def __init__(self, entityType):
        self.form = entityType
        self.origin = -1
        self.target = -1
        self.size = -1

    def isMove(self):
        return (self.form == "MOVE")

class MOVE(Action):

    def __init__(self, args):
        Action.__init__(self, "MOVE")
        self.origin = int(args[0])
        self.target = int(args[1])
        self.size = int(args[2])

    def printCmd(self):
        return "MOVE {0} {1} {2}".format(self.origin, self.target, self.size)

class BOMB(Action):

    def __init__(self, args):
        Action.__init__(self, "BOMB")
        self.origin = int(args[0])
        self.target = int(args[1])

    def printCmd(self):
        return "BOMB {0} {1}".format(self.origin, self.target)

class INC(Action):

    def __init__(self, args):
        Action.__init__(self, "INC")
        self.origin = int(args[0])

    def printCmd(self):
        return "INC {0}".format(self.origin)

class FactorySimulation(object):

    def __init__(self, facID, args):
        self.ID = facID
        self.owner = int(args[0])
        self.troops = int(args[1])
        self.production = int(args[2])
        self.cooldown = int(args[3])

    def tick(self):
        if (self.cooldown > 0):
            self.cooldown -= 1
        if (self.owner != 0 and self.cooldown <= 0):
            self.troops += self.production

    def bombed(self):
        self.troops -= 0.5*self.troops if 0.5*self.troops > 10 else self.troops
        self.cooldown = BOMB_PRODUCTION_COOLDOWN

    def procPacket(self, packet):
        if (packet.owner == self.owner):
            self.troops += packet.size
        else:
            self.troops -= packet.size
            if (self.troops < 0):
                self.troops = abs(self.troops)
                self.owner = packet.owner

class Factory(object):

    def __init__(self, facID):
        self.ID = facID
        self.owner = 0
        self.troops = 0
        self.production = 0
        self.cooldown = 0
        self.incomming = []
        self.outgoing = [] #TODO: not necessary? since outgoing == incomming somewhere else
        self.actions = []
        self.blacklist = [] # Blacklisted enemy targets
        self.TROOP_OFFENSIVE = TROOP_OFFENSIVE # Local threshold
        self.TROOP_DEFENSIVE = TROOP_DEFENSIVE # Local threshold

    def tick(self):
        del self.incomming[:]
        del self.outgoing[:]
        del self.actions[:]
        del self.blacklist[:]

    def update(self, args):
        self.owner = args[0]
        self.troops = args[1]
        self.production = args[2]
        self.cooldown = args[3]

    def updateBlacklist(self, argList):
        self.blacklist = argList

    def pushIncomming(self, packet):
        self.incomming.append(packet)

    def delIncomming(self, packetID):
        idList = [pack.ID for pack in self.incomming]
        if (packetID not in idList): # Error, packet not found
            return False
        else:
            del self.incomming[idList.index(packetID)]
            return True

    def getAvailTroops(self, simulStates):
        curTroops = min(self.troops, readMaxAvailTroops(simulStates[self.ID])[0])
        return curTroops

    def closestEnemy(self):
        nearestFactory = -1
        nearestDistance = MAX_INT
        for facID in range(NUM_FACTORIES):
            if (adjMatrix[self.ID][facID] < nearestDistance and factoryInfo[facID].owner == -1):
                nearestDistance = adjMatrix[self.ID][facID]
                nearestFactory = facID
        if (nearestFactory != -1):
            return (nearestFactory, nearestDistance)
        else:
            return (nearestFactory, MAX_INT)

    def closestFriendly(self):
        nearestFactory = -1
        nearestDistance = MAX_INT
        for facID in range(NUM_FACTORIES):
            if (facID == self.ID):
                continue
            if (adjMatrix[self.ID][facID] < nearestDistance and factoryInfo[facID].owner == 1):
                nearestDistance = adjMatrix[self.ID][facID]
                nearestFactory = facID
        if (nearestFactory != -1):
            return (nearestFactory, nearestDistance)
        else:
            return (nearestFactory, MAX_INT)

    def viable_upgrade(self, resolution, prevUpgrades):
        updatedResolutions = []
        # Builds updated states for next FACTORY_UPGRADE_COST turns
        for i in range(min(SIMUL_TURNS, FACTORY_UPGRADE_COST)):
            curState = resolution[i]
            newState = FactoryMsg(curState.ID, [curState.owner, curState.troops, curState.production, curState.cooldown])
            newState.troops = curState.troops - FACTORY_UPGRADE_COST*(prevUpgrades+1) + i*(prevUpgrades+1)
            newState.updateOwnership()
            updatedResolutions.append(newState)
        # Checks for viability given an upgrade
        for state in updatedResolutions:
            if (state.owner != 1):
                return False
        return True

    '''
    Simulation function
        - Takes incomming troop packets
        - Runs turn-by-turn simulation
        - Outputs an array of states for SIMUL_TURNS turns
    '''
    def resolve(self): #TODO: Huge function, simulates game till last troop packet arrives
        # Generates array to store simulation
        curState = FactorySimulation(self.ID, (self.owner, self.troops, self.production, self.cooldown))
        simulMap = []
        packetIdx = 0

        # If there's no contention, extend current state
        if (len(self.incomming) == 0):
            for turn in range(SIMUL_TURNS):
                # Ticks cooldown timer and produces troops
                if (turn > 0):
                    curState.tick()
                # Explodes bombs
                for bomb in bombInfo:
                    if (bomb.owner == 1 and bomb.target == self.ID and bomb.ttt < 1):
                        curState.bombed()
                # Stores current turn simulated result
                args = (curState.owner, curState.troops, curState.production, curState.cooldown)
                facState = FactoryMsg(self.ID, args)
                simulMap.append(facState)

        # Computes a turn-by-turn simulation upon this factory
        else:
            self.incomming = sorted(self.incomming, key=lambda x: x.ttt) # Sort by time to target
        
            # Simulates ownership for SIMUL_TURNS turns
            # print("Starting resolution for Factory {0}...".format(self.ID), file=sys.stderr)
            for turn in range(SIMUL_TURNS):
                # Produces Units
                if (turn > 0):
                    curState.tick()
                # Resolves Battles
                curTtt = 0
                tttPackets = []
                while (packetIdx < len(self.incomming) and self.incomming[packetIdx].ttt <= turn):
                    # print("Turn {0}:".format(turn), file=sys.stderr)
                    # print("Packet: Owner->{0} | Troops->{1}".format(self.incomming[packetIdx].owner, self.incomming[packetIdx].size), file=sys.stderr)
                    # print("Current Troops in Factory: {0}".format(curState.troops), file=sys.stderr)
                    #BUG_FIX: Resolves all packets comming at the same time prior to resolving to curState
                    if (self.incomming[packetIdx].ttt > curTtt):
                        curTtt = self.incomming[packetIdx].ttt
                        # Process last ttt's list of packets
                        if (len(tttPackets) == 1): # Only 1 packet
                            curState.procPacket(tttPackets[-1])
                            del tttPackets[:]
                        elif (len(tttPackets) > 1):
                            curTroops = 0
                            for packet in tttPackets:
                                if (packet.owner == 1):
                                    curTroops += packet.size
                                else:
                                    curTroops -= packet.size
                            curOwner = 1 if curTroops > 0 else -1
                            args = (curOwner, tttPackets[-1].origin, self.ID, abs(curTroops), 0)
                            newPacket = TroopMsg((random.randint(2,100)*-100), args)
                            curState.procPacket(newPacket)
                            del tttPackets[:]
                    if (self.incomming[packetIdx].ttt == curTtt):
                        tttPackets.append(self.incomming[packetIdx])
                    # print("Resolved Troops in Factory: {0}".format(curState.troops), file=sys.stderr)
                    packetIdx += 1
                # Process the last turn's packets
                if (len(tttPackets) == 1): # Only 1 packet
                    curState.procPacket(tttPackets[-1])
                    del tttPackets[:]
                elif (len(tttPackets) > 1):
                    curTroops = 0
                    for packet in tttPackets:
                        if (packet.owner == 1):
                            curTroops += packet.size
                        else:
                            curTroops -= packet.size
                    curOwner = 1 if curTroops > 0 else -1
                    args = (curOwner, tttPackets[-1].origin, self.ID, abs(curTroops), 0)
                    newPacket = TroopMsg((random.randint(2,100)*-100), args)
                    curState.procPacket(newPacket)
                    del tttPackets[:]
                # Explodes bombs
                for bomb in bombInfo:
                    #BUG_FIX: bomb.ttt < 1 ==> turn >= bomb.ttt
                    if (bomb.owner == 1 and bomb.target == self.ID and turn >= bomb.ttt):
                        curState.bombed()
                # Stores current turn simulated result
                args = (curState.owner, curState.troops, curState.production, curState.cooldown)
                facState = FactoryMsg(self.ID, args)
                simulMap.append(facState)

        #DEBUG: Prints out states of each turn
        if (SHOW_RESOLUTION):
            print("======================\nResolved Factory {0}:\n======================".format(self.ID), file=sys.stderr)
            print("Initial Troop count: {0}".format(self.troops), file=sys.stderr)
            for i in range(7):
                print("Step {0}: Owner->{1} | Troops->{2} | Production->{3} | Cooldown->{4}".format(i, simulMap[i].owner, simulMap[i].troops, simulMap[i].production, simulMap[i].cooldown), file=sys.stderr)
            print("Max Available Units: {0}".format(readMaxAvailTroops(simulMap)[0]), file=sys.stderr)
            print("Turns before being overrun: {0}".format(readMaxAvailTroops(simulMap)[1]), file=sys.stderr)
        return simulMap # Outputs list of simulated factory state tuples
    
    '''
    Reinforce function
        - Takes a list of targets to be reinforced
        - Weighs targets
        - Sends reinforcements if available
    '''
    def reinforce(self, simulStates): #TODO: How to bring troops to the front?
        curTroops = min(self.troops, readMaxAvailTroops(simulStates[self.ID])[0])
        print("Factory {0} Reinforcing...|Current Troops: {1}".format(self.ID, curTroops), file=sys.stderr)
        if (curTroops < 1):
            return self.actions

        # Get connected friendly reinforcible factories
        adjMyFactories = [facTup[0] for facTup in adjList[self.ID] if (factoryInfo[facTup[0]].owner == 1)]

        # Weighs targets
        weightedTargets = []
        for target in adjMyFactories:
            weightedTargets.append((target, scoreRedistribution(target, self.ID, factoryInfo[target].closestEnemy()[1])))
        weightedTargets = sorted(weightedTargets, key=lambda x: x[1], reverse=True)
        
        # Reinforces targets in weighted order
        for targetTup in weightedTargets:
            if (curTroops < 1):
                self.troops = curTroops
                return self.actions
            target = targetTup[0]
            ttt = floydWarMatrix[self.ID][target]+1
            print("Reinforcing factory {0}:".format(target), file=sys.stderr)
            requestTroops = needed_reinforcements(ttt, curTroops, simulStates[target])
            if (requestTroops < 0):
                continue
            self.actions.append(MOVE([self.ID, target, requestTroops]))
            print(self.actions[-1].printCmd(), file=sys.stderr)
            curTroops -= requestTroops

        self.troops = curTroops
        return self.actions

    '''
    Attack function
        - Prioritizes Upgrade if base will not get overrun in the future
        - Gets a list of valid targets (enemy + neutrals) not in blacklist
        - Weigh valid targets
        - Issues attack commands by priority of weight
    '''
    def attack(self, simulStates): #TODO: Where to upgrade factories??
        if (self.production == 0 and self.ID != INITIAL_FACTORY):
            self.TROOP_OFFENSIVE = 1
            self.TROOP_DEFENSIVE = 1
        else:
            self.TROOP_OFFENSIVE = TROOP_OFFENSIVE
            self.TROOP_DEFENSIVE = TROOP_DEFENSIVE
        curTroops = min(self.troops, readMaxAvailTroops(simulStates[self.ID])[0])
        print("Factory {0}|Current Troops: {1}".format(self.ID, curTroops), file=sys.stderr)
        if (curTroops < 1):
            self.troops = curTroops
            return self.actions

        validTargets = []
        for adj in adjList[self.ID]:
            ignore = False
            targetFac = factoryInfo[adj[0]]
            targetStates = simulStates[adj[0]]
            ttt = floydWarMatrix[self.ID][targetFac.ID]+1
            
            # print("Evaluating target Factory: {0}".format(adj[0]), file=sys.stderr)
            # Filters targets and add some to valid target list
            if (targetStates[ttt].owner == 1):
                # print("IGNORE -> Owned", file=sys.stderr)
                ignore = True # Ignore our own factories (no attack necessary)
            else:
                if (targetFac.production == 0):
                    # print("IGNORE -> Production 0", file=sys.stderr)
                    ignore = True # Ignore factories that do not give production
            
            # Ignores blacklisted targets
            if (targetFac.ID in self.blacklist):
                # print("IGNORE -> Blacklisted", file=sys.stderr)
                ignore = True
            
            # Adds valid targets
            if (ignore):
                continue
            else:
                # print("VALID! :)", file=sys.stderr)
                validTargets.append(targetFac)

        # Naive case: no cyborgs!
        for targetFac in validTargets:
            if (curTroops < 1):
                self.troops = curTroops
                return self.actions
            ttt = floydWarMatrix[self.ID][targetFac.ID]+1
            targetState = simulStates[targetFac.ID][ttt]
            if (targetState.troops == 0 and targetState.owner == 0):
                self.actions.append(MOVE([self.ID, targetFac.ID, 1]))
                print(self.actions[-1].printCmd(), file=sys.stderr)
                curTroops -= 1
                targetFac = None #TODO: Removes target from list?
        validTargets = [fac for fac in validTargets if fac != None] # Removes None-types

        #TODO: Ad-Hoc upgrades (temporary)
        upgradeFactory = True
        curProduction = self.production
        upgrades = 0
        #EXPERIMENTAL: Don't too aggressively upgrade factories close to the enemy
        adjFriendlyTup = self.closestFriendly()
        adjEnemyTup = self.closestEnemy()
        # if (adjFriendlyTup[0] == -1): # Initial Factory or only factory
        #     if (adjEnemyTup[0] != -1):
        #         if (adjEnemyTup[1] < MAP_RUSH_SIZE):
        #             upgradeFactory = False
        if (adjFriendlyTup[0] != -1 and adjEnemyTup[0] != -1):
            # print("Testing viability for upgrade based on distance to enemy", file=sys.stderr)
            # print("Distance to friendly factory {0}: {1} | Distance to enemy factory {2}: {3}".format(adjFriendlyTup[0], adjFriendlyTup[1], adjEnemyTup[0], adjEnemyTup[1]), file=sys.stderr)
            if (adjEnemyTup[1] <= adjFriendlyTup[1] and (CYBORGS_OWN - CYBORGS_ENEMY) < FACTORY_UPGRADE_COST):
                upgradeFactory = False
        # Decides suitability for upgrading
        while (upgradeFactory):
            # Safety check for troops available
            if (curTroops < FACTORY_UPGRADE_COST):
                upgradeFactory = False
            # Disables upgrades if nearby neutral exists with production
                # On the condition that one can take it
                # And such a move would bring about more overall units than upgrading
            neutralFactories = []
            for targetFac in validTargets:
                targetStates = simulStates[targetFac.ID]
                ttt = floydWarMatrix[self.ID][targetFac.ID]+1
                tttState = targetStates[ttt]
                if (tttState.owner == 0 and tttState.production > 0):
                    tttDiff = FACTORY_UPGRADE_COST - ttt
                    if (tttDiff < 0 or tttState.production*tttDiff > FACTORY_UPGRADE_COST and tttState.troops < curTroops):
                        neutralFactories.append(targetFac.ID)
            if (len(neutralFactories) > 0):
                upgradeFactory = False
            # Checks conditions for an upgrade
            if (curProduction == 3 or not self.viable_upgrade(simulStates[self.ID], upgrades)):
                upgradeFactory = False
            # Upgrades Current Factory
            if (upgradeFactory):
                upgrades += 1
                curProduction += 1
                print("Upgrading factory with {0} troops at level {1} production".format(curTroops, factoryInfo[self.ID].production), file=sys.stderr)
                self.actions.append(INC([self.ID]))
                curTroops -= FACTORY_UPGRADE_COST
        
        # Weighs targets
        weightedTargets = []
        for targetFac in validTargets:
            weightedTargets.append((targetFac, scoreTarget(targetFac.ID, self.ID)))
        weightedTargets = sorted(weightedTargets, key=lambda x: x[1], reverse=True)
        
        # Prioritizes targets that can be overwhelmed
        overwhelmTargets = []
        ignoreTargets = []
        # Classifies targets
        for targetTup in weightedTargets:
            if (curTroops < 1):
                self.troops = curTroops
                return self.actions
            targetFac = targetTup[0]
            targetStates = simulStates[targetFac.ID]
            ttt = floydWarMatrix[self.ID][targetFac.ID]+1
            tttState = targetStates[ttt]

            # Checks that troops won't arrive before bomb :O
            ignore = False
            for bomb in bombInfo:
                if (bomb.owner == 1):
                    print("Bomb from {0}->{1} arrives in: {2} | Attack arrives in: {3}".format(bomb.origin, bomb.target, bomb.ttt, ttt), file=sys.stderr)
                    if (bomb.target == targetFac.ID and ttt <= bomb.ttt):
                        ignore = True
                        break
            if (ignore):
                ignoreTargets.append(targetFac)
                continue

            targetAttack = False
            targetTroops = 0
            if (tttState.owner == 0): # Neutral Target
                targetTroops = tttState.troops+TROOP_EXCESS_NEUTRAL
                if (targetTroops <= curTroops): # Can overwhelm target
                    targetAttack = True
            else: # Enemy Target
                targetTroops = int((tttState.troops+TROOP_EXCESS_ENEMY)*TROOP_OFFENSIVE_MULTIPLIER)+1
                if (targetTroops <= curTroops): # Can overwhelm target
                    targetAttack = True

            # Adds target to priority list if can be overwhelmed
            if (targetAttack):
                overwhelmTargets.append(targetFac)
                self.actions.append(MOVE([self.ID, targetFac.ID, targetTroops]))
                print(self.actions[-1].printCmd(), file=sys.stderr)
                curTroops -= targetTroops

        # Attacks targets in weighted order
        for targetTup in weightedTargets:
            if (curTroops < 1):
                self.troops = curTroops
                return self.actions
            targetFac = targetTup[0]
            # Filters targets on ignore list or priority list
            if (targetFac in ignoreTargets or targetFac in overwhelmTargets):
                continue
            targetStates = simulStates[targetFac.ID]
            ttt = floydWarMatrix[self.ID][targetFac.ID]+1
            tttState = targetStates[ttt]
            print("Attacking: {0} | ttt: {1} | tttState: Owner->{2} Troops->{3}".format(targetFac.ID, ttt, tttState.owner, tttState.troops), file=sys.stderr)
            # Determines how many troops to send
            targetAttack = False
            targetTroops = 0
            if (tttState.owner == 0): # Neutral Target
                targetTroops = tttState.troops+TROOP_EXCESS_NEUTRAL
                if (targetTroops <= curTroops): # Can overwhelm target
                    print("Overwhelming...", file=sys.stderr)
                    targetAttack = True
                #EXPERIMENTAL: Disabling suspension of attacks
                # elif (targetTroops <= curTroops+self.production): # Able to target next turn
                #     print("Suspend attacks", file=sys.stderr)
                #     self.troops = curTroops
                #     return self.actions
                else: # Unable to overwhelm target immediately
                    targetTroops = int(self.TROOP_OFFENSIVE*curTroops)
                    print("Cannot overwhelm, sending {0} troops".format(targetTroops), file=sys.stderr)
                    targetAttack = True
            elif (tttState.owner == -1): # Enemy Target
                # We only attack when our attack can overwhelm enemy
                targetTroops = int((tttState.troops+TROOP_EXCESS_ENEMY)*TROOP_OFFENSIVE_MULTIPLIER)+1
                if (targetTroops <= curTroops):
                    print("ENEMY! Sending {0} troops".format(targetTroops), file=sys.stderr)
                    targetAttack = True
            # Issues attack command if available
            if (targetAttack):
                self.actions.append(MOVE([self.ID, targetFac.ID, targetTroops]))
                print(self.actions[-1].printCmd(), file=sys.stderr)
                curTroops -= targetTroops
        self.troops = curTroops
        return self.actions

    '''
    Upgrade function
        - Sends troops to nearby factories to facilitate their upgrading
    '''
    def upgrade(self, simulStates):
        curTroops = min(self.troops, readMaxAvailTroops(simulStates[self.ID])[0])
        print("Factory {0} Sending troops for Upgrading...|Current Troops: {1}".format(self.ID, curTroops), file=sys.stderr)
        if (curTroops < 1):
            self.troops = curTroops
            return self.actions
        # Scans for nearby factories
        for adj in adjList[self.ID]:
            if (curTroops < 1):
                self.troops = curTroops
                return self.actions
            adjFac = factoryInfo[adj[0]]
            #EXPERIMENTAL: We send units in bulk
            requestTroops = min(curTroops, needed_upgradeTroops(self, adjFac, simulStates))
            # requestTroops = needed_upgradeTroops(self, adjFac, simulStates)
            if (requestTroops > 0 and requestTroops <= curTroops):
                self.actions.append(MOVE([self.ID, adjFac.ID, requestTroops]))
                print(self.actions[-1].printCmd(), file=sys.stderr)
                curTroops -= requestTroops
        self.troops = curTroops
        return self.actions

    '''
    Redistribution function
        - Scans for nearby friendly factories closer than self to enemy
        - Sends excess troops proportionally to those factories
    '''
    def redistribute(self, simulStates):
        curTroops = min(self.troops, readMaxAvailTroops(simulStates[self.ID])[0])
        print("Factory {0} Redistributing...|Current Troops: {1}".format(self.ID, curTroops), file=sys.stderr)
        if (curTroops < 1):
            return self.actions

        #TODO: If have excess troops, send them off proportionally to nearby friendly factories?
        # Get connected friendly reinforcible factories
        adjMyFactories = [facTup[0] for facTup in adjList[self.ID] if (factoryInfo[facTup[0]].owner == 1)]
        myDistToEnemy = self.closestEnemy()[1]
        print("My distance to enemy: {0}".format(myDistToEnemy), file=sys.stderr)
       
        # Get list of 'frontline' friendly factories
        adjFrontlineFactories = [facID for facID in adjMyFactories if (len([enID for enID in range(NUM_FACTORIES) if factoryInfo[enID].owner == -1]) > 0) and factoryInfo[facID].closestEnemy()[1] < myDistToEnemy]
        weightedFrontlineFactories = []
        for facID in adjFrontlineFactories:
            print("Adjacent factory distance to enemy: {0}".format(factoryInfo[facID].closestEnemy()[1]), file=sys.stderr)
            weightedFrontlineFactories.append((facID, scoreRedistribution(facID, self.ID, factoryInfo[facID].closestEnemy()[1])))
        weightedFrontlineFactories = sorted(weightedFrontlineFactories, key=lambda x: x[1])

        # Sends available troops based on score
        totScore = 0
        minScore = MAX_INT
        scoreList = [scoreTup[1] for scoreTup in weightedFrontlineFactories]
        limTroops = 0 if self.production == 3 else FACTORY_UPGRADE_COST
        totTroops = max(0, curTroops - limTroops)
        for score in scoreList: # Get min score
            if (score < minScore):
                minScore = score
        for score in scoreList: # Transform range of scoreList to [0, INF)
            score -= minScore
            totScore += score
        for scoreTup in weightedFrontlineFactories:
            if (curTroops <= limTroops):
                self.troops = curTroops
                return self.actions
            normScore = scoreTup[1] - minScore
            weightedTroops = max(curTroops,int((float)(normScore/max(1,totScore))*totTroops))
            if (weightedTroops <= curTroops):
                self.actions.append(MOVE([self.ID, scoreTup[0], weightedTroops]))
                print(self.actions[-1].printCmd(), file=sys.stderr)
                curTroops -= weightedTroops

        # Just send whatever amts of troops off to the highest-weighted factory
        if (curTroops > 0 and len(weightedFrontlineFactories) > 0):
            self.actions.append(MOVE([self.ID, weightedFrontlineFactories[0][0], curTroops]))
            print(self.actions[-1].printCmd(), file=sys.stderr)
            curTroops -= curTroops

        self.troops = curTroops
        return self.actions

class Strategizer(object):

    def __init__(self, resolutions, simulation, bombs, incs, simulIDCounter):
        self.resolutions = resolutions # 2D list of FactoryMsg objects
        self.actions = []
        self.evalActions = []
        self.blacklistedEnemies = [] # Enemies we can overpower
        self.simulation = simulation
        self.bombs = bombs
        self.incs = incs
        self.simulIDCounter = simulIDCounter

    '''
    Simulated pushing of troop packets to targeted factories
        - Takes some list of actions and 'executes' them
        - Results in troop packets pushed to incomming queue for targeted factories
    '''
    def simulate(self, actions):
        # print("Simulating: ", file=sys.stderr)
        for move in actions:
            if (move.isMove()):
                if (move.size < 1): # Prunes off no troop packets
                    continue
                args = [1, move.origin, move.target, move.size, adjMatrix[move.origin][move.target]+1]
                curPacket = TroopMsg(self.simulIDCounter, args)
                self.simulIDCounter += 1
                self.simulation[move.target].pushIncomming(curPacket)
                # print("Pushed: "+move.print()+" to Factory: {0} | CurPackets: {1}".format(move.target, len(self.simulation[move.target].incomming)), file=sys.stderr)

    '''
    Conservative troop processing strategy
        - Block attacks to resolved targets
        - Orders priority of troop movement as such:
            1) Reinforces nearby factories
            2) Attack nearby factories
            3) Sends troops to upgrade nearby factories
            4) Redistributes remaining troops to nearby factories
    '''
    def execute(self):
        # Prune off excess attacks
        myFactories = [self.simulation[facID] for facID in range(NUM_FACTORIES) if (self.simulation[facID].owner == 1)] # Own factories
        for i in range(len(self.resolutions)):
            simulState = self.resolutions[i]
            if (simulState[-1].owner == 1 and self.simulation[i].owner != 1):
                print("Battle for {0} resolved in our favor, preventing further troops".format(i), file=sys.stderr)
                # Add target to blacklist
                self.blacklistedEnemies.append(i)
        
        # 1) Sends reinforcements
        for fac in myFactories:
            print("Factory {0} reinforcing...".format(fac.ID), file=sys.stderr)
            fac.reinforce(self.resolutions)

        # 2) Re-evaluates attack options
        for fac in myFactories:
            print("======================\nFactory {0} attacking...\n======================".format(fac.ID), file=sys.stderr)
            fac.updateBlacklist(self.blacklistedEnemies)
            fac.attack(self.resolutions)

        # 3) Runs troop movements for upgrades
        upgradeFactories = [self.simulation[facID] for facID in range(NUM_FACTORIES) if should_reinforce(facID)]
        for fac in upgradeFactories:
            fac.upgrade(self.resolutions)

        # 4) Redistributes excess troops
        for fac in myFactories:
            fac.redistribute(self.resolutions)

    '''
    Redirects troops along floyd-warshall path instead of naive direct pathing
    '''
    def redirect(self): #TODO: run floyd-warshall per turn?
        # Runs simulation for redirecting
        myFactories = [self.simulation[facID] for facID in range(NUM_FACTORIES) if (self.simulation[facID].owner == 1)] # Own factories
        for fac in myFactories:
            self.evalActions.extend(fac.actions)
        self.simulate(self.evalActions)

        # Re-paths troop packets
        for fac in self.simulation:
            # print("Redirecting for target Factory {0} | Packets: {1}".format(fac.ID, len(fac.incomming)), file=sys.stderr)
            delList = []
            for troop in fac.incomming:
                closestIntermediate = floydWarPath[troop.origin][fac.ID][0]
                ttt = floydWarMatrix[troop.origin][closestIntermediate]+1
                closestIntermediateOwner = self.resolutions[closestIntermediate][ttt].owner
                # print("Attempting Redirect:\nTroop destination: {0}\nOrigin: {1}\nIntermediate: {2}".format(fac.ID, troop.origin, closestIntermediate), file=sys.stderr)
                if (closestIntermediate != fac.ID):
                    troop.target = closestIntermediate
                    troop.ttt = ttt
                    self.simulation[closestIntermediate].pushIncomming(troop)
                    # print("Redirection troop: {0}-->{1} from initial target {2}".format(troop.origin, closestIntermediate, fac.ID), file=sys.stderr)
                    delList.append(troop.ID)
            if (len(delList) > 0):
                for i in range(len(delList)):
                    fac.delIncomming(delList[i])

    def prune(self): #TODO: prunes excess troops sent and orgnize co-ordinated attacks
        return None

    def whack(self): #TODO: Barrage with all available troops
        myFactories = [self.simulation[facID] for facID in range(NUM_FACTORIES) if (self.simulation[facID].owner == 1)] # Own factories
        whackActions = []
        #TODO: All focus whack on a single enemy factory?
        for fac in myFactories:
            if (fac.getAvailTroops(self.resolutions) < 1 or fac.production < 3):
                continue
            adjEnemy = fac.closestEnemy()[0]
            if (adjEnemy != -1):
                targetID = adjEnemy
                closestIntermediate = floydWarPath[fac.ID][targetID][0]
                if (closestIntermediate != -1):
                    targetID = closestIntermediate
                whackActions.append(MOVE([fac.ID, targetID, fac.getAvailTroops(self.resolutions)]))
                print(whackActions[-1].printCmd(), file=sys.stderr)
                fac.troops -= fac.getAvailTroops(self.resolutions)
        self.simulate(whackActions)
        return None

    def printCmd(self):
        # Adds movement commands
        for fac in self.simulation:
            for troop in fac.incomming:
                self.actions.append(MOVE([troop.origin,fac.ID,troop.size]).printCmd())
        # Adds bomb commands
        for bomb in self.bombs:
            self.actions.append(bomb.printCmd())
        # Adds upgrade commands
        for action in self.evalActions:
            if (action.form == "INC"):
                self.actions.append(action.printCmd())
        for inc in self.incs:
            self.actions.append(inc.printCmd())
        # Adds in debuggin message
        if (MSG_OUTPUT):
            self.actions.append("MSG {0}".format(MSG_CONTENT))
        # Outputs current turn's actions
        if (len(self.actions) < 1):
            print("WAIT")
        else:
            outputCommand = ""
            for cmd in self.actions:
                outputCommand += ";"
                outputCommand += cmd
            print(outputCommand[1:])

# Handle Inputs
NUM_FACTORIES = int(input())  # Number of factories
for i in range(NUM_FACTORIES): # Initialize Factories
    adjList.append([])
    adjMatrix.append([0 for x in range(NUM_FACTORIES)])
    floydWarMatrix.append([MAX_INT for x in range(NUM_FACTORIES)]) # Matrix to store shortest distances
    floydWarPath.append([[-1] for x in range(NUM_FACTORIES)]) # Matrix to store path
    floydWarNext.append([-1 for x in range(NUM_FACTORIES)]) # Optimized matrix storing only next target
    factoryInfo.append(Factory(i))
    simulFac.append(Factory(i))
link_count = int(input())  # Number of links between factories
for i in range(link_count): # Initialize adjList/adjMatrix
    factory_1, factory_2, distance = [int(j) for j in input().split()]
    adjList[factory_1].append((factory_2, distance))
    adjList[factory_2].append((factory_1, distance))
    adjMatrix[factory_1][factory_2] = distance
    adjMatrix[factory_2][factory_1] = distance
    # Stores links into floyd-warshall graph
    #TODO: do not store if distance > 5?
    floydWarMatrix[factory_1][factory_2] = distance
    floydWarMatrix[factory_2][factory_1] = distance
    floydWarPath[factory_1][factory_2] = [factory_2]
    floydWarPath[factory_2][factory_1] = [factory_1]
    floydWarNext[factory_1][factory_2] = factory_2
    floydWarNext[factory_2][factory_1] = factory_1
for i in range(NUM_FACTORIES): # Filter out paths > MAX_LINK_DISTANCE whilst preserving at least 1 link
    minLinkDistance = MAX_INT
    minLinkTarget = []
    numLinks = 0
    for j in range(len(floydWarMatrix[i])):
        if (floydWarMatrix[i][j] < minLinkDistance):
            minLinkDistance = floydWarMatrix[i][j]
            minLinkTarget.append(j)
        if (floydWarMatrix[i][j] > MAX_LINK_DISTANCE):
            floydWarMatrix[i][j] = MAX_INT
            floydWarPath[i][j] = [-1]
            floydWarNext[i][j] = -1
        else:
            numLinks += 1
    if (numLinks < 1): # Establish shortest link
        for minLink in minLinkTarget:
            floydWarMatrix[i][minLink] = minLinkDistance
            floydWarPath[i][minLink] = [minLink]
            floydWarNext[i][minLink] = minLink
    minLinkDistance = MAX_INT
    minLinkTarget = []
    numLinks = 0
    for j in range(len(adjList[i])):
        if (adjList[i][j][1] < minLinkDistance):
            minLinkDistance = adjList[i][j][1]
            minLinkTarget.append(adjList[i][j][0])
        if (adjList[i][j][1] > MAX_LINK_DISTANCE):
            adjList[i][j] = None
        else:
            numLinks += 1
    if (numLinks < 1):
        for minLink in minLinkTarget:
            adjList[i][minLink] = (minLink, minLinkDistance)
    adjList[i] = [adjList[i][idx] for idx in range(len(adjList[i])) if adjList[i][idx] is not None]
for i in range(NUM_FACTORIES): # Sort adjList by order of increasing distance
    adjList[i] = sorted(adjList[i], key=lambda x: x[1])

# Floyd-Warshall to compute All-Pair Shortest-Paths
for k in range(NUM_FACTORIES):
    for i in range(NUM_FACTORIES):
        for j in range(NUM_FACTORIES):
            if (i==j or k==j):
                continue
            intermediate = floydWarMatrix[i][k] + floydWarMatrix[k][j] + 1
            if (intermediate < floydWarMatrix[i][j]):
                newPath = [k]
                newPath.extend(floydWarPath[k][j])
                floydWarPath[i][j] = newPath
                floydWarNext[i][j] = floydWarNext[k][j]
                floydWarMatrix[i][j] = intermediate
            elif (intermediate == floydWarMatrix[i][j] and len(floydWarPath[i][j]) < len(floydWarPath[k][j])+1):
                newPath = [k]
                newPath.extend(floydWarPath[k][j])
                floydWarPath[i][j] = newPath
                floydWarNext[i][j] = floydWarNext[k][j]
                floydWarMatrix[i][j] = intermediate

# Game Loop
while True:
    del troopInfo[:] # Resets turn variables
    del bombInfo[:]
    del turnMoves[:]
    del turnBombs[:]
    del turnIncs[:]
    CYBORGS_OWN = 0
    CYBORGS_ENEMY = 0
    GAME_TURNS += 1
    myFactories = []
    simulIDCounter = -100
    for i in range(NUM_FACTORIES): # Ticks each factory
        factoryInfo[i].tick()
        simulFac[i].tick()

    # Reads game turn state
    entity_count = int(input())  # the number of entities (e.g. factories and troops)
    for i in range(entity_count):
        entity_id, entity_type, arg_1, arg_2, arg_3, arg_4, arg_5 = input().split()
        entity_id = int(entity_id)
        args = [int(arg_1), int(arg_2), int(arg_3), int(arg_4), int(arg_5)]
        if (entity_type == "FACTORY"):
            factoryInfo[entity_id].update(args)
            simulFac[entity_id].update(args)
            if (factoryInfo[entity_id].owner == 1):
                myFactories.append(entity_id)
                CYBORGS_OWN += factoryInfo[entity_id].troops
            elif (factoryInfo[entity_id].owner == -1):
                CYBORGS_ENEMY += factoryInfo[entity_id].troops
        elif (entity_type == "TROOP"):
            curPacket = TroopMsg(entity_id, args)
            factoryInfo[curPacket.target].pushIncomming(curPacket)
            troopInfo.append(curPacket)
            if (curPacket.owner == 1):
                CYBORGS_OWN += curPacket.size
            elif (curPacket.owner == -1):
                CYBORGS_ENEMY += curPacket.size
        elif (entity_type == "BOMB"):
            curPacket = BombMsg(entity_id, args)
            bombInfo.append(curPacket)

    # Searches for enemy's initial location
    if (INITIAL_FACTORY_ENEMY == -1 or INITIAL_FACTORY == -1):
        for i in range(len(factoryInfo)):
            curFac = factoryInfo[i]
            if (curFac.owner == 1 and INITIAL_FACTORY == -1):
                INITIAL_FACTORY = curFac.ID
            if (curFac.owner == -1 and INITIAL_FACTORY_ENEMY == -1):
                INITIAL_FACTORY_ENEMY = curFac.ID
    print("Map Distance: {0}".format(adjMatrix[INITIAL_FACTORY][INITIAL_FACTORY_ENEMY]), file=sys.stderr)
    if (adjMatrix[INITIAL_FACTORY][INITIAL_FACTORY_ENEMY] >= MAP_RUSH_SIZE):
        BOMB_SCORE_THRESHOLD = BOMB_SCORE_THRESHOLD_LARGE

    # Searches for frontline factory
    FRONTLINE_FACTORY = -1
    FRONTLINE_DISTANCE = MAX_INT
    for i in range(len(factoryInfo)):
        curFac = factoryInfo[i]
        if (curFac.owner == 1): # Determine a 'frontline' factory
            # Find shortest distance to enemy
            closestEnemyTup = curFac.closestEnemy()
            nearestFactory = closestEnemyTup[0]
            nearestDistance = closestEnemyTup[1]
            if (nearestFactory != -1 and nearestDistance < FRONTLINE_DISTANCE):
                FRONTLINE_DISTANCE = nearestDistance
                FRONTLINE_FACTORY = curFac.ID
                print("Determined FRONTLINE factory: {0}".format(FRONTLINE_FACTORY), file=sys.stderr)

    #TODO: Simulates Nearby enemies' attacks upon self
    currentSituation = [fac.resolve() for fac in factoryInfo]
    if (SIMULATE_ENEMY):
        enemies = [fac for fac in factoryInfo if fac.owner == -1]
        enemyActions = [] # Storing enemy movements
        for enemyFac in enemies:
            # Simulates enemy attacks
            enemyActions.extend(simulateEnemySmart(enemyFac, currentSituation))
        # Enemy has made some moves, add to simulation
        if (len(enemyActions) > 0):
            for action in enemyActions:
                if (action.isMove()):
                    args = (-1, action.origin, action.target, action.size, adjMatrix[action.origin][action.target] + 1)
                    enemyPacket = TroopMsg(simulIDCounter, args)
                    simulIDCounter += 1
                    factoryInfo[enemyPacket.target].pushIncomming(enemyPacket)
    enemySimulatedSituation = [fac.resolve() for fac in factoryInfo] if (SIMULATE_ENEMY) else currentSituation
    
    # Launch BOMBS!
    #TODO: Launch bombs in prune()?
    if (num_bombs > 0 and FRONTLINE_FACTORY != -1):
        print("Attempting BOMB | Scoring from Factory {0}".format(FRONTLINE_FACTORY), file=sys.stderr)
        # Scores all enemy factores for bombing! :D
        bombTargets = [(fac.ID, scoreBomb(fac.ID, (FRONTLINE_FACTORY if factoryInfo[fac.ID].closestFriendly()[0] == -1 else factoryInfo[fac.ID].closestFriendly()[0]), enemySimulatedSituation)) for fac in factoryInfo]
        bombTargets = sorted(bombTargets, key=lambda x: x[1], reverse=True)
        for targetTup in bombTargets:
            if (num_bombs < 1 or len(myFactories) < 1):
                break
            target = targetTup[0]
            score = targetTup[1]
            # Find the closest base to launch bomb from
            nearestFactory = factoryInfo[target].closestFriendly()[0]
            if (nearestFactory == -1):
                nearestFactory = FRONTLINE_FACTORY
            # Do not bomb a target that would be captured upon ttt
            if (not should_bomb(target, nearestFactory, enemySimulatedSituation)):
                continue
            print("Factory {0} Score: {1}".format(target, score), file=sys.stderr)
            launch = True
            # Only bomb targets above threshold score
            if (score < BOMB_SCORE_THRESHOLD):
                continue
            # Do not bomb same target twice
            for bomb in bombInfo:
                if (bomb.owner == 1 and bomb.target == target):
                    launch = False
                    break
            if (not launch):
                continue
            turnMoves.append(BOMB([nearestFactory, target]))
            num_bombs -= 1
            #EXPERIMENTAL: Add own bombs into simulation
            args = (1, nearestFactory, target, adjMatrix[nearestFactory][target]+1)
            bombInfo.append(BombMsg(simulIDCounter, args))
            simulIDCounter += 1

    # Constructs simulated scenario to feed into strategizer
    for move in turnMoves:
        print(move.printCmd(), file=sys.stderr)
        if (move.isMove()):
            args = [1, move.origin, move.target, move.size, adjMatrix[move.origin][move.target]+1]
            curPacket = TroopMsg(simulIDCounter, args)
            simulIDCounter += 1
            simulFac[move.target].pushIncomming(curPacket)
        else:
            if (move.form == "BOMB"):
                turnBombs.append(move)
            elif (move.form == "INC"):
                turnIncs.append(move)

    # Feed Strategizer
    strategize = Strategizer(enemySimulatedSituation, simulFac, turnBombs, turnIncs, simulIDCounter)

    # Strategize!
    strategize.execute() # Executes strategy for turn
    strategize.redirect() # Redirects troops and paths them via floyd-warshall
    strategize.prune() # Prunes and organizes co-ordinated attacks
    strategize.whack() # All out constant barrage of attacks

    # Fun little MSG
    if (MSG_OUTPUT):
        random.seed()
        if (MSG_RANDIDX == -1):
            MSG_RANDIDX = random.randint(0,len(HITCHHIKER_GALAXY_QUOTES)-1)
        elif (MSG_START >= MSG_END):
            MSG_RANDIDX = random.randint(0,len(HITCHHIKER_GALAXY_QUOTES)-1)
            MSG_START = 0
            MSG_DELAY = MSG_MAXLEN
            MSG_END = MSG_MAXLEN
        delay = ">"
        if (MSG_DELAY <= 0):
            MSG_START += MSG_RATE
            if (MSG_END < len(HITCHHIKER_GALAXY_QUOTES[MSG_RANDIDX])):
                MSG_END += min(len(HITCHHIKER_GALAXY_QUOTES[MSG_RANDIDX])-MSG_END, MSG_RATE)
        if (MSG_DELAY > 0):
            for i in range(MSG_DELAY):
                delay += " "
            MSG_DELAY -= min(MSG_RATE, MSG_DELAY)
        MSG_CONTENT = delay+HITCHHIKER_GALAXY_QUOTES[MSG_RANDIDX][min(len(HITCHHIKER_GALAXY_QUOTES[MSG_RANDIDX]), MSG_START):min(len(HITCHHIKER_GALAXY_QUOTES[MSG_RANDIDX]), MSG_END)]

    # Output final strategy for the turn
    strategize.printCmd()