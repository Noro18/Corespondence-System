import csv
from django.http import HttpResponse

def export_csv_response(filename, headers, rows):
    """
    Helper to generate a CSV HttpResponse with UTF-8 BOM for Excel compatibility.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    # Write UTF-8 BOM so Excel opens special characters and symbols correctly
    response.write('\ufeff'.encode('utf-8'))
    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    return response
