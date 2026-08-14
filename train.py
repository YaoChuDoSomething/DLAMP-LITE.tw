"""Repository-root wrapper delegating to the ``dlamp-train`` entry point.

Usage::

    python train.py
    python train.py --config-name train_diffusion
"""

import sys

import dlamp.train

if __name__ == "__main__":
    sys.exit(dlamp.train.main())