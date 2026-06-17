from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.companies.serializers import CompanySerializer
from apps.companies.services import register_company

from .serializers import RegisterSerializer, UserSerializer
from .ws_tickets import WS_TICKET_TTL_SECONDS, issue_ws_ticket


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=RegisterSerializer, responses={201: dict})
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user, company = register_company(
            email=data["email"],
            password=data["password"],
            company_name=data["company_name"],
            industry=data.get("industry", ""),
        )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "company": CompanySerializer(company).data,
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class WsTicketView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"], responses={200: dict})
    def post(self, request):
        ticket = issue_ws_ticket(request.user.id)
        return Response(
            {"ticket": ticket, "expires_in": WS_TICKET_TTL_SECONDS},
            status=status.HTTP_200_OK,
        )
