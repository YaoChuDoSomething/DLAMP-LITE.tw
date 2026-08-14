"""Repository-root wrapper delegating to the ``dlamp-predict`` entry point.

Usage::

    python predict.py
"""

import sys

from dlamp.analysis.prediction import main

if __name__ == "__main__":
    sys.exit(main())