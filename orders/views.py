import os
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import render_to_string

from .forms import OrderCreateForm
from .models import OrderItem, Order
from cart.cart import Cart

# 1. FIX: Add the DLL directory BEFORE importing weasyprint
gtk_path = r'C:\Program Files\GTK3-Runtime Win64\bin'
if os.path.exists(gtk_path):
    os.add_dll_directory(gtk_path)
    os.environ['PATH'] = gtk_path + os.pathsep + os.environ['PATH']
    # This is a specific WeasyPrint variable
    os.environ['WEASYPRINT_DLL_DIRECTORIES'] = gtk_path

# 2. Now import weasyprint
try:
    import weasyprint
except OSError as e:
    print(f"WeasyPrint Error: {e}")

# ... the rest of your views follow here ...


# from .tasks import order_created  # Make sure this import exists!

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            # clear the cart
            cart.clear()

            # --- THESE 3 LINES MUST BE INDENTED INSIDE THE IF BLOCK ---
            # launch asynchronous task
            # order_created.delay(order.id)
            
            # set the order in the session
            request.session['order_id'] = order.id
            
            # redirect for payment
            return redirect('payment:process')
            # ---------------------------------------------------------
            
    else:
        form = OrderCreateForm()

    return render(
        request,
        'orders/order/create.html',
        {'cart': cart, 'form': form}
    )


# ... your other views (order_create, etc.) ...

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(
        request, 
        'admin/orders/order/detail.html', 
        {'order': order}
    )




@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html', {'order': order})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    
    # 1. We generate the PDF data into a variable called 'pdf_data'
    # NOTICE: 'response' is NOT inside these parentheses anymore!
    pdf_data = weasyprint.HTML(string=html).write_pdf(
        stylesheets=[weasyprint.CSS(finders.find('css/pdf.css'))]
    )
    
    # 2. We write that data to the response
    response.write(pdf_data)
    
    return response