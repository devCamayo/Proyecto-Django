from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import Course, Lesson, Question, Choice, Submission, Enrollment, Instructor, Learner

# ============ Inline Classes ============

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['choice_text', 'is_correct']

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True
    fields = ['text', 'points', 'course']

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']
    fields = ['title', 'content', 'order']

# ============ ModelAdmin Classes ============

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['choice_text', 'question', 'is_correct']
    list_filter = ['is_correct', 'question']
    search_fields = ['choice_text']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'lesson', 'course', 'points']
    list_filter = ['lesson__course', 'lesson', 'course']
    search_fields = ['text']
    inlines = [ChoiceInline]
    
    def save_model(self, request, obj, form, change):
        if not obj.course and obj.lesson:
            obj.course = obj.lesson.course
        super().save_model(request, obj, form, change)

class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'content']
    inlines = [QuestionInline]
    ordering = ['course', 'order']

class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']
    list_filter = ['created_at']
    inlines = [LessonInline]
    readonly_fields = ('created_at',)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'enrollment', 'question', 'selected_choice', 'is_correct', 'submitted_at']
    list_filter = ['enrollment__course', 'is_correct', 'submitted_at']
    search_fields = ['user__username', 'question__text']
    readonly_fields = ['submitted_at']

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['learner', 'course', 'enrolled_at']  # ← Cambiado de 'user' a 'learner'
    list_filter = ['course']
    search_fields = ['learner__user__username', 'course__title']
    readonly_fields = ['enrolled_at']

class InstructorAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_courses']
    list_filter = ['courses']
    search_fields = ['user__username', 'bio']
    
    def get_courses(self, obj):
        return ", ".join([c.title for c in obj.courses.all()])
    get_courses.short_description = 'Courses'

class LearnerAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_enrolled_courses']
    search_fields = ['user__username']
    
    def get_enrolled_courses(self, obj):
        return ", ".join([e.course.title for e in obj.enrollment_set.all()])
    get_enrolled_courses.short_description = 'Enrolled Courses'

# ============ Registrar modelos ============

admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Learner, LearnerAdmin)