import csv
import sys

ballots = "meme-election-ballots.csv"
if len(sys.argv) > 1:
    ballots = sys.argv[1]

ballots = open(ballots, 'r')
ballots = csv.reader(ballots)
header = next(ballots)
ballots = [[int(rank) - 1 for rank in ballot] for ballot in ballots]
ncandidates = len(header)

borda_systems = [
    ("BC", lambda rank: ncandidates - rank),
    ("0-BC", lambda rank: ncandidates - rank - 1),
    ("Dowdall", lambda rank: 1 / (rank + 1)),
    ("Dowdall-AR", lambda rank: round(1 / (rank + 1), 2)),
    ("Power", lambda rank: 1 / 2**rank),
]

class Borda(object):
    def __init__(self):
        votes = [[0] * ncandidates for _ in range(len(borda_systems))]
        for ballot in ballots:
            for candidate, rank in enumerate(ballot):
                for index, system in enumerate(borda_systems):
                    votes[index][candidate] += system[1](rank)
        self.votes = votes

    def report(self):
        for index, system in enumerate(borda_systems):
            print(system[0])
            for candidate, name in enumerate(header):
                print("   ", name, self.votes[index][candidate])
            print()

class IRV(object):
    def __init__(self):
        self.log = []
        headr = list(header)
        ballts = [list(ballot) for ballot in ballots]
        nballts = len(ballts)
        round = 0
        while len(headr) > 0:
            ncandidates = len(headr)
            round += 1
            self.log.append("Round {}".format(round))
            firsts = [0]*ncandidates
            for ballot in ballts:
                first = min(range(ncandidates), key=lambda i: ballot[i])
                firsts[first] += 1
            for candidate, votes in enumerate(firsts):
                self.log.append("    {}: {}".format(
                    headr[candidate],
                    firsts[candidate],
                ))
            leader = max(range(ncandidates), key=lambda i: firsts[i])
            leader_votes = firsts[leader]
            if leader_votes > 0.5 * nballts:
                self.log.append("    Winner {}".format(headr[leader]))
                return
            trail_votes = min(*firsts)
            trailers = {candidate for candidate in range(ncandidates)
                        if firsts[candidate] == trail_votes}
            for trailer in trailers:
                self.log.append("    Eliminate {}".format(headr[trailer]))
                for ballot in ballts:
                    trail_rank = ballot[trailer]
                    for candidate in range(len(ballot)):
                        if ballot[candidate] > trail_rank:
                            ballot[candidate] -= 1
                    del ballot[trailer]
                del headr[trailer]
        round += 1
        self.log.append("Round {}".round)
        self.log.append("    Tie")

    def report(self):
        print("IRV")
        for line in self.log:
            print("    {}".format(line))
        print()

IRV().report()
Borda().report()
