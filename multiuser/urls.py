from django.urls import path
from . import views

urlpatterns = [
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
]