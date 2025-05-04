# KeeganGPT

Click [here](https://arxiv.org/pdf/2504.03857) to read the white paper!

To fine-tune your own model, first run frame_extracter.py on your raw video input, followed by image_summarizer.py to summarize all of the extracted frames. Then run summary_hierarchy.py to generate a hierarchy of summaries, followed by generate_jsonl.py to format the data for fine-tuning. Finally, run fine_tune.py to fine-tune a GPT model on your data using the OpenAI API. 
