from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path("",views.home,name="home"),
    path("products",views.products,name="products"),
    path("login",views.login_view,name="login"),
    path("signup",views.signup_view,name="signup"),
    path("logout",views.logout_view,name="logout")
]
