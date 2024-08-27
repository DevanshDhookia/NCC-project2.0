from django.contrib import admin
from .models import Director_General, Brigadier, Colonel, Clerk, Student

@admin.register(Director_General)
class DirectorGeneralAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(Brigadier)
class BrigadierAdmin(admin.ModelAdmin):
    list_display = ('user', 'director_general')

@admin.register(Colonel)
class ColonelAdmin(admin.ModelAdmin):
    list_display = ('user', 'brigadier')

@admin.register(Clerk)
class ClerkAdmin(admin.ModelAdmin):
    list_display = ('user', 'colonel')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('CBSE_No', 'Name', 'clerk', 'colonel', 'brigadier', 'director_general')
