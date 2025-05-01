from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
#index
def HolaMundo(request):

    #return render(request, 'index.html')
    
    return HttpResponse("Hola Mundo desde Django!")