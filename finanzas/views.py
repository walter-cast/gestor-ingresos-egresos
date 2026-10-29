from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, MovimientoForm
from .models import Categoria, Movimiento

# Create your views here.


CATEGORIAS_INICIALES = ["Salario", "Gasto fijo", "Gasto variable", "Ahorro"]


def registro(request):
    if request.user.is_authenticated:
        return redirect("lista")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Categoria.objects.bulk_create(
            [Categoria(usuario=user, nombre=n) for n in CATEGORIAS_INICIALES]
        )
        login(request, user)
        return redirect("lista")
    return render(request, "finanzas/registro.html", {"form": form})


@login_required
def lista_movimientos(request):
    mes = request.GET.get("mes")
    categoria_id = request.GET.get("categoria")
    base = Movimiento.objects.filter(usuario=request.user)
    movimientos = base.select_related("categoria").order_by("-fecha")

    if categoria_id:
        movimientos = movimientos.filter(categoria_id=categoria_id)
    if mes:
        try:
            anio, mes_num = mes.split("-")
            movimientos = movimientos.filter(fecha__year=anio, fecha__month=mes_num)
        except ValueError:
            pass

    meses = base.dates("fecha", "month", order="DESC")
    categorias = Categoria.objects.filter(usuario=request.user)

    total_ingresos = (
        movimientos.filter(tipo="ingreso").aggregate(total=Sum("monto"))["total"] or 0
    )
    total_gastos = (
        movimientos.filter(tipo="gasto").aggregate(total=Sum("monto"))["total"] or 0
    )
    balance = total_ingresos - total_gastos
    gastos_categoria = (
        movimientos.filter(tipo="gasto")
        .values("categoria__nombre")
        .annotate(total=Sum("monto"))
        .order_by("-total")
    )
    return render(
        request,
        "finanzas/lista.html",
        {
            "movimientos": movimientos,
            "total_ingresos": total_ingresos,
            "total_gastos": total_gastos,
            "balance": balance,
            "gastos_por_categoria": gastos_categoria,
            "meses": meses,
            "categorias": categorias,
            "mes_seleccionado": mes,
            "categoria_seleccionada": categoria_id,
        },
    )


@login_required
def crear_movimiento(request):
    if request.method == "POST":
        form = MovimientoForm(request.POST, usuario=request.user)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.usuario = request.user
            movimiento.save()
            return redirect("lista")
    else:
        form = MovimientoForm(usuario=request.user)
    return render(request, "finanzas/form.html", {"form": form})


@login_required
def editar_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk, usuario=request.user)
    if request.method == "POST":
        form = MovimientoForm(request.POST, instance=movimiento, usuario=request.user)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = MovimientoForm(instance=movimiento, usuario=request.user)
    return render(request, "finanzas/form.html", {"form": form})


@login_required
def borrar_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk, usuario=request.user)
    if request.method == "POST":
        movimiento.delete()
        return redirect("lista")
    return render(request, "finanzas/confirmar.html", {"movimiento": movimiento})


@login_required
def crear_categoria(request):
    form = CategoriaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        categoria = form.save(commit=False)
        categoria.usuario = request.user
        categoria.save()
        return redirect("lista")
    return render(
        request, "finanzas/form.html", {"form": form, "titulo": "Nueva categoría"}
    )
