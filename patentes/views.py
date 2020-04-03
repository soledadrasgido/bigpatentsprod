from django.shortcuts import render

# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from scraper.models import Ecuacion,Project,Patentes,Estados,NumerosPatentes
from django.db.models import Count


class StaffRequiredMixin(object):
    """
    Este mixin requerirá que el usuario sea miembro del staff
    """
    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)

# Create your views here.
class PatentDetailView(DetailView):
    model = Patentes
    template_name = 'patentes/patentes_detail.html'
    

@method_decorator(staff_member_required, name='dispatch')
class PatentUpdate(UpdateView):
    model = Patentes
 

@method_decorator(staff_member_required, name='dispatch')
class PatentDelete(DeleteView):
    model = Patentes
    success_url = reverse_lazy('patentes:patentes')



