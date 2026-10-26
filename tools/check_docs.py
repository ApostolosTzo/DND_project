"""Fail when a generated documentation file or HTML shell is stale.

    py tools/check_docs.py     # exit 0 = fresh, exit 1 = regenerate

Checks two things:

1. AGENTS.md: regenerates it in memory and diffs against the file on disk.
   AGENTS.md drifts silently because it is easy to edit by hand or to forget
   after changing the generator - this makes the forgetfulness loud, the same
   way parity_check.py polices js/game_data.js.
2. Both HTML shells: runs gen_html_shells.py --check, which fails when
   index.html or templates/index.html no longer match tools/shells/.

GAME_GUIDE.md has its own checker (tools/audit_guide.py) and game data its own
(parity_check.py); this script stays with the docs those do not cover.
"""
import difflib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gen_agents_md  # noqa: E402
import gen_html_shells  # noqa: E402


def check():
    path = gen_agents_md.AGENTS_OUT
    rel = os.path.relpath(path, gen_agents_md.ROOT).replace("\\", "/")
    on_disk = io.open(path, encoding="utf-8").read() if os.path.exists(path) else None
    fresh = gen_agents_md.build()

    if on_disk == fresh:
        print("%s is up to date" % rel)
        return 0

    if on_disk is None:
        print("FAIL: %s is missing - run: py tools/gen_agents_md.py" % rel)
        return 1

    print("FAIL: %s is stale - run: py tools/gen_agents_md.py" % rel)
    diff = list(difflib.unified_diff(
        on_disk.splitlines(), fresh.splitlines(),
        fromfile="on disk", tofile="regenerated", lineterm="", n=1))
    for line in diff[:40]:
        print(line)
    if len(diff) > 40:
        print("... (%d more diff lines)" % (len(diff) - 40))
    return 1


def check_shells():
    """Delegate to gen_html_shells.py --check; exit 1 when a shell is stale."""
    return gen_html_shells.main(["--check"])


if __name__ == "__main__":
    rc = check()
    rc = check_shells() or rc
    sys.exit(rc)
