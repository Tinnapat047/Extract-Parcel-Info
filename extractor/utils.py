import os
import re
import pandas as pd
from typhoon_ocr import ocr_document
import openai
from dotenv import load_dotenv
import tempfile

def extract_parcel_info_from_file(fileobj):
    load_dotenv()
    api_key = os.environ.get("TYPHOON_API_KEY", "")
    if not api_key or not api_key.startswith("sk-"):
        return {"error": "API Key not found or invalid. Please check your .env file and key format."}
    os.environ["TYPHOON_OCR_API_KEY"] = api_key
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.tmp')
    try:
        for chunk in fileobj.chunks():
            tmp.write(chunk)
        tmp.flush()
        tmp.close()  # Close file so ocr_document can access it on Windows
        try:
            markdown = ocr_document(
                pdf_or_image_path=tmp.name,
                task_type="default",
                page_num=1
            )
        except Exception as e:
            return {"error": f"OCR Error: {str(e)}"}
        prompt = f"""
Please extract the following fields from the text below:
a. Parcel number  
b. Recipient's name  
c. Recipient's address  
d. Recipient's phone number  
e. Recipient's postal code

Text:
{markdown}

Please reply in this format:
Parcel number: <value or ->\nRecipient's name: <value or ->\nRecipient's address: <value or ->\nRecipient's phone number: <value or ->\nRecipient's postal code: <value or ->
"""
        try:
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.opentyphoon.ai/v1"
            )
            response = client.chat.completions.create(
                model="typhoon-v2-70b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=512
            )
            text = response.choices[0].message.content
            result = {}
            patterns = {
                'parcel_number': r'Parcel number:\s*(.*)',
                'recipient_name': r"Recipient's name:\s*(.*)",
                'recipient_address': r"Recipient's address:\s*(.*)",
                'recipient_phone': r"Recipient's phone number:\s*(.*)",
                'recipient_postal_code': r"Recipient's postal code:\s*(.*)"
            }
            for key, pat in patterns.items():
                m = re.search(pat, text)
                value = m.group(1).strip() if m else None
                if value is None or value.strip() == '' or value.strip() == '-' or value.strip() == '->':
                    result[key] = '-'
                else:
                    result[key] = value
            return result
        except Exception as e:
            return {"error": f"AI Error: {str(e)}"}
    finally:
        try:
            os.remove(tmp.name)
        except Exception as e:
            pass

def export_to_excel(data, out_path):
    df = pd.DataFrame([data])
    df.to_excel(out_path, index=False)
