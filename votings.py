import csv
import functools
import sys

ballots = "meme-election-ballots.csv"
if len(sys.argv) > 1:
    ballots = sys.argv[1]

ballots = open(ballots, 'r')
ballots = csv.reader(ballots)
header = next(ballots)
ballots = [[int(rank) - 1 for rank in ballot] for ballot in ballots]
ncandidates = len(header)

class IRV(object):
    """
    Instant-Runoff Voting. Ties broken by dropping all trailing
    candidates simultaneously. Can tie when all candidates
    are dropped in a round.
    """
    def __init__(self):
        self.log = []

        # Copy the header and all the ballots so they can be
        # mutilated locally later.
        # XXX The misspellings are deliberate, because
        # Python can't deal with making a local variable
        # with the same name as a global (as far as I know).
        headr = list(header)
        ballts = [list(ballot) for ballot in ballots]
        nballts = len(ballts)
        round = 0
        while len(headr) > 0:
            ncandidates = len(headr)
            round += 1
            self.log.append("Round {}".format(round))
            firsts = [0]*ncandidates
            # Count and log the number of firsts for each candidate.
            for ballot in ballts:
                first = min(range(ncandidates), key=lambda i: ballot[i])
                firsts[first] += 1
            for candidate, votes in enumerate(firsts):
                self.log.append("    {}: {}".format(
                    headr[candidate],
                    firsts[candidate],
                ))

            # Check for a majority winner.
            leader = max(range(ncandidates), key=lambda i: firsts[i])
            leader_votes = firsts[leader]
            if leader_votes > 0.5 * nballts:
                self.log.append("    Winner {}".format(headr[leader]))
                return

            # Eliminate "trailing" candidates (those with
            # least first-rank).
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

        # All remaining candidates were eliminated in the
        # last round. This means that they were tied.
        round += 1
        self.log.append("    Tie")

    def report(self):
        print("IRV")
        for line in self.log:
            print("    {}".format(line))
        print()

class RPV(object):
    """
    Ranked-Pairs Voting. Single-round with no tiebreaking
    mechanism for tied leading cycles or tied pairs.
    """
    def __init__(self):
        # Tally.
        ncandidates = len(header)
        scores = dict()
        for c1 in range(ncandidates):
            for c2 in range(c1 + 1, ncandidates):
                votes1 = 0
                votes2 = 0
                for ballot in ballots:
                    if ballot[c1] < ballot[c2]:
                        votes1 += 1
                    else:
                        votes2 += 1
                if votes1 >= votes2:
                    w, wv, l, lv = c1, votes1, c2, votes2
                else:
                    w, wv, l, lv = c2, votes2, c1, votes1
                scores[(w, l)] = wv - lv
        self.scores = scores
        
        # Sort.

        # Objective function for sorting. XXX Note that this
        # is set up to sort decreasing.
        def order(p1, p2):
            # Normalize the pair for comparison.
            def find(c1, c2):
                if (c1, c2) in scores:
                    return scores[(c1, c2)]
                return -scores[(c2, c1)]

            # Primary criterion: better pair.
            diff = scores[p2] - scores[p1]
            if diff != 0:
                return diff

            # Secondary criterion: better minority.
            w1, l1 = p1
            w2, l2 = p2
            opw1 = find(w1, l2)
            opw2 = find(w2, l1)
            return scores[opw2] - scores[opw1]

        pairs = list(scores.keys())
        pairs.sort(key=functools.cmp_to_key(order))
        self.pairs = pairs

        # Lock.

        # Represent the graph as an edge list.  This will be
        # less efficient than a multimap, but easier to work
        # with.
        dag = []

        # Reflexive Transitive Closure.
        def rtclose(candidate):
            closure = set()
            opens = {candidate}
            while len(opens) > 0:
                to_close = list(opens)[0]
                for parent, child in dag:
                    if parent != to_close:
                        continue
                    if child not in closure:
                        opens.add(child)
                opens.remove(to_close)
                closure.add(to_close)
            return closure

        for w, l in pairs:
            if w not in rtclose(l):
                dag.append((w, l))
        
        # Winners.
        winners = set(range(ncandidates))
        for _, l in dag:
            if l in winners:
                winners.remove(l)
        self.winners = winners

    def report(self):
        print("RPV")
        for w, l in self.pairs:
            print("    {} > {}: {}".format(
                header[w],
                header[l],
                self.scores[(w, l)],
            ))
        nwinners = len(self.winners)
        if nwinners == 0:
            print("    No winner.")
        elif nwinners == 1:
            print("    Winner {}".format(header[list(self.winners)[0]]))
        else:
            for winner in self.winners:
                print("    Tied {}".format(header[winner]))

borda_systems = [
    ("BC", lambda rank: ncandidates - rank),
    ("0-BC", lambda rank: ncandidates - rank - 1),
    ("Dowdall", lambda rank: 1 / (rank + 1)),
    ("Dowdall-AR", lambda rank: round(1 / (rank + 1), 2)),
    ("Power", lambda rank: 1 / 2**rank),
]

class Borda(object):
    "Various Borda Count systems. No tie-breaking included."
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

IRV().report()
Borda().report()
RPV().report()
