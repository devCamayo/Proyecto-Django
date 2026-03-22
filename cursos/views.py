from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Question, Choice, Submission
from django.db import transaction

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lesson_set.all()
    
    # Obtener respuestas del usuario para este curso
    user_submissions = {}
    if request.user.is_authenticated:
        submissions = Submission.objects.filter(user=request.user, course=course)
        for sub in submissions:
            user_submissions[sub.question_id] = sub.selected_choice_id
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'user_submissions': user_submissions
    })

@login_required
def submit(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        
        with transaction.atomic():
            # Eliminar submissions anteriores
            Submission.objects.filter(user=request.user, course=course).delete()
            
            # Procesar nuevas respuestas
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    question_id = int(key.split('_')[1])
                    choice_id = int(value)
                    
                    question = Question.objects.get(id=question_id)
                    choice = Choice.objects.get(id=choice_id)
                    
                    Submission.objects.create(
                        user=request.user,
                        course=course,
                        question=question,
                        selected_choice=choice,
                        is_correct=choice.is_correct
                    )
            
            messages.success(request, '¡Examen enviado exitosamente!')
            return redirect('show_exam_result', course_id=course_id)
    
    return redirect('course_detail', course_id=course_id)

@login_required
def show_exam_result(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    submissions = Submission.objects.filter(user=request.user, course=course)
    
    if not submissions.exists():
        messages.info(request, 'No has realizado este examen aún.')
        return redirect('course_detail', course_id=course_id)
    
    # Calcular puntuación
    total_questions = submissions.count()
    correct_answers = submissions.filter(is_correct=True).count()
    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Obtener resultados detallados
    results = []
    for submission in submissions:
        results.append({
            'question': submission.question,
            'selected_choice': submission.selected_choice,
            'is_correct': submission.is_correct
        })
    
    passed = score >= 70
    
    return render(request, 'courses/exam_result.html', {
        'course': course,
        'score': round(score, 2),
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'results': results,
        'passed': passed
    })