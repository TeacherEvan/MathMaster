from importlib import import_module
import sys

# ---------------------------------------------------------------------------
# Compatibility shim ---------------------------------------------------------
# ---------------------------------------------------------------------------
# The project was re-structured into the ``mathmistress`` package.  To avoid
# touching every single ``import <old_module>`` line in legacy code and tests
# we expose the most commonly used top-level modules under their historical
# names.  This way, statements such as ``from lock_animation_improved import
# LockAnimation`` continue to work after the re-organisation.
# ---------------------------------------------------------------------------

_legacy_modules = [
    # Core gameplay windows / utilities
    "gameplay_screen",
    "welcome_screen",
    "level_select_screen",
    "help_display",
    "algebra_helper",
    # Visuals & animations
    "lock_animation",
    "lock_animation_improved",
    "window_b_solution_symbols",
    "WormsWindow_B",
]

for _name in _legacy_modules:
    try:
        # Import the module as a sub-module of the current package
        _module = import_module(f".{_name}", package=__name__)
        # Expose as attribute of this package (e.g. mathmistress.lock_animation)
        globals()[_name] = _module
        # Inject into sys.modules under its original top-level name so that
        # ``import lock_animation`` still resolves to the relocated module.
        sys.modules[_name] = _module
    except ModuleNotFoundError:
        # Ignore missing modules – some may be optional or removed later.
        pass