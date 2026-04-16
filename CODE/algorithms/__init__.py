"""
algorithms/__init__.py
Export public API của package algorithms.

Dùng:
    from algorithms import FIFO, LRU, OPT, LRUClock, AlgoRegistry
"""

from algorithms.fifo      import FIFO
from algorithms.lru       import LRU, LRUClock
from algorithms.opt       import OPT
from algorithms.base      import PageReplacementAlgorithm
from algorithms.registry  import AlgoRegistry

__all__ = [
    "FIFO",
    "LRU",
    "LRUClock",
    "OPT",
    "PageReplacementAlgorithm",
    "AlgoRegistry",
]
