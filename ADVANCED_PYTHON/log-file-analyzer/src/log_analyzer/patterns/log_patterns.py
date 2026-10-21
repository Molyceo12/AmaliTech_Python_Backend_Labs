"""Compiled regex patterns for Apache/Nginx access logs.

Example lines (one log line each)::

    Common:
    192.168.1.10 - - [21/Oct/2026:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326

    Combined (common + referrer + user agent):
    192.168.1.10 - - [21/Oct/2026:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326
    "https://example.com/" "Mozilla/5.0"

Every field is a named group, so a match gives a readable ``groupdict()``.
``re.VERBOSE`` ignores spaces in the pattern, so literal spaces are written
as ``[ ]``.
"""

import re

# Fields shared by both formats, ending with the response size.
_COMMON_FIELDS = r"""
    (?P<ip>\d{1,3}(?:\.\d{1,3}){3})       # client IPv4, e.g. 192.168.1.10
    [ ]\S+[ ]\S+                          # identity and user, usually "- -"
    [ ]\[(?P<timestamp>[^\]]+)\]          # [21/Oct/2026:13:55:36 +0000]
    [ ]"(?P<method>[A-Z]+)                # "GET
    [ ](?P<url>\S+)                       # /index.html?page=2
    [ ](?P<protocol>HTTP/\d(?:\.\d)?)"    # HTTP/1.1"
    [ ](?P<status>\d{3})                  # 200
    [ ](?P<size>\d+|-)                    # 2326, or - when no body was sent
"""

# Extra fields of the combined format.
_COMBINED_EXTRA = r"""
    [ ]"(?P<referrer>[^"]*)"              # "https://example.com/" (may be "-")
    [ ]"(?P<user_agent>[^"]*)"            # "Mozilla/5.0 ..."
"""

COMMON_LOG = re.compile(_COMMON_FIELDS + r"$", re.VERBOSE)
COMBINED_LOG = re.compile(_COMMON_FIELDS + _COMBINED_EXTRA + r"$", re.VERBOSE)

# Most detailed format first, so combined lines keep their extra fields.
LOG_FORMATS: tuple[re.Pattern[str], ...] = (COMBINED_LOG, COMMON_LOG)

# Layout of the timestamp group, for datetime.strptime.
TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"
