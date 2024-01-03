from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import Entity, Organisation, Business, Branch
from guardian.shortcuts import get_objects_for_user, get_perms


class EntityMixin(LoginRequiredMixin):
    def get_form(self, form_class=None): # Overrides get_form() in CreateView and UpdateView 
        form = super().get_form(form_class)
        if self.model.is_top(): # If the model is a top level entity, hide the parent field
            form.fields['parent'].widget = form.fields['parent'].hidden_widget()
        else: # Otherwise, filter it to a list of those for which the user has change permission
            user = self.request.user
            prev_level = self.model.prev_level().lower()
            form.fields['parent'].queryset = get_objects_for_user(user, f'multiuser.change_{prev_level}')
        return form


class EntityCreateView(EntityMixin, CreateView):
    def form_valid(self, form):
        form.instance.created_by = self.request.user # Assign the user who created the instance to the created_by field
        return super().form_valid(form)


class EntityDetailView(EntityMixin, DetailView):
    def get_queryset(self):
        user = self.request.user
        curr_level = self.model.curr_level().lower()
        queryset = get_objects_for_user(user, f'multiuser.view_{curr_level}')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_perms = get_perms(self.request.user, self.object)
        if f'change_{self.model.curr_level().lower()}' in user_perms: # Check whether the user has change permission for the object
            context['has_change_perm'] = True
        if not self.model.is_bottom(): # Add children to the context if the model is not a bottom level entity
            context['children'] = Entity.objects.filter(parent=self.object)
        return context


class EntityUpdateView(EntityMixin, UpdateView):
    def get_queryset(self):
        user = self.request.user
        curr_level = self.model.curr_level().lower()
        queryset = get_objects_for_user(user, f'multiuser.change_{curr_level}')
        return queryset


class OrganisationListView(LoginRequiredMixin, ListView):
    model = Organisation
    template_name = 'organisation_list.html'
    context_object_name = 'organisations'

    def get_queryset(self):
        user = self.request.user
        queryset = get_objects_for_user(user, 'multiuser.view_organisation') 
        return queryset


class OrganisationCreateView(EntityCreateView):
    model = Organisation
    template_name = 'organisation_create.html'
    fields = '__all__'
    success_url = reverse_lazy('organisation_list')


class OrganisationDetailView(EntityDetailView):
    model = Organisation
    template_name = 'organisation_detail.html'
    context_object_name = 'organisation'


class OrganisationUpdateView(EntityUpdateView):
    model = Organisation
    template_name = 'organisation_update.html'
    fields = '__all__'
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

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = super().get_queryset() # Get all businesses
    #     organisations = get_objects_for_user(user, 'multiuser.view_organisation') # Get all organisations the user has view permission for
    #     businesses = get_objects_for_user(user, 'multiuser.view_business') # Get all businesses the user has view permission for
    #     queryset = queryset.filter(Q(organisation__in=organisations) | Q(pk__in=businesses)) # Filter the queryset to only include businesses that belong to the organisations the user has view permission for, or the user has view permission for
    #     return queryset


class BusinessCreateView(EntityCreateView):
    model = Business
    template_name = 'business_create.html'
    fields = '__all__'
    success_url = reverse_lazy('business_list') 


class BusinessDetailView(EntityDetailView):
    model = Business
    template_name = 'business_detail.html'
    context_object_name = 'business'


class BusinessUpdateView(EntityUpdateView):
    model = Business
    template_name = 'business_update.html'
    fields = '__all__'
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

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = super().get_queryset() # Get all branches
    #     organisations = get_objects_for_user(user, 'multiuser.view_organisation') # Get all organisations the user has view permission for
    #     businesses = get_objects_for_user(user, 'multiuser.view_business') # Get all businesses the user has view permission for
    #     branches = get_objects_for_user(user, 'multiuser.view_branch') # Get all branches the user has view permission for
    #     queryset = queryset.filter(Q(business__organisation__in=organisations) | Q(business__in=businesses) | Q(pk__in=branches)) # Filter the queryset to only include branches that belong to the organisations the user has view permission for, or the businesses the user has view permission for, or the user has view permission for
    #     return queryset


class BranchCreateView(EntityCreateView):
    model = Branch
    template_name = 'branch_create.html'
    fields = '__all__'
    success_url = reverse_lazy('branch_list')


class BranchDetailView(EntityDetailView):
    model = Branch
    template_name = 'branch_detail.html'
    context_object_name = 'branch'


class BranchUpdateView(EntityUpdateView):
    model = Branch
    template_name = 'branch_update.html'
    fields = '__all__'
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
