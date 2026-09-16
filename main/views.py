from django.shortcuts import render
from main.models import Experience, Skill
from .forms import SkillForm

from django.contrib import messages
from django.shortcuts import render, redirect

from django.core import serializers
from django.http import HttpResponse


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
    json_response = get_skills_json(request)

    skills = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )

    skills = [skill.object for skill in skills]

    name_query = request.GET.get("name", "").strip()

    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "skill_list": skills,
        "name_query": name_query,
    }

    return render(
        request,
        "skills.html",
        context
    )

def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Skill baru berhasil ditambahkan!"
        )

        return redirect("main:show_skill")

    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "form": form,
    }

    return render(
        request,
        "skill_form.html",
        context
    )


def get_skills_json(request):
    name_query = request.GET.get("name", "").strip()

    skills = Skill.objects.all()

    if name_query:
        skills = skills.filter(name__icontains=name_query)

    skills_json = serializers.serialize("json", skills)

    return HttpResponse(
        skills_json,
        content_type="application/json"
    )