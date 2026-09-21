from django.urls import path

from main.views import show_main, show_experience, show_skill, create_skill, get_skills_json, update_skill, delete_skill

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("skills/", show_skill, name="show_skill"),
    path("skills/add/", create_skill, name="create_skill"),
    path("api/skills/", get_skills_json, name="get_skills_json"),
    path("skills/<int:skill_id>/edit/", update_skill, name="update_skill"),
    path("skills/<int:skill_id>/delete/", delete_skill, name="delete_skill"),
]