# src/__init__.py
# Package initialiser for the Riverside Books FAQ chatbot.
# Re-exports the public API so consumers can simply do:
#   from src import FAQ, MatchResult, find_best_match

from .types import FAQ, MatchResult      # Data structures used across the package
from .matcher import find_best_match     # Core semantic-search routine

__version__ = "1.0.0"
__author__ = "Ryan"