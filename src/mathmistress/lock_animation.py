# Lock Animation compatibility wrapper
# ------------------------------------
# Historically, the project had both ``lock_animation.py`` and
# ``lock_animation_improved.py``.  The latter is the maintained,
# feature-rich implementation.  To avoid updating every legacy import we
# keep this thin wrapper that re-exports all public symbols from the
# improved module.

from .lock_animation_improved import *  # type: ignore F401 F403

__all__ = [
    name for name in globals().keys() if not name.startswith("_")
]
    
