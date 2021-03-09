from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/<int:task_id>/', views.get_task_result, name='get_task_result'),
    path('tower/', views.tower, name='tower'),
    path('tower/add_tower/', views.add_tower, name='add_tower'),
    path('tower/<int:tower_id>/sync_tower/', views.sync_tower, name='sync_tower'),
    path('tower/<int:tower_id>/delete_tower/', views.delete_tower, name='delete_tower'),
]
