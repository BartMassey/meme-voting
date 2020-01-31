import csv
import sys

ballots = "meme-election-ballots.csv"
if len(sys.argv) > 3:
    ballots = sys.argv[3]

ballots = open(ballots, 'r')
ballots = csv.reader(ballots)
header = next(ballots)
ballots = [[int(rank) - 1 for rank in ballot] for ballot in ballots]
ncandidates = len(header)

header_index = { name : candidate for candidate, name in enumerate(header) }
c1 = header_index[sys.argv[1]]
c2 = header_index[sys.argv[2]]

v1 = 0
v2 = 0
for ballot in ballots:
    if ballot[c1] < ballot[c2]:
        v1 += 1
    else:
        v2 += 1

print(header[c1], v1)
print(header[c2], v2)
print(v1 - v2)
