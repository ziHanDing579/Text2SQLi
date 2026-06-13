import pandas as pd

fileOne = "gemini_labelled_train.csv"
fileTwo = "gemini_labelled_val.csv"
fileThree = "gemini_labelled_test.csv"
fileFour = "gemini_labelled_imba_data.csv"
fileFive = "SQLShieldOnly.csv"

classes = ["Reconnaissance", "Modification", "Exfiltration", "Escalation", "Disruption", "Benign"]

# There are individual columns with either 0 or 1 for each of the first five classes
# If all of those columns are 0, then the label is benign
# Headers: text,Reconnaissance,Modification,Exfiltration,Escalation,Disruption

fileOneDF = pd.read_csv(fileOne)
fileTwoDF = pd.read_csv(fileTwo)
fileThreeDF = pd.read_csv(fileThree)
fileFourDF = pd.read_csv(fileFour)
fileFiveDF = pd.read_csv(fileFive)

def count_classes(df):
    class_counts = {cls: 0 for cls in classes}
    for _, row in df.iterrows():
        if row.iloc[1:].sum() == 0:
            class_counts["Benign"] += 1
        else:
            for cls in classes[:-1]:  # Exclude "Benign"
                if row[cls] == 1:
                    class_counts[cls] += 1
    return class_counts

train_counts = count_classes(fileOneDF)
val_counts = count_classes(fileTwoDF)
test_counts = count_classes(fileThreeDF)
imba_counts = count_classes(fileFourDF)
sqlshield_counts = count_classes(fileFiveDF)
print("Training Set Class Distribution:")
print(train_counts)
print("\nValidation Set Class Distribution:")
print(val_counts)
print("\nTest Set Class Distribution:")
print(test_counts)
print("\nImbalanced Set Class Distribution:")
print(imba_counts)
print("\nSQLShield Only Set Class Distribution:")
print(sqlshield_counts)

#count total number of samples, malicious samples is total samples - benign samples
total_train_samples = len(fileOneDF)
total_val_samples = len(fileTwoDF)
total_test_samples = len(fileThreeDF)
total_imba_samples = len(fileFourDF)
malicious_train_samples = total_train_samples - train_counts["Benign"]
malicious_val_samples = total_val_samples - val_counts["Benign"]
malicious_test_samples = total_test_samples - test_counts["Benign"]
malicious_imba_samples = total_imba_samples - imba_counts["Benign"]
malicious_sqlshield_samples = len(fileFiveDF) - sqlshield_counts["Benign"]
print(f"Total Training Samples: {total_train_samples}, Malicious Training Samples: {malicious_train_samples}, Benign Training Samples: {train_counts['Benign']}")
print(f"Total Validation Samples: {total_val_samples}, Malicious Validation Samples: {malicious_val_samples}, Benign Validation Samples: {val_counts['Benign']}")
print(f"Total Test Samples: {total_test_samples}, Malicious Test Samples: {malicious_test_samples}, Benign Test Samples: {test_counts['Benign']}")
print(f"Total Imbalanced Samples: {total_imba_samples}, Malicious Imbalanced Samples: {malicious_imba_samples}, Benign Imbalanced Samples: {imba_counts['Benign']}")
print(f"Total SQLShield Only Samples: {len(fileFiveDF)}, Malicious SQLShield Only Samples: {malicious_sqlshield_samples}, Benign SQLShield Only Samples: {sqlshield_counts['Benign']}")
