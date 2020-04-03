from django.contrib import admin
from .models import Paises, Repositorios,cip,Tiposcip

# Register your models here.
admin.site.register(Paises)
admin.site.register(Repositorios)
admin.site.register(cip)
admin.site.register(Tiposcip)