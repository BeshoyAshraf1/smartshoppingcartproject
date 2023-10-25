from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from .models import Customer, Cart, Product, Order, OrderItem, OrderItemProduct,CartMembership
###read it at the end
# i play on the last order created on the cart beacause no one will use this cart except the user until finish shopping


#First I start from the welcome page that explain to the user how to use the cart
# when the customer enter the supermarket with the cart he will enter from the different gate but at that gate
# will be a rfid to make the cart return to welcome page     
def welcome(request):
    return render(request, 'pages/welcome.html')

#Second this pageforwarding  to scan the qrcode to login 
def befscan(request):
    # current_cart = Cart.objects.get(cartid=1,id=1)
    # print(current_cart)
    # if current_cart.rfid:
    #     return redirect('success')
    return render(request, 'pages/befscan.html')

#Third the scan page it scan the qrcode and decode it then send the result in a post request to the scan method 
#then Find the customer associated with the QR code or return an error message
#the user use any cart the system is on any cart but the customer will connect to the cart that he will use and 
#and here he will connected to the cart "1" or there is no cart 1 create cart "1" which is the first time to use the cart so it will create cart by itself
#then if the customer is not connected to it to create another cart membership of relation between the cart and customers one to many
#then create new order for the customer and then make the total weight and the rfid of the cart is 0 then  redirect to home page 
def scan(request):
    if request.method == 'POST':
        # Get the scanned QR code
        result = request.POST.get('scanned_result')
        # Find the customer associated with the QR code or return an error message
        try:
            customer = Customer.objects.get(password=result)
        except Customer.DoesNotExist:
             return redirect('error404')

        #just to know which cart used when he do shopping
        #Get the first cart object or create a new one if it doesn't exist
        cart, created = Cart.objects.get_or_create(cartid=1)

        # Check if the customer is already connected to the first cart
        if not CartMembership.objects.filter(customer=customer, cart=cart).exists():
            # Create a new CartMembership for the customer and the first cart
            membership = CartMembership.objects.create(customer=customer, cart=cart)


        # Create a new order for the customer
        order = Order.objects.create(cart=cart, customer=customer)

        #default values for rfid and tweight safarhom 0
        cart.tweight = 0
        cart.rfid = 0
        cart.save()
        #go to home page 
        return redirect('home')
    return render(request, 'pages/scan.html')

#fourth this method is used to check the rfid of the cart 1 and id 1 and send the values in json to home page each 1 sec 
#if the rfid = true to go to success page 
def check_rfid(request):
    #get the cart with id 1 and cart 1
    current_cart = Cart.objects.get(cartid=1, id=1)
    #make context -> data  to be return the result of the rfid  
    data = {'rfid': current_cart.rfid}
    #convert it in json
    return JsonResponse(data)

#fifth check weight method is used to check the weight of the products and send the results to home 
#if it is (added or not) (add another product with different weight)
#first get the current cart that the user use which is cart 1 and id 1 then get the rfid result
#then initailize 2 variables MAX_WEIGHT_DIFFERENCE and MIN_WEIGHT_DIFFERENCE = 10 
#then the condition is if the difference between them is more than 10 and less than 10 or equal each other to send true to the home page 
#else false to  forward to alert page and
#then the customer press go to home page so he has 10 seconds to add thew product or remove it from the cart
def check_weight(request):
    current_cart = Cart.objects.get(cartid=1, id=1)
    rfid = current_cart.rfid
    #dfine max weight difference to 10 
    MAX_WEIGHT_DIFFERENCE = 10
    MIN_WEIGHT_DIFFERENCE = 10
    #get the last order created
    last_order = Order.objects.last()
    #if the difference between them is more than 10 and less than 10 or equal each other to send true to the home page to forward to alert page and 
    #then the customer press go to home page so he has 10 seconds to add thew product or remove it from the cart
    if abs(last_order.ptotal_weight - current_cart.tweight) < MAX_WEIGHT_DIFFERENCE and abs(last_order.ptotal_weight - current_cart.tweight) > MIN_WEIGHT_DIFFERENCE or last_order.ptotal_weight == current_cart.tweight:
     #make context -> data  to be return the result of the weight   
     data = {'weight': True } #true
     #convert it in json
     return JsonResponse(data)
    else :    
     #make context -> data  to be return the result of the weight   
     data = {'weight': False }
     #convert it in json
     return JsonResponse(data)
    return JsonResponse(data)

