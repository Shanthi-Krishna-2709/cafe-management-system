from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import logout
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.core.mail import send_mail, BadHeaderError
from django.contrib import messages
from .models import Menu, Order, OrderError
from .menu_catalog import MENU_CATALOG
from django.db import OperationalError  # FIX: Import OperationalError
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json
import logging  # FIX: Add logging

logger = logging.getLogger(__name__)  # FIX: Logger for debugging

try:
    import razorpay  # type: ignore[import]
except ImportError:
    razorpay = None
try:
    import qrcode  # type: ignore[import]
except ImportError:
    qrcode = None
try:
    from reportlab.platypus import SimpleDocTemplate, Paragraph  # type: ignore[import]
    from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import]
except ImportError:
    SimpleDocTemplate = None
    Paragraph = None
    getSampleStyleSheet = None


# ──────────────────────────────────────────
# MENU PAGE
# ──────────────────────────────────────────
def menu(request):
    menu_sections = []
    for section in MENU_CATALOG:
        menu_sections.append(
            {
                "category": section["category"],
                "items": [
                    {
                        "name": item["name"],
                        "price": item["price"],
                        "image": item["image"],
                        "is_external": item["image"].startswith("http"),
                    }
                    for item in section["items"]
                ],
            }
        )
    return render(request, 'menu.html', {'menu_sections': menu_sections})


