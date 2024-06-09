# Post OCR-Correction in the Princeton Prosody Archive (PPA)

Code and prompt templates for the "Post-OCR Correction with OpenAI’s GPT Models on Challenging
English Prosody Texts" short-paper submission to DocEng 2024. The seven templates are listed in this readme. 

While we are unable to share data from the PPA, please feel free to experiment with your own data and modify the prompts as you wish.

## (1) Universal System Prompt


You are an assistant trained to correct text from OCR outputs that may contain errors. Your task is to reconstruct the likely original text. Restore the text to its original form, including handling non-standard elements that aligns with their intended meaning and use.


## (2) Vanilla

###Instruction###

Reconstruct the likely original text based on the OCR output provided. Interpret the possible errors introduced by the OCR process and correct them to best represent the initial text. Only provide the corrected version, do not say any other words in your response. You will be penalized for adding extra words.
    
###OCR text###

`{OCR_text}`


## (3) Explaining "_Typographically Unique_"

###Context###

The original text may have had musical notation, invented diacritical marks, phonetic scripts, universal alphabets, and more common marks for stress (the ictus or an "x" mark). As a result, the text may intentionally not adhere to standard English conventions or content.

###Instruction###

Reconstruct the likely original text based on the OCR output provided. Interpret the possible errors introduced by the OCR process and correct them to best represent the initial text. Only provide the corrected version, do not say any other words in your response. You will be penalized for adding extra words.
    
###OCR text###

`{OCR_text}`


## (4) Work-Specific Metadata

###Context###

The text is from the work `{work_title}`. It is by `{author}` and published in `{publication_year}`. The work is tagged as `{tagged_collections}`.

Here is more information about the tags: 
    `{collection_descriptions}`

###Instruction###

Reconstruct the likely original text based on the OCR output provided. Interpret the possible errors introduced by the OCR process and correct them to best represent the initial text. Only provide the corrected version, do not say any other words in your response. You will be penalized for adding extra words.
    
###OCR text###

`{OCR_text}`

## (5) Temperature

Same as the Vanilla prompt but with the temperature parameter settings at intervals of 0.2, from 0 to 1.2. Note that the temperature at 1 is exactly the baseline.

## (6) Correctness Aware

###Context###

Compared with the ground truth, the character error rate of the OCR text is `{CER}`. Out of `{num_total_char}` total characters in the ground truth, `{num_correct}` are already correct here. It will need `{num_sub}` substitutions, `{num_ins}` inserts, `{num_del}` deletions.

###Instruction###

Reconstruct the likely original text based on the OCR output provided. Interpret the possible errors introduced by the OCR process and correct them to best represent the initial text. Only provide the corrected version, do not say any other words in your response. You will be penalized for adding extra words.
    
###OCR text###

`{OCR_text}`


## (7) LLM as Second Reader

Same as the Vanilla prompt but use the output of one correction pass as the input to a second pass. That output is the final correction.
