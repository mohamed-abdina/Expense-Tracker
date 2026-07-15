from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'type', 'category', 'date', 'user')
    list_filter = ('type', 'category')
    search_fields = ('title', 'notes', 'user__username')
    date_hierarchy = 'date'
