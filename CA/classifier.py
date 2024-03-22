import re
from ocr import perform_ocr

def classify_text(text):
    regexS1 = r'\bS-?1\b'
    regexTaxReturn = r'\b1040\b|IRS\s*Form\s*1040'
    regexW2 = r'\bW-2\b'
    regex1099MISCForms = r'\b1099-MISC\b'
    regexScheduleCForms = r'\bSchedule\s*C\b'
    regexScheduleAForms = r'\bSchedule\s*A\b'
    regex1099INTForms = r'\b1099-INT\b'
    regex1099DIVForms = r'\b1099-DIV\b'
    regex1099RForms = r'\b1099-R\b'
    regex1099BForms = r'\b1099-B\b'
    regex1098Forms = r'\b1098\b'
    regex5498Forms = r'\b5498\b'
    regex8867Forms = r'\b8867\b'
    regexTaxAccountTranscript = r'\bTax\s*Account\s*Transcript\b'
    regexTaxReturnTranscript = r'\bTax\s*Return\s*Transcript\b'
    regexNoticeOfFederalTaxLien = r'\bNotice\s*of\s*Federal\s*Tax\s*Lien\b'
    USApassportRegex = r'\bPASSPORT\b'
    collegeIDRegex = r'\bStudent\b'

    #print("About to run tests")
    #print("Text type:", type(text))
    
    if re.search(regexS1, text, re.IGNORECASE):
        #print('Found S-1')
        return 'S1'
    elif re.search(regexW2, text, re.IGNORECASE):
        #print('Found W-2')
        return 'W2'
    elif re.search(USApassportRegex, text, re.IGNORECASE):
        #print('Found PASSPORT')
        return 'USA passport'
    elif re.search(collegeIDRegex, text, re.IGNORECASE):
        #print('Found Student')
        return 'college ID'
    else:
        #print('Unknown')
        return 'unknown'

def run_classification(image_path):
    ocr_result = perform_ocr(image_path)

    if ocr_result:
        #print("OCR Result:")
        #print(ocr_result)
        
        classification_result = classify_text(str(ocr_result))
        #print("Classification Result:")
        #print(classification_result)
        
        return classification_result
    else:
        #print("OCR failed or unsupported image format.")
        return ""
    
