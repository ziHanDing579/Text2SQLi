import numpy as np
import time
import sys
import json

import spacy
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer

from promptInject import promptData

class CheckPrompts():
    def __init__(self, promptFile):
        self.prompts = self.loadPrompts(promptFile)
        self.promptData = promptData.ignore_prompts
        self.nlp = spacy.load("en_core_web_trf")
        self.bert = SentenceTransformer("all-mpnet-base-v2")
        self.vectorizer = TfidfVectorizer()
        self.promptText = [value["prompt"] for key, value in self.promptData.items()]
        self.promptNLP = self.loadPromptNLP()
        self.promptBERT = self.loadPromptBERT()
        self.timeResults = {}
        self.f1Results = {}
    
    def loadPrompts(self, promptFile):
        prompts = []
        with open(promptFile, "r") as f:
            for line in f:
                text = line.strip().split(":")
                prompt = {}
                prompt["prompt"] = text[0]
                prompt["label"] = int(text[1])
                prompts.append(prompt)
        return prompts
    
    def loadPromptNLP(self):
        promptList = []
        for key, value in self.promptData.items():
            doc = self.nlp(value["prompt"])
            promptList.append(doc)
        return promptList
    
    def loadPromptBERT(self):
        promptList = []
        for key, value in self.promptData.items():
            promptList.append(self.bert.encode(value["prompt"]))
        return promptList
            
    def checkPromptSpacy(self):
        startTime = time.time()
        averageTime = 0
        indvTimes = []
        totalTP = 0
        totalFP = 0
        totalFN = 0
        totalTN = 0
        
        for prompt in self.prompts:
            indvStart = time.time()
            promptText = prompt["prompt"]
            promptLabel = prompt["label"]
            firstTenWords = promptText.split()[:10]
            doc = self.nlp(" ".join(firstTenWords))
            maxSimilarity = 0
            maxPrompt = ""
            threshold = 0.8
            
            for promptNLP in self.promptNLP:
                similarity = doc.similarity(promptNLP)
                if similarity > maxSimilarity:
                    maxSimilarity = similarity
                    maxPrompt = promptNLP.text
                    
            if promptLabel == 1 and maxSimilarity > threshold:
                totalTP += 1
            elif promptLabel == 1 and maxSimilarity <= threshold:
                totalFN += 1
            elif promptLabel == 0 and maxSimilarity > threshold:
                totalFP += 1
            else:
                totalTN += 1
                
            indvEnd = time.time() - indvStart
            self.timeResults[prompt["prompt"]] = {"Time": indvEnd, "Similarity": maxSimilarity, "Prompt": maxPrompt}
            indvTimes.append(indvEnd)
            
        finalTime = time.time() - startTime
        averageTime = np.mean(indvTimes)
        self.timeResults["Total Time"] = finalTime
        self.timeResults["Average Time"] = averageTime
        self.f1Results["Total"] = {"TP": totalTP, "FP": totalFP, "FN": totalFN, "TN": totalTN}
        
    def checkPromptBERT(self):
        startTime = time.time()
        averageTime = 0
        indvTimes = []
        totalTP = 0
        totalFP = 0
        totalFN = 0
        totalTN = 0
        
        for prompt in self.prompts:
            indvStart = time.time()
            promptText = prompt["prompt"]
            promptLabel = prompt["label"]
            firstTenWords = promptText.split()[:10]
            promptEmbedding = self.bert.encode(" ".join(firstTenWords))
            maxSimilarity = 0
            maxPrompt = ""
            threshold = 0.6
            
            for i in range(len(self.promptBERT)):
                similarity = self.bert.similarity(promptEmbedding, self.promptBERT[i]).item()
                if similarity > maxSimilarity:
                    maxSimilarity = similarity
                    maxPrompt = self.promptText[i]
                    
            indvEnd = time.time() - indvStart
                    
            if promptLabel == 1 and maxSimilarity > threshold:
                totalTP += 1
            elif promptLabel == 1 and maxSimilarity <= threshold:
                totalFN += 1
            elif promptLabel == 0 and maxSimilarity > threshold:
                totalFP += 1
            else:
                totalTN += 1
                
            self.timeResults[prompt["prompt"]] = {"Time": indvEnd, "Similarity": maxSimilarity, "Prompt": maxPrompt}
            indvTimes.append(indvEnd)
            
        finalTime = time.time() - startTime
        averageTime = np.mean(indvTimes)
        self.timeResults["Total Time"] = finalTime
        self.timeResults["Average Time"] = averageTime
        self.f1Results["Total"] = {"TP": totalTP, "FP": totalFP, "FN": totalFN, "TN": totalTN}
    
    def exportTime(self):
        with open("timeResults.json", "w") as f:
            json.dump(self.timeResults, f, indent=4)
            
    def exportF1(self):
        with open("f1Results.json", "w") as f:
            json.dump(self.f1Results, f, indent=4)
                    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        print("Usage: python semantics.py <promptFile>")
        sys.exit(1)
    checkPrompts = CheckPrompts(args[0])
    checkPrompts.checkPromptBERT()
    checkPrompts.exportTime()
    checkPrompts.exportF1()