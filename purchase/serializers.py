from rest_framework import serializers
from django.db import transaction
from itertools import product
from purchase.models import *
from itertools import product as cartesian_product






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

import uuid
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    PurchaseOrder, PurchaseItem, Supplier, SupplierLedger, PurchasePayment,
    VariantType, CashMonitor, BankPaymentsMonitor, Product
)
from .serializers import SupplierSerializer, ProductSerializer, PurchasePaymentSerializer


# class PurchaseOrderSerializer(serializers.Serializer):
#     supplier = SupplierSerializer()
#     products = ProductSerializer(many=True)
#     payment = PurchasePaymentSerializer()

#     def create(self, validated_data):
#         request = self.context['request']
#         user = request.user
#         company = user.company
#         branch = user.branch

#         supplier_data = validated_data.pop('supplier')
#         products_data = validated_data.pop('products')
#         payment_data = validated_data.pop('payment')

#         # Get or create supplier
#         supplier, created = Supplier.objects.get_or_create(
#             name=supplier_data['name'],
#             contact=supplier_data['contact'],
#             defaults={
#                 'user': user,
#                 'company': company,
#                 'branch': branch
#             }
#         )

#         # Create purchase order
#         purchase_order = PurchaseOrder.objects.create(
#             purchase_order_id=f"PO-{uuid.uuid4().hex[:6].upper()}",
#             supplier=supplier,
#             user=user,
#             company=company,
#             branch=branch,
#             total_price=0
#         )

#         total_price = 0

#         # Create purchase items
#         for product_data in products_data:
#             product = Product.objects.create(
#                 name=product_data['name'],
#                 description='N/A',
#                 user=user,
#                 company=company,
#                 branch=branch,
#             )

#             item_data = product_data['items']
#             quantity = item_data['quantity']
#             unit_price = item_data['unit_price']
#             item_total = quantity * unit_price
#             total_price += item_total

#             purchase_item = PurchaseItem.objects.create(
#                 order=purchase_order,
#                 product=product,
#                 quantity=quantity,
#                 unit_price=unit_price,
#                 total_price=item_total,
#                 has_variant=item_data.get('has_variant', False),
#                 user=user,
#                 company=company,
#                 branch=branch,
#             )

#             if purchase_item.has_variant:
#                 for variant_data in item_data.get('variant_types', []):
#                     options = variant_data['options']
#                     if isinstance(options, list):
#                         options = ', '.join(options)
#                     VariantType.objects.create(
#                         title=variant_data['title'],
#                         options=options,
#                         purchase_item=purchase_item,
#                         purchase_item_name=product.name,
#                         user=user,
#                         company=company,
#                         branch=branch,
#                     )

#         purchase_order.total_price = total_price
#         purchase_order.save()

#         # Supplier Ledger - Credit
#         SupplierLedger.objects.create(
#             supplier=supplier,
#             transaction_type="Credit",
#             reference_purchase_order=purchase_order,
#             credit_amount=total_price,
#             company=company,
#         )

#         # Create payment
#         cash_paid = float(payment_data.get('cash_paid', 0))
#         bank_paid = float(payment_data.get('bank_paid', 0))
#         total_paid = cash_paid + bank_paid

#         payment = PurchasePayment.objects.create(
#             order=purchase_order,
#             payment_type=payment_data['payment_type'],
#             cash_paid=cash_paid,
#             bank_paid=bank_paid,
#             total_paid=total_paid,
#             user=user,
#             company=company,
#             branch=branch,
#             supplier=supplier
#         )

#         # Supplier Ledger - Debit
#         SupplierLedger.objects.create(
#             supplier=supplier,
#             transaction_type="Debit",
#             reference_payment=payment,
#             debit_amount=total_paid,
#             company=company
#         )

#         # Monitor cash/bank payment
#         payment_type = payment_data['payment_type'].lower()
#         payment_ct = ContentType.objects.get_for_model(PurchasePayment)
#         notes = f"Payment for Purchase Order {purchase_order.purchase_order_id}"

