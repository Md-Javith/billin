from rest_framework import serializers
from django.db import transaction
from itertools import product
from purchase.models import *





class VariantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantType
        fields = ['title', 'options', 'user', 'company', 'branch']
class PurchaseItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    has_variant = serializers.BooleanField()
    variant_types = VariantTypeSerializer(many=True, required=False)



class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    items = PurchaseItemSerializer()



class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['name', 'contact']





class PurchasePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePayment
        fields = ['payment_type', 'cash_paid', 'bank_paid']


import uuid

class PurchaseOrderSerializer(serializers.Serializer):
    supplier = SupplierSerializer()
    products = ProductSerializer(many=True)
    payment = PurchasePaymentSerializer()

    def create(self, validated_data):
        request = self.context['request']
        user = request.user
        company = user.company
        branch = user.branch

        supplier_data = validated_data.pop('supplier')
        products_data = validated_data.pop('products')
        payment_data = validated_data.pop('payment')

        supplier, created = Supplier.objects.get_or_create(
            name=supplier_data['name'],
            contact=supplier_data['contact'],
            defaults={
                'user': user,
                'company': company,
                'branch': branch
            }
        )

        purchase_order = PurchaseOrder.objects.create(
            purchase_order_id=f"PO-{uuid.uuid4().hex[:6].upper()}",
            supplier=supplier,
            user=user,
            company=company,
            branch=branch,
            total_price=0
        )

        total_price = 0

        for product_data in products_data:
            product = Product.objects.create(
                name=product_data['name'],
                description='N/A',
                user=user,
                company=company,
                branch=branch,
            )

            item_data = product_data['items']
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            item_total = quantity * unit_price
            total_price += item_total

            purchase_item = PurchaseItem.objects.create(
                order=purchase_order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=item_total,
                has_variant=item_data.get('has_variant', False),
                user=user,
                company=company,
                branch=branch,
            )

            if purchase_item.has_variant:
                for variant_data in item_data.get('variant_types', []):
                    options = variant_data['options']
                    if isinstance(options, list):
                        options = ', '.join(options)
                    VariantType.objects.create(
                        title=variant_data['title'],
                        options=options,
                        purchase_item=purchase_item,
                        purchase_item_name=product.name,
                        user=user,
                        company=company,
                        branch=branch,
                    )

        purchase_order.total_price = total_price
        purchase_order.save()

        total_paid = payment_data['cash_paid'] + payment_data['bank_paid']
        PurchasePayment.objects.create(
            order=purchase_order,
            payment_type=payment_data['payment_type'],
            cash_paid=payment_data['cash_paid'],
            bank_paid=payment_data['bank_paid'],
            total_paid=total_paid,
            user=user,
            company=company,
            branch=branch,
            supplier=supplier
        )

        return purchase_order
