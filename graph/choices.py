"""Abbreviations used to write data to the graph database (or to retrieve it)."""

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019-2020, Martin Woelke'

LABEL_STATUS = {
    'A': 'active',
    'C': 'closed',
    'U': 'unknown'
}

BAND_STATUS = {
    'A': 'Active',
    'H': 'On hold',
    'C': 'Changed name',
    'S': 'Split-up',
    'U': 'Unknown',
    'D': 'Disputed'
}

MEMBER_STATUS = {
    'C': 'Current',
    'L': 'Last known',
    'P': 'Past',
    'CL': 'Current (Live)',
    'PL': 'Past (Live)',
    'LL': 'Last known (Live)'
}

RELEASE_TYPES = {
    'D': 'Demo',
    'F': 'Full-length',
    'S': 'Single',
    'T': 'Split',
    'L': 'Live album',
    'C': 'Compilation',
    'E': 'EP',
    'V': 'Video',
    'B': 'Boxed set',
    'P': 'Split video',
    'O': 'Collaboration'
}

GENDER = {
    'M': 'Male',
    'F': 'Female',
    'U': 'Unknown',
    'O': 'Other',
    'N': 'Non-binary'
}
