from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default=None)

    class Meta:
        model = Transaction
        fields = (
            'id', 'title', 'amount', 'type', 'category', 'category_name',
            'notes', 'date', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate_category(self, category):
        if category is None:
            return category
        request = self.context['request']
        if category.user_id != request.user.id:
            raise serializers.ValidationError('Category does not belong to you.')
        return category

    def validate(self, attrs):
        category = attrs.get('category', getattr(self.instance, 'category', None))
        type_ = attrs.get('type', getattr(self.instance, 'type', None))
        if category is not None and category.type != type_:
            raise serializers.ValidationError(
                {'category': f"Category type ('{category.type}') must match transaction type ('{type_}')."}
            )
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
