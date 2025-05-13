SEX_CATEGORIES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('UN', 'Unknown or Not Reported')
]

RACIAL_CATEGORIES = [
    ('AI', 'American Indian or Alaska Native'),
    ('A', 'Asian'),
    ('NHPI', 'Native Hawaiian or Other Pacific Islander'),
    ('B', 'Black or African American'),
    ('W', 'White'),
    ('M', 'More than One Race'),
    ('UN', 'Unknown or Not Reported'),
]

ETHNIC_CATEGORIES = [
    ('H', 'Hispanic or Latino'),
    ('NH', 'Not Hispanic or Latino'),
    ('UN', 'Unknown or Not Reported Ethnicity'),
]

BOOLEAN_CHOICES = [
    (True, 'Yes'),
    (False, 'No'),
]

ENCOUNTER_TYPE_CHOICES = [
    ('clinic', 'Clinic'),
    ('simcenter', 'Sim Center'),
    ('pennpersonalizedcare', 'Penn Personalized Care'),
]

FILE_TYPE_CHOICES = [
    ('room_view', 'Room View'),
    ('provider_view', 'Provider View'),
    ('patient_view', 'Patient View'),
    ('audio', 'Audio'),
    ('transcript', 'Transcript'),
    ('patient_survey', 'Patient Survey'),
    ('provider_survey', 'Provider Survey'),
    ('patient_annotation', 'Patient Annotation'),
    ('provider_annotation', 'Provider Annotation'),
    ('rias_transcript', 'RIAS Transcript'),
    ('rias_codes', 'RIAS Codes'),
    ('other', 'Other'),
]
FILE_TYPE_CHOICES_DICT = dict(FILE_TYPE_CHOICES)
