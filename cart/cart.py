from store.models import Product

class Cart:
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        self.cart = self.session.get('cart', {})
        if 'cart' not in self.session:
            self.session['cart'] = self.cart

    def add(self, product, quantity=1):
        """Add a product to the cart or update its quantity."""
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {'quantity': quantity, 'price': str(product.price)}
        self.save()

    def remove(self, product):
        """Remove a product from the cart."""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.save()

    def save(self):
        """Save the cart to the session."""
        self.session['cart'] = self.cart
        self.session.modified = True

    def __iter__(self):
        """Iterate over the items in the cart and get their data from the database."""
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            yield {
                'product': item['product'],
                'quantity': item['quantity'],
                'price': float(item['price']),
                'total_price': item['quantity'] * float(item['price']),
            }

    def get_total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(item['quantity'] * float(item['price']) for item in self)
