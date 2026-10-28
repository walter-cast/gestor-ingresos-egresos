from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MovimientoForm
from .models import Categoria, Movimiento


# Create your views here.
def lista_movimientos(request):
    mes = request.GET.get("mes")
    categoria_id = request.GET.get("categoria")
    movimientos = Movimiento.objects.select_related("categoria").order_by("-fecha")

    if categoria_id:
        movimientos = movimientos.filter(categoria_id=categoria_id)
    if mes:
        try:
            anio, mes_num = mes.split("-")
            movimientos = movimientos.filter(fecha__year=anio, fecha__month=mes_num)
        except ValueError:
            pass

    meses = Movimiento.objects.dates("fecha", "month", order="DESC")
    categorias = Categoria.objects.all()

    total_ingresos = (
        movimientos.filter(tipo="Ingreso").aggregate(total=Sum("monto"))["total"] or 0
    )
    total_gastos = (
        movimientos.filter(tipo="Gasto").aggregate(total=Sum("monto"))["total"] or 0
    )
    balance = total_ingresos - total_gastos
    gastos_categoria = (
        (movimientos.filter(tipo="Gasto"))
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


def crear_movimiento(request):
    if request.method == "POST":
        form = MovimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = MovimientoForm()
    return render(request, "finanzas/form.html", {"form": form})


def editar_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    if request.method == "POST":
        form = MovimientoForm(request.POST, instance=movimiento)
        if form.is_valid():
            form.save()
            return redirect("lista")
    else:
        form = MovimientoForm(instance=movimiento)
    return render(request, "finanzas/form.html", {"form": form})


def borrar_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    if request.method == "POST":
        movimiento.delete()
        return redirect("lista")
    return render(request, "finanzas/confirmar.html", {"movimiento": movimiento})
