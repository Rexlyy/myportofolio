from main.models import Experience, Skill
from .forms import SkillForm

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from django.core import serializers
from django.http import HttpResponse, JsonResponse

from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from django.urls import reverse

from django.views.decorators.http import require_POST

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
    name_query = request.GET.get("name", "").strip()

    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "name_query": name_query,
        "form": SkillForm(),
    }

    return render(
        request,
        "skills.html",
        context
    )


@login_required(login_url="/login/")
def create_skill(request):

    if not request.user.is_superuser:
        raise PermissionDenied

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

    return render(request, "skill_form.html", context)

@require_POST
def create_skill_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {
                "message": "Hanya pemilik portfolio yang dapat menambahkan skill."
            },
            status=403,
        )

    form = SkillForm(request.POST)

    if form.is_valid():
        skill = form.save(commit=False)

        skill.user = request.user

        skill.save()

        return JsonResponse(
            {
                "message": "Skill berhasil ditambahkan.",
                "pk": str(skill.id),
            },
            status=201,
        )

    return JsonResponse(
        {
            "errors": form.errors.get_json_data()
        },
        status=400,
    )


def get_skills_json(request):
    name_query = request.GET.get("name", "").strip()

    skills = Skill.objects.all()

    if name_query:
        skills = skills.filter(name__icontains=name_query)

    skills_data = []

    for skill in skills:
        skills_data.append({
            "id": skill.id,
            "name": skill.name,
            "category": skill.category,
            "proficiency": skill.proficiency,
            "description": skill.description,

            "star_count": skill.starred_by.count(),

            "is_starred": (
                request.user.is_authenticated
                and skill.starred_by.filter(id=request.user.id).exists()
            ),

            "starred_by_names": list(
                skill.starred_by.values_list(
                    "username",
                    flat=True
                )
            ),

            "is_authenticated": request.user.is_authenticated,

            # Hak untuk Edit
            "can_update": (
                request.user.is_authenticated
                and (
                    request.user.is_superuser
                    or request.user.has_perm(
                        "main.change_skill"
                    )
                )
            ),

            # Hak untuk Delete
            "can_delete": (
                request.user.is_authenticated
                and request.user.is_superuser
            ),

            # URL Edit
            "update_url": reverse(
                "main:update_skill",
                args=[skill.id]
            ),

            # URL Delete
            "delete_url": reverse(
                "main:delete_skill",
                args=[skill.id]
            ),

            # URL Star
            "toggle_star_url": reverse(
                "main:toggle_star",
                args=[skill.id]
            ),
        })

    return JsonResponse({
        "skills": skills_data
    })
    

    return JsonResponse({
        "skills": skills_data
    })

@login_required(login_url="/login/")
def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, pk=skill_id)

    if not request.user.is_superuser and not request.user.has_perm("main.change_skill"):
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

    if not request.user.is_superuser:
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

    if request.method != "POST":
        return JsonResponse(
            {"error": "Method tidak diizinkan."},
            status=405
        )

    if request.user in skill.starred_by.all():
        skill.starred_by.remove(request.user)
        is_starred = False
        message = "Star dihapus."
    else:
        skill.starred_by.add(request.user)
        is_starred = True
        message = "Skill berhasil di-star."

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": message,
            "is_starred": is_starred,
            "star_count": skill.starred_by.count(),
        })

    messages.success(request, message)
    return redirect("main:show_skill")