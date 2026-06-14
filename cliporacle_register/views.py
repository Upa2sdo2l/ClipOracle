from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate  # Импортируем функцию входа
import json
from .models import Video, Genre

def home_page(request):
    # Здесь мы можем подготовить данные из базы или просто переменные
    context = {
        'title': 'Мой крутой сайт',
        'items': ['Питон', 'Django', 'FastAPI']
    }
    # Связываем: берем файл index.html и передаем туда данные context
    return render(request, 'index.html', context)

def register_page(request):
    if request.method == "POST":
        print(request.POST)
        # Собираем данные из атрибутов "name" нашего HTML
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Пользователь с таким логином уже существует!",
                "email": email
            })
        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "Пользователь с такой почтой уже существует!",
                "username": username
            })
        if password1 != password2:
            return render(request, "register.html", {
                "error": "Пароли не совпадают!",
                "username": username,
                "email": email
            })
        try:
            user = User.objects.create_user(username=username, email=email, password=password2)
            login(request, user)
            return redirect('home')
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return render(request, 'register.html')


def login_page(request):
    if request.method == "POST":
        # 1. Забираем данные из формы
        email = request.POST.get('email')
        passw = request.POST.get('password')

        try:
            # 1. Пытаемся найти пользователя по email
            user_obj = User.objects.get(email=email)
            # 2. Если нашли, берем его настоящий username и проверяем пароль
            user = authenticate(request, username=user_obj.username, password=passw)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Неверный пароль")
        except User.DoesNotExist:
            # Если пользователя с таким email нет
            messages.error(request, "Пользователь с такой почтой не найден")
        return redirect('login')
    return render(request, 'login.html')

def favourites_page(request):
    return render(request, 'favorites.html')


def get_categories(request):
    categories = list(Genre.objects.values('id', 'name').order_by('id'))
    return JsonResponse(categories, safe=False)


def get_videos(request):
    category_id = request.GET.get('category_id')
    videos = Video.objects.all()
    if category_id:
        videos = videos.filter(genre_id=category_id)
    if request.GET.get('min_views'):
        videos = videos.filter(views__gte=request.GET.get('min_views'))
    if request.GET.get('max_views'):
        videos = videos.filter(views__lte=request.GET.get('max_views'))
    if request.GET.get('min_likes'):
        videos = videos.filter(likes__gte=request.GET.get('min_likes'))
    video = videos.order_by('?').first()

    if video:
        data = [{
            "id": video.id,
            "video_text": video.video_text,
            "views": video.views,
            "likes": video.likes,
            "comments": video.comments,
            "shares": video.shares,
            "tags": video.tags,
            "genre_name": video.genre.name if video.genre else None,
            "file_path": video.file_path
        }]
        return JsonResponse(data, safe=False)

    return JsonResponse([], safe=False)