
from django.urls import path

from main.api_views import (
    skill_list_api,
    skill_detail_api,
    skill_star_api,
)

app_name = 'api'

urlpatterns = [
    path('skills/',skill_list_api,name='skill-list'),
    path('skills/<int:skill_id>/',skill_detail_api,name='skill-detail'),
    path('skills/<int:skill_id>/star/',skill_star_api,name='skill-star'),
]
