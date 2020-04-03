# Create your views here.
from django.views.generic.edit import  UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect,render, get_object_or_404
from .models import Ecuacion,Project,Patentes,Estados,NumerosPatentes,PatentesRepositorios, Repositorios,Paises
from .forms import BusquedaForm
from .scrapylens import lensexcel, getIndivTrials,getnroresult,getSearchResults
from .clustering import obtenerdatos, tokenize_and_stem,tokenize_only
from django.db import connection
from datetime import date
import numpy as np
import pandas as pd
import nltk
from bs4 import BeautifulSoup
import re
import os
from django.db.models import Count

# Create your views here.
@login_required
def Patente(request,pk):
    idecuacion=get_object_or_404(Ecuacion,pk=pk)
    patentess=NumerosPatentes.objects.select_related('patente').filter(patente__ecuacion_id=idecuacion)
    patente=patentess.filter(tipo_numero=2) 
    fecha1='1900-01-01'
    fecha2=date.today()
    paisel=Paises.objects.all()
    paisel=list(paisel)
    if request.method == "POST":
        paisel= request.POST.getlist('paisel')
        #print(paisel)
        if not paisel:
            paisel=Paises.objects.all()
            paisel=list(paisel)
            #print('pasos')
        fecha1 = request.POST.get('fecha1')
        fecha2 = request.POST.get('fecha2')
        if fecha1 =='' :
            fecha1='1900-01-01'
        if fecha2 =='' :
            fecha2=date.today()

        patente = patente.filter(fecha_numero_patente__gte=fecha1, fecha_numero_patente__lte=fecha2,num_pat_pais_id__in=paisel)
    
    return render(request,"scraper/ecuacion_detail.html",{'patente':patente,'ecu':idecuacion,'fecha1':fecha1,'fecha2':fecha2,'paisel':paisel}) 

@login_required
def AnalisisEcuacion(request,pk,fecha1,fecha2,paisel):
    if paisel.find("<Paises:") != -1:
        paisel=Paises.objects.all()
        paisel=list(paisel) 

    else:
        paisel=paisel.replace("[", "")
        paisel=paisel.replace("]", "")
        paisel=paisel.replace("'", "")
        paisel=paisel.split(",")
        #print(paisel)

    idecuacion=get_object_or_404(Ecuacion,pk=pk)
    patentess=NumerosPatentes.objects.select_related('patente').filter(patente__ecuacion_id=idecuacion)
    patente = patentess.filter(tipo_numero=2,fecha_numero_patente__gte=fecha1, fecha_numero_patente__lte=fecha2,num_pat_pais_id__in=paisel)
    
    #obtenerdatos(request,patente)
    paises=NumerosPatentes.objects.select_related('patente').values('num_pat_pais_id__desc_pais').filter(patente__ecuacion_id=idecuacion,tipo_numero=2).annotate(num_books=Count('num_pat_pais_id')).order_by('-num_books')
    print(paises)
    fechas=NumerosPatentes.objects.select_related('patente').values('fecha_numero_patente__year').filter(patente__ecuacion_id=idecuacion,tipo_numero=2).annotate(num_patentes=Count('fecha_numero_patente__year')).order_by('fecha_numero_patente__year')
    tipodoc=Patentes.objects.select_related('estado').values('estado__desc_estado').filter(ecuacion_id=idecuacion).annotate(num_tipo=Count('estado_id'))
    figure=obtenerdatos(patente)
    return render(request,"scraper/analisisresult2.html",{'figure':figure, 'paises':paises, 'fechas':fechas, 'tipodoc':tipodoc})

