from main.models import Experience, Skill
from .forms import SkillForm

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.core import serializers
from django.http import HttpResponse

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

import datetime

def show_main(request):
    experience_list = Experience.objects.all()
    skill_list = Skill.objects.all()  

    last_login = request.COOKIES.get("last_login", "Belum ada sesi login / Cookie tidak ditemukan")
      
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "experience_list": experience_list,
        "skill_list": skill_list,
        "last_login": last_login,
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

@login_required(login_url="/login/")
def create_skill(request):
    form = SkillForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        skill = form.save(commit=False)
        skill.user = request.user
        skill.save()

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

    skills_json = serializers.serialize("json", skills, use_natural_foreign_keys =True)

    return HttpResponse(
        skills_json,
        content_type="application/json"
    )

@login_required(login_url="/login/")
def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if skill.user != request.user and not request.user.is_superuser:
        raise PermissionDenied

    form = SkillForm(request.POST or None, instance=skill)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(request, "Skill berhasil diperbarui")

        return redirect("main:show_skill")

    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "form": form,
        "skill": skill,
    }

    return render(request, "skill_form.html", context)

@login_required(login_url="/login/")
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if skill.user != request.user and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        skill.delete()

        messages.success(request, "Skill berhasil dihapus!")

        return redirect("main:show_skill")

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("main:login")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)

        response = redirect("main:show_main")

        response.set_cookie("last_login",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        return response

    context = {"name": "Lynorexly Imanuel Tatipikalawan","form": form,}

    return render(request, "login.html", context)

def logout_user(request):
    logout(request)

    response = redirect("main:show_main")

    response.delete_cookie("last_login")

    return response

@login_required(login_url="/login/")
def toggle_star(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if request.method == "POST":
        if request.user in skill.starred_by.all():
            skill.starred_by.remove(request.user)
            messages.success(request, "Star dihapus.")
        else:
            skill.starred_by.add(request.user)
            messages.success(request, "Skill berhasil di-star.")

    return redirect("main:show_skill")