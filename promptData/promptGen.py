import os
import random

payload_file = "payload.txt"
prefix = "prefix.txt"
suffix = "suffix.txt"
transform_file = "transforms.txt"
language = "chinese"

#load payload, each line is a payload
payloads = []
with open(payload_file, "r") as f:
    payloads = f.readlines()
    #remove newline characters and trailing spaces
    payloads = [x.strip() for x in payloads]
    
#load prefix
prefixes = []
with open(prefix, "r") as f:
    prefixes = f.readlines()
    prefixes = [x.strip() for x in prefixes]
    
#load suffix
suffixes = []
with open(suffix, "r") as f:
    suffixes = f.readlines()
    suffixes = [x.strip() for x in suffixes]
    
#load transform
transforms = []
with open(transform_file, "r") as f:
    transforms = f.readlines()
    transforms = [x.strip() for x in transforms]
    
#generate prompts
col = "users"
x = 100
file = "test.txt"
row = "101"
value = 999
prompts = []
for payload in payloads:
    for prefix in prefixes:
        for suffix in suffixes:
            prompt = prefix + " " + payload + " " + suffix
            if "{col}" in prompt:
                prompt = prompt.replace("{col}", col)
            if "{x}" in prompt:
                prompt = prompt.replace("{x}", str(x))
            if "{file}" in prompt:
                prompt = prompt.replace("{file}", file)
            if "{row}" in prompt:
                prompt = prompt.replace("{row}", row)
            if "{value}" in prompt:
                prompt = prompt.replace("{value}", str(value))
            prompts.append(prompt)
            
#write prompts to file
with open("prompts.txt", "w") as f:
    for prompt in prompts:
        f.write(prompt + "\n")
        
#generate transformed prompts
transformed_prompts = []
for prompt in prompts:
    for transform in transforms:
        transformed_prompt = prompt + " " + transform
        if "{language}" in transformed_prompt:
            transformed_prompt = transformed_prompt.replace("{language}", language)
        transformed_prompts.append(transformed_prompt)
        
#write transformed prompts to file
with open("transformed_prompts.txt", "w") as f:
    for prompt in transformed_prompts:
        f.write(prompt + "\n")

legitQuestions = []
with open("chatbot-questions-claude.txt", "r") as f:
    legitQuestions = f.readlines()
    legitQuestions = [x.strip() for x in legitQuestions]
with open("chatbot-questions-gpt.txt", "r") as f:
    legitQuestions += f.readlines()
    legitQuestions = [x.strip() for x in legitQuestions]

#random sample of prompts
random_prompts = random.sample(prompts, len(legitQuestions))
with open("random_prompts.txt", "w") as f:
    for prompt in random_prompts:
        f.write(prompt + "\n")

#write a file of random and legit questions mixed, with a :0 or :1 label at the end
mixed_questions = []
for i in range(len(legitQuestions)):
    mixed_questions.append(legitQuestions[i] + ":1")
    mixed_questions.append(random_prompts[i] + ":0")
random.shuffle(mixed_questions)

with open("mixed_questions.txt", "w") as f:
    for question in mixed_questions:
        f.write(question + "\n")