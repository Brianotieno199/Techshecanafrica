from django.shortcuts import render, redirect
from .models import BlogPost, GalleryImage, ContactMessage, Event


def home(request):
    posts = BlogPost.objects.filter(is_published=True)[:3]
    gallery_images = GalleryImage.objects.all()[:6]
    events = Event.objects.filter(is_active=True)

    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            subject=request.POST.get('subject'),
            message=request.POST.get('message')
        )
        return redirect('home')

    context = {
        'posts': posts,
        'gallery_images': gallery_images,
        'events': events,
    }

    return render(request, 'website/home.html', context)