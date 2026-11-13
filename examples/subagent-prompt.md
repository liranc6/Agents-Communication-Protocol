# Subagent prompt (T2: another agent reads it)

The peer starts cold, so state goal and why, constraints, paths, done-criteria and known facts.

Verbose:

    Hi! Could you please take a look at the repository and try to figure out why the tests in the runner module
    are failing sometimes? When you are done, I would really appreciate a full explanation of what you found.

COP style:

    Goal: find why tests/test_runner.py flaky (~1 in 5 runs), so we can fix retry logic.
    Constraints: read-only, no installs. Known: failure only when run in parallel (obs).
    Paths: runner.py, tests/test_runner.py. Done: root cause + evidence path:line.
    Reply <=10 lines.

The hook appends the PEER block automatically to prompts without a line starting `COP:`. To opt a subagent out (for example one that must return JSON), include `cop:off` in its prompt or list its type in `COP_SKIP_SUBAGENTS`.
