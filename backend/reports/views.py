from django.db.models import Sum, Count
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer

INCOME = Transaction.INCOME
EXPENSE = Transaction.EXPENSE


def _totals(qs):
    income = qs.filter(type=INCOME).aggregate(total=Sum('amount'))['total'] or 0
    expense = qs.filter(type=EXPENSE).aggregate(total=Sum('amount'))['total'] or 0
    return income, expense


class DashboardView(APIView):
    """
    GET /api/dashboard/

    Returns total income, total expenses, current balance, number of
    transactions, and the 5 most recent transactions for the logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        income, expense = _totals(qs)
        recent = qs.order_by('-date', '-created_at')[:5]

        return Response({
            'total_income': income,
            'total_expenses': expense,
            'current_balance': income - expense,
            'number_of_transactions': qs.count(),
            'recent_transactions': TransactionSerializer(recent, many=True).data,
        })


class MonthlyReportView(APIView):
    """
    GET /api/reports/monthly/?month=YYYY-MM  (defaults to the current month)

    Returns income, expenses, net balance, and a per-category breakdown
    for the given month.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        month = request.query_params.get('month')
        qs = Transaction.objects.filter(user=request.user)

        if month:
            try:
                year_str, month_str = month.split('-')
                qs = qs.filter(date__year=int(year_str), date__month=int(month_str))
            except (ValueError, AttributeError):
                return Response({'error': 'month must be in YYYY-MM format'}, status=400)
        else:
            from django.utils import timezone
            now = timezone.now()
            month = f'{now.year}-{now.month:02d}'
            qs = qs.filter(date__year=now.year, date__month=now.month)

        income, expense = _totals(qs)

        by_category = list(
            qs.values('type', 'category__name')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('type', '-total')
        )
        for row in by_category:
            row['category'] = row.pop('category__name') or 'Uncategorized'

        return Response({
            'month': month,
            'income': income,
            'expenses': expense,
            'net_balance': income - expense,
            'by_category': by_category,
        })


class CategoryReportView(APIView):
    """
    GET /api/reports/category/?type=income|expense&date_from=&date_to=

    Returns totals grouped by category, optionally filtered by type and
    date range.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        params = request.query_params

        type_ = params.get('type')
        if type_:
            qs = qs.filter(type=type_)

        date_from = params.get('date_from')
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            qs = qs.filter(date__lte=date_to)

        by_category = list(
            qs.values('type', 'category__name')
            .annotate(total=Sum('amount'), count=Count('id'))
            .order_by('type', '-total')
        )
        for row in by_category:
            row['category'] = row.pop('category__name') or 'Uncategorized'

        return Response({'by_category': by_category})


class IncomeVsExpenseView(APIView):
    """
    GET /api/reports/income-vs-expense/?date_from=&date_to=

    Simple side-by-side comparison of total income vs total expenses
    for the (optionally bounded) period.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        params = request.query_params

        date_from = params.get('date_from')
        if date_from:
            qs = qs.filter(date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            qs = qs.filter(date__lte=date_to)

        income, expense = _totals(qs)

        return Response({
            'income': income,
            'expenses': expense,
            'net_balance': income - expense,
        })


class HighestExpenseView(APIView):
    """
    GET /api/reports/highest-expense/?date_from=&date_to=

    Returns the single largest expense transaction in the (optionally
    bounded) period.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user, type=EXPENSE)
        qs = _apply_date_range(qs, request.query_params)

        top = qs.order_by('-amount').first()
        if not top:
            return Response({'detail': 'No expense transactions found.'}, status=404)
        return Response(TransactionSerializer(top).data)


class HighestIncomeView(APIView):
    """
    GET /api/reports/highest-income/?date_from=&date_to=

    Returns the single largest income transaction in the (optionally
    bounded) period.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user, type=INCOME)
        qs = _apply_date_range(qs, request.query_params)

        top = qs.order_by('-amount').first()
        if not top:
            return Response({'detail': 'No income transactions found.'}, status=404)
        return Response(TransactionSerializer(top).data)


def _apply_date_range(qs, params):
    date_from = params.get('date_from')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    date_to = params.get('date_to')
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs
