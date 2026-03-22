from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=500)
    points = models.IntegerField(default=1)
    
    def __str__(self):
        return self.text[:50]
    
    def is_get_score(self, selected_choice):
        """Verifica si la respuesta seleccionada es correcta"""
        if selected_choice:
            return selected_choice.is_correct
        return False

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Choice"
        verbose_name_plural = "Choices"
    
    def __str__(self):
        return self.choice_text[:50]

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    courses = models.ManyToManyField(Course, related_name='instructors', blank=True)
    
    def __str__(self):
        return f"Instructor: {self.user.username}"

class Enrollment(models.Model):
    learner = models.ForeignKey('Learner', on_delete=models.CASCADE)  # ← Cambiado
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['learner', 'course']
    
    def __str__(self):
        return f"{self.learner.user.username} - {self.course.title}"

class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enrolled_courses = models.ManyToManyField(Course, through='Enrollment', related_name='learners')
    
    def __str__(self):
        return f"Learner: {self.user.username}"

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['enrollment', 'question']
    
    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}"