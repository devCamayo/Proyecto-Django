from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Course, Question, Choice, Submission, Enrollment, Learner

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lesson_set.all()
    
    user_submissions = {}
    if request.user.is_authenticated:
        try:
            learner = Learner.objects.get(user=request.user)
            enrollment = Enrollment.objects.get(learner=learner, course=course)
            submissions = Submission.objects.filter(enrollment=enrollment)
            for sub in submissions:
                user_submissions[sub.question_id] = sub.selected_choice_id
        except (Learner.DoesNotExist, Enrollment.DoesNotExist):
            pass
    
    return render(request, 'cursos/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'user_submissions': user_submissions
    })

@login_required
def submit(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, id=course_id)
        
        # Obtener o crear Learner y Enrollment
        learner, created = Learner.objects.get_or_create(user=request.user)
        enrollment, created = Enrollment.objects.get_or_create(
            learner=learner, 
            course=course
        )
        
        with transaction.atomic():
            # Eliminar submissions anteriores
            Submission.objects.filter(enrollment=enrollment).delete()
            
            # Procesar nuevas respuestas
            submissions_created = []
            for key, value in request.POST.items():
                if key.startswith('question_'):
                    question_id = int(key.split('_')[1])
                    choice_id = int(value)
                    
                    question = Question.objects.get(id=question_id)
                    choice = Choice.objects.get(id=choice_id)
                    
                    # Usar el método is_get_score() para verificar la respuesta
                    is_correct = question.is_get_score(choice)
                    
                    submission = Submission.objects.create(
                        user=request.user,
                        enrollment=enrollment,
                        question=question,
                        selected_choice=choice,
                        is_correct=is_correct  # Usando el método is_get_score()
                    )
                    submissions_created.append(submission)
            
            messages.success(request, '¡Examen enviado exitosamente!')
            
            # Redirigir con el último submission.id (o el primero)
            if submissions_created:
                return redirect('show_exam_result', submission_id=submissions_created[0].id)
    
    return redirect('course_detail', course_id=course_id)

@login_required
def show_exam_result(request, submission_id):
    # Obtener la submission para encontrar el enrollment y course
    submission = get_object_or_404(Submission, id=submission_id, user=request.user)
    enrollment = submission.enrollment
    course = enrollment.course
    
    # Obtener todas las submissions para este enrollment
    submissions = Submission.objects.filter(enrollment=enrollment)
    
    if not submissions.exists():
        messages.info(request, 'No has realizado este examen aún.')
        return redirect('course_detail', course_id=course.id)
    
    # Calcular puntuación usando is_get_score() para cada pregunta
    total_questions = submissions.count()
    correct_answers = 0
    
    results = []
    for sub in submissions:
        # Usar el método is_get_score() para verificar cada respuesta
        is_correct = sub.question.is_get_score(sub.selected_choice)
        if is_correct:
            correct_answers += 1
        
        results.append({
            'question': sub.question,
            'selected_choice': sub.selected_choice,
            'is_correct': is_correct  # Resultado del método is_get_score()
        })
    
    score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    passed = score >= 70
    
    return render(request, 'cursos/exam_result.html', {
        'course': course,
        'score': round(score, 2),
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'results': results,
        'passed': passed,
        'submission_id': submission_id
    })