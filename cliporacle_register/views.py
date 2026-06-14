from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import login, authenticate  # Импортируем функцию входа
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import Video, Genre
import datetime
import secrets

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
        email = request.POST.get('email')
        passw = request.POST.get('password')

        try:
            user_obj = User.objects.get(email=email)

            user = authenticate(request, username=user_obj.username, password=passw)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, "login.html", {
                    "error": "Неверный пароль!",
                    "username": email
                })
        except User.DoesNotExist:
            return render(request, "login.html", {
                "error": "Пользователь с такой почтой не существует!",
                "username": email
            })
    return render(request, 'login.html')

def favourites_page(request):
    print('abab')
    return render(request, 'favorites.html')

def request_password_reset(request):
    """Функция запроса сброса пароля (ввод email)"""
    if request.method == 'POST':
        email = request.POST.get('email')
        users = User.objects.filter(email=email)
        if users.exists():
            for user in users:
                try:
                    uid = urlsafe_base64_encode(force_bytes(user.pk))

                    token = default_token_generator.make_token(user)
                    domain = request.get_host()
                    protocol = 'https' if request.is_secure() else 'http'
                    reset_url = f"{protocol}://{domain}/reset/{uid}/{token}/"

                    subject = "Восстановление пароля"
                    message = f"Для сброса пароля перейдите по ссылке: {reset_url}"

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL or 'noreply@example.com',
                        [user.email],
                        fail_silently=False,
                    )
                    return render(request, 'forgot-password.html', {"message": "Ссылка отправлена!"})
                except Exception as e:
                    return render(request, 'forgot-password.html', {"message": str(e)})
        else:
            return render(request, 'forgot-password.html', {"message": "Пользователь не существует!"})
    return render(request, 'forgot-password.html')


def reset_password_confirm(request, uidb64, token):
    """Функция проверки токена и установки нового пароля"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # 2. Проверяем валидность токена и срок его действия
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_pwd1 = request.POST.get('pwd1')
            new_pwd2 = request.POST.get('pwd2')
            if new_pwd1 != new_pwd2:
                return render(request, 'forgot-password.html', {"message": "Пароли не совпадают!"})

            # 3. Устанавливаем новый пароль (Django автоматически захэширует его)
            user.set_password(new_pwd1)
            user.save()  # Сохраняем обновленный хэш в PostgreSQL

            return redirect('login')

        # Если метод GET — показываем форму ввода нового пароля
        return render(request, 'reset-password.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        # Если токен недействителен или просрочен
        return render(request, 'reset-password.html', {
            'validlink': False
        })

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