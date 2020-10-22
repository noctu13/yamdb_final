from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from rest_framework import (
    viewsets,
    generics,
    filters,
    pagination,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from api import models, serializers
from api.permissions import IsReadOnly, IsAdminClient, IsAuthorOrStaff
from api.filters import TitleFilter


class AuthViewSet(generics.CreateAPIView):
    queryset = models.Client.objects.all()
    serializer_class = serializers.AuthSerializer

    def perform_create(self, serializer):
        email_to = serializer.validated_data["email"]
        confirmation_code = get_random_string()
        serializer.save(confirmation_code=confirmation_code, is_active=False)
        send_mail(
            "Yambd account activation",
            "confirmation_code: " + confirmation_code,
            "admin@yambd.com",
            [email_to],
            fail_silently=False,
        )


class TokenViewSet(TokenObtainPairView):
    serializer_class = serializers.TokenSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    permission_classes = [IsAdminClient]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]
    lookup_field = "username"

    @action(
        detail=False,
        methods=["get", "patch"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if request.method == "GET":
            serializer = serializers.ClientSerializer(request.user)
            return Response(serializer.data)
        if request.method == "PATCH":
            serializer = serializers.ClientSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    permission_classes = [IsReadOnly | IsAdminClient]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = models.Genre.objects.all()
    serializer_class = serializers.GenreSerializer
    permission_classes = [IsReadOnly | IsAdminClient]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class TitleViewSet(viewsets.ModelViewSet):
    queryset = models.Title.objects.annotate(
        rating=Avg("review_title__score")
    ).all()
    permission_classes = [IsReadOnly | IsAdminClient]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return serializers.TitleReadSerializer
        return serializers.TitleWriteSerializer


class ActionPermissionsMixins:
    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[
                    self.action
                ]
            ]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class ReviewViewSet(ActionPermissionsMixins, viewsets.ModelViewSet):
    queryset = models.Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "partial_update": [IsAuthorOrStaff],
        "destroy": [IsAuthorOrStaff],
    }

    def get_queryset(self):
        title = get_object_or_404(models.Title, id=self.kwargs.get("title_id"))
        queryset = models.Review.objects.filter(title=title)
        return queryset

    def create(self, request, *args, **kwargs):
        title = get_object_or_404(models.Title, id=self.kwargs.get("title_id"))

        if (
            models.Review.objects.filter(author=request.user, title=title)
            .all()
            .count()
            != 0
        ):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.ReviewSerializer(data=request.data)

        if serializer.is_valid():
            if not (1 <= serializer.validated_data["score"] <= 10):
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save(author=request.user, title=title)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(ActionPermissionsMixins, viewsets.ModelViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    permission_classes_by_action = {
        "create": [IsAuthenticated],
        "partial_update": [IsAuthorOrStaff],
        "destroy": [IsAuthorOrStaff],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[
                    self.action
                ]
            ]
        except KeyError:
            return [permission() for permission in self.permission_classes]

    def create(self, request, *args, **kwargs):
        review = get_object_or_404(
            models.Review, id=self.kwargs.get("review_id")
        )
        serializer = serializers.CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(author=request.user, review=review)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        title = get_object_or_404(models.Title, id=self.kwargs.get("title_id"))
        review = models.Review.objects.get(
            title=title, id=self.kwargs.get("review_id")
        )
        queryset = models.Comment.objects.filter(review=review)
        return queryset
