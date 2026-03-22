from django.contrib import admin
from .models import Course, Lesson, Question, Choice, Submission

# Importamos las clases necesarias
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'lesson', 'points']
    list_filter = ['lesson__course', 'lesson']
    search_fields = ['text']
    inlines = [ChoiceInline]

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'content']
    inlines = [QuestionInline]
    ordering = ['course', 'order']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    inlines = [LessonInline]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'question', 'is_correct', 'submitted_at']
    list_filter = ['course', 'is_correct', 'submitted_at']
    search_fields = ['user__username', 'question__text']

# Registrar los modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission, SubmissionAdmin)

# Asegurar que las clases de autenticación están registradas
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