#         if payment_type == "cash":
#             if cash_paid > 0:
#                 try:
#                     CashMonitor.objects.create(
#                         branch=branch,
#                         transaction_type="Debit",
#                         amount=cash_paid,
#                         notes=notes,
#                         content_type=payment_ct,
#                         object_id=payment.id,
#                         user=user,
#                         company=company
#                     )
#                 except Exception as e:
#                     print("Error creating CashMonitor:", e)

#         elif payment_type == "bank":
#             if bank_paid > 0:
#                 try:
#                     BankPaymentsMonitor.objects.create(
#                         branch=branch,
#                         to_branch=None,
#                         transaction_type="Debit",
#                         amount=bank_paid,
#                         notes=notes,
#                         content_type=payment_ct,
#                         object_id=payment.id,
#                         user=user,
#                         company=company
#                     )
#                 except Exception as e:
#                     print("Error creating BankPaymentsMonitor:", e)

#         elif payment_type == "mixed":
#             if cash_paid > 0:
#                 try:
#                     CashMonitor.objects.create(
#                         branch=branch,
#                         transaction_type="Debit",
#                         amount=cash_paid,
#                         notes=notes,
#                         content_type=payment_ct,
#                         object_id=payment.id,
#                         user=user,
#                         company=company
#                     )
#                 except Exception as e:
#                     print("Error creating CashMonitor (mixed):", e)

#             if bank_paid > 0:
#                 try:
#                     BankPaymentsMonitor.objects.create(
#                         branch=branch,
#                         to_branch=None,
#                         transaction_type="Debit",
#                         amount=bank_paid,
#                         notes=notes,
#                         content_type=payment_ct,
#                         object_id=payment.id,
#                         user=user,
#                         company=company
#                     )
#                 except Exception as e:
#                     print("Error creating BankPaymentsMonitor (mixed):", e)

#         # Debugging logs
#         print("Total Price:", total_price)
#         print("Cash Paid:", cash_paid)
#         print("Bank Paid:", bank_paid)
#         print("Created CashMonitor count:", CashMonitor.objects.count())
#         print("Created BankPaymentsMonitor count:", BankPaymentsMonitor.objects.count())

#         return purchase_order
# class PurchaseItemSerializer(serializers.Serializer):
#     quantity     = serializers.IntegerField(min_value=1)
#     unit_price   = serializers.DecimalField(max_digits=10, decimal_places=2)
#     has_variant  = serializers.BooleanField(default=False)
#     # incoming: list of { id?, title, options: [ { id?, name}, ... ] }
#     variant_types = serializers.ListField(child=serializers.DictField(), required=False)

#     def create(self, validated_data):
#         """
#         This method is not directly used; PurchaseOrderSerializer.create()
#         handles item creation. We include it to satisfy DRF structure.
#         """
#         return validated_data


# class PurchaseOrderSerializer(serializers.Serializer):
#     supplier = SupplierSerializer()
#     products = serializers.ListField(child=serializers.DictField())
#     payment  = PurchasePaymentSerializer()

#     def create(self, validated_data):
#         request      = self.context['request']
#         user         = request.user
#         company      = user.company
#         branch       = user.branch

#         supplier_data = validated_data.pop('supplier')
#         products_data = validated_data.pop('products')
#         payment_data  = validated_data.pop('payment')

#         with transaction.atomic():
#             # 1) Supplier
#             supplier, _ = Supplier.objects.get_or_create(
#                 name    = supplier_data['name'],
#                 contact = supplier_data['contact'],
#                 defaults={
#                     'user':   user,
#                     'company':company,
#                     'branch': branch
#                 }
#             )

#             # 2) PurchaseOrder
#             purchase_order = PurchaseOrder.objects.create(
#                 purchase_order_id = f"PO-{uuid.uuid4().hex[:6].upper()}",
#                 supplier          = supplier,
#                 user              = user,
#                 company           = company,
#                 branch            = branch,
#                 total_price       = 0
#             )

