from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


#paginación para los posts y comentarios
class BlogPostPagination(PageNumberPagination):
    page_size = 10  # Tamaño de página predeterminado
    page_size_query_param = 'page_size'  # Parámetro para personalizar tamaño de página
    max_page_size = 10  # Tamaño máximo permitido
    page_query_param = 'page'  # Parámetro para número de página

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            'results': data,
        })


#paginación para los likes
class LikePagination(PageNumberPagination):
    page_size = 20  # Tamaño de página predeterminado
    page_size_query_param = 'page_size'  # Parámetro para personalizar tamaño de página
    max_page_size = 20  # Tamaño máximo permitido
    page_query_param = 'page'  # Parámetro para número de página

    def get_paginated_response(self, data):
        return Response({
            'current_page': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_count': self.page.paginator.count,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            'results': data,
        })

