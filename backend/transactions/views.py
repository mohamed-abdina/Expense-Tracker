from rest_framework import viewsets, permissions

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    """
    GET    /api/transactions/       - list the logged-in user's transactions
    POST   /api/transactions/       - create a transaction
    GET    /api/transactions/{id}/  - retrieve a transaction
    PUT    /api/transactions/{id}/  - update a transaction
    PATCH  /api/transactions/{id}/  - partially update a transaction
    DELETE /api/transactions/{id}/  - delete a transaction

    Optional filters:
      ?type=income|expense
      ?category=<category_id>
      ?date_from=YYYY-MM-DD&date_to=YYYY-MM-DD
      ?search=<text in title/notes>
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related('category')
        params = self.request.query_params

        type_ = params.get('type')
        if type_:
            qs = qs.filter(type=type_)

        category_id = params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)

        date_from = params.get('date_from')
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            qs = qs.filter(date__lte=date_to)

        search = params.get('search')
        if search:
            qs = qs.filter(title__icontains=search) | qs.filter(notes__icontains=search)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
