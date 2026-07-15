from rest_framework import viewsets, permissions

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    GET    /api/categories/       - list the logged-in user's categories
    POST   /api/categories/       - create a category
    GET    /api/categories/{id}/  - retrieve a category
    PUT    /api/categories/{id}/  - update a category
    PATCH  /api/categories/{id}/  - partially update a category
    DELETE /api/categories/{id}/  - delete a category

    Optional filter: ?type=income|expense
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Category.objects.filter(user=self.request.user)
        type_ = self.request.query_params.get('type')
        if type_:
            qs = qs.filter(type=type_)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
