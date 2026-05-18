# inventory/serializers.py
from rest_framework import serializers
from .models import Item, GemDetail, Color, Clarity, Cut
from .models import Item, GemDetail, Color, Clarity, Cut, StockMovement


class GemDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GemDetail
        fields = [
            'certification_number', 'carat_weight', 'origin',
            'color', 'clarity', 'cut',
            'is_treated', 'has_fluorescence',
        ]

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Color
        fields = ['id', 'name', 'code']


class ClaritySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Clarity
        fields = ['id', 'code', 'num_code', 'order']


class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cut
        fields = ['id', 'name']


class ItemSerializer(serializers.ModelSerializer):
    gem_detail = GemDetailSerializer(required=False, allow_null=True)

    class Meta:
        model  = Item
        fields = [
            'id', 'sku', 'name', 'description',
            'status', 'base_price', 'currency',
            'gem_detail',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        gem_data = validated_data.pop('gem_detail', None)
        item = Item.objects.create(**validated_data)

        if gem_data:
            GemDetail.objects.create(item=item, **gem_data)

        return item        # ← same level as 'if'

    def update(self, instance, validated_data):
        gem_data = validated_data.pop('gem_detail', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if gem_data is not None:
            GemDetail.objects.update_or_create(
                item=instance,
                defaults=gem_data
            )

        return instance    # ← same level as 'if'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Color
        fields = ['id', 'name', 'code']


class ClaritySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Clarity
        fields = ['id', 'name', 'code', 'order']


class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Cut
        fields = ['id', 'name', 'code']
        # Create StoneDetail if provided


    def update(self, instance, validated_data):
        gem_data = validated_data.pop('gem_detail', None)

        # Update Item fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or create StoneDetail
        if gem_data is not None:
            GemDetail.objects.update_or_create(
                item=instance,
                defaults=gem_data
            )

        return instance


class StockMovementSerializer(serializers.ModelSerializer):
    item_sku          = serializers.CharField(source='item.sku', read_only=True, default=None)
    item_name         = serializers.CharField(source='item.name', read_only=True, default=None)
    supplier_name     = serializers.CharField(source='supplier.bp_name', read_only=True, default=None)
    customer_name     = serializers.CharField(source='customer.bp_name', read_only=True, default=None)
    po_reference      = serializers.CharField(source='purchase_order.reference', read_only=True, default=None)
    memo_reference    = serializers.CharField(source='customer_memo.reference', read_only=True, default=None)
    transaction_label = serializers.CharField(source='get_transaction_type_display', read_only=True)
    value             = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model  = StockMovement
        fields = [
            'id', 'transaction_type', 'transaction_label', 'date',
            'item', 'item_sku', 'item_name',
            'parcel_description',
            'quantity', 'weight_carats', 'price_per_carat',
            'unit_value', 'currency', 'value',
            'purchase_order', 'po_reference',
            'customer_memo', 'memo_reference',
            'supplier', 'supplier_name',
            'customer', 'customer_name',
            'notes', 'created_at',
            'appro_reference',
        ]
        read_only_fields = ['id', 'created_at']