from django.core.paginator import Paginator


def paginate_queryset(request, queryset, page_size=5):
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    pagination_query_params = request.GET.copy()
    pagination_query_params.pop('page', None)
    return page_obj, pagination_query_params.urlencode()
