from django.contrib import admin
from .models import MyUser, Subscribe

admin.site.empty_value_display = 'Не задано'


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('username', 'email')
    search_fields = ('username',)

@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')