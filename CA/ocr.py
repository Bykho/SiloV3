import os
import cv2
import pytesseract

def preprocess_image(image):
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to convert to binary image
    #_, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    
    # Apply morphological operations (optional)
    #kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    #processed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)
    
    return gray

def ocr_image(image_path):
    try:
        # Read the image using OpenCV
        image = cv2.imread(image_path)
        
        # Preprocess the image
        processed_image = preprocess_image(image)
        
        # Perform OCR on the preprocessed image
        text = pytesseract.image_to_string(processed_image)
        print(text)
        return text
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return ""

def perform_ocr(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return ""

    if not file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        print(f"File {file_path} is not a supported image format.")
        return ""
    return ocr_image(file_path)

def main(input_directory):
    # Iterate over the files in the input directory
    for filename in os.listdir(input_directory):
        # Check if the file is a supported image format
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Construct the full path to the image file
            image_path = os.path.join(input_directory, filename)
            
            # Perform OCR on the image
            ocr_result = perform_ocr(image_path)
            
            # Display the OCR result
            print(f"OCR Result for {filename}:")
            print(ocr_result)
            print("=" * 50)  # Separator for clarity

if __name__ == "__main__":
    input_directory = os.path.join(os.path.expanduser("~/Desktop"), "SiloV3/SH")
    main(input_directory)
