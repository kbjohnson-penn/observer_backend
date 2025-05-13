from django import forms


class CustomDateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, **kwargs):
        kwargs['format'] = self.format
        super().__init__(**kwargs)
