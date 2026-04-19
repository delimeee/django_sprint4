from django.contrib import admin
from .models import Post, Category, Location
# Register your models here.

admin.site.register(Category)
admin.site.register(Location)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'location',
        'category',
        'is_published',
        'created_at'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


admin.site.empty_value_display = 'Не задано'
admin.site.register(Post, PostAdmin)
