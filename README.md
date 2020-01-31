# Meme-Voting: various voting methods in Python
Bart Massey

This project deals with a "meme election". Please see the
first part of this document for background and description,
and the second part for technical information.

## About This Project

I got interested in a [Reddit](http://reddit.com) article
about voting today
(2020-01-30). [This article](https://www.reddit.com/r/dankmemes/comments/ew731f/did_pepe_really_win_a_look_at_the_math_behind_the/)
discusses a contest held in the subreddit
[/r/dankmemes](https://www.reddit.com/r/dankmemes) to
determine which of the memes "Pepe", "Spongebob", "Tom \&
Jerry" and "Rick Roll" is the "greatest meme".

To be honest, it wasn't the contest itself that interested
me. It was some facts about the contest that made me take
notice:

* The contest organizers used ranked-choice voting and made
  all the ballots available. Useful data of this type is
  hard to find.

* The contest organizers tried a number of different
  ranked-choice voting methods and reported the results.

* There was some, er, controversy about the
  results. Originally
  [Instant-Runoff Voting](https://en.wikipedia.org/wiki/Instant-runoff_voting)
  was used and selected Spongebob as the winner. However,
  the organizers felt that they had selected their voting
  protocol poorly, and subsequently tried
  [Ranked-Pairs Voting](https://en.wikipedia.org/wiki/Ranked_pairs)
  and
  [Borda Count](https://en.wikipedia.org/wiki/Borda_count),
  both of which reportedly produced Pepe as the winner (but
  see below). Thus, Pepe was declared the winner *post
  facto.*

I took all of this as an opportunity to re-implement the
chosen vote tabulation methods in Python to replicate and
explore the original election results. I have always taken
the position that fancy voting protocols have some issues
that are not adequately addressed:

* These methods, especially the Condorcet methods, tend to
  be deceptively difficult to understand and implement. I
  have seen formal methods studies that attempt to prove an
  implementation of related methods correct; it is a
  tremendous amount of effort. The methods are also hard to
  test for lack of an effective oracle: small tabulations
  are hard to do by hand and may not reveal subtle flaws.
  Sampling is a common technique for validating election
  results, but is difficult to do with these systems.

* Because these methods are complicated, the inability of
  people of average skill and intelligence to hand-check and
  understand the results of an election can lead to a lack
  of trust in the results even if they are correct.

My implementations were primarily driven by the descriptions
of the voting protocols on Wikipedia (linked above). This
was modulated by the informal descriptions given by the
election organizers in the Reddit post (also linked above).
My goals were to:

* When possible, replicated the reported election results
  under various systems.

* Produce implementations that followed reported standard
  practice for these systems.

### First Past The Post

This is the simplest system to implement, and the most hated
by voting-system people. My implementation is about 15 lines
of Python ("LOC", including blank lines and comments). Pepe
is the clear winner.

### Instant Runoff Voting

My implementation of Instant Runoff Voting (IRV) comprises
about 65 LOC. I follow the standard iterative procedure for
IRV, breaking ties at each stage by dropping all tied
least-first-ranked candidates.

I was able to reproduce exactly the reported IRV results
with minimal difficulty. Spongebob is the winner.

### Borda Count

Borda Count is more a family of voting procedures than
a specific one. The Borda Count methods share in common the idea that
each rank should be assigned a weight and that these weights
should be combined by summation to produce a final
candidate. Indeed, the one-person one-vote
First-Past-The-Post (FPTP) method is a special case of Borda
Count where the first-ranked candidate is given a weight of
one and other candidates zero.

I initially implemented four different Borda Count methods:

* Standard Borda Count assigns a weight of *n* to the
  first-ranked of *n* candidates, a rank of *n-1* to the
  second-ranked candidate, and so forth, with the
  last-ranked candidate receive a weight of 1.

* Zero-Based Borda Count gives a one-smaller weight to
  each candidate, assigning weight *n-1* to the first-ranked
  candidate and so forth.

* Dowdall's Method is a commonly-used Borda Count variant
  that assigns the *r*-th ranked candidate a weight
  *1/r*. This is intended to minimize the impact of
  low-ranked candidates.

* To achieve a more pronounced Dowdall effect, I implemented
  a Power Series Borda Count variant in which the *r*-th
  ranked candidate gets weight *1/2^n*.

This was definitely the simplest method: the total source
for all variants was about 25 LOC of low complexity.

Interestingly, the Standard and Zero-Based methods produced
Spongebob as the election winner, while Dowdall and Power
Series produced Pepe as the winner. The election organizers
reported using Dowdall, but my results did not quite match
theirs (although the outcome was the same). Perusing the
comments on the Reddit article revealed that Excel was
unintentionally rounding fractions to two places: in this
four-candidate election the only weight affected was *1/3*,
which was reduced by rounding to *0.33*. I implemented this
fifth method and was able to reproduce the election results
exactly.

### Ranked-Pairs Voting

The last method attempted by the contest organizers was
Ranked-Pairs Voting (RPV). RPV is a fairly complex method
that achieves the Condorcet criterion by calculating the
winner of all pairwise tournaments and constructing a
directed acyclic graph (DAG) in decreasing pair-difference
order: this will normally produce a single dominant (source)
node in the DAG as the winner of the election.

My implementation of RPV follows the Wikipedia description
closely, comprising about 100 LOC including some moderately
tricky algorithms: for example, an iterative
reflexive-transitive-closure calculation.

It is not clear from the contest organizers' description
that they closely followed the standard RPV algorithm. In
particular, the order in which edges were added to the DAG
was not described.

I was not able to reproduce the contest organizers' result
using my code. I wrote a couple of extra utilities: one to
check that none of the ballots were spoiled (they were not),
and another to calculate the specific ranking of a
particular pair using very simple code. While the contest
organizers found that Pepe was the winner, I found (and was
able to check) that Spongebob received a slightly higher
relative ranking than Pepe and dominated the other
candidates.

I was concerned that I might have a bug here, but I was at a
loss as to how to further verify my code and results. Thanks
to Reddit user `/u/reonhato99` who pointed out that the
margin of 329 I found for Spongebob over Pepe is consistent
with the contest organizers' report of a 329-vote margin of
Spongebob over Pepe in IRV. This greatly increased my
confidence in this result.

### Conclusions

This study has validated my concerns about using advanced
voting methods in elections with real-world consequences. I
have identified at least one and possibly two bugs in the
contest organizers' implementations of voting methods. I
have found that RPV in particular is difficult to implement
correctly and to understand. I definitely trust the meme
voting results much less than I did before I started, and
would extend that lack of trust even more to unaudited
voting code with greater systems complexity in more fragile
languages.

## About This Software

There are several files here:

* `meme-election-ballots.csv` is a CSV version of the
  ballots provided by the meme voting organizers.

* `test-ballots.csv` is toy ballots I used when working on
  the software.

* `checkballots.py` does a simple spoilage check on the
  ballots.

* `checkrp.py` accepts a pair of candidate names as
  arguments and produces information about their pairwise
  ranking.

* `votings.py` is the actual voting system implementation.

All of the Python code accepts an extra optional argument to
use a CSV file other than the meme election ballots.

### Acknowledgments

I want to acknowledge the absolutely fantastic generosity of
the meme voting team in providing a detailed description of
their process and results and giving access to their
ballots. This work would not have been possible without
that.

### License

This work is available under an "MIT License". Please see
the file `LICENSE` in this distribution for license terms.
