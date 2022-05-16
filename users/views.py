
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import MyUserCreationForm
from .models import MyUser
from main_app.models import Exam, TakenExam
from django.shortcuts import get_object_or_404
from django.contrib import messages


def home(request):
    my_user = MyUser.objects.get(user=request.user)
    if my_user.is_examiner:
        return HttpResponseRedirect("/users/examiners/" + my_user.slug + "/")
    elif my_user.is_student:
        return HttpResponseRedirect("/users/students/" + my_user.slug + "/")


def examiner_sign_up(request):

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            MyUser.objects.get_or_create(user=user, is_examiner=True)

            messages.success(request, f"Your account created successfully")
            return redirect('users:login')

    else:
        form = MyUserCreationForm()

    data = {
        'form': form
    }
    return render(request, 'users/examiners/examiner_sign_up.html', data)


def student_sign_up(request):
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            MyUser.objects.get_or_create(user=user, is_student=True)

            messages.success(request, f"Your account created successfully")
            return redirect('users:login')

    else:
        form = MyUserCreationForm()

    data = {
        'form': form
    }
    return render(request, 'users/students/student_sign_up.html', data)


# the reason behind using the name 'the_login' , 'the_logout' , is to not conflict with the built in login function
def the_login(request):

    form = AuthenticationForm()

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome ( {username} )")
            return redirect('users:home')

        else:
            messages.error(request, f"Invalid Username or Password !!")

    data = {
        'form': form
    }
    return render(request, 'users/login.html', data)


def the_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('main:home')


def examiner_profile(request, slug):

    if request.method == 'POST':
        profile = get_object_or_404(MyUser, slug=slug)

        if profile.is_valid():
            redirect('users/examiners/examiner_profile.html')

    else:
        profile = AuthenticationForm()

    profile = get_object_or_404(MyUser, slug=slug)
    data = {
        'profile': profile
    }
    return render(request, 'users/examiners/examiner_profile.html', data)


def student_profile(request, slug):

    if request.method == 'POST':
        profile = get_object_or_404(MyUser, slug=slug)

        if profile.is_valid():
            redirect('users/students/student_profile.html')

    else:
        profile = AuthenticationForm()

    profile = get_object_or_404(MyUser, slug=slug)

    exams = Exam.objects.filter(is_published=True)


    rank, score, full, examName_list, category_list, type_list = resultQuery(profile)

    
   
    data = {
        'profile': profile,
        'exams': exams,
        'rank': rank, 
        'score': score,
        'full': full,
        'examName': examName_list,
        'category': category_list,
        'type': type_list
    }
    return render(request, 'users/students/student_profile.html', data)


def resultQuery(student_name):

    rank_list = []
    score_list =[]
    full_mark_list = []
    examName_list = []
    category_list = []
    type_list = []
    exams = []

    student_id = list(MyUser.objects.filter(slug = student_name).values())
    student_id = student_id[0].get("id")

    student_exams = list(TakenExam.objects.filter(student_id = student_id).values())
    


    exams_id = []
    for i in student_exams:
        exams_id.append(i.get("exam_id"))

    exams_id = list(set(exams_id))

    for exam in exams_id:
        print("Exam No.:   ",exam)
        students = list(TakenExam.objects.filter(exam_id = exam).values())

        rank = sorted(students, key = lambda i: i['score'] , reverse=True)

        count = 1
        if len(rank) == 0:
            return rank_list , score_list , full_mark_list, examName_list, category_list, type_list
        else:
            for x in rank:
                print("checkkkk:", x)
                if x['student_id'] == student_id:
                    rank_list.append(count)
                    score_list.append(x['score'])
                    full_mark_list.append(x['full_mark'])
                    exams.append(x['exam_id'])

                count += 1
        print("===================================")

    for exam in exams:
        students = list(Exam.objects.filter(id = exam).values())
        examName_list.append(students[0].get('exam_name'))
        category_list.append(students[0].get('category'))
        type_list.append(students[0].get('exam_type'))
        


    print("examName_list: ",examName_list)
    print("category_list: ",category_list)
    return rank_list , score_list , full_mark_list, examName_list, category_list, type_list


