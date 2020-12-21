"""Classes to export data into different formats."""
from enum import Enum


class ExportMode(Enum):
    Raw = 0
    Markdown = 1
