# Shared constants for all apps

# NULL_MARKER is used to represent NULL database values in API responses.
# Since JSON arrays cannot contain actual null values in a meaningful way for filtering,
# we use this special marker string. The frontend displays this as "Not Specified".
# This allows users to filter for records where demographic values are not recorded.
NULL_MARKER = "__NULL__"

# SimCenter Patient ID range
SIMCENTER_PATIENT_ID_LOWER_LIMIT = 1000000
SIMCENTER_PATIENT_ID_UPPER_LIMIT = 9999999

# SimCenter Provider ID range
SIMCENTER_PROVIDER_ID_LOWER_LIMIT = 1000000
SIMCENTER_PROVIDER_ID_UPPER_LIMIT = 9999999
