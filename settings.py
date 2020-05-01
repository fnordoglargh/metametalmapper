"""Settings definitions for Meta Metal Mapper.
"""

__author__ = 'Martin Woelke'
__license__ = 'Licensed under the Non-Profit Open Software License version 3.0'
__copyright__ = 'Copyright 2019, Martin Woelke'

NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "CHANGE_ME"
NEO4J_IP_ADDRESS = "localhost"

# 8 might be a bit high (leaves some forbidden messages on getting the JSON data or the bands).
CRAWLER_THREAD_COUNT = 8

# Minimum values for releases to appear in the reports.
RELEASE_REVIEW_COUNT_MIN = 3
RELEASE_AVERAGE_MIN = 80
# See RELEASE_TYPES in graph/choices.py for possible values. Default: Full-length, EP and Demo.
RELEASE_TYPES_REVIEW = ["F", "E", "D"]

# Maximum number for all reports using a TOP X
TOP = 5

# Filter options for graph exports.
IS_LIVE_MEMBER_IN_BAND = True
FILTER_UNCONNECTED = False

# Useful flag to find inconsistencies in M-A data. Don't set to True unless you know what you're doing. Setting to True
# will result in graphs with invalid connections. This _might_ actually be useful while merging graphs with Gephi.
FIND_MA_INCONSISTENCIES = False
