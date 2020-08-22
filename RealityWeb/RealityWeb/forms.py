from django import forms
from .models import GetPriceModel
from django.forms.widgets import HiddenInput
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Div, Field

class GetPriceForm(forms.ModelForm):
    class Meta:
        model = GetPriceModel
        fields = '__all__'
        widgets = {
            'area': forms.NumberInput(attrs={'class': 'form-control m-input form-control-sm',
                                             'placeholder': 'Enter the area in m2 i.e. 61'}),
            'typ_zabudowy': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'rok_zabudowy': forms.NumberInput(attrs={'class': 'form-control m-input form-control-sm',
                                                     'placeholder': 'Enter the year of construction i.e. 2020'}),
            'liczba_pokoi': forms.NumberInput(attrs={'class': 'form-control m-input form-control-sm',
                                                     'placeholder': 'Enter number of rooms i.e. 2'}),
            'pietro': forms.NumberInput(attrs={'class': 'form-control m-input form-control-sm',
                                               'placeholder': 'Enter the floor number i.e. 0'}),
            'max_liczba_pieter': forms.NumberInput(attrs={'class': 'form-control m-input form-control-sm',
                                                          'placeholder': str('Enter the number of buidling' +"'" + 's floors i.e. 12')}),
            'parking': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'kuchnia': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'wlasnosc': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'stan': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'material': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'okna': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'rynek': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'opis': forms.Textarea(attrs={'class': 'form-control m-input form-control-sm'})
        }

    def __init__(self, *args, **kwargs):
        super(GetPriceForm, self).__init__(*args, **kwargs)
        self.fields['lat'].widget = HiddenInput()
        self.fields['lon'].widget = HiddenInput()
        # self.fields['csrftoken'].widget = HiddenInput()

        # self.helper = FormHelper(self)
        # self.helper.layout = Layout(
        #     Div(
        #         Field('area', wrapper_class='col-md-4'),
        #         Field('typ_zabudowy', wrapper_class='col-md-6'),
        #         css_class='form-row'),
        #     )
