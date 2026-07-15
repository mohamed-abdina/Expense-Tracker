from rest_framework import serializers

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'type', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        request = self.context['request']
        name = attrs.get('name', getattr(self.instance, 'name', None))
        type_ = attrs.get('type', getattr(self.instance, 'type', None))

        qs = Category.objects.filter(user=request.user, name__iexact=name, type=type_)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                'You already have a category with this name and type.'
            )
        return attrs
