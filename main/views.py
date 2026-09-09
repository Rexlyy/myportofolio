from django.shortcuts import render
from main.models import Experience


def show_main(request):
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "npm": "2206000000",
        "study_program": "S1 Ilmu Komputer",
        "bio": "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik pada pengembangan perangkat lunak dan keamanan siber.",
    }

    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Lynorexly Imanuel Tatipikalawan",
        "experience_list": Experience.objects.all(),
    }

    return render(request, "experience.html", context)