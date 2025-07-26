from django.shortcuts import render,redirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.urls import reverse


# Create your views here.
def home(request):
    return render(request,'index.html')
def products(request):
    return render(request,'products.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        u = authenticate(username=username,password=password)
        if u is not None:
            login(request,u)

            return redirect("main:home")
        else:
            print("user doesnt exists")
        
    return render(request,'login.html')
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user_created = User(username=username,password=password)
        user_created.save()

    return render(request,"signup.html")

def logout_view(request):
    logout(request)
    return redirect("main:home")