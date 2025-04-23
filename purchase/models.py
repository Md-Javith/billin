
# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from core.models import *
import uuid
from django.utils.timezone import now
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
def generate_po_id():
    return f"PO-{uuid.uuid4().hex[:6].upper()}"
class CashMonitor(models.Model):
    notes = models.TextField(max_length=255)
    transaction_type = models.CharField(max_length=10, choices=[('Credit', 'Credit'), ('Debit', 'Debit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='cash_monitors', null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    common_reference = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True, null=True)
    updated_at = models.DateTimeField(null=True)
    Bank_entries = GenericRelation("BankPaymentsMonitor")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    
class BankPaymentsMonitor(models.Model):
    notes = models.TextField(max_length=255)
    transaction_type = models.CharField(max_length=10, choices=[('Credit', 'Credit'), ('Debit', 'Debit')])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branch', null=True)
    to_branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='to_branch', null=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    common_reference = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True, null=True)
    updated_at = models.DateTimeField(null=True)
    cash_entries = GenericRelation(CashMonitor)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    # Add other fields as needed

    def __str__(self):
        return self.name
class SupplierLedger(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="ledger_entries", null=True)
    reference_payment = models.ForeignKey("PurchasePayment",  on_delete=models.CASCADE, null=True)
    reference_purchase_order = models.ForeignKey("PurchaseOrder",  on_delete=models.CASCADE, null=True)
    transaction_type = models.CharField(max_length=10, choices=[('Credit', 'Credit'), ('Debit', 'Debit')])
    notes = models.CharField(max_length=50, blank=True, null=True)
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True, null=True)
    updated_at = models.DateTimeField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
class PurchaseOrder(models.Model):
    purchase_order_id = models.CharField(primary_key=True, max_length=20, editable=False, default=generate_po_id)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders', null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
class PurchaseItem(models.Model):
    order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    has_variant = models.BooleanField(default=False)
    variant_types = models.ManyToManyField("VariantType", related_name="purchase_items", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)

class VariantType(models.Model):
    title = models.CharField(max_length=50)
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    
    class Meta:
        unique_together = (('title', 'company', 'branch'),)
    
class VariantOption(models.Model):
    variant_type = models.ForeignKey(
        VariantType,
        related_name="options",
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.variant_type.title}: {self.name}"
class VariantCombination(models.Model):
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, related_name='combinations')
    options = models.ManyToManyField(VariantOption)
    quantity = models.PositiveIntegerField()
    sku = models.CharField(max_length=50)

class ProductVarient(models.Model):
    purchase_item = models.ForeignKey(PurchaseItem, on_delete=models.CASCADE, null =True)
    options = models.ManyToManyField(VariantType)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)

class PurchasePayment(models.Model):
    order = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='payment')
    payment_type = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Bank', 'Bank'),('Mixed','Mixed')])
    cash_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    bank_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True)
