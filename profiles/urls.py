from django.conf.urls.static import static
from django.urls import path

from Squest import settings
from . import views

app_name = 'profiles'

urlpatterns = [
    # common URLs
    path('profile/', views.profile, name='profile'),
    path('profile/token/create', views.token_create, name='token_create'),
    path('profile/token/<int:token_id>/generate', views.token_generate, name='token_generate'),
    path('profile/token/<int:token_id>/edit', views.token_edit, name='token_edit'),
    path('profile/token/<int:token_id>/delete', views.token_delete, name='token_delete'),
    path('users/', views.user_list, name='user_list'),

    # group URLs
    path('group/<int:group_id>/users/', views.user_by_group_list, name='user_by_group_list'),
    path('group/<int:group_id>/users/update/', views.user_in_group_update, name='user_in_group_update'),
    path('group/<int:group_id>/users/remove/<int:user_id>/', views.user_in_group_remove, name='user_in_group_remove'),
    path('group/', views.group_list, name='group_list'),
    path('group/create/', views.group_create, name='group_create'),
    path('group/<int:group_id>/edit/', views.group_edit, name='group_edit'),
    path('group/<int:group_id>/delete/', views.group_delete, name='group_delete'),

    # billing group URLs
    path('billing-group/<int:billing_group_id>/users/', views.user_by_billing_group_list,
       name='user_by_billing_group_list'),
    path('billing-group/<int:billing_group_id>/users/update/', views.user_in_billing_group_update,
       name='user_in_billing_group_update'),
    path('billing-group/<int:billing_group_id>/users/remove/<int:user_id>/',
       views.user_in_billing_group_remove, name='user_in_billing_group_remove'),
    path('billing-group/', views.billing_group_list, name='billing_group_list'),
    path('billing-group/create/', views.billing_group_create, name='billing_group_create'),
    path('billing-group/<int:billing_group_id>/edit/', views.billing_group_edit, name='billing_group_edit'),
    path('billing-group/<int:billing_group_id>/delete/', views.billing_group_delete, name='billing_group_delete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
