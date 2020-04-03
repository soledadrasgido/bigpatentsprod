from django.shortcuts import render

# Create your views here.
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from .models import Project
from scraper.models import Ecuacion
from django.db.models import Count
from .forms import ProjectForm
from registration.views import SignUpView
# Create your views here.
class ProjectListView(ListView):
    model = Project

class ProjectDetailView(DetailView):
    model = Project
    
@method_decorator(login_required, name='dispatch')
class ProjectCreate(CreateView):
    model = Project
    form_class = ProjectForm
    success_url = reverse_lazy('projects:projects')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ProjectCreate, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ProjectUpdate(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('projects:update', args=[self.object.id]) + '?ok'

@method_decorator(login_required, name='dispatch')
class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('projects:projects')



