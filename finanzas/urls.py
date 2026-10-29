from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_movimientos, name="lista"),
    path("nuevo/", views.crear_movimiento, name="crear"),
    path("<int:pk>/editar/", views.editar_movimiento, name="editar"),
    path("<int:pk>/borrar/", views.borrar_movimiento, name="borrar"),
    path("categorias/nueva/", views.crear_categoria, name="crear_categoria"),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="finanzas/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
