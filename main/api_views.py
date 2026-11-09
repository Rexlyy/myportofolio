from django.shortcuts import get_object_or_404

from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from main.models import Skill
from main.serializers import SkillSerializer
from main.permissions import IsSkillEditorOrReadOnly


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsSkillEditorOrReadOnly])
def skill_list_api(request):

    if request.method == 'GET':
        name_query = request.GET.get('name', '').strip()
        skills = Skill.objects.all()

        if name_query:
            skills = skills.filter(name__icontains=name_query)

        serializer = SkillSerializer(
            skills,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SkillSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            skill = serializer.save(user=request.user)

            return Response(
                SkillSerializer(
                    skill,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsSkillEditorOrReadOnly])
def skill_detail_api(request, skill_id):

    skill = get_object_or_404(Skill, pk=skill_id)

    # Pemeriksaan permission terhadap objek
    permission = IsSkillEditorOrReadOnly()

    if not permission.has_object_permission(request, None, skill):
        return Response(
            {'detail': 'Permission denied.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if request.method == 'GET':
        serializer = SkillSerializer(
            skill,
            context={'request': request}
        )

        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        serializer = SkillSerializer(
            skill,
            data=request.data,
            partial=(request.method == 'PATCH'),
            context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    elif request.method == 'DELETE':
        skill.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def skill_star_api(request, skill_id):

    skill = get_object_or_404(Skill, pk=skill_id)

    if skill.starred_by.filter(pk=request.user.pk).exists():
        skill.starred_by.remove(request.user)
        message = "Skill unstarred successfully."
    else:
        skill.starred_by.add(request.user)
        message = "Skill starred successfully."

    serializer = SkillSerializer(
        skill,
        context={'request': request}
    )

    return Response({
        'message': message,
        'skill': serializer.data
    })
