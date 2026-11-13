# Scratch notes (T1: only agents read it)

Verbose:

    I looked at the config loader and it seems that it reads the file twice, which I believe is the cause of the slowdown.

COP style:

    config loader reads file 2x (obs loader.py:40,88) -> slowdown (inf). next: cache first read.

Approximate size: 118 characters verbose vs 92 characters COP (character count, not tokens; single sample).