#             total_price = 0

#             # 3) Items + Variants + Combinations
#             for prod in products_data:
#                 # create the Product record
#                 product = Product.objects.create(
#                     name        = prod['name'],
#                     description = prod.get('description', 'N/A'),
#                     user        = user,
#                     company     = company,
#                     branch      = branch
#                 )

#                 item_data = prod['items']
#                 qty       = item_data['quantity']
#                 up        = item_data['unit_price']
#                 line_total= qty * up
#                 total_price += line_total

#                 purchase_item = PurchaseItem.objects.create(
#                     order       = purchase_order,
#                     product     = product,
#                     quantity    = qty,
#                     unit_price  = up,
#                     total_price = line_total,
#                     has_variant = item_data.get('has_variant', False),
#                     user        = user,
#                     company     = company,
#                     branch      = branch
#                 )

#                 # handle variant_types M2M
#                 variant_defs = item_data.get('variant_types', [])
#                 all_option_lists = []  # for combinations

#                 for vt in variant_defs:
#                     # either use existing VariantType by id, or get/create by title
#                     if vt.get('id'):
#                         variant_type = VariantType.objects.get(pk=vt['id'])
#                     else:
#                         variant_type, _ = VariantType.objects.get_or_create(
#                             title   = vt['title'],
#                             defaults={
#                                 'user':    user,
#                                 'company': company,
#                                 'branch':  branch
#                             }
#                         )
#                     purchase_item.variant_types.add(variant_type)

#                     # ensure each VariantOption exists
#                     opts_for_type = []
#                     for o in vt.get('options', []):
#                         if o.get('id'):
#                             option = VariantOption.objects.get(pk=o['id'])
#                         else:
#                             option, _ = VariantOption.objects.get_or_create(
#                                 variant_type = variant_type,
#                                 name         = o['name']
#                             )
#                         opts_for_type.append(option)
#                     all_option_lists.append(opts_for_type)

#                 # create cartesian product of options
#                 for combo in product(*all_option_lists):
#                     # build a readable map for response
#                     vc = VariantCombination.objects.create(
#                         purchase_item = purchase_item,
#                         quantity      = purchase_item.quantity,
#                         sku           = f"{purchase_item.id}-{'-'.join(str(opt.id) for opt in combo)}"
#                     )
#                     vc.options.add(*combo)

#             # 4) update order total
#             purchase_order.total_price = total_price
#             purchase_order.save()

#             # 5) Supplier Ledger – Credit
#             SupplierLedger.objects.create(
#                 supplier                = supplier,
#                 transaction_type        = "Credit",
#                 reference_purchase_order= purchase_order,
#                 credit_amount           = total_price,
#                 company                 = company,
#                 user                    = user
#             )

#             # 6) PurchasePayment + Supplier Ledger Debit
#             cash_paid = float(payment_data.get('cash_paid', 0))
#             bank_paid = float(payment_data.get('bank_paid', 0))
#             total_paid= cash_paid + bank_paid

#             payment = PurchasePayment.objects.create(
#                 order       = purchase_order,
#                 payment_type= payment_data['payment_type'],
#                 cash_paid   = cash_paid,
#                 bank_paid   = bank_paid,
#                 total_paid  = total_paid,
#                 user        = user,
#                 company     = company,
#                 branch      = branch,
#                 supplier    = supplier
#             )

#             SupplierLedger.objects.create(
#                 supplier         = supplier,
#                 transaction_type = "Debit",
#                 reference_payment= payment,
#                 debit_amount     = total_paid,
#                 company          = company,
#                 user             = user
#             )

#             # 7) Cash / Bank Monitoring
#             pt_lower = payment.payment_type.lower()
#             ct       = ContentType.objects.get_for_model(PurchasePayment)
#             notes    = f"Payment for PurchaseOrder {purchase_order.purchase_order_id}"

