# Agent-only doc (T3)

Only agents read and write this kind of file (insights log, runbook, state file). Dense COP with a local legend.

Verbose:

    ## Known issues
    The deployment script sometimes fails when the staging environment has not finished warming up. When this
    happens, the best approach is to wait for about two minutes and then try the deployment again.

COP style:

    Legend: DS=deploy script, STG=staging
    - DS fail when STG not warm (obs, 3 of 5 runs). Fix: wait ~2 min -> rerun.

Rules: file-local legend at top, not the project glossary. Never abbreviate inside quoted or literal content.
If a human reads or maintains the doc, write it as T0 prose.
