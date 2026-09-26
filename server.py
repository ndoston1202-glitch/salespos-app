"""
SalesPOS - Kafe/Restoran POS tizimi
Single-file Django backend. Faqat Python kerak, Node.js/npm YO'Q.
Ishga tushirish: python server.py
"""
import os
import sys
import uuid
from pathlib import Path

import django
from django.conf import settings
from django.urls import path
from django.http import HttpResponse
from django.core.management import execute_from_command_line

BASE_DIR = Path(__file__).resolve().parent

# ============================================================
#  SOZLAMALAR
# ============================================================
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='salespos-kafe-secret-key-2024',
        ALLOWED_HOSTS=['*'],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'rest_framework',
            'rest_framework.authtoken',
            '__main__',
        ],
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'salespos.sqlite3',
            }
        },
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR],
            'APP_DIRS': True,
            'OPTIONS': {'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]},
        }],
        STATIC_URL='/static/',
        STATICFILES_DIRS=[BASE_DIR / 'static'],
        MEDIA_URL='/media/',
        MEDIA_ROOT=BASE_DIR / 'media',
        DEFAULT_AUTO_FIELD='django.db.models.BigAutoField',
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework.authentication.TokenAuthentication',
            ],
            'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
        },
        LANGUAGE_CODE='uz',
        TIME_ZONE='Asia/Tashkent',
        USE_I18N=True,
        USE_TZ=True,
    )
    django.setup()

# ============================================================
#  MODELLAR
# ============================================================
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        app_label = '__main__'
        ordering = ['order', 'name']


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    printer = models.CharField(max_length=100, blank=True, help_text='Kompyuterga ulangan printer nomi')
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    class Meta:
        app_label = '__main__'


class Table(models.Model):
    number = models.IntegerField(unique=True)
    capacity = models.IntegerField(default=4)
    status = models.CharField(max_length=20, default='free')
    location = models.CharField(max_length=100, blank=True)
    class Meta:
        app_label = '__main__'
        ordering = ['number']


class Order(models.Model):
    number = models.CharField(max_length=20, unique=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    order_type = models.CharField(max_length=20, default='dine_in')
    status = models.CharField(max_length=20, default='pending')
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = '__main__'
        ordering = ['-created_at']

    def recalc(self):
        self.total = sum(i.price * i.quantity for i in self.items.all())
        self.save(update_fields=['total'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='pending')
    note = models.CharField(max_length=255, blank=True)
    class Meta:
        app_label = '__main__'


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    method = models.CharField(max_length=20, default='cash')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        app_label = '__main__'



# ============================================================
#  API
# ============================================================
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import Sum


def u_data(u):
    return {'id': u.id, 'username': u.username, 'full_name': u.get_full_name() or u.username, 'is_staff': u.is_staff}


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
    if not user:
        return Response({'detail': "Login yoki parol noto'g'ri"}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': u_data(user)})


@api_view(['GET'])
def me_view(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'auth'}, status=401)
    return Response(u_data(request.user))


# ---- PRINTERLAR (kompyuterga ulangan, ishlatilgan nomlar ro'yxati) ----
@api_view(['GET'])
def printers(request):
    # Menyuda ishlatilgan printer nomlarini qaytaradi (tanlash uchun)
    names = MenuItem.objects.exclude(printer='').values_list('printer', flat=True).distinct()
    return Response(sorted(set(names)))


# ---- CATEGORIES ----
@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'POST':
        c = Category.objects.create(name=request.data.get('name', ''), order=request.data.get('order', 0),
                                    is_active=request.data.get('is_active', True))
        return Response({'id': c.id})
    return Response([{'id': c.id, 'name': c.name, 'order': c.order, 'is_active': c.is_active,
                      'items_count': c.items.count()} for c in Category.objects.all()])


@api_view(['PATCH', 'DELETE'])
def category_detail(request, pk):
    try:
        c = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    if request.method == 'DELETE':
        c.delete(); return Response({'ok': True})
    for f in ['name', 'order', 'is_active']:
        if f in request.data: setattr(c, f, request.data[f])
    c.save(); return Response({'ok': True})


def mi_data(m):
    return {'id': m.id, 'name': m.name, 'price': float(m.price), 'cost_price': float(m.cost_price),
            'profit': float(m.price) - float(m.cost_price), 'is_available': m.is_available, 'description': m.description,
            'category': m.category_id, 'category_name': m.category.name if m.category else '',
            'printer': m.printer, 'printer_name': m.printer}


# ---- MENU ----
@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'POST':
        m = MenuItem.objects.create(name=request.data.get('name', ''), price=request.data.get('price') or 0,
                                    cost_price=request.data.get('cost_price') or 0,
                                    category_id=request.data.get('category') or None,
                                    printer=request.data.get('printer') or '',
                                    is_available=request.data.get('is_available', True),
                                    description=request.data.get('description', ''))
        return Response(mi_data(m))
    qs = MenuItem.objects.select_related('category').all()
    if request.GET.get('category'):
        qs = qs.filter(category_id=request.GET['category'])
    return Response([mi_data(m) for m in qs])


@api_view(['PATCH', 'DELETE'])
def menu_item_detail(request, pk):
    try:
        m = MenuItem.objects.get(pk=pk)
    except MenuItem.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    if request.method == 'DELETE':
        m.delete(); return Response({'ok': True})
    for f in ['name', 'price', 'cost_price', 'is_available', 'description', 'printer']:
        if f in request.data: setattr(m, f, request.data[f])
    if 'category' in request.data: m.category_id = request.data['category'] or None
    m.save(); return Response(mi_data(m))


# ---- TABLES ----
@api_view(['GET', 'POST'])
def tables(request):
    if request.method == 'POST':
        t = Table.objects.create(number=request.data.get('number'), capacity=request.data.get('capacity', 4),
                                 location=request.data.get('location', ''))
        return Response({'id': t.id})
    result = []
    for t in Table.objects.all():
        active = t.orders.exclude(status__in=['completed', 'cancelled']).first()
        result.append({'id': t.id, 'number': t.number, 'capacity': t.capacity, 'status': t.status,
                       'location': t.location, 'active_order': active.id if active else None})
    return Response(result)


@api_view(['PATCH', 'DELETE'])
def table_detail(request, pk):
    try:
        t = Table.objects.get(pk=pk)
    except Table.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    if request.method == 'DELETE':
        t.delete(); return Response({'ok': True})
    for f in ['number', 'capacity', 'status', 'location']:
        if f in request.data: setattr(t, f, request.data[f])
    t.save(); return Response({'ok': True})


def o_data(o):
    return {'id': o.id, 'number': o.number, 'order_type': o.order_type, 'status': o.status,
            'table': o.table_id, 'table_number': o.table.number if o.table else None,
            'customer_name': o.customer_name, 'customer_phone': o.customer_phone, 'address': o.address,
            'total': float(o.total), 'created_at': o.created_at.isoformat(),
            'items': [{'id': i.id, 'menu_item': i.menu_item_id, 'name': i.menu_item.name, 'quantity': i.quantity,
                       'price': float(i.price), 'status': i.status, 'note': i.note,
                       'printer_name': i.menu_item.printer}
                      for i in o.items.select_related('menu_item').all()]}


# ---- ORDERS ----
@api_view(['GET', 'POST'])
def orders(request):
    if request.method == 'POST':
        d = request.data
        table_id = d.get('table') or None
        if table_id:
            ex = Order.objects.filter(table_id=table_id).exclude(status__in=['completed', 'cancelled']).first()
            if ex:
                return Response({'detail': f'Bu stolda faol buyurtma bor: {ex.number}', 'order_id': ex.id}, status=400)
        o = Order.objects.create(number=f"#{uuid.uuid4().hex[:6].upper()}", table_id=table_id,
                                 order_type=d.get('order_type', 'dine_in'), customer_name=d.get('customer_name', ''),
                                 customer_phone=d.get('customer_phone', ''), address=d.get('address', ''))
        for it in d.get('items', []):
            mi = MenuItem.objects.get(pk=it['menu_item'])
            OrderItem.objects.create(order=o, menu_item=mi, quantity=it.get('quantity', 1), price=mi.price,
                                     note=it.get('note', ''))
        o.recalc()
        if o.table:
            o.table.status = 'occupied'; o.table.save()
        return Response(o_data(o))
    qs = Order.objects.prefetch_related('items').all()
    if request.GET.get('order_type'): qs = qs.filter(order_type=request.GET['order_type'])
    if request.GET.get('status'): qs = qs.filter(status__in=request.GET['status'].split(','))
    return Response([o_data(o) for o in qs])


@api_view(['GET', 'PATCH', 'DELETE'])
def order_detail(request, pk):
    try:
        o = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    if request.method == 'DELETE':
        o.delete(); return Response({'ok': True})
    if request.method == 'PATCH':
        st = request.data.get('status')
        if st:
            o.status = st
            if st in ['completed', 'cancelled']:
                o.completed_at = timezone.now()
                if o.table: o.table.status = 'free'; o.table.save()
            o.save()
        return Response(o_data(o))
    return Response(o_data(o))


@api_view(['POST'])
def order_add_item(request, pk):
    try:
        o = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    mi = MenuItem.objects.get(pk=request.data['menu_item'])
    qty = request.data.get('quantity', 1)
    ex = o.items.filter(menu_item=mi).first()
    if ex:
        ex.quantity += qty; ex.save()
    else:
        OrderItem.objects.create(order=o, menu_item=mi, quantity=qty, price=mi.price, note=request.data.get('note', ''))
    o.recalc(); return Response(o_data(o))


@api_view(['DELETE'])
def order_remove_item(request, pk, item_id):
    try:
        it = OrderItem.objects.get(pk=item_id, order_id=pk)
    except OrderItem.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    o = it.order; it.delete(); o.recalc()
    return Response(o_data(o))


@api_view(['POST'])
def pay_order(request, pk):
    try:
        o = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    paid = request.data.get('paid') or o.total
    Payment.objects.update_or_create(order=o, defaults={'method': request.data.get('method', 'cash'),
                                                        'amount': o.total, 'paid': paid})
    o.status = 'completed'; o.completed_at = timezone.now(); o.save()
    if o.table: o.table.status = 'free'; o.table.save()
    return Response({'ok': True, 'change': float(paid) - float(o.total)})


@api_view(['GET'])
def dashboard(request):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    revenue = Payment.objects.filter(created_at__gte=today).aggregate(s=Sum('amount'))['s'] or 0
    return Response({'today_orders': Order.objects.filter(created_at__gte=today).count(),
                     'today_revenue': float(revenue),
                     'active_orders': Order.objects.exclude(status__in=['completed', 'cancelled']).count(),
                     'tables_total': Table.objects.count(),
                     'tables_free': Table.objects.filter(status='free').count()})


# ---- KITCHEN (oshxona) ----
@api_view(['GET'])
def kitchen(request):
    qs = Order.objects.exclude(status__in=['completed', 'cancelled']).prefetch_related('items')
    return Response([o_data(o) for o in qs])


@api_view(['PATCH'])
def kitchen_item(request, item_id):
    try:
        it = OrderItem.objects.get(pk=item_id)
    except OrderItem.DoesNotExist:
        return Response({'detail': 'topilmadi'}, status=404)
    it.status = request.data.get('status', it.status); it.save()
    return Response({'ok': True})



# ============================================================
#  INDEX + URLS
# ============================================================
def index(request):
    html = (BASE_DIR / 'index.html').read_text(encoding='utf-8')
    app_js = (BASE_DIR / 'static' / 'app.js').read_text(encoding='utf-8')
    # app.js ni to'g'ridan HTML ichiga joylash (static serve muammosini oldini olish)
    html = html.replace('<script src="/static/app.js"></script>',
                        f'<script>\n{app_js}\n</script>')
    return HttpResponse(html)


from django.contrib import admin
from django.conf.urls.static import static as static_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', login_view),
    path('api/me/', me_view),
    path('api/printers/', printers),
    path('api/categories/', categories),
    path('api/categories/<int:pk>/', category_detail),
    path('api/menu/', menu_items),
    path('api/menu/<int:pk>/', menu_item_detail),
    path('api/tables/', tables),
    path('api/tables/<int:pk>/', table_detail),
    path('api/orders/', orders),
    path('api/orders/<int:pk>/', order_detail),
    path('api/orders/<int:pk>/items/', order_add_item),
    path('api/orders/<int:pk>/items/<int:item_id>/', order_remove_item),
    path('api/orders/<int:pk>/pay/', pay_order),
    path('api/kitchen/', kitchen),
    path('api/kitchen/item/<int:item_id>/', kitchen_item),
    path('api/dashboard/', dashboard),
    path('', index),
]
urlpatterns += static_urls(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# ============================================================
#  ISHGA TUSHIRISH
# ============================================================
def setup_db():
    from django.core.management import call_command
    from django.db import connection
    # Auth/admin/token jadvallari
    call_command('migrate', interactive=False, verbosity=0, run_syncdb=True)
    # __main__ modellari — eski/buzuq jadvalni avtomatik qayta qurish
    models_order = [Category, Table, MenuItem, Order, OrderItem, Payment]
    # Teskari tartibda buzuq jadvallarni o'chirish (FK bog'liqlik uchun)
    for model in reversed(models_order):
        try:
            list(model.objects.all()[:1])  # ustunlar mosligi to'liq tekshiriladi
        except Exception:
            try:
                with connection.schema_editor() as se:
                    se.delete_model(model)
                print(f">>> Eski jadval o'chirildi: {model.__name__}")
            except Exception:
                pass
    # To'g'ri tartibda mavjud bo'lmaganlarini yaratish
    existing = connection.introspection.table_names()
    for model in models_order:
        if model._meta.db_table not in existing:
            try:
                with connection.schema_editor() as se:
                    se.create_model(model)
                print(f">>> Jadval yaratildi: {model.__name__}")
            except Exception as e:
                print(f"  {model.__name__}: {e}")
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@salespos.uz', 'admin123', first_name='Admin')
        print(">>> Admin yaratildi: admin / admin123")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        setup_db()
        print(">>> SalesPOS ishga tushdi: http://localhost:8000")
        execute_from_command_line(['server.py', 'runserver', '0.0.0.0:8000', '--noreload'])
    else:
        execute_from_command_line(sys.argv)
