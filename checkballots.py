# Check ballots for spoilage.
# Bart Massey

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

good = set(range(ncandidates))
for line, ballot in enumerate(ballots):
    if set(ballot) != good:
        print("line {}: spoiled ballot: {}", line + 1, ballot)