# ──────────────────────────────────────────
# ADD TO CART
# ──────────────────────────────────────────
def add_to_cart(request, id):
    cart = request.session.get('cart', {})
    item_id = str(id)
    cart[item_id] = cart.get(item_id, 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')


# ──────────────────────────────────────────
# CART PAGE
# ──────────────────────────────────────────
def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for key, qty in cart.items():
        try:
            item = Menu.objects.get(id=int(key))
            price = item.price * qty
            items.append((item, qty, price))
            total += price
        except Menu.DoesNotExist:
            continue
        except OperationalError as e:  # FIX: Catch DB errors gracefully
            logger.error(f"DB error loading cart item {key}: {e}")
            continue

    return render(request, 'cart.html', {'items': items, 'total': total})


# ──────────────────────────────────────────
# CHECKOUT
# ──────────────────────────────────────────
def checkout(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for key, qty in cart.items():
        try:
            item = Menu.objects.get(id=int(key))
            price = item.price * qty
            items.append((item, qty, price))
            total += price
        except Menu.DoesNotExist:
            continue
        except OperationalError as e:  # FIX: Catch DB errors gracefully
            logger.error(f"DB error in checkout for item {key}: {e}")
            continue

    gst = total * 0.05
    grand_total = total + gst

    request.session['grand_total'] = int(grand_total * 100)  # paise
    request.session.modified = True

    return render(request, 'bill.html', {
        'items': items,
        'total': total,
        'gst': gst,
        'grand_total': grand_total
    })


# ──────────────────────────────────────────
# CLEAR CART
# ──────────────────────────────────────────
def clear_cart(request):
    request.session['cart'] = {}
    return redirect('menu')


# ──────────────────────────────────────────
# PDF BILL
# ──────────────────────────────────────────
def pdf(request):
    if SimpleDocTemplate is None or Paragraph is None or getSampleStyleSheet is None:
        return HttpResponse(
            "PDF generation support is unavailable. "
            "Install reportlab with: pip install reportlab"
        )

    total = request.session.get('grand_total')
    if total is None:
        return HttpResponse("No order total found. Please go through the checkout page first.")

    total_inr = total / 100.0

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bill.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("Cafe Invoice", styles['Title']),
        Paragraph(f"Total Amount: \u20b9{total_inr:.2f}", styles['Normal']),
        Paragraph("Thank you for your order!", styles['Normal']),
    ]
    doc.build(content)
    return response


# ──────────────────────────────────────────
# PAYMENT PAGE
# ──────────────────────────────────────────
@ensure_csrf_cookie
def payment(request):
    amount = request.session.get('grand_total', 50000)
    amount_in_rupees = amount / 100.0

    upi_id = getattr(settings, 'UPI_ID', 'merchant@bank')
    bank_account = getattr(settings, 'BANK_ACCOUNT', '1234567890')
    bank_name = getattr(settings, 'BANK_NAME', 'Your Bank')
    ifsc = getattr(settings, 'IFSC_CODE', 'BANK0001')

    order = None
    key_id = None

    if razorpay is not None:
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', None)
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', None)

        if key_id and key_secret and (
            key_id.startswith('rzp_test_') or key_id.startswith('rzp_live_')
        ):
            # FIX: Only create Razorpay order if keys are real (not placeholder)
            if 'XXXX' not in key_id:
                client = razorpay.Client(auth=(key_id, key_secret))
                try:
                    order = client.order.create({
                        'amount': amount,
                        'currency': 'INR',
                        'payment_capture': '1'
                    })
                    request.session['order_id'] = order['id']
                except Exception as e:
                    logger.warning(f"Razorpay order creation failed: {e}")
                    order = None

    return render(request, 'payment.html', {
        'amount': amount_in_rupees,
        'payment': order,
        'razorpay_key': key_id,
        'upi_id': upi_id,
        'bank_account': bank_account,
        'bank_name': bank_name,
        'ifsc': ifsc,
        'csrf_token': get_token(request),
    })


# ──────────────────────────────────────────
# CONFIRM ORDER  ← Main fix for I/O error
# ──────────────────────────────────────────
def confirm_order(request):
    """Save order to database when customer confirms payment."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

    # ── Parse payload ──────────────────────────────────────────────
    payload = {}
    if request.content_type and request.content_type.startswith('application/json'):
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except (ValueError, json.JSONDecodeError):
            payload = {}
    else:
        payload = request.POST.dict()

    payment_method = payload.get('payment_method', 'cash')
    customer_name = payload.get('customer_name', 'Guest')
    customer_phone = payload.get('customer_phone', '')
    customer_email = payload.get('customer_email', '')

    # ── Build items list ───────────────────────────────────────────
    items_payload = payload.get('items')
    items_list = []
    subtotal = 0.0

    if items_payload:
        raw_items = []
        if isinstance(items_payload, str):
            try:
                raw_items = json.loads(items_payload)
            except json.JSONDecodeError:
                _log_order_error(
                    customer_name, customer_phone, customer_email,
                    payment_method, items_payload, None, None, None,
                    'Invalid cart data received.', 'invalid'
                )
                return JsonResponse(
                    {'success': False, 'message': 'Invalid cart data received.'},
                    status=400
                )
        elif isinstance(items_payload, (list, tuple)):
            raw_items = items_payload

        for item in raw_items:
            name = item.get('name', 'Unknown item')
            qty = int(item.get('qty', 0) or 0)
            unit_price = float(item.get('unit_price', 0) or 0)
            if qty <= 0:
                continue
            line_total = unit_price * qty
            items_list.append({'name': name, 'qty': qty, 'price': round(line_total, 2)})
            subtotal += line_total
    else:
        # Fall back to session cart
        cart = request.session.get('cart', {})
        for key, qty in cart.items():
            try:
                item = Menu.objects.get(id=int(key))
                price = item.price * qty
                items_list.append({'name': item.name, 'qty': qty, 'price': round(price, 2)})
                subtotal += price
            except Menu.DoesNotExist:
                continue
            except OperationalError as e:  # FIX: Handle DB read error
                logger.error(f"DB error reading menu item {key}: {e}")
                return JsonResponse(
                    {'success': False, 'message': f'Database error reading menu: {e}'},
                    status=500
                )

    if not items_list:
        _log_order_error(
            customer_name, customer_phone, customer_email,
            payment_method, json.dumps(items_list), subtotal, 0, 0,
            'Your cart is empty.', 'invalid'
        )
        return JsonResponse(
            {'success': False, 'message': 'Your cart is empty.'},
            status=400
        )

    subtotal = round(subtotal, 2)
    gst = round(subtotal * 0.05, 2)
    total = round(subtotal + gst, 2)

    # ── Save order ─────────────────────────────────────────────────
    # FIX: Wrap in try/except OperationalError specifically to catch
    # SQLite I/O errors (locked DB, disk full, bad path, permissions)
    try:
        order = Order.objects.create(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            items=json.dumps(items_list),
            subtotal=subtotal,
            gst=gst,
            total_amount=total,
            payment_method=payment_method,
            status='completed',
        )

        # Clear cart from session after successful save
        request.session['cart'] = {}
        request.session['grand_total'] = 0
        request.session.modified = True

        logger.info(f"Order #{order.id} saved successfully for {customer_name}.")
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': f'Order #{order.id} saved successfully!'
        })

    except OperationalError as e:
        # FIX: SQLite I/O / lock error — log it and return clear message
        err_msg = str(e)
        logger.error(f"SQLite OperationalError saving order: {err_msg}")
        _log_order_error(
            customer_name, customer_phone, customer_email,
            payment_method, json.dumps(items_list), subtotal, gst, total,
            f'OperationalError: {err_msg}', 'failed'
        )
        return JsonResponse({
            'success': False,
            'message': (
                'Database error while saving your order. '
                'Please run: python manage.py migrate  — then try again.'
            )
        }, status=500)

    except Exception as e:
        err_msg = str(e)
        logger.error(f"Unexpected error saving order: {err_msg}")
        _log_order_error(
            customer_name, customer_phone, customer_email,
            payment_method, json.dumps(items_list), subtotal, gst, total,
            err_msg, 'failed'
        )
        return JsonResponse({
            'success': False,
            'message': f'Error saving order: {err_msg}'
        }, status=500)


def _log_order_error(name, phone, email, method, items, subtotal, gst, total, msg, status):
    """Helper — safely write an OrderError without crashing if DB is broken."""
    try:
        OrderError.objects.create(
            customer_name=name,
            customer_phone=phone,
            customer_email=email,
            payment_method=method,
            items=items or '',
            subtotal=subtotal,
            gst=gst,
            total_amount=total,
            error_message=msg,
            status=status,
        )
    except Exception as log_err:
        logger.error(f"Could not log OrderError: {log_err}")


# ──────────────────────────────────────────
# QR CODE
# ──────────────────────────────────────────
def qr(request):
    if qrcode is None:
        return HttpResponse(
            "QR code support is unavailable. "
            "Install with: pip install qrcode[pil]"
        )
    qr_img = qrcode.make("http://127.0.0.1:8000/")
    response = HttpResponse(content_type="image/png")
    qr_img.save(response, "PNG")
    return response


# ──────────────────────────────────────────
# GENERAL PAGES
# ──────────────────────────────────────────
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def testimonials(request):
    return render(request, 'testimonials.html')

def gallery(request):
    return render(request, 'gallery.html')


def contact(request):
    if request.method == 'POST':
        logger.info("Contact form submitted")
        email = request.POST.get('c-email', '').strip()
        subject = request.POST.get('c-subject', 'New message from website').strip() or 'New message from website'
        message_body = request.POST.get('c-msg', '').strip()

        reviewer_name = request.POST.get('r-name', '').strip()
        visit_type = request.POST.get('r-visit', '').strip()
        review_text = request.POST.get('r-review', '').strip()
        rating = request.POST.get('r-rating', '0').strip()

        logger.info(f"Email: {email}, Subject: {subject}, Message: {message_body}, Review: {review_text}")

        if not email or (not message_body and not review_text):
            messages.error(request, 'Please provide your email and a message or review before sending.')
        else:
            email_content = f"From: {email}\nSubject: {subject}\n\n"
            if message_body:
                email_content += f"Message:\n{message_body}\n\n"
            if reviewer_name or visit_type or rating != '0' or review_text:
                email_content += "Review details:\n"
                if reviewer_name:
                    email_content += f"Name: {reviewer_name}\n"
                if visit_type:
                    email_content += f"Visit Type: {visit_type}\n"
                if rating and rating != '0':
                    email_content += f"Rating: {rating}/5\n"
                if review_text:
                    email_content += f"Review: {review_text}\n"

            try:
                send_mail(
                    subject, email_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                logger.info("Email sent successfully")
                messages.success(request, '✅ Your message/review was sent successfully!')
                return redirect('contact')
            except BadHeaderError:
                logger.error("Bad header error")
                messages.error(request, 'Invalid header found. Message not sent.')
            except Exception as e:
                logger.error(f"Email send error: {e}")
                messages.error(request, f'Could not send message: {e}')

    return render(request, 'contact.html')


# ──────────────────────────────────────────
# ADMIN PORTAL  ← Fix for login issue
# ──────────────────────────────────────────
def admin_portal(request):
    """
    FIX: Do NOT logout before redirecting to admin login.
    Logging out here was destroying the session BEFORE Django admin
    could authenticate, causing OperationalError / redirect loops.
    Just redirect directly to admin login.
    """
    return redirect(reverse('admin:index'))


# ──────────────────────────────────────────
# SALES REPORT
# ──────────────────────────────────────────
def sales_report(request):
    """Display sales report and orders placed by customers."""
    try:
        all_orders = Order.objects.all()

        total_orders = all_orders.count()
        total_revenue = all_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_gst = all_orders.aggregate(Sum('gst'))['gst__sum'] or 0
        total_subtotal = all_orders.aggregate(Sum('subtotal'))['subtotal__sum'] or 0

        orders_by_payment = all_orders.values('payment_method').annotate(
            count=Count('id'), total=Sum('total_amount')
        )
        orders_by_status = all_orders.values('status').annotate(
            count=Count('id'), total=Sum('total_amount')
        )

        today = timezone.now().date()
        today_orders = all_orders.filter(created_at__date=today)
        today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        today_count = today_orders.count()

        last_7_days = timezone.now() - timedelta(days=7)
        week_orders = all_orders.filter(created_at__gte=last_7_days)
        week_revenue = week_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        from django.core.paginator import Paginator
        paginator = Paginator(all_orders, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_gst': total_gst,
            'total_subtotal': total_subtotal,
            'today_revenue': today_revenue,
            'today_count': today_count,
            'week_revenue': week_revenue,
            'orders_by_payment': orders_by_payment,
            'orders_by_status': orders_by_status,
            'page_obj': page_obj,
            'all_orders': page_obj.object_list,
        }

    except OperationalError as e:
        # FIX: If DB tables don't exist yet, show helpful message instead of crash
        logger.error(f"OperationalError in sales_report: {e}")
        context = {
            'db_error': (
                'Database tables are missing. '
                'Please run: python manage.py migrate'
            )
        }

    return render(request, 'sales_report.html', context)