# home page is used to display the all the products and offers and enable the customer to add product or remove product
# display the context of that the home page needs
# if the user in data page select add product then there is a post request send to the the home method with the serial no of the product want to add
# after check the post request ,receive the serial no , if there is serial no received and remove product not in the request 
# get the product that has the same serial no of the product that recieved
# then create new order item to connect the product with the order and add the price and productquantity
# then create order item prouct to connect the order item and product together
# i made 2 tables for connecton the second order item is because connection "1 to many" and add more information about the product 
# then connect it to the order item product and product relation "1 to many"
# each time the customer adds product to the cart it subrtact one from quantity in stock then save it 
# then send the context tp home page
def home(request):

    # Get the last order
    last_order = Order.objects.last()
    # Query all the order items associated with the last order
    #filter -> get query
    #get -> get one object
    order_items = OrderItem.objects.filter(order=last_order)

    # Use a dictionary to keep track of the products seen 
    product_dict = {}
    filtered_order_items = []

    #for loop to loop on the items in the query of order_items 
    for order_item in order_items:
        #then each time get the serial no of the product of the orderitem in the last order
        product_serial_no = order_item.product.pserialno
        # check if the order item in the in the product dictionary or not
        # if not it adds the product serial no to the dictionary and add true to the key of product serialno
        # and add the order item to the filterd list   
        if product_serial_no not in product_dict:
            # If the product has not been seen before, add it to the dictionary and the filtered list
            #we use it to check every time the product in the dictionary or not
            product_dict[product_serial_no] = True
            #to print the orders that we filltered to prevent duplicate products to be displayed 
            filtered_order_items.append(order_item)
            #else it loops on the filtered order items  
            # if it finds the first order item in the filtered list that has the same serial number and increments its quantity by one.
        else:
            # If the product has been seen before, increment the quantity of the first order item with the same serial number
            for item in filtered_order_items:
                if item.product.pserialno == product_serial_no:
                    item.pquantity += 1
                    break
    #then it make the context  to pass it to the home page 
    context = {
        'lastorderprice': last_order.ptotal_price,
        'lastorderitems': last_order.ptotal_items,
        'order_items': filtered_order_items,
    }


    # if the user in data page select add product then there is a post request send to the the home method with the serial no of the product want to add
    # after check the post request ,receive the serial no , if there is serial no received and remove product not in the request 
    # get the product that has the same serial no of the product that recieved
    # then create new order item to connect the product with the order and add the price and productquantity
    # then create order item prouct to connect the order item and product together
    # i made 2 tables for connecton the second order item is because connection "1 to many" and add more information about the product 
    # then connect it to the order item product and product relation "1 to many"
    # each time the customer adds product to the cart it subrtact one from quantity in stock then save it 
    # then send the context tp home page
    if request.method == 'POST': # receive the post request
        serial_no = request.POST.get('product_serial_no')
        if serial_no:
            if 'remove_product' not in request.POST:
                product = Product.objects.get(pserialno=serial_no)
                # Subtract 1 from quantity_in_stock of the associated Product
                product.quantity_in_stock -= 1
                product.save()
                order_item = OrderItem.objects.create(
                    order=last_order,
                    product=product,
                    pprice_of_pro=product.pprice,
                    pquantity=1
                )
                OrderItemProduct.objects.create(order_item=order_item, product=product)



        
            # Update the ptotal_items and ptotal_price of the order
            #by using update totals method that found in the models.py
            order = Order.objects.get(id=last_order.id)
            order.update_totals()

            # """"""this part is written again beacuase in some conditions the redirect to it must pass the context """"""""
             
            # Retrieve the updated order information
            last_order = Order.objects.get(id=last_order.id)
            order_items = OrderItem.objects.filter(order=last_order)

            # Use a dictionary to keep track of the products seen 
            product_dict = {}
            filtered_order_items = []
            #for loop to loop on the items in the query of order_items 
            for order_item in order_items:
                #then each time get the serial no of the product of the orderitem in the last order
                product_serial_no = order_item.product.pserialno
                # check if the order item in the in the product dictionary or not
                # if not it adds the product serial no to the dictionary and add true to the key of product serialno
                # and add the order item to the filterd list   
                if product_serial_no not in product_dict:
                    # If the product has not been seen before, add it to the dictionary and the filtered list
                    #we use it to check every time the product in the dictionary or not
                    product_dict[product_serial_no] = True
                    #to print the orders that we filltered to prevent duplicate products to be displayed 
                    filtered_order_items.append(order_item)
                    #else it loops on the filtered order items  
                    # if it finds the first order item in the filtered list that has the same serial number and increments its quantity by one.
                else:
                    # If the product has been seen before, increment the quantity of the first order item with the same serial number
                    for item in filtered_order_items:
                        if item.product.pserialno == product_serial_no:
                            item.pquantity += 1
                            break
            #then it make the context  to pass it to the home page 
            context = {
                'lastorderprice': last_order.ptotal_price,
                'lastorderitems': last_order.ptotal_items,
                'order_items': filtered_order_items,
            }

    return render(request, 'pages/home.html', context=context)

