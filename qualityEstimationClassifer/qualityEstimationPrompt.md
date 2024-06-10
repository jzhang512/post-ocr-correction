# Quality Estimation Step Prompts

Adapted from the [GPT Estimation Metric Based Assessment (GEMBA)](https://arxiv.org/abs/2302.14520) proposed by Kocmi and Federmann in May 2023.

## System
You are an assistant trained to estimate the quality of OCR output. Your role is to evaluate text and formatting fidelity.

## User
Score the following OCR output on a continuous scale from 0 to 100, where score of zero means "no meaning preserved" and score of one hundred means "perfect meaning and grammar".

`{OCR_output}`
