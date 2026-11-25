
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from main.api_views import (
    skill_list_api,
    skill_detail_api,
    skill_star_api,
    project_list_create_api,
)

from main.auth_views import logout_api

app_name = 'api'

urlpatterns = [
    # Authentication
    path(
        'auth/token/',
        obtain_auth_token,
        name='api-token-auth',
    ),
    path(
        'auth/logout/',
        logout_api,
        name='api-logout',
    ),

    # Skills
    path('skills/', skill_list_api, name='skill-list'),
    path('skills/<int:skill_id>/', skill_detail_api, name='skill-detail'),
    path('skills/<int:skill_id>/star/', skill_star_api, name='skill-star'),

    path('projects/',project_list_create_api,name='project-list-create'),
]
