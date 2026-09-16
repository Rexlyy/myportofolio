from django.forms import ModelForm, TextInput, Textarea, NumberInput

from main.models import Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill

        fields = [
            "name",
            "category",
            "proficiency",
            "description",
        ]

        labels = {
            "name": "Nama Skill",
            "category": "Kategori",
            "proficiency": "Proficiency",
            "description": "Deskripsi Skill",
        }

        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Python",
                    "maxlength": 100,
                }
            ),

            "category": TextInput(
                attrs={
                    "placeholder": "Programming Language",
                    "maxlength": 100,
                }
            ),

            "proficiency": NumberInput(
                attrs={
                    "placeholder": "85",
                    "min": 0,
                    "max": 100,
                }
            ),

            "description": Textarea(
                attrs={
                    "placeholder": "Jelaskan pengalamanmu dengan skill ini",
                    "rows": 3,
                }
            ),
        }