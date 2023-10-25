from django.db import models

# Create your models here.


# Define the Customers table
class Customer(models.Model):
    fname = models.CharField(max_length=50)
    lname = models.CharField(max_length=50)
    email = models.EmailField()
    password = models.CharField(max_length=50)
    cardno = models.CharField(max_length=50)
    cvc = models.CharField(max_length=50)
    expdate = models.DateField()


# Define the Products table
class Product(models.Model):
    categorychoices=[('Dairy Products','Dairy Products'),('Meat','Meat'),('Seafood','Seafood'),('Other Products','Other Products'),('Bakery Products','Bakery Products'),('Frozen Foods','Frozen Foods'),('Beverages','Beverages'),('Snacks and Confectionery','Snacks and Confectionery'),]
    categorylocation=[('1A','1A'),('2A','2A'),('3A','3A'),('1B','1B'),('2B','2B'),('3B','3B'),('1D','1D'),('2D','2D'),('3D','3D'),]
    pname = models.CharField(max_length=50)
    pdescription = models.TextField()
    pprice = models.DecimalField(max_digits=10, decimal_places=2)
    pserialno = models.IntegerField()
    pexpdate = models.DateField()
    pbrand = models.CharField(max_length=50,null=True)
    pimage = models.ImageField()
    pweight = models.IntegerField()
    poffer = models.IntegerField()
    pofferimg = models.ImageField(null=True,blank=True)
    pcategory = models.CharField(max_length=50,null=True,blank=True,choices=categorychoices)
    plocation = models.CharField(max_length=50,null=True,blank=True,choices=categorylocation)
    quantity_in_stock = models.PositiveIntegerField(null=True)


# Define the Carts table
class Cart(models.Model):
    # customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart',null=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='cart',null=True)
    # customers = models.ManyToManyField(Customer)
    cartid = models.IntegerField(null=True)
    tweight = models.IntegerField(null=True,default=0)
    rfid = models.BooleanField(null=True)



class CartMembership(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,related_name='customerscart')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name='cartcustomers')


# Define the Orders table
class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders',null=True)
    ptotal_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ptotal_items = models.PositiveIntegerField(default=0)
    pdate_placed = models.DateTimeField(auto_now_add=True)
    ptotal_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    
    #method update totals is used 
    #this method pass to it the order that we use 
    # it get the order items of that order 
    # and calculate  the totals again    
    def update_totals(self):
        order_items = self.items.all()
        total_weight = 0
        total_items = 0
        total_price = 0
        for item in order_items:
            total_weight += item.product.pweight * item.pquantity
            total_items += item.pquantity
            total_price += item.pprice_of_pro * item.pquantity
        self.ptotal_weight = total_weight
        self.ptotal_items = total_items
        self.ptotal_price = total_price
        self.save()

        

# Define the Order items table
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    pquantity = models.PositiveIntegerField()
    pprice_of_pro = models.DecimalField(max_digits=10, decimal_places=2)

    # def save(self, *args, **kwargs):
    #     # Call the superclass save method to save the OrderItem object
    #     # super is a built in 
    #     super().save(*args, **kwargs)

    #     # Update the total price and total items of the order
    #     self.order.update_totals()

    #     # Update the order's total weight by adding the weight of the added product quantity
    #     self.order.ptotal_weight += self.product.pweight * self.pquantity

    #     # Save the updated order object
    #     self.order.save()

    # def delete(self, *args, **kwargs):
    #     # Save a reference to the associated order before deleting the order item
    #     order = self.order

    #     # Call the superclass delete method to delete the order item object
    #     super().delete(*args, **kwargs)

    #     # Subtract the weight of the deleted product quantity from the order's total weight
    #     order.ptotal_weight -= self.product.pweight * self.pquantity

    #     # Save the updated order object
    #     order.save()

    #     # Update the total price and total items of the updated order
    #     order.update_totals()


# Define the intermediate table for the many-to-many relationship between Products and Order items
class OrderItemProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='order_item_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_item_products')


