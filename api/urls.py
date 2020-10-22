from django.urls import path, include

from rest_framework.routers import DefaultRouter

import api.views as views


router = DefaultRouter()
router.register("users", views.ClientViewSet)
router.register("categories", views.CategoryViewSet, basename="categories")
router.register("genres", views.GenreViewSet, basename="genres")
router.register("titles", views.TitleViewSet, basename="titles")
router.register(
    r"titles/(?P<title_id>\d+)/reviews",
    views.ReviewViewSet,
    basename="reviews",
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    views.CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("auth/email/", views.AuthViewSet.as_view()),
    path("auth/token/", views.TokenViewSet.as_view()),
    path("", include(router.urls)),
]
