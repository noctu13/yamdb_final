from django.contrib import admin

from api.models import Category, Genre, Title, Client, Review, Comment


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "--"


class GenreAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "slug")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "--"


class TitleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "year", "description", "category")
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "--"


class ReviewAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "title", "score")
    search_fields = (
        "text",
        "title",
    )
    list_filter = ("pub_date",)
    empty_value_display = "--"


class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "author", "review", "pub_date")
    search_fields = ("review",)
    list_filter = ("review",)
    empty_value_display = "--"


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Client)