#             if pt_lower == "cash" and cash_paid > 0:
#                 CashMonitor.objects.create(
#                     branch       = branch,
#                     transaction_type = "Debit",
#                     amount       = cash_paid,
#                     notes        = notes,
#                     content_type = ct,
#                     object_id    = payment.id,
#                     user         = user,
#                     company      = company
#                 )
#             elif pt_lower == "bank" and bank_paid > 0:
#                 BankPaymentsMonitor.objects.create(
#                     branch        = branch,
#                     to_branch     = None,
#                     transaction_type = "Debit",
#                     amount        = bank_paid,
#                     notes         = notes,
#                     content_type  = ct,
#                     object_id     = payment.id,
#                     user          = user,
#                     company       = company
#                 )
#             elif pt_lower == "mixed":
#                 if cash_paid > 0:
#                     CashMonitor.objects.create(
#                         branch       = branch,
#                         transaction_type = "Debit",
#                         amount       = cash_paid,
#                         notes        = notes + " (Cash)",
#                         content_type = ct,
#                         object_id    = payment.id,
#                         user         = user,
#                         company      = company
#                     )
#                 if bank_paid > 0:
#                     BankPaymentsMonitor.objects.create(
#                         branch        = branch,
#                         to_branch     = None,
#                         transaction_type = "Debit",
#                         amount        = bank_paid,
#                         notes         = notes + " (Bank)",
#                         content_type  = ct,
#                         object_id     = payment.id,
#                         user          = user,
#                         company       = company
#                     )

#         return purchase_order



