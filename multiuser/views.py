from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Organisation, Business, Branch
from guardian.shortcuts import get_objects_for_user

class OrganisationListView(LoginRequiredMixin, ListView):
    model = Organisation
    template_name = 'organisation_list.html'
    context_object_name = 'organisations'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_organisation')
        return queryset

class OrganisationCreateView(LoginRequiredMixin, CreateView):
    model = Organisation
    template_name = 'organisation_create.html'
    fields = ['name', 'address', 'contact_number', 'email']
    success_url = reverse_lazy('organisation_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class OrganisationDetailView(LoginRequiredMixin, DetailView):
    model = Organisation
    template_name = 'organisation_detail.html'
    context_object_name = 'organisation'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_organisation')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['businesses'] = Business.objects.filter(organisation=self.object)
        return context

class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organisation
    template_name = 'organisation_update.html'
    fields = ['name', 'address', 'contact_number', 'email']
    context_object_name = 'organisation'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.change_organisation')
        return queryset

class OrganisationDeleteView(LoginRequiredMixin, DeleteView):
    model = Organisation
    template_name = 'organisation_confirm_delete.html'
    success_url = reverse_lazy('organisation_list')

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.delete_organisation')
        return queryset

class BusinessListView(LoginRequiredMixin, ListView):
    model = Business
    template_name = 'business_list.html'
    context_object_name = 'businesses'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_business')
        return queryset

class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    template_name = 'business_create.html'
    fields = ['name', 'organisation', 'industry', 'established_date']
    success_url = reverse_lazy('business_list') 

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['organisation'].queryset = get_objects_for_user(self.request.user, 'multiuser.change_organisation')
        return form

class BusinessDetailView(LoginRequiredMixin, DetailView):
    model = Business
    template_name = 'business_detail.html'
    context_object_name = 'business'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_business')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.filter(business=self.object)
        return context

class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    template_name = 'business_update.html'
    fields = ['name', 'organisation', 'industry', 'established_date']
    context_object_name = 'business'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.change_business')
        return queryset

class BusinessDeleteView(LoginRequiredMixin, DeleteView):
    model = Business
    template_name = 'business_confirm_delete.html'
    success_url = reverse_lazy('business_list')

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.delete_business')
        return queryset

class BranchListView(ListView):
    model = Branch
    template_name = 'branch_list.html'
    context_object_name = 'branches'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_branch')
        return queryset

class BranchCreateView(CreateView):
    model = Branch
    template_name = 'branch_create.html'
    fields = ['name', 'business', 'address', 'contact_number', 'email']
    success_url = reverse_lazy('branch_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['business'].queryset = get_objects_for_user(self.request.user, 'multiuser.change_business')
        return form

class BranchDetailView(DetailView):
    model = Branch
    template_name = 'branch_detail.html'
    context_object_name = 'branch'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_branch')
        return queryset

class BranchUpdateView(UpdateView):
    model = Branch
    template_name = 'branch_update.html'
    fields = ['name', 'business', 'address', 'contact_number', 'email']
    context_object_name = 'branch'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.change_branch')
        return queryset

class BranchDeleteView(DeleteView):
    model = Branch
    template_name = 'branch_confirm_delete.html'
    success_url = reverse_lazy('branch_list')

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.delete_branch')
        return queryset
