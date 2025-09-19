
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.voter_login, name='login'),  # fixed name
    path('logout/', views.user_logout, name='logout'),
    path('reset/', views.reset_password, name='reset_password'),
    path('vote/', views.vote_view, name='vote'),
    path('vote/cast/', views.cast_vote, name='cast_vote'),
    path('results/', views.results, name='results'),
    path('subadmin/results/', views.subadmin_results, name='subadmin_results'),
]
