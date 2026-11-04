from django.utils.html import strip_tags
from django.urls import reverse
from rest_framework import serializers

from main.models import Skill


class SkillSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    is_authenticated = serializers.SerializerMethodField()
    can_update = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    update_url = serializers.SerializerMethodField()
    delete_url = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = '__all__'
        read_only_fields = ('id', 'user', 'starred_by')

    def validate_name(self, value):
        value = strip_tags(value).strip()

        if not value:
            raise serializers.ValidationError(
                "Skill name cannot be empty."
            )

        return value

    def validate_description(self, value):
        return strip_tags(value)

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return obj.starred_by.filter(pk=request.user.pk).exists()

    def get_starred_by_names(self, obj):
        return ", ".join(
            user.username for user in obj.starred_by.all()
        )

    def get_is_authenticated(self, obj):
        request = self.context.get("request")
        return request is not None and request.user.is_authenticated

    def get_can_update(self, obj):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return (
            request.user.is_superuser
            or request.user.has_perm("main.change_skill")
        )

    def get_can_delete(self, obj):
        request = self.context.get("request")

        return (
            request is not None
            and request.user.is_authenticated
            and request.user.is_superuser
        )

    def get_update_url(self, obj):
        return reverse(
            "main:update_skill",
            args=[obj.pk]
        )

    def get_delete_url(self, obj):
        return reverse(
            "main:delete_skill",
            args=[obj.pk]
        )