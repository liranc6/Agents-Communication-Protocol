# Chat reply (T0: a human reads it)

Chat stays normal prose. COP codes and symbols do not appear here, even if the work behind it was done in COP.

Wrong (COP leaked into a human-facing reply):

    DONE|runner.py:120 retry fix|TP 14/14|obs|next PR

Right:

    I fixed the retry bug in runner.py (line 120). All 14 tests pass. Next I can open the PR if you want.

Exception: if the user explicitly asks for terse or radio-style replies, chat may go telegraphic. Peer shorthand is still rewritten for the user.
