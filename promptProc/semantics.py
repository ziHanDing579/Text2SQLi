from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

from promptProc.promptInject import promptData

class analysis():
    def __init__(self):
        self.threshold = 0.5
        self.data = promptData.ignore_prompts
        self.text = None
        self.similarity = None
        self.vectorizer = TfidfVectorizer()
        self.vectors = None
        self.data_vectors = self.vectorizer.fit_transform(self.data.values())
    
    def set_text(self, text):
        self.text = self.split_text(text)
        self.vectors = self.vectorizer.transform(self.text)

    def split_text(self, text):
        # Split the text into sentences
        return text.split(".")
    
    def compute_similarity(self):
        for i in range(len(self.vectors)):
            # Compute the similarity between the text and the prompt data
            local_max = 0
            local_data = None
            for j in range(len(self.data_vectors)):
                similarity = np.dot(self.vectors[i].toarray(), self.data_vectors[j].toarray().T)
                if similarity > local_max:
                    local_max = similarity
                    local_data = self.data.keys()[j]
            
            self.similarity.append((local_max, local_data))
        return self.similarity
    
    def flag_prompts(self):
        flags = []
        for i in range(len(self.similarity)):
            if self.similarity[i][0] > self.threshold:
                flags.append(self.text[i], self.similarity[i][1])
        
        return flags