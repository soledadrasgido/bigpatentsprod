from django import forms
#from forms import renderer
from .models import Ecuacion
from django.utils.safestring import mark_safe

CAMPO_OPCIONES= [
    
    ('full_text', 'FullText'),
    ('title', 'Titulo'),
    ('abstract', 'Resumén'),
    ('claims', 'Reinvidicaciones'),
    ]
CONECTOR_CHOICES= [
    
    ('and', 'AND'),
    ('or', 'OR'),
    ('not', 'NOT'),
] 



class BusquedaForm(forms.Form):
    campo1= forms.CharField(label="",required=True,widget=forms.Select(choices=CAMPO_OPCIONES))
    palabra_clave1= forms.CharField(label="", required=True, widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Escribe Palabras a Buscar'}
    ), max_length=100)
    conector1= forms.CharField(label="",widget=forms.RadioSelect(attrs={
        'style': 'display: inline-block'},choices=CONECTOR_CHOICES))
    
    campo2= forms.CharField(label="",widget=forms.Select(choices=CAMPO_OPCIONES))
    palabra_clave2= forms.CharField(label="", widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Escribe Palabras a Buscar'}), max_length=100)
    conector2= forms.CharField(label="",widget=forms.RadioSelect(attrs={'style': 'display: inline-block'},choices=CONECTOR_CHOICES))
    campo3= forms.CharField(label="",widget=forms.Select(choices=CAMPO_OPCIONES))
    palabra_clave3= forms.CharField(label="", widget=forms.TextInput(
        attrs={'class':'form-control', 'placeholder':'Escribe Palabras a Buscar'}
    ), max_length=100)
    
    