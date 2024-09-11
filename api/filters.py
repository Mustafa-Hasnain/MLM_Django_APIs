# api/filters.py
from django_filters import rest_framework as filters
from .models import Product
from django.db.models import Q  # Import Q for complex lookups


class ProductFilter(filters.FilterSet):
    search_term = filters.CharFilter(method='filter_by_all_fields')

    class Meta:
        model = Product
        fields = []

    # Define a custom filter method to search by name, description, brand, and price
    def filter_by_all_fields(self, queryset, name, value):
        # Convert the search value to lowercase for case-insensitive comparison
        try:
            # Attempt to convert value to a decimal for price filtering
            price_value = float(value)
        except ValueError:
            price_value = None

        # Search by name, description, brand, or price
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__icontains=value) |
            (Q(price=price_value) if price_value is not None else Q())
        )
