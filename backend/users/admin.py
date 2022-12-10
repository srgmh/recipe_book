from django.contrib import admin
from .models import MyUser


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'email', )
    search_fields = ('username', 'email', )
    list_filter = ('first_name', 'email', )

