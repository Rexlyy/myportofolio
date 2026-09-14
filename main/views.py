from django.shortcuts import render
from main.models import Experience, Skill


def show_main(request):
    experience_list = Experience.objects.all();
    skill_list = Skill.objects.all()    
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "experience_list": experience_list,
        "skill_list": skill_list,
    }

    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "experience_list": Experience.objects.all(),
    }

    return render(request, "experience.html", context)

def show_skill(request):
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "skill_list" : Skill.objects.all(),
    }

    return render(request, "skills.html", context)