class PurchaseOrderSerializer(serializers.Serializer):
    supplier = SupplierSerializer()
    products = serializers.ListField(child=serializers.DictField())
    payment  = PurchasePaymentSerializer()

    def create(self, validated_data):
        request       = self.context['request']
        user          = request.user
        company       = user.company
        branch        = user.branch

        supplier_data = validated_data.pop('supplier')
        products_data = validated_data.pop('products')
        payment_data  = validated_data.pop('payment')

        with transaction.atomic():
            # 1) Supplier
            supplier, _ = Supplier.objects.get_or_create(
                name    = supplier_data['name'],
                contact = supplier_data['contact'],
                defaults={
                    'user':    user,
                    'company': company,
                    'branch':  branch
                }
            )

            # 2) PurchaseOrder
            purchase_order = PurchaseOrder.objects.create(
                purchase_order_id = f"PO-{uuid.uuid4().hex[:6].upper()}",
                supplier          = supplier,
                user              = user,
                company           = company,
                branch            = branch,
                total_price       = 0
            )

            total_price = 0

            # 3) Items + Variants + Combinations
            for prod in products_data:
                # create Product record
                product = Product.objects.create(
                    name        = prod['name'],
                    description = prod.get('description', 'N/A'),
                    user        = user,
                    company     = company,
                    branch      = branch
                )

                item_data = prod['items']
                qty       = item_data['quantity']
                up        = item_data['unit_price']
                line_total= qty * up
                total_price += line_total

                purchase_item = PurchaseItem.objects.create(
                    order       = purchase_order,
                    product     = product,
                    quantity    = qty,
                    unit_price  = up,
                    total_price = line_total,
                    has_variant = item_data.get('has_variant', False),
                    user        = user,
                    company     = company,
                    branch      = branch
                )

                # collect option‐lists for the cartesian product
                all_option_lists = []
                for vt in item_data.get('variant_types', []):
                    title = vt['title']

                    # lookup‐or‐create VariantType safely
                    qs_vt = VariantType.objects.filter(
                        title   = title,
                        company = company,
                        branch  = branch
                    )
                    variant_type = None
                    if vt.get('id'):
                        variant_type = qs_vt.filter(pk=vt['id']).first()
                    if not variant_type:
                        variant_type = qs_vt.first()
                    if not variant_type:
                        variant_type = VariantType.objects.create(
                            title   = title,
                            user    = user,
                            company = company,
                            branch  = branch
                        )
                    purchase_item.variant_types.add(variant_type)

                    # ensure VariantOption exists
                    opts_for_type = []
                    for o in vt.get('options', []):
                        name = o.get('name')
                        qs_opt = VariantOption.objects.filter(
                            variant_type = variant_type,
                            name         = name
                        )
                        option = None
                        if o.get('id'):
                            option = qs_opt.filter(pk=o['id']).first()
                        if not option:
                            option = qs_opt.first()
                        if not option:
                            option = VariantOption.objects.create(
                                variant_type = variant_type,
                                name         = name
                            )
                        opts_for_type.append(option)

                    all_option_lists.append(opts_for_type)

                # **use the aliased cartesian_product()** here
                for combo in cartesian_product(*all_option_lists):
                    vc = VariantCombination.objects.create(
                        purchase_item = purchase_item,
                        quantity      = purchase_item.quantity,
                        sku           = f"{purchase_item.id}-" +
                                        "-".join(str(opt.id) for opt in combo)
                    )
                    vc.options.add(*combo)

            # 4) finalize PurchaseOrder total
            purchase_order.total_price = total_price
            purchase_order.save()

            # 5) SupplierLedger Credit entry
            SupplierLedger.objects.create(
                supplier                 = supplier,
                transaction_type         = "Credit",
                reference_purchase_order = purchase_order,
                credit_amount            = total_price,
                company                  = company,
                user                     = user
            )

            # 6) Create PurchasePayment & SupplierLedger Debit
            cash_paid = float(payment_data.get('cash_paid', 0))
            bank_paid = float(payment_data.get('bank_paid', 0))
            total_paid= cash_paid + bank_paid

            payment = PurchasePayment.objects.create(
                order        = purchase_order,
                payment_type = payment_data['payment_type'],
                cash_paid    = cash_paid,
                bank_paid    = bank_paid,
                total_paid   = total_paid,
                user         = user,
                company      = company,
                branch       = branch,
                supplier     = supplier
            )

            SupplierLedger.objects.create(
                supplier          = supplier,
                transaction_type  = "Debit",
                reference_payment = payment,
                debit_amount      = total_paid,
                company           = company,
                user              = user
            )

            # 7) Cash / Bank monitoring entries
            pt_lower = payment.payment_type.lower()
            ct       = ContentType.objects.get_for_model(PurchasePayment)
            notes    = f"Payment for PurchaseOrder {purchase_order.purchase_order_id}"

            if pt_lower == "cash" and cash_paid > 0:
                CashMonitor.objects.create(
                    branch            = branch,
                    transaction_type = "Debit",
                    amount            = cash_paid,
                    notes             = notes,
                    content_type      = ct,
                    object_id         = payment.id,
                    user              = user,
                    company           = company
                )
            elif pt_lower == "bank" and bank_paid > 0:
                BankPaymentsMonitor.objects.create(
                    branch            = branch,
                    to_branch         = None,
                    transaction_type = "Debit",
                    amount            = bank_paid,
                    notes             = notes,
                    content_type      = ct,
                    object_id         = payment.id,
                    user              = user,
                    company           = company
                )
            elif pt_lower == "mixed":
                if cash_paid > 0:
                    CashMonitor.objects.create(
                        branch            = branch,
                        transaction_type = "Debit",
                        amount            = cash_paid,
                        notes             = notes + " (Cash)",
                        content_type      = ct,
                        object_id         = payment.id,
                        user              = user,
                        company           = company
                    )
                if bank_paid > 0:
                    BankPaymentsMonitor.objects.create(
                        branch            = branch,
                        to_branch         = None,
                        transaction_type = "Debit",
                        amount            = bank_paid,
                        notes             = notes + " (Bank)",
                        content_type      = ct,
                        object_id         = payment.id,
                        user              = user,
                        company           = company
                    )

        return purchase_order
