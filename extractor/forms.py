from django import forms

class UploadParcelForm(forms.Form):
    file = forms.FileField(
        label='อัปโหลดรูปภาพหรือไฟล์ PDF',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-lg',
            'accept': 'image/*,.pdf',
            'required': True
        })
    )
