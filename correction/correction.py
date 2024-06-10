import sys
import os
from openai import OpenAI
from gpt_token_counter import num_tokens

API_ENDPOINT = "https://api.openai.com/v1/completions"
MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-0125-preview"]

# Retrieve API key from environment variable.
API_KEY = os.getenv("OPENAI_API_KEY")

if API_KEY is None:
    raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(
    api_key=API_KEY,
)

SYSTEM_PROMPT = "You are an assistant trained to correct text from OCR outputs that may contain errors. Your task is to reconstruct the likely original text. Restore the text to its original form, including handling non-standard elements that aligns with their intended meaning and use."


# Corrects and prints given OCR output.
# arguments is a dict with work_id as keys (work_id: (arg1, arg2, arg3, etc.)). Used to fill in the template prompts.
# only_works is a list (work_ids) specifying which specific works to run correction on.
# ocr_texts is a dict that associates work_id (key) and corresponding ocr text (to be corrected)
# ** NOTE: user_prompt_base is string with user prompt without the to-be-corrected OCR text appended
def run_correction(model, ocr_texts, user_prompt_base, arguments = None, only_works = None):
    
    llm_output = {}  # key is work_id

    for key in ocr_texts:
        assert(num_tokens(ocr_texts[key]) < 2048)  # control for too long (costly) prompts

    if only_works == None:
        for key in ocr_texts:

            chat_completion = client.chat.completions.create(
                model=model,
                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": user_prompt_base + ocr_texts[key],
                    }
                ]
            )
            llm_output[key] = chat_completion.choices[0].message.content
    else:
        for key in only_works:

            chat_completion = client.chat.completions.create(
                model=model,
                messages=[

                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": (user_prompt_base % arguments[key])+ ocr_texts[key]
                    }
                ]
            )

            llm_output[key] = chat_completion.choices[0].message.content

    print(llm_output, end = '')  # make sure to save output to avoid re-running

# ----------------------------------------------------------------------

# Helpful functions for writing LLM output to files.

# Saves corrections from a correction run to a new file in a Python list variable (for easy re-use).
# file_name, var_name are the names of the file and variable created respectively.
# Adjust iter to vary the number of corrections per run (default in paper is 10).
def correct_and_write(file_name, var_name, ocr_texts, user_prompt_base, model = "gpt-3.5-turbo", iter = 10, arguments = None, only_works = None):

    with open(file_name, "w") as results_f:
        sys.stdout = results_f

        print(var_name + " = [", end = '')

        for i in range(iter):
            if i != 0:
                print(", ")

            run_correction(model, ocr_texts, user_prompt_base, arguments, only_works)

        print("]", end = '')

# ----------------------------------------------------------------------
        
# Runs and saves corrections with all 3 GPT models, saving in 3 separate files (one per model).
def run_all(experiment_name, ocr_texts, user_prompt_base, iter = 10, arguments = None, only_works = None):

    for running_model in MODELS:
        new_file_name = "o_" + experiment_name + "_" + running_model + ".py"   
        var_name = experiment_name + "_" + running_model
        
        correct_and_write(new_file_name, var_name, ocr_texts, user_prompt_base, model = running_model, iter = iter, arguments=arguments, only_works= only_works)


if __name__ == "__main__":
    run_all("re_OCR", times_per= 10, ocr_texts= "###OCR OUTPUTS TO BE CORRECTED###")