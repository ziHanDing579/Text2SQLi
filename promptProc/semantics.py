import numpy as np
import time
import sys
import json
import os
from dotenv import load_dotenv
import csv

from openai import OpenAI
import spacy
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity

from promptInject import promptData

THRESHOLD = 0.35

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

class CheckPrompts():
    def __init__(self, promptFile):
        self.prompts = self.loadPrompts(promptFile)
        self.promptData = promptData.payloads
        self.promptPrefix = promptData.prefix
        
        self.bert = SentenceTransformer("BAAI/bge-base-en-v1.5", device="cuda")
        self.gpt = OpenAI(api_key=openai_api_key)
        self.gemini = genai.Client(api_key=gemini_api_key)
        
        self.promptText = [value["prompt"] for key, value in self.promptData.items()]
        self.promptText += [value["prompt"] for key, value in self.promptPrefix.items()]
        self.promptBERT = self.loadPromptBERT()
        self.promptOpenAI = self.loadPromptGPT()
        self.promptGemini = self.loadPromptGemini()

        self.timeResults = {}
        self.f1Results = {}
    
    def loadPrompts(self, promptFile):
        prompts = []
        with open(promptFile, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prompt = {}
                prompt["prompt"] = row['text']
                prompt["label"] = int(row['label'])
                prompts.append(prompt)
        return prompts
        # with open(promptFile, "r", encoding="utf-8") as f:
        #     print(f"Loading prompts from {promptFile}")
        #     count = 0
        #     for line in f:
        #         count += 1
        #         print(f"Loaded {count} prompts", end="\r")
        #         text = line.strip().split(":-:")
        #         prompt = {}
        #         prompt["prompt"] = text[0]
        #         prompt["label"] = int(text[1])
        #         prompts.append(prompt)
        # return prompts
    
    def loadPromptBERT(self):
        promptList = []
        for key, value in self.promptData.items():
            promptList.append(self.bert.encode(value["prompt"]))
        
        for key, value in self.promptPrefix.items():
            promptList.append(self.bert.encode(value["prompt"]))

        return promptList
    
    def loadPromptGPT(self):
        if os.path.exists("gpt_prompts.json"):
            with open("gpt_prompts.json", "r") as f:
                print("Loading GPT prompts from file")
                return json.load(f)
            
        promptList = []

        for key, value in self.promptData.items():
            text = self.gpt.embeddings.create(
                input = value["prompt"], 
                model = "text-embedding-3-large").data[0].embedding
            promptList.append(text)

        for key, value in self.promptPrefix.items():
            text = self.gpt.embeddings.create(
                input = value["prompt"], 
                model = "text-embedding-3-large").data[0].embedding
            promptList.append(text)

        with open("gpt_prompts.json", "w") as f:
            json.dump(promptList, f, indent=4)

        return promptList
    
    def loadPromptGemini(self):
        if os.path.exists("gemini_prompts.json"):
            with open("gemini_prompts.json", "r") as f:
                print("Loading Gemini prompts from file")
                return json.load(f)
            
        promptList = []

        for key, value in self.promptData.items():
            text = self.gemini.models.embed_content(
                model="gemini-embedding-001",
                contents=[value["prompt"]],
                config=types.EmbedContentConfig(task_type="CLASSIFICATION")).embeddings[0].values
            # convert from contentEmbedding to list
            promptList.append(text)

        for key, value in self.promptPrefix.items():
            text = self.gemini.models.embed_content(
                model="gemini-embedding-001",
                contents=[value["prompt"]],
                config=types.EmbedContentConfig(task_type="CLASSIFICATION")).embeddings[0].values
            # convert from contentEmbedding to list
            promptList.append(text)

        with open("gemini_prompts.json", "w") as f:
            json.dump(promptList, f, indent=4)

        return promptList
    
    def generateEmbeddings(self, prompts, method):
        embeddings = []
        total = len(prompts)
        current = 0
        print(f"Generating embeddings using {method} for {total} prompts.")
        if method == "bert":
            for prompt in prompts:
                embedding = self.bert.encode(prompt["prompt"])
                converted = embedding.tolist()  # Convert numpy array to list for JSON serialization
                embeddings.append({prompt["prompt"]: [converted, prompt["label"]]})
                current += 1
                print(f"Progress: {current}/{total} prompts processed.", end="\r")

        elif method == "gpt":
            for prompt in prompts:
                text = self.gpt.embeddings.create(
                    input = prompt["prompt"], 
                    model = "text-embedding-3-large").data[0].embedding
                embeddings.append({prompt["prompt"]: [text, prompt["label"]]})
                current += 1
                print(f"Progress: {current}/{total} prompts processed.", end="\r")

        elif method == "gemini":
            for prompt in prompts:
                text = self.gemini.models.embed_content(
                    model="gemini-embedding-001",
                    contents=[prompt["prompt"]],
                    config=types.EmbedContentConfig(task_type="CLASSIFICATION")).embeddings[0].values
                embeddings.append({prompt["prompt"]: [text, prompt["label"]]})
                current += 1
                print(f"Progress: {current}/{total} prompts processed.", end="\r")
        else:
            raise ValueError(f"Unknown method: {method}")
        return embeddings

    def clearResults(self):
        self.timeResults = {}
        self.f1Results = {}
        
    def checkPrompt(self, method, threshold=THRESHOLD):
        startTime = time.time()
        averageTime = 0
        indvTimes = []
        indvTimeNoInfer = []
        totalTP = 0
        totalFP = 0
        totalFN = 0
        totalTN = 0

        total_progress = len(self.prompts)
        current_progress = 0

        print("Starting prompt checks for method:", method)
        
        for prompt in self.prompts:
            indvStart = time.time()
            promptText = prompt["prompt"]
            promptLabel = prompt["label"]
            promptEmbedding = None
            
            if method == "bert":
                promptEmbedding = self.bert.encode(promptText)

            elif method == "gpt":
                promptEmbedding = self.gpt.embeddings.create(
                    input = promptText, 
                    model = "text-embedding-3-large").data[0].embedding
                
            elif method == "gemini":
                promptEmbedding = self.gemini.models.embed_content(
                    model="gemini-embedding-001",
                    contents=[promptText],
                    config=types.EmbedContentConfig(task_type="CLASSIFICATION")).embeddings[0].values
                promptEmbedding = np.array(promptEmbedding)
            else:
                raise ValueError(f"Unknown method: {method}")

            postInferStart = time.time()
            maxSimilarity = 0.0
            maxPrompt = ""
            prompts = []

            if method == "bert":
                prompts = self.promptBERT
            elif method == "gpt":
                prompts = self.promptOpenAI
            elif method == "gemini":
                prompts = self.promptGemini
                
            for i in range(len(prompts)):
                similarity = 0
                if method == "bert":
                    similarity = self.bert.similarity(promptEmbedding, prompts[i]).item()
                elif method == "gpt":
                    similarity = np.dot(promptEmbedding, prompts[i]) / (np.linalg.norm(promptEmbedding) * np.linalg.norm(prompts[i]))
                elif method == "gemini":
                    similarity = cosine_similarity([promptEmbedding], [prompts[i]])[0][0]

                if similarity > maxSimilarity:
                    maxSimilarity = similarity
                    maxPrompt = self.promptText[i]
                    
            if promptLabel == 0 and maxSimilarity > threshold:
                totalTP += 1
            elif promptLabel == 0 and maxSimilarity <= threshold:
                totalFN += 1
            elif promptLabel == 1 and maxSimilarity > threshold:
                totalFP += 1
            else:
                totalTN += 1
                
            indvEnd = time.time() - indvStart
            self.timeResults[promptText] = {"Time": indvEnd, "Similarity": maxSimilarity, "Prompt": maxPrompt, "Label": promptLabel}
            indvTimes.append(indvEnd)
            indvTimeNoInfer.append(time.time() - postInferStart)
            current_progress += 1
            print(f"Progress: {current_progress}/{total_progress} prompts checked.", end="\r")
            
        finalTime = time.time() - startTime
        averageTime = np.mean(indvTimes)
        averageTimeNoInfer = np.mean(indvTimeNoInfer)
        self.timeResults["Total Time"] = finalTime
        self.timeResults["Average Time"] = averageTime
        if totalTP == 0:
            precision = 0
            recall = 0
            f1 = 0
        else:
            precision = totalTP / (totalTP + totalFP)
            recall = totalTP / (totalTP + totalFN)
            f1 = 2 * (precision * recall) / (precision + recall)
        self.f1Results["Total"] = {"TP": totalTP, 
                                   "FP": totalFP, 
                                   "FN": totalFN,
                                   "TN": totalTN,
                                   "Precision": precision, 
                                   "Recall": recall,
                                   "F1": f1, 
                                   "Average Time": averageTime,
                                   "Average Time No Infer": averageTimeNoInfer,
                                   "Threshold": threshold}
     
    def exportTime(self, filename):  
        #check if the file exists
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                data.update(self.timeResults)
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
        else:
            with open(filename, "w") as f:
                json.dump(self.timeResults, f, indent=4)
            
    def exportF1(self, filename):
        #check if the file exists
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
                data.update(self.f1Results)
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
        else:
            with open(filename, "w") as f:
                json.dump(self.f1Results, f, indent=4)
                    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print("Usage: python semantics.py <promptFile> <name>")
        sys.exit(1)

    checkPrompts = CheckPrompts(args[0])
    checkPrompts.checkPrompt("bert", 0.6)
    checkPrompts.exportF1(f"bert_f1_results_0.60_SQLShield.json")
    checkPrompts.exportTime(f"bert_time_results_0.60_SQLShield.json")
    checkPrompts.clearResults()