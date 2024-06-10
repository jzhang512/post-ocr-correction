from openai import OpenAI
import subprocess
import os
import io
from PIL import Image
import fitz # PyMuPDF

API_ENDPOINT = "https://api.openai.com/v1/completions"
MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-0125-preview"]

# Retrieve API key from environment variable.
API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(
    api_key=API_KEY,
)

# Must add OCR text at the ends.
QE_PROMPT = """Score the following OCR output on a continuous scale from 0 to 100, where score of zero means "no meaning preserved" and score of one hundred means "perfect meaning and grammar".\n"""
SYSTEM_QE = "You are an assistant trained to estimate the quality of OCR output. Your role is to evaluate text and formatting fidelity."

QE_CHECKER = """Is the overall score from this assessment over %d? Give a one-word answer: yes or no. You will be penalized for being incorrect.\n"""
SYSTEM_CHECKER = "You are an assistant trained to determine whether an assessment of OCR quality is above a threshold score or not. The assessment will report an overall score. Identify it."


# Gives LLM assessment of an OCR text. Takes in a string, returns the string. Uses gpt4-turbo.
def qe_assess(ocr_text):
    chat_completion = client.chat.completions.create(
        model = "gpt-4-0125-preview",      # cheaper than gpt-4, comparable performance
        messages = [
            {
                "role": "system",
                "content": SYSTEM_QE
            },
            {
                "role":"user",
                "content": QE_PROMPT + ocr_text
            }
        ]
    )

    return chat_completion.choices[0].message.content

# -------------------------------------------------------------------

# Determines whether the LLM assessment form qe_assess is above a certain
# threshold (default 30). Returns a boolean (True) if above. 
def qe_check(assessment, threshold = 30):

    # Model is not perfect with the parsing task. ~80% of time right.
    # Run multiple to make sure. First to 3 will be our answer.
    counter = [0,0]     # yes, no

    while (True):
        chat_completion = client.chat.completions.create(
            model = "gpt-4-0125-preview",
            messages = [
                {
                    "role":"system",
                    "content": SYSTEM_CHECKER
                },
                {
                    "role":"user",
                    "content": (QE_CHECKER % threshold) + assessment
                }
            ]
        )
        output = chat_completion.choices[0].message.content.lower()

        if "yes" in output:
            counter[0] += 1
        elif "no" in output:
            counter[1] += 1

        if counter[0] == 3:
            return True    # above threshold, no need re-OCR
        elif counter[1] == 3:
            return False

# -------------------------------------------------------------------
        
# MASTER function for qe_assess and qe_check.
# Returns a list of work_ids that need to be re-OCRed. Takes in a dict
# of OCR output text (ocr_txt). Assumes work_ids are the keys of input dict.

## ** work_ids are the ids given to the works of the the pages we selected.
## Use your own identifiers here.
def get_re_ocr_files(ocr_text):
    to_re_ocr = []
    for txt_id in ocr_text:        # txt is a key
        assessment = qe_assess(ocr_text[txt_id]) 

        if (qe_check(assessment, 30) == False):
            to_re_ocr.append(txt_id)
    return to_re_ocr

# -------------------------------------------------------------------

# Returns a list of work_ids that won't need to be corrected. Takes in a dict
# of OCR'ed text. Assuming work_ids are the keys of input dict.
def get_no_correction_files(ocr_text):
    no_corrections = []
    for txt_id in ocr_text:        # txt is a key
        assessment = qe_assess(ocr_text[txt_id])   

        if (qe_check(assessment, 80) == True):
            no_corrections.append(txt_id)
    return no_corrections


# -------------------------------------------------------------------

# Optional.
# All of our files were in.pdf. Must be converted to .png for Tesseract.js.

# Takes a list of filenames and name for folder where converted files are saved.
# directory is path of string where files originally stored.
# ASSUMES our naming convention (order_work_id) + ".pdf" is filename.
def convert_to_png(filenames, directory, save_path):
    # Create the new directory if it doesn't exist
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    for filename in filenames:
        pdf_path = os.path.join(directory, filename) + ".pdf"

        doc = fitz.open(pdf_path)
        page = doc.load_page(0)

        # Set zoom factor for image.
        zoom_x = 3
        zoom_y = 3
        mat = fitz.Matrix(zoom_x, zoom_y)   # Create a transformation matrix for the zoom (resolution)

         # Render page to an image (pix) object
        pix = page.get_pixmap(matrix=mat)

        # Convert the image to a bytes array
        img_bytes = pix.tobytes("ppm")

        # Convert bytes to a PIL Image
        image = Image.open(io.BytesIO(img_bytes))

        saved_name = filename + ".png"
        full_save_path = os.path.join(save_path, saved_name)
        image.save(full_save_path)

# -------------------------------------------------------------------

# Reruns OCR on the files in specified directory using reOCR_tesseract.js.
# Returns dict in form {work_id: new_ocr}.
def re_OCR(run_directory_path):
    reOCR_file_path = "###FILE PATH TO reOCR_tesseract.js###"
    result = subprocess.run(["node", reOCR_file_path, run_directory_path], capture_output=True, text= True)
    
    segments = result.stdout.strip().split("$%$%$%$%*#DELZ")    # $%$%$%$%*#DELZ is delimiter (set in reOCR_tesseract.js)
    new_ocr_dict = {}

    for seg in segments:
        if seg:
            path, *content = (seg).split("\n", 1)

            # Last 4 characters are .png
            new_ocr_dict[path[:-4]] = content[0].strip() if content else ""

    return new_ocr_dict
