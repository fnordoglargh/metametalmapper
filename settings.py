NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "CHANGE_ME"
NEO4J_IP_ADDRESS = "localhost"

# 8 might be a bit high (leaves some forbidden messages on getting the JSON data or the bands).
CRAWLER_THREAD_COUNT = 8

# Minimum values for releases to appear in the reports.
RELEASE_REVIEW_COUNT_MIN = 3
RELEASE_AVERAGE_MIN = 80
RELEASE_TYPES_REVIEW = ["F", "E", "D"]

# Maximum number for all reports using a TOP X
TOP = 5

# Filter options for graph exports.
IS_LIVE_MEMBER_IN_BAND = True
FILTER_UNCONNECTED = False
