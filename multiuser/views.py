from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse_lazy, reverse
from django.db.models import Prefetch, F
from django.conf import settings
from .models import Invitation, Entity, Organisation, Business, Branch
from guardian.shortcuts import get_objects_for_user, get_groups_with_perms, get_users_with_perms


class InvitationSentListView(LoginRequiredMixin, ListView):
    model = Invitation
    template_name = 'invitation_sent_list.html'
    context_object_name = 'invitations'

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        queryset = queryset.filter(invited_by=user).filter(accepted=False)
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
    success_url = reverse_lazy('invitationsent_list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user
        queryset = Entity.objects.none()

        # Only allow the user to invite others to entities for which they have change permission
        for model in Entity.get_all_models():
            sub_queryset = model.get_objects_for_user(user, settings.ENTITY_PERM_CHANGE)
            queryset = queryset | Entity.objects.filter(id__in=sub_queryset) # Upcast to allow union
        form.fields['entity'].queryset = queryset

        return form

    def form_valid(self, form):
        # Assign the user who created the instance to the invited_by field
        form.instance.invited_by = self.request.user 
        return super().form_valid(form)


class InvitationAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, pk=kwargs['pk'])
        invitation.accept(request.user)
        return redirect('invitationreceived_list')


class InvitationRejectView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, pk=kwargs['pk'])
        invitation.delete()
        return redirect('invitationreceived_list')


class InvitationCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        invitation = get_object_or_404(Invitation, pk=kwargs['pk'])
        invitation.delete()
        return redirect('invitationsent_list')


class EntityMixin(LoginRequiredMixin):
    pass


class EntityListView(EntityMixin, ListView):
    def get_queryset(self):
        return Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_VIEW)


class EntityCreateView(EntityMixin, CreateView):
    def form_valid(self, form):
        # Create and associate the content_object with an entity instance
        form.instance.save()
        parent = None
        parent_pk = self.kwargs.get('parent_pk')
        if parent_pk is not None:
            parent = Entity.objects.get(pk=parent_pk)
        entity = Entity.objects.create(content_object=form.instance, created_by=self.request.user, parent=parent)
        return super().form_valid(form)


class EntityDetailView(EntityMixin, DetailView):
    def get_queryset(self):
        return Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_VIEW)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entities_that_user_can_change = Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_CHANGE)
        entities_that_user_can_delete = Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_DELETE)

        # Whether the user has relevant permissions for the current or ancestor models
        context['can_change'] = entities_that_user_can_change.filter(content_object=self.object).exists()
        context['can_delete'] = entities_that_user_can_delete.filter(content_object=self.object).exists()
        
        # Add children to the context if the model is not a bottom level entity
        if not Entity.is_bottom(self.model): 
            context['children'] = Entity.objects.filter(parent=Entity.objects.get(content_object=self.object))

        # Current user can manage users if they have change permission 
        if context['can_change']:
            # Get the groups pertaining to the entity instance
            groups = get_groups_with_perms(self.object)
            groups = groups.annotate(role=F('name'))
            groups = Prefetch('groups', queryset=groups, to_attr='object_groups')
            # Get the users who have any permission for the entity instance
            users = get_users_with_perms(self.object)
            users = users.prefetch_related(groups).exclude(id=self.request.user.id) # Exclude the current user
            for user in users:
                for group in user.object_groups:
                    group.role = Entity.get_role(group.name)
            context['users'] = users

        return context

    def post(self, request, *args, **kwargs):
        if '/removeuser/' in self.request.path:
            user = get_object_or_404(User, pk=self.kwargs['user_pk'])
            group = get_object_or_404(Group, pk=self.kwargs['group_pk'])
            user.groups.remove(group)
        return redirect(self.request.path)


class EntityUpdateView(EntityMixin, UpdateView):
    def get_queryset(self):
        return Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_CHANGE)


class EntityDeleteView(EntityMixin, DeleteView):
    def get_queryset(self):
        return Entity.get_objects_for_user(self.model, self.request.user, settings.ENTITY_PERM_DELETE)


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
