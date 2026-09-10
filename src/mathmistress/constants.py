"""Module-level constants for the mathmistress package.

Hoisted from repeated string literals found in ``gameplay_screen.py``
during the 2026-09-10 surgical-implementation pass.  Keeping them here
makes the strings single-source-of-trivial and trivially localisable.
"""

# Default help text shown by ``HelpDisplay`` before the player clicks the
# HELP button.  Previously hard-coded (3x) inside gameplay_screen.py.
DEFAULT_HELP_TEXT = "Click HELP button for algebra assistance"

# Equation-pattern literals hoisted from gameplay_screen.py
# (2026-09-10 surgical-implementation pass — repeated 3x each).
EQUATION_PATTERN_A = "a + x - c = b"
EQUATION_PATTERN_B = "x + a - c = b"
EQUATION_PATTERN_B_PREFIX = "x +"
