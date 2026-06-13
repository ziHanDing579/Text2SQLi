import pandas as pd
from sklearn.model_selection import train_test_split
import json
import numpy as np

fileOne = "D:\Text2SQLi\mixed_questions_bal_v2_labeled.csv"
fileTwo = "D:\Text2SQLi\mixed_questions_imba_labeled.csv"
fileThree = "D:\Text2SQLi\\bert_time_results_0.60_bal_miscasd.json"
fileFour = "D:\Text2SQLi\SQLShieldComb_labeled.csv"
fileFive = "D:\Text2SQLi\\bert_time_results_0.60_SQLShield.json"

df1 = pd.read_csv(fileOne)
df2 = pd.read_csv(fileTwo)
df3 = pd.read_csv(fileFour)
sim_scores_BERT = []
sim_scores_BERT_2 = []

with open(fileThree, 'r') as f:
    bert_data = json.load(f)
    for key, item in bert_data.items():
        if key == "Total Time":
            break
        sim_scores_BERT.append(item['Similarity'])

with open(fileFive, 'r') as f:
    bert_2_data = json.load(f)
    for key, item in bert_2_data.items():
        if key == "Total Time":
            break
        sim_scores_BERT_2.append(item['Similarity'])
    
df1['Maliciousness'] = sim_scores_BERT
df3['Maliciousness'] = sim_scores_BERT_2

def min_max_normalize(series):
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        return series.apply(lambda x: 0.5)  # If all values are the same, return 0.5 for all
    return (series - min_val) / (max_val - min_val)

def soft_l2_normalize(row, epsilon=3e-3):
    norm = np.sqrt(np.sum(row**2)) + epsilon
    return row / norm 

cols_to_normalize = df1.columns[1:-1]  # Assuming the first column is 'text' and the last column is 'Maliciousness'
df1[cols_to_normalize] = df1[cols_to_normalize].astype(float)
df3[cols_to_normalize] = df3[cols_to_normalize].astype(float)

#drop the 'label' column
df1 = df1.drop('label', axis=1)
df2 = df2.drop('label', axis=1)
df3 = df3.drop('label', axis=1)

df1.iloc[:, 1:-1] = df1.iloc[:, 1:-1].apply(soft_l2_normalize, axis=1, result_type='broadcast')
df2.iloc[:, 1:-1] = df2.iloc[:, 1:-1].apply(soft_l2_normalize, axis=1, result_type='broadcast')
df3.iloc[:, 1:-1] = df3.iloc[:, 1:-1].apply(soft_l2_normalize, axis=1, result_type='broadcast')

train_size_1 = int(0.7 * len(df1))
val_size_1 = int(0.1 * len(df1))
test_size_1 = len(df1) - train_size_1 - val_size_1
train_size_2 = int(0.7 * len(df2))
val_size_2 = int(0.1 * len(df2))
test_size_2 = len(df2) - train_size_2 - val_size_2
train_size_3 = int(0.7 * len(df3))
val_size_3 = int(0.1 * len(df3))
test_size_3 = len(df3) - train_size_3 - val_size_3

train_df1, temp_df1 = train_test_split(df1, train_size=train_size_1, random_state=42)
val_df1, test_df1 = train_test_split(temp_df1, test_size=test_size_1, random_state=42)
train_df2, temp_df2 = train_test_split(df2, train_size=train_size_2, random_state=42)
val_df2, test_df2 = train_test_split(temp_df2, test_size=test_size_2, random_state=42)
train_df3, temp_df3 = train_test_split(df3, train_size=train_size_3, random_state=42)
val_df3, test_df3 = train_test_split(temp_df3, test_size=test_size_3, random_state=42)

#save each split as csv for both files
train_df1.to_csv('mixed_questions_bal_labeledv2_train_dataset.csv', index=False)
val_df1.to_csv('mixed_questions_bal_labeledv2_val_dataset.csv', index=False)
test_df1.to_csv('mixed_questions_bal_labeledv2_test_dataset.csv', index=False)
train_df2.to_csv('mixed_questions_imba_labeled_train_dataset.csv', index=False)
val_df2.to_csv('mixed_questions_imba_labeled_val_dataset.csv', index=False)
test_df2.to_csv('mixed_questions_imba_labeled_test_dataset.csv', index=False)
train_df3.to_csv('mixed_questions_SQLShield_labeled_train_dataset.csv', index=False)
val_df3.to_csv('mixed_questions_SQLShield_labeled_val_dataset.csv', index=False)
test_df3.to_csv('mixed_questions_SQLShield_labeled_test_dataset.csv', index=False)