# add product method receive post request with the scanned result 
#then check if this qrcode match any product in system 
# if true pass the product to the data method  in redirect we pass the context like this **context
#if flase redirect to error 404
def addproduct(request):
    # current_cart = Cart.objects.get(cartid=1,id=1)
    # print(current_cart)
    # if current_cart.rfid:
    #     return redirect('success')

    # add product method receive post request with the scanned result 
    if request.method == 'POST':
        result = request.POST.get('scanned_result')
        my_model_objects = Product.objects.filter(pserialno=result)
        #then check if this qrcode match any product in system 
        # if true pass the product to the data  in redirect we pass the context like this **context
        if my_model_objects.exists():
            context = {'pserialno': result}
            return redirect('data', **context)
        else:
            #if false redirect to error 404
            return redirect('error404')
    return render(request, 'pages/addproduct.html')

# data method is used to display the product data
#in the data page if the user choose add product it will go to home page to add the product
#else it will go to home page without post request which means will not need to add any thing and the part 1 in the code only will works
def data(request, pserialno):
    # current_cart = Cart.objects.get(cartid=1,id=1)
    # print(current_cart)
    # if current_cart.rfid:
    #     return redirect('success')
    #match the the result with the product serial no 
    product = Product.objects.get(pserialno=pserialno)
    #pass it to the data page
    context = {'product': product}
    return render(request, 'pages/data.html', context)

#in the remove method it delete the product 
#first get the post request that has the scanned result
# then match the serial no of the product with the last order  products of order items 
#if not found wich means it is not found in the system 
#thenif it si found then delete the order item and order item product the data of that produyt in them and the connection
# and increamnt the quantity of stock by one 
# then use the update mehtod to update totals in the order
# then do the same sequence of code to get the context then pass it to the home page  
def removeproduct(request):
    # current_cart = Cart.objects.get(cartid=1,id=1)
    # print(current_cart)
    # if current_cart.rfid:
    #     return redirect('success')


    if request.method == 'POST':
        result = request.POST.get('scanned_result')
        product = Product.objects.get(pserialno=result)

        # Retrieve the last OrderItem object with the scanned serial number
        order_item = OrderItem.objects.filter(product__pserialno=result).last()

        if not order_item:
            return HttpResponse("The product is not in your order items")

        # Delete the OrderItem and its associated OrderItemProduct
        order_item.order_item_products.all().delete()
        order_item.delete()

        # Increment the quantity_in_stock of the associated Product
        product.quantity_in_stock += 1
        product.save()
        
        # Update the ptotal_items and ptotal_price of the order
        order = Order.objects.get(id=order_item.order.id)
        order.update_totals()

        # Retrieve the updated order information
        last_order = Order.objects.last()
        order_items = OrderItem.objects.filter(order=last_order)

        # Use a dictionary to keep track of the products seen so far
        product_dict = {}
        filtered_order_items = []

        for order_item in order_items:
            product_serial_no = order_item.product.pserialno
            if product_serial_no not in product_dict:
                # If the product has not been seen before, add it to the dictionary and the filtered list
                product_dict[product_serial_no] = True
                filtered_order_items.append(order_item)
            else:
                # If the product has been seen before, increment the quantity of the first order item with the same serial number
                for item in filtered_order_items:
                    if item.product.pserialno == product_serial_no:
                        item.pquantity += 1
                        # Recalculate the product price based on the updated quantity
                        item.pprice_of_pro = item.product.pprice * item.pquantity
                        break

        context = {
            'lastorderprice': last_order.ptotal_price,
            'lastorderitems': last_order.ptotal_items,
            'order_items': filtered_order_items,
        }

        return render(request, 'pages/home.html', context=context)

    return render(request, 'pages/removeproduct.html')

#in the search method we receive post request with the category and product name 
# then try to match the product by name 
#if found it pass it to search page to display the data of the product by context
# if productdoesnot exist = false return the product not found
def search(request):
    # current_cart = Cart.objects.get(cartid=1,id=1)
    # print(current_cart)
    # if current_cart.rfid:
    #     return redirect('success')

    if request.method == 'POST':
        #receive the category and products that the the user choose from the dynamic list in the search part 
        category = request.POST.get('Category')
        product = request.POST.get('ProductSearch')
        # Use the selected category and product to perform a search
        # fillter -> Queryset
        # get -> one object
        # "stack over flow" we removed (if - else) because the get() method raises a Product.DoesNotExist exception if no object is found.
        try:
            my_model_objects = Product.objects.get(pname=product) # search by product pname that received from the javascript code of dynamic list 
        except Product.DoesNotExist:
            return HttpResponse('This product is not Found , Please return to Home Page ')
    print(my_model_objects.pbrand)
    context = {'products': my_model_objects}
    return render(request, 'pages/search.html', context)

#display the alert page each 10 second if there is any thing wrong in the weight of the cart 
def alert(request):
    return render(request, 'pages/alert.html')

#display error 404 page
def error404(request):
    return render(request, 'pages/404.html')

#when the rfid = true it display the success page and 
# if when it still refresh it self every one sec when it comes false
#  go to welcome page to reuse the cart
def success(request):
    current_cart = Cart.objects.get(cartid=1, id=1)
    if current_cart.rfid == False:
        return redirect('welcome')
    return render(request, 'pages/success.html')


