from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Paginacion por defecto que permite al cliente ajustar el tamano de pagina.

    Habilita ?page_size= (p.ej. el Scanner pide solo 1 fila para reducir egress).
    """

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
