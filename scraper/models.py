from django.db import models
from projects.models import Project
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.
#Ecuaciones
class Ecuacion(models.Model):
    ecuacion = models.CharField(max_length=300, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated = models.DateTimeField(auto_now=True, verbose_name="Fecha de edición")
    proyecto = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'ecuacion'
        verbose_name = "ecuacion"
        verbose_name_plural = "ecuaciones"
        ordering = ['proyecto']

    def __str__(self):
        return self.ecuacion

class Estados(models.Model):
    desc_estado = models.CharField(unique=True, max_length=250)

    class Meta:
        db_table = 'estados'
        verbose_name = "estado"
        verbose_name_plural = "estados"
        ordering = ['desc_estado']

    def __str__(self):
        return self.desc_estado

class Tiposcip(models.Model):
    desc_tip_cip = models.CharField(db_column='desc_tip_cip', max_length=50,verbose_name='tipo de cip')  # Field name made lowercase.

    class Meta:
        db_table = 'tipos_cip'
        verbose_name = "tipo_cip"
        verbose_name_plural = "tipos_cip"
        ordering = ['desc_tip_cip']

    def __str__(self):
        return self.desc_tip_cip

class cip(models.Model):
    cod_cip = models.CharField(db_column='cod_cip', unique=True, max_length=45)  # Field name made lowercase.
    desc_cip = models.TextField(db_column='desc_cip', blank=True, null=True)  # Field name made lowercase.
    parent_cip = models.IntegerField(db_column='parent_cip', blank=True, null=True)  # Field name made lowercase.
    tipo_cip = models.ForeignKey('Tiposcip', on_delete=models.CASCADE, db_column='tipo_cip_id')  # Field name made lowercase.

    class Meta:
        db_table = 'cip'
        verbose_name = "cip"
        verbose_name_plural = "cips"
        ordering = ['cod_cip']

    def __str__(self):
        return self.cod_cip

#patente
class Patentes(models.Model):
    titulo_patente = models.CharField(max_length=300)
    resumen_patente = models.TextField(blank=True, null=True)
    claims_patente = models.TextField(blank=True, null=True)
    estado = models.ForeignKey(Estados, on_delete=models.CASCADE)
    clasificacion = models.ForeignKey(cip, on_delete=models.CASCADE)
    ecuacion_id = models.ForeignKey(Ecuacion,on_delete=models.CASCADE)

    class Meta:
        db_table = 'patentes'
        verbose_name = "patente"
        verbose_name_plural = "patentes"

    def __str__(self):
        return self.titulo_patente


class Paises(models.Model):
    cod_pais = models.CharField(max_length=2)
    desc_pais = models.CharField(max_length=200)

    class Meta:
        db_table = 'paises'
        verbose_name = "pais"
        verbose_name_plural = "paises"
        ordering = ['desc_pais']

    def __str__(self):
        return self.desc_pais

class TipoNumero(models.Model):
    nombre_tipo_numero = models.CharField(max_length=50)

    class Meta:
        db_table = 'tipo_numero'
        verbose_name = "tipo_numero"
        verbose_name_plural = "tipos_numeros"
        ordering = ['nombre_tipo_numero']

    def __str__(self):
        return self.nombre_tipo_numero
		
class NumerosPatentes(models.Model):
    cod_serie_patente = models.CharField(max_length=30)
    fecha_numero_patente = models.DateField()
    num_pat_pais = models.ForeignKey('Paises', on_delete=models.CASCADE)
    tipo_numero = models.ForeignKey('TipoNumero', on_delete=models.CASCADE)
    patente = models.ForeignKey('Patentes', on_delete=models.CASCADE)

    class Meta:
        db_table = 'numeros_patentes'
        verbose_name = "numero_patente"
        verbose_name_plural = "numeros_patentes"

#Repositorio
class Repositorios(models.Model):
    nombre_repositorio = models.CharField(max_length=50)
    link_repositorio = models.CharField(max_length=100)

    class Meta:
        db_table = 'repositorios'
        verbose_name = "repositorio"
        verbose_name_plural = "repositorios"
        ordering = ['nombre_repositorio']

    def __str__(self):
        return self.nombre_repositorio

class PatentesRepositorios(models.Model):
    repositorio = models.ForeignKey('Repositorios', on_delete=models.CASCADE)
    patente = models.ForeignKey(Patentes, on_delete=models.CASCADE)
    link_patente_repositorio = models.CharField(max_length=100)

    class Meta:
        db_table = 'patentes_repositorios'
    def __str__(self):
        return self.link_patente_repositorio

#Inventores Solicitantes
class InventoresSolicitantes(models.Model):
    nombre_inventor_solicitante = models.CharField(unique=True, max_length=200)

    class Meta:
        db_table = 'inventores_solicitantes'
        verbose_name = "inventor_solicitante"
        verbose_name_plural = "inventores_solicitantes"
        ordering = ['nombre_inventor_solicitante']

    def __str__(self):
        return self.nombre_inventor_solicitante

class PatInvSol(models.Model):
    tipo_pat_inv_sol = models.CharField(max_length=1)
    inventor_solicitante = models.ForeignKey(InventoresSolicitantes, on_delete=models.CASCADE)
    patente = models.ForeignKey('Patentes', on_delete=models.CASCADE)

    class Meta:
        db_table = 'pat_inv_sol'
        verbose_name = "pat_inv_sol"
        ordering = ['tipo_pat_inv_sol']


    def __str__(self):
        return self.tipo_pat_inv_sol

#Categorias	
class CategoriaVt(models.Model):
    nombre_categoria_vt = models.CharField(db_column='nombre_Clasificacion_VT', max_length=45)  # Field name made lowercase.

    class Meta:
        db_table = 'CategoriaVt'
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nombre_categoria_vt']

    def __str__(self):
        return self.nombre_categoria_vt


class PatenteCatvt(models.Model):
    patentes_id_patente = models.ForeignKey('Patentes', on_delete=models.CASCADE, db_column='patentes_id_patente')
    categoria_vt_id_categoria_vt = models.ForeignKey(CategoriaVt, on_delete=models.CASCADE, db_column='categoria_vt_id_categoria_vt')  # Field name made lowercase.

    class Meta:
        db_table = 'patente_catVT'