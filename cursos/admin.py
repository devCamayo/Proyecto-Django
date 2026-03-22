from django.contrib import admin
from .models import Course, Lesson, Question, Choice, Submission

# 1. Definir los Inlines primero
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

class LessonInline(admin.TabularInline):  # ← Definir LessonInline ANTES de usarlo
    model = Lesson
    extra = 1
    ordering = ['order']

# 2. Definir los ModelAdmin después
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'content']
    inlines = [QuestionInline]
    ordering = ['course', 'order']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'lesson', 'points']
    list_filter = ['lesson__course', 'lesson']
    search_fields = ['text']
    inlines = [ChoiceInline]

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    inlines = [LessonInline]  # ← Ahora LessonInline ya está definido

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'question', 'is_correct', 'submitted_at']
    list_filter = ['course', 'is_correct', 'submitted_at']
    search_fields = ['user__username', 'question__text']

# 3. Registrar todos los modelos
admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)
admin.site.register(Submission, SubmissionAdmin)