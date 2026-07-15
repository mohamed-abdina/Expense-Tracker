from django.urls import path

from .views import (
    DashboardView,
    MonthlyReportView,
    CategoryReportView,
    IncomeVsExpenseView,
    HighestExpenseView,
    HighestIncomeView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('reports/monthly/', MonthlyReportView.as_view(), name='report-monthly'),
    path('reports/category/', CategoryReportView.as_view(), name='report-category'),
    path('reports/income-vs-expense/', IncomeVsExpenseView.as_view(), name='report-income-vs-expense'),
    path('reports/highest-expense/', HighestExpenseView.as_view(), name='report-highest-expense'),
    path('reports/highest-income/', HighestIncomeView.as_view(), name='report-highest-income'),
]
