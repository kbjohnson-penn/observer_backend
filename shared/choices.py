# Shared choices for all apps

SEX_CATEGORIES = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
    ("U", "Unknown"),
]

RACIAL_CATEGORIES = [
    ("AI", "American Indian or Alaska Native"),
    ("AS", "Asian"),
    ("BA", "Black or African American"),
    ("NH", "Native Hawaiian or Other Pacific Islander"),
    ("WH", "White"),
    ("MR", "Multiple Race"),
    ("OT", "Other"),
    ("UN", "Unknown"),
]

ETHNIC_CATEGORIES = [
    ("H", "Hispanic or Latino"),
    ("NH", "Not Hispanic or Latino"),
    ("U", "Unknown"),
]

BOOLEAN_CHOICES = [
    (True, "Yes"),
    (False, "No"),
]

ENCOUNTER_TYPE_CHOICES = [
    ("clinic", "Clinic"),
    ("simcenter", "Sim Center"),
    ("pennpersonalizedcare", "Penn Personalized Care"),
]

FILE_TYPE_CHOICES = [
    ("video", "Video"),
    ("audio", "Audio"),
    ("image", "Image"),
    ("document", "Document"),
    ("transcript", "Transcript"),
    ("room_view", "Room View"),
    ("provider_view", "Provider View"),
    ("patient_view", "Patient View"),
    ("patient_survey", "Patient Survey"),
    ("provider_survey", "Provider Survey"),
    ("provider_annotation", "Provider Annotation"),
    ("patient_annotation", "Patient Annotation"),
]

FILE_TYPE_CHOICES_DICT = dict(FILE_TYPE_CHOICES)
