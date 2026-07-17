import csv

from django.http import HttpResponse
from django.utils import timezone


def build_csv_response(filename_prefix, rows):
    timestamp = timezone.localtime().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="{filename_prefix}_{timestamp}.csv"'
    )

    # Excel opens UTF-8 CSV files more reliably when the BOM is included.
    response.write('\ufeff')

    writer = csv.writer(response)
    for row in rows:
        writer.writerow(row)

    return response
