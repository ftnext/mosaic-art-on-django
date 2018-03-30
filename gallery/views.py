from django.shortcuts import render
from .models import MosaicArt

def art_list(request):
    mosaic_arts = MosaicArt.objects.order_by('-created_date')
    return render(request, 'gallery/art_list.html', {'mosaic_arts': mosaic_arts})
