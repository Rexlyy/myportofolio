
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    request.user.auth_token.delete()

    return Response(
        {'detail': 'Successfully logged out.'},
        status=status.HTTP_204_NO_CONTENT,
    )
