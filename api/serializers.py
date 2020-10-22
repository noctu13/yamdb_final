from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Category, Genre, Title, Client, Review, Comment


class AuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("email",)


class TokenSerializer(TokenObtainSerializer):
    def __init__(self, *args, **kwargs):
        super(TokenObtainSerializer, self).__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields["confirmation_code"] = serializers.CharField()

    def validate(self, attrs):
        field = "confirmation_code"
        credentials = {
            self.username_field: attrs.get(self.username_field),
            field: attrs.get(field),
        }
        if all(credentials.values()):
            try:
                user = Client.objects.get(
                    email=credentials[self.username_field],
                    confirmation_code=credentials[field],
                )
            except Client.DoesNotExist:
                user = None
            if user:
                user.is_active = True
                user.save()
                refresh = RefreshToken.for_user(user)
                return {"token": str(refresh.access_token)}
            else:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "{field}".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role",
        )
        extra_kwargs = {"username": {"required": True}}


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("name", "slug")
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(required=False)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all(), required=False
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Genre.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        fields = ("id", "name", "year", "description", "genre", "category")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        fields = ("id", "text", "score", "author", "pub_date")
        model = Review


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        fields = ("id", "text", "pub_date", "author")
        model = Comment
