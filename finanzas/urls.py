from django.urls import path

from . import views

urlpatterns = [
    path("", views.lista_movimientos, name="lista"),
    path("nuevo/", views.crear_movimiento, name="crear"),
    path("<int:pk>/editar/", views.editar_movimiento, name="editar"),
    path("<int:pk>/borrar/", views.borrar_movimiento, name="borrar"),
]
