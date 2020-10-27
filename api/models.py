from django.contrib.auth.models import AbstractUser, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models


class Role(models.TextChoices):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class ClientManager(UserManager):
    def _create_user(
        self, email, username=None, password=None, **extra_fields
    ):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        client = self.model(username=username, email=email, **extra_fields)
        client.set_password(password)
        client.save(using=self._db)
        return client

    def create_user(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(
        self, email, username=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, username, password, **extra_fields)


class Client(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits "
            "and @/./+/-/_ only."
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
        blank=True,
        null=True,
    )
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.USER,
    )
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(max_length=12, null=True)
    objects = ClientManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, related_name="title_genre")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name="title_category",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        "Title", on_delete=models.CASCADE, related_name="review_title"
    )
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="review_author"
    )
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        "Review", on_delete=models.CASCADE, related_name="comment_review"
    )
    author = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="comment_author"
    )
    text = models.TextField()
    pub_date = models.DateTimeField("date_created", auto_now_add=True)

    def __str__(self):
        return self.text
