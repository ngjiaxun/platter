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
        queryset = get_objects_for_user(user, 'multiuser.view_organisation', klass=Organisation)
        return queryset

class OrganisationCreateView(LoginRequiredMixin, CreateView):
    model = Organisation
    template_name = 'organisation_create.html'
    fields = ['name', 'address', 'contact_number', 'email']
    success_url = reverse_lazy('organisation_list')

class OrganisationDetailView(LoginRequiredMixin, DetailView):
    model = Organisation
    template_name = 'organisation_detail.html'
    context_object_name = 'organisation'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_organisation', klass=Organisation)
        return queryset

class OrganisationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organisation
    template_name = 'organisation_update.html'
    fields = ['name', 'address', 'contact_number', 'email']
    context_object_name = 'organisation'

class OrganisationDeleteView(LoginRequiredMixin, DeleteView):
    model = Organisation
    template_name = 'organisation_confirm_delete.html'
    success_url = reverse_lazy('organisation_list')

# class OrganisationUserListView(ListView):
#     model = OrganisationUser
#     template_name = 'organisation_user_list.html'
#     context_object_name = 'organisation_users'

# class OrganisationUserCreateView(CreateView):
#     model = OrganisationUser
#     template_name = 'organisation_user_create.html'
#     fields = ['organisation', 'user', 'role']
#     success_url = reverse_lazy('organisation_user_list')

# class OrganisationUserDetailView(DetailView):
#     model = OrganisationUser
#     template_name = 'organisation_user_detail.html'
#     context_object_name = 'organisation_user'

# class OrganisationUserUpdateView(UpdateView):
#     model = OrganisationUser
#     template_name = 'organisation_user_update.html'
#     fields = ['organisation', 'user', 'role']
#     context_object_name = 'organisation_user'

# class OrganisationUserDeleteView(DeleteView):
#     model = OrganisationUser
#     template_name = 'organisation_user_confirm_delete.html'
#     success_url = reverse_lazy('organisation_user_list')

class BusinessListView(LoginRequiredMixin, ListView):
    model = Business
    template_name = 'business_list.html'
    context_object_name = 'businesses'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(businessassignment__user=user)
        return queryset

class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    template_name = 'business_create.html'
    fields = ['name', 'organisation', 'industry', 'established_date']
    success_url = reverse_lazy('business_list')

class BusinessDetailView(LoginRequiredMixin, DetailView):
    model = Business
    template_name = 'business_detail.html'
    context_object_name = 'business'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(businessassignment__user=user)
        return queryset

class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    template_name = 'business_update.html'
    fields = ['name', 'organisation', 'industry', 'established_date']
    context_object_name = 'business'

class BusinessDeleteView(LoginRequiredMixin, DeleteView):
    model = Business
    template_name = 'business_confirm_delete.html'
    success_url = reverse_lazy('business_list')

# class BranchListView(ListView):
#     model = Branch
#     template_name = 'branch_list.html'
#     context_object_name = 'branches'

# class BranchCreateView(CreateView):
#     model = Branch
#     template_name = 'branch_create.html'
#     fields = ['name', 'business', 'address', 'contact_number', 'email']
#     success_url = reverse_lazy('branch_list')

# class BranchDetailView(DetailView):
#     model = Branch
#     template_name = 'branch_detail.html'
#     context_object_name = 'branch'

# class BranchUpdateView(UpdateView):
#     model = Branch
#     template_name = 'branch_update.html'
#     fields = ['name', 'business', 'address', 'contact_number', 'email']
#     context_object_name = 'branch'

# class BranchDeleteView(DeleteView):
#     model = Branch
#     template_name = 'branch_confirm_delete.html'
#     success_url = reverse_lazy('branch_list')
