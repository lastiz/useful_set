from django.shortcuts import render


def my_500(request):
    return render(request, 'main/500.html')

def my_404(request, exception):
    return render(request, 'main/404.html')