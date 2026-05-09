# inventory/serializers.py
from rest_framework import serializers
from .models import Item, GemDetail, Color, Clarity, Cut


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