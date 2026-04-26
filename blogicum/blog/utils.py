from django.core.paginator import Paginator


def get_paginated_objects(queryset, request, paginate_by=10):
    paginator = Paginator(queryset, paginate_by)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
