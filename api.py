from .models import Customer,Order,OrderItem,OrderItemProduct,Product
from .serializers import Customerserializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Customer, OrderItem


#class based api
#receive all data of the customer and send it if any field no complete send that field to be completed
class CreateCustomerView(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = Customerserializer

#function based api
#first retrieve the email and password then check them if found return login successful 200
#else Invalid email or password 400 bad request
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        customer = Customer.objects.get(email=email, password=password)
    except Customer.DoesNotExist:
        return Response({'error': 'Invalid email or password'}, status=400)

    serializer = Customerserializer(customer)
    response_data = {'message': 'login successful'}
    status_code = 200

    return Response(response_data, status=status_code)

#function based api
#to get the orders of the customer is by his email and password
#if not found it get 404 error "not found"
# Build a dictionary of product names and their quantities for each order
#to not dublicate products so the condition ahter the loop if found again add the quantity by one 
# i made it here in the code to retreive every product like in the home page by dtl
# then gate the sum of the price of one product by the quantity * price  
# then pass the result to response that convert it to json  
@api_view(['POST'])
def order_details(request):
    # Retrieve the customer by their email and password
    email = request.data.get('email')
    password = request.data.get('password')
    customer = get_object_or_404(Customer, email=email, password=password)

    # Retrieve the customer's orders
    orders = Order.objects.filter(customer=customer)
    
    # Build a dictionary of product names and their quantities for each order
    #to not dublicate products so the condition ahter the loop if found again add the quantity by one 
    # i made it here in the code to retreive every product like in the home page by dtl
    # then gate the sum of the price of one product by the quantity * price   
    order_details = [] #global empty for each time the api is send 
    for order in orders:
        product_quantities = {}
        for item in order.items.all():
            product_name = item.product.pname
            #to not dublicate products so the condition ahter the loop if found again add the quantity by one
            # i made it here in the code to retreive every product like in the home page by dtl
            if product_name in product_quantities:
                product_quantities[product_name] += item.pquantity
            else:
                product_quantities[product_name] = item.pquantity

        items = []
        # then the for loop is for to store the items detatils in items list
        for name, quantity in product_quantities.items():
            product = Product.objects.get(pname=name)
            # then get the sum of the price of one product by the quantity * price   
            item_total_price = product.pprice * quantity
            item_details = {
                'product_name': name,
                'product_price': str(product.pprice),
                'product_quantity': quantity,
                'item_total_price': str(item_total_price),
                
                
            }
            items.append(item_details)
        #at the end get the data that will send by the api 
        total_items = sum(product_quantities.values())
        #I made it like this because i convert it to string to be stored in the list 
        total_price = sum(float(item['item_total_price']) for item in items)
        order_details.append({
            'id': order.id,
            'total_items': total_items,
            'total_price': str(total_price),
            'items': items,
            'pdate_placed': str(order.pdate_placed),
        })

    return Response({'orders': order_details})






