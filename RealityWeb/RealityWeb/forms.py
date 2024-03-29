from django import forms
from .models import GetPriceModel, FindFeaturesModel
from django.forms.widgets import HiddenInput, Textarea
# from crispy_forms.helper import FormHelper
# from crispy_forms.layout import Layout, Div, Field

class GetPriceForm(forms.ModelForm):
    class Meta:
        model = GetPriceModel
        fields = '__all__'
        widgets = {
            'area': forms.NumberInput(attrs={
                                                'class': 'form-control m-input form-control-sm',
                                                'placeholder': 'Wpisz powierzchnie mieszkania w m2 np.  62.8'
                                        }),
            'typ_zabudowy': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'rok_zabudowy': forms.NumberInput(attrs={
                                                        'class': 'form-control m-input form-control-sm',
                                                        'placeholder': 'Wpisz rok wybudowania budynku np.  2020'
                                                }),
            'liczba_pokoi': forms.NumberInput(attrs={
                                                        'class': 'form-control m-input form-control-sm',
                                                        'placeholder': 'Wpisz licznę pomieszczen w mieszkaniu np.  2'
                                                }),
            'pietro': forms.NumberInput(attrs={
                                                'class': 'form-control m-input form-control-sm',
                                               'placeholder': 'Wpisz pietro, na ktorym znajduje sie mieszkanie np.  0'
                                        }),
            'max_liczba_pieter': forms.NumberInput(attrs={
                                                            'class': 'form-control m-input form-control-sm',
                                                            'placeholder': 'Wpisz maksymalna liczbe pieter w budynku np.  12'
                                                    }),
            'parking': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'kuchnia': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'wlasnosc': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'stan': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'material': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'okna': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'rynek': forms.Select(attrs={'class': 'form-control m-input form-control-sm'}),
            'tagi': forms.Textarea(attrs={
                                            'class': 'form-control m-input form-control-sm',
                                            'placeholder': 'Wpisz najważniejsze dane opisujące mieszkanie i okolice lub opis mieszkania w języku polskim, maksymalnie 2000 znaków'
            })
        }


    def __init__(self, *args, **kwargs):
        super(GetPriceForm, self).__init__(*args, **kwargs)
        self.fields['lat'].widget = HiddenInput()
        self.fields['lon'].widget = HiddenInput()    
        self.fields['area'].label = "Powierzchnia"
        self.fields['typ_zabudowy'].label = "Typ zabudowy"
        self.fields['rok_zabudowy'].label = "Rok wybudowania"
        self.fields['liczba_pokoi'].label = "Liczba pomieszczen"
        self.fields['pietro'].label = "Pietro"
        self.fields['max_liczba_pieter'].label = "Wysokosc budynku (liczba pieter)"
        self.fields['parking'].label = "Parking"
        self.fields['kuchnia'].label = "Typ kuchni"
        self.fields['material'].label = "Material budynku"
        self.fields['okna'].label = "Typ okien"
        self.fields['rynek'].label = "Rynek"
        self.fields['tagi'].label = "Tagi i/lub opis"
class FindFeaturesForm(forms.ModelForm):
    class Meta:
        model = FindFeaturesModel
        fields = '__all__'
    
        widgets = {
            'feature_shop': forms.SelectMultiple(attrs={'size': 25,
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_amenity_fun': forms.SelectMultiple(attrs={'size': 17, 
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_amenity_healthcare': forms.SelectMultiple(attrs={'size': 7, 
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_amenity_schooling': forms.SelectMultiple(attrs={'size': 7,
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_leisure': forms.SelectMultiple(attrs={'size': 7,
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_transport': forms.SelectMultiple(attrs={'size': 7, 
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
            'feature_tourism': forms.SelectMultiple(attrs={'size': 7, 
                                                                'class': 'form-control m-input form-control-sm'
                                                    }),
        }                                


    def __init__(self, *args, **kwargs):
        super(FindFeaturesForm, self).__init__(*args, **kwargs)
        self.fields['lat'].widget = HiddenInput()
        self.fields['lon'].widget = HiddenInput()
        self.fields['mapka_radius'].widget = HiddenInput()
        self.fields['city'].widget = HiddenInput()

        self.fields['feature_shop'].label = "Sklepy"
        self.fields['feature_amenity_fun'].label = "Udogodnienia"
        self.fields['feature_amenity_healthcare'].label = "Opieka zdrowotna"
        self.fields['feature_amenity_schooling'].label = "Szkolnictwo"
        self.fields['feature_leisure'].label = "Czas wolny"
        self.fields['feature_transport'].label = "Transport publiczny"
        self.fields['feature_tourism'].label = "Turystyka"

