from django.urls import path
from . import views

urlpatterns = [
    path('inviteduser/create/', views.InvitedUserCreateView.as_view(), name='inviteduser_create'),
    path('inviteduser/sent/', views.InvitedUserSentListView.as_view(), name='invitedusersent_list'),
    path('inviteduser/received/', views.InvitedUserReceivedListView.as_view(), name='inviteduserreceived_list'),
    path('organisation/', views.OrganisationListView.as_view(), name='organisation_list'),
    path('organisation/create/', views.OrganisationCreateView.as_view(), name='organisation_create'),
    path('organisation/<int:pk>/', views.OrganisationDetailView.as_view(), name='organisation_detail'),
    path('organisation/<int:pk>/update/', views.OrganisationUpdateView.as_view(), name='organisation_update'),
    path('organisation/<int:pk>/delete/', views.OrganisationDeleteView.as_view(), name='organisation_delete'),
    path('business/', views.BusinessListView.as_view(), name='business_list'),
    path('business/create/', views.BusinessCreateView.as_view(), name='business_create'),
    path('business/<int:pk>/', views.BusinessDetailView.as_view(), name='business_detail'),
    path('business/<int:pk>/update/', views.BusinessUpdateView.as_view(), name='business_update'),
    path('business/<int:pk>/delete/', views.BusinessDeleteView.as_view(), name='business_delete'),
    path('branch/', views.BranchListView.as_view(), name='branch_list'),
    path('branch/create/', views.BranchCreateView.as_view(), name='branch_create'),
    path('branch/<int:pk>/', views.BranchDetailView.as_view(), name='branch_detail'),
    path('branch/<int:pk>/update/', views.BranchUpdateView.as_view(), name='branch_update'),
    path('branch/<int:pk>/delete/', views.BranchDeleteView.as_view(), name='branch_delete'),
]