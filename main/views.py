from django.shortcuts import render


def index(request):
    """Основная страница"""
    return render(request, 'main/index.html', )