from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, CartItem
from .forms import AddToCartForm, OrderForm


def product_list(request):
    products = Product.objects.all()
    return render(request, 'main/product_list.html', {'products': products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': form.cleaned_data['quantity']}
            )
            if not created:
                cart_item.quantity += form.cleaned_data['quantity']
                cart_item.save()
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.items.add(cart_item)
            return redirect('cart_detail')
    else:
        form = AddToCartForm()
    return render(request, 'main/product_detail.html', {'product': product, 'form': form})


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            for item in cart.items.all():
                order.items.add(item)
            cart.items.clear()
            return redirect('order_success')
    else:
        form = OrderForm()
    return render(request, 'main/cart_detail.html', {'cart': cart, 'form': form})


@login_required
def cart_remove_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart_detail')


@login_required
def order_success(request):
    return render(request, 'main/order_success.html')