@login_required
def AnalisisProyecto(request,pk):
    
    idproyecto=get_object_or_404(Project,pk=pk)
    ecuaciones=Ecuacion.objects.filter(proyecto=idproyecto)
    patente=NumerosPatentes.objects.select_related('patente').filter(patente__ecuacion_id__in=ecuaciones,tipo_numero=2).order_by('-fecha_numero_patente')
    
    paises=NumerosPatentes.objects.select_related('patente').values('num_pat_pais_id__desc_pais').filter(patente__ecuacion_id__in=ecuaciones,tipo_numero=2).annotate(num_books=Count('num_pat_pais_id')).order_by('-num_books')
    """for p in paises:
        print(p["num_pat_pais_id__desc_pais"],p["num_books"] )
        if str(p["num_pat_pais_id__desc_pais"]) == 'European Patents':
            print(str(p["num_pat_pais_id__desc_pais"]))
            p['Albania']=p['num_books']
            p['Austria']=p['num_books']
            p['Belgium']=p['num_books']
            p['Bulgaria']=p['num_books']
            p['Croatia']=p['num_books']
            p['Cyprus']=p['num_books']
            p['Czech Republic']=p['num_books']
            p['Denmark']=p['num_books']
            p['Estonia']=p['num_books']
            p['Finland']=p['num_books']
            p['France']=p['num_books']
            p['Germany']=p['num_books']
            p['Greece']=p['num_books']
            p['Hungary']=p['num_books']
            p['Iceland']=p['num_books']
            p['Ireland']=p['num_books']
            p['Italy']=p['num_books']
            p['Latvia']=p['num_books']
            p['Liechtenstein']=p['num_books']
            p['Lithuania']=p['num_books']
            p['Luxembourg']=p['num_books']
            p['Macedonia']=p['num_books']
            p['Malta']=p['num_books']
            p['Monaco']=p['num_books']
            p['Netherlands']=p['num_books']
            p['Norway, Poland']=p['num_books']
            p['Portugal']=p['num_books']
            p['Romania']=p['num_books']
            p['San Marino']=p['num_books']
            p['Serbia']=p['num_books']
            p['Slovakia']=p['num_books']
            p['Slovenia']=p['num_books']
            p['Spain']=p['num_books']
            p['Sweden']=p['num_books']
            p['Switzerland']=p['num_books']
            p['Turkey']=p['num_books']
            p['United Kingdom']=p['num_books']"""
        
      
    fechas=NumerosPatentes.objects.select_related('patente').values('fecha_numero_patente__year').filter(patente__ecuacion_id__in=ecuaciones,tipo_numero=2).annotate(num_patentes=Count('fecha_numero_patente__year')).order_by('fecha_numero_patente__year')
    tipodoc=Patentes.objects.select_related('estado').values('estado__desc_estado').filter(ecuacion_id__in=ecuaciones).annotate(num_tipo=Count('estado_id'))
    
    figure=obtenerdatos(patente)
    return render(request,"scraper/analisisresult2.html",{'figure':figure,'paises':paises,'fechas':fechas,'tipodoc':tipodoc})



@login_required
def EcuacionCreate(request,pk):
    model = Ecuacion
    proyecto=get_object_or_404(Project,pk=pk)
    Ecu_form = BusquedaForm()
    if request.method == "POST":
        Ecu_form = BusquedaForm(data=request.POST)
        if Ecu_form.is_valid():
            palabra_clave1 = request.POST.get('palabra_clave1','')
            campo1 = request.POST.get('campo1','')
            conector1 = request.POST.get('conector1','')
            palabra_clave2 = request.POST.get('palabra_clave2','')
            campo2 = request.POST.get('campo2','')
            conector2 = request.POST.get('conector2','')
            palabra_clave3 = request.POST.get('palabra_clave3','')
            campo3 = request.POST.get('campo3','')
            ecuacion= campo1 +':('+ palabra_clave1 +') '+conector1+' ' +campo2 +':('+ palabra_clave2 +') '+conector2+' '+campo3 +':('+ palabra_clave3 +')'
            query=ecuacion.replace(' ','%20')
            paginas=getnroresult(query)
            #print(query)
            #paginas=12
            if paginas != None:
                model=Ecuacion(ecuacion=ecuacion,proyecto=proyecto)
                model.save()
                idecu=model.pk
                getSearchResults(query,paginas)
                getIndivTrials(query)
                lensexcel(query,idecu)
 
                return redirect(reverse('scraper:ecuacion', args=(idecu,)))

    return render(request,"scraper/scraper_form.html",{'form':Ecu_form,'project':proyecto})


@method_decorator(login_required, name='dispatch')
class EcuacionDelete(DeleteView):
    model = Ecuacion
  
    def get_success_url(self):
    # Assuming there is a ForeignKey from Comment to Post in your model
        proyecto = self.object.proyecto 
        return reverse_lazy( 'projects:project', kwargs={'pk': proyecto.id})