from django.urls import path
from . import views
from . import api
from .views import error404
#from django.urls import handler404
from django.views.generic import TemplateView

urlpatterns = [
    path('welcome',views.welcome,name='welcome'),
    path('scan',views.scan,name='scan'),
    path('befscan',views.befscan,name='befscan'),
    path('home',views.home,name='home'),
    path('check_rfid/', views.check_rfid, name='check_rfid'),
    path('check_weight/', views.check_weight, name='check_weight'),
    path('search',views.search,name='search'),
    path('alert',views.alert,name='alert'),
    path('error404',views.error404,name='error404'),
    path('data/<int:pserialno>/', views.data, name='data'),
    path('success',views.success,name='success'),
    path('addproduct',views.addproduct,name='addproduct'), 
    path('removeproduct',views.removeproduct,name='removeproduct'), 

    #api
    ### signup send fname, lname , email , password , credit card no , cvc , exp date.
    ### response 201 and return the results that stored and add the id of the user in DB
    ### response 400 bad request and "error": "Invalid email or password"
    path('customers/create/', api.CreateCustomerView.as_view(), name='customer_create'), 
    ##### login send the email and password
    ##### response 200 and login successfully
    ##### response 400 bad request and "This field may not be blank."
    path('login/', api.login, name='login'), 
    ##### send the email and password
    ##### response 200 and retrieve all orders and order items
    ##### response 404 and "detail": "Not found."
    path('orders/', api.order_details),  #### get all orders
]  

