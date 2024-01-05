from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import *


class InvitedUserCreateView(LoginRequiredMixin, CreateView):
    model = InvitedUser
    template_name = 'invited_user_create.html'
    fields = ['email', 'entity', 'role']
    success_url = reverse_lazy('organisation_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        queryset = Entity.objects.none()

        # Only allow the user to invite others to entities for which they have change permission
        for model in Entity.get_all_models():
            sub_queryset = model.get_objects_for_user(user, Entity.PERM_CHANGE)
            queryset = queryset | Entity.objects.filter(id__in=sub_queryset)
            
        form.fields['entity'].queryset = queryset
        return form

    def form_valid(self, form):
        # Assign the user who created the instance to the invted_by field
        form.instance.invited_by = self.request.user 
        return super().form_valid(form)


class InvitedUserListView(LoginRequiredMixin, ListView):
    model = InvitedUser
    template_name = 'invited_user_list.html'
    context_object_name = 'invited_users'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(invited_by=user).filter(accepted=False)
        return queryset


class EntityMixin(LoginRequiredMixin):
        def get_form(self, form_class=None): # Overrides get_form() in CreateView and UpdateView 
            form = super().get_form(form_class)
            if isinstance(self, DeleteView): # Don't override the form for the DeleteView
                return form
            if self.model.is_top(): # Top level entities don't have a parent field
                form.fields['parent'].widget = form.fields['parent'].hidden_widget()
            else: # Only allow the user to select parents for which they have change permission
                user = self.request.user
                parent_model_str = self.model.get_parent_model().__name__.lower()
                form.fields['parent'].queryset = get_objects_for_user(user, f'multiuser.change_{parent_model_str}')
            return form


class EntityListView(EntityMixin, ListView):
    def get_queryset(self):
        return self.model.get_objects_for_user(self.request.user, Entity.PERM_VIEW)


class EntityCreateView(EntityMixin, CreateView):
    def form_valid(self, form):
        # Assign the user who created the instance to the created_by field
        form.instance.created_by = self.request.user 
        return super().form_valid(form)


class EntityDetailView(EntityMixin, DetailView):
    def get_queryset(self):
        return self.model.get_objects_for_user(self.request.user, Entity.PERM_VIEW)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Whether the user has relevant permissions for the current or ancestor models
        context['can_change'] = self.object in self.model.get_objects_for_user(self.request.user, Entity.PERM_CHANGE)
        context['can_delete'] = self.object in self.model.get_objects_for_user(self.request.user, Entity.PERM_DELETE)
        
        # Add children to the context if the model is not a bottom level entity
        if not self.model.is_bottom(): 
            context['children'] = Entity.objects.filter(parent=self.object)
        return context


class EntityUpdateView(EntityMixin, UpdateView):
    def get_queryset(self):
        return self.model.get_objects_for_user(self.request.user, Entity.PERM_CHANGE)


class EntityDeleteView(EntityMixin, DeleteView):
    def get_queryset(self):
        return self.model.get_objects_for_user(self.request.user, Entity.PERM_DELETE)


class OrganisationListView(EntityListView):
    model = Organisation
    template_name = 'organisation_list.html'
    context_object_name = 'organisations'


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


class OrganisationDeleteView(EntityDeleteView):
    model = Organisation
    template_name = 'organisation_confirm_delete.html'
    success_url = reverse_lazy('organisation_list')


class BusinessListView(EntityListView):
    model = Business
    template_name = 'business_list.html'
    context_object_name = 'businesses'


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


class BusinessDeleteView(EntityDeleteView):
    model = Business
    template_name = 'business_confirm_delete.html'
    success_url = reverse_lazy('business_list')


class BranchListView(EntityListView):
    model = Branch
    template_name = 'branch_list.html'
    context_object_name = 'branches'


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


class BranchDeleteView(EntityDeleteView):
    model = Branch
    template_name = 'branch_confirm_delete.html'
    success_url = reverse_lazy('branch_list')
