from django.shortcuts import render, redirect
from apps.guest.forms import ImageForm
from apps.guest.models import Image

# Create your views here.
def upload_images(request):
    context = {}
    if request.method == "POST":
        form = ImageForm(data=request.POST, files=request.FILES)
        print(form)
        if form.is_valid():
            print("Is Valid")
            source_path = form.image.path
            return_path = source_path + ".infer.jpg"
            print(source_path)
            form.save()
            # context['path'] = return_path
            context['obj'] = form.instance
            return render(request, "guest/upload_images.html", context=context)
    else:
        form = ImageForm()
    img = Image.objects.all()
    context['form'] = form
    context['img'] = img

    return render(request, "guest/upload_images.html", context=context)
