from django.contrib import admin
from .models import User
@admin.register(User)

# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['Name' , 'email', 'account' , 'username' , 'baseURL' , 'password']