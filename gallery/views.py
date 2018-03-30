from django.shortcuts import render

def art_list(request):
    return render(request, 'gallery/art_list.html', {})
