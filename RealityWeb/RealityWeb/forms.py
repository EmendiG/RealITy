from django import forms
from .models import GetPriceModel
from django.forms.widgets import HiddenInput


class GetPriceForm(forms.ModelForm):
    class Meta:
        model = GetPriceModel
        fields = [
            'lat',
            'lon',
            'category',
            'subject',
        ]
    # def __init__(self, *args, **kwargs):
    #     super(GetPriceForm, self).__init__(*args, **kwargs)
    #     self.fields['lat'].widget = HiddenInput()
    #     self.fields['lon'].widget = HiddenInput()

# lat = forms.DecimalField(label='lat', max_digits=7, decimal_places=4 ,widget=forms.HiddenInput())
# lon = forms.DecimalField(label='lat', max_digits=7, decimal_places=4, widget=forms.HiddenInput())
# category = forms.ChoiceField(choices=[('domek', 'domek'), ('mieszkanie', 'mieszkanie')])
# subject = forms.CharField()