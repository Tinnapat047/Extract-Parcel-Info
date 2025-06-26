from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, FileResponse
from .forms import UploadParcelForm
from .utils import extract_parcel_info_from_file, export_to_excel
from .models import ParcelInfo
import os
import pandas as pd
import logging
import json

def index(request):
    import json
    import tempfile
    logger = logging.getLogger(__name__)
    result = None
    error = None
    filename = None
    excel_url = None
    warning = None
    saved = False
    file_uploaded = False
    form = UploadParcelForm()
    # ใช้ session เก็บ result, filename หลังอัปโหลด
    if request.method == 'POST':
        if 'save' in request.POST and request.session.get('result') and request.session.get('filename'):
            result = request.session.get('result')
            filename = request.session.get('filename')
            obj = ParcelInfo.objects.create(
                file_name=filename,
                parcel_number=result.get('parcel_number'),
                recipient_name=result.get('recipient_name'),
                recipient_address=result.get('recipient_address'),
                recipient_phone=result.get('recipient_phone'),
                recipient_postal_code=result.get('recipient_postal_code')
            )
            logger.info(f"[SAVE] ParcelInfo created: id={obj.id}")
            saved = True
            excel_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"{filename}.xlsx")
            export_to_excel(result, excel_path)
            excel_url = f"/download/{filename}/"
            # ลบค่าใน session หลังบันทึก
            if saved:
                from django.contrib import messages
                messages.success(request, "บันทึกข้อมูลเรียบร้อยแล้ว!")
            request.session.pop('result', None)
            request.session.pop('filename', None)
            result = None
            filename = None
            excel_url = None
        else:
            form = UploadParcelForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['file']
                filename = file.name
                result = extract_parcel_info_from_file(file)
                logger.info(f"[UPLOAD] filename={filename} result={result}")
                file_uploaded = True
                excel_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"{filename}.xlsx")
                export_to_excel(result, excel_path)
                excel_url = f"/download/{filename}/"
                request.session['result'] = result
                request.session['filename'] = filename
                missing_fields = [
                    label for label, key in [
                        ("หมายเลขพัสดุ", 'parcel_number'),
                        ("ชื่อผู้รับ", 'recipient_name'),
                        ("ที่อยู่ผู้รับ", 'recipient_address'),
                        ("เบอร์โทรศัพท์ผู้รับ", 'recipient_phone'),
                        ("รหัสไปรษณีย์ผู้รับ", 'recipient_postal_code')
                    ] if result.get(key) == '-'
                ]
                if missing_fields:
                    warning = f"OCR ไม่สามารถอ่านข้อมูลบางส่วนได้: {', '.join(missing_fields)}"
                else:
                    warning = None
            else:
                warning = None
    else:
        form = UploadParcelForm()
        warning = None
    return render(request, 'extractor/index.html', {
        'form': form,
        'result': result,
        'error': error,
        'excel_url': excel_url,
        'warning': warning,
        'saved': saved,
        'file_uploaded': file_uploaded,
        'filename': filename
    })

def download_excel(request, filename):
    if filename == 'all':
        # Export all ParcelInfo to Excel
        parcels = ParcelInfo.objects.all().order_by('-created_at')
        data = [
            {
                'วันที่': p.created_at.strftime('%Y-%m-%d %H:%M'),
                'ไฟล์': p.file_name,
                'หมายเลขพัสดุ': p.parcel_number,
                'ชื่อผู้รับ': p.recipient_name,
                'ที่อยู่': p.recipient_address,
                'เบอร์โทร': p.recipient_phone,
                'รหัสไปรษณีย์': p.recipient_postal_code,
            }
            for p in parcels
        ]
        df = pd.DataFrame(data)
        from io import BytesIO
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        response = FileResponse(output, as_attachment=True, filename='parcel_info_all.xlsx')
        return response

    excel_path = os.path.join(settings.MEDIA_ROOT, 'uploads', f"{filename}.xlsx")
    if not os.path.exists(excel_path):
        return HttpResponse('File not found', status=404)
    response = FileResponse(open(excel_path, 'rb'), as_attachment=True, filename=f'parcel_info_{filename}.xlsx')
    return response

def history(request):
    parcels = ParcelInfo.objects.order_by('-created_at')[:50]  # แสดง 50 รายการล่าสุด
    return render(request, 'extractor/history.html', {'parcels': parcels})
