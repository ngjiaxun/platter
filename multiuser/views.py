from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .models import *


class InvitationSentListView(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = 'invitation_sent_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user}")
        queryset = super().get_queryset()
        queryset = queryset.filter(invited_by=user).filter(accepted=False)
        print(f"Queryset: {queryset}")
        return queryset


class InvitationReceivedListView(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = 'invitation_received_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(email=user.email).filter(accepted=False)
        return queryset


class InvitationCreateView(LoginRequiredMixin, CreateView):
    model = Invitation
    template_name = 'invitation_create.html'
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


class InvitationAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, pk=kwargs['pk'])
        invitation.accepted = True
        invitation.save()


        # # Create the user group
        # user_group, created = Group.objects.get_or_create(name=f'{instance.name}_{instance.pk}_{instance._meta.model_name}_{user_role}')
        # # Assign the view permission for the instance to the user group
        # assign_perm(f'view_{instance._meta.model_name}', user_group, instance)

        # # Add the user who created the instance to the admin group
        # instance.created_by.groups.add(admin_group)


        # Add the user to the relevant group
        role = invitation.role.lower() + 's'
        group = Group.objects.get(name=f'{invitation.entity.name}_{invitation.entity.pk}_{invitation.entity._meta.model_name}_{role}')
        request.user.groups.add(group)

        return redirect('organisation_list')


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
