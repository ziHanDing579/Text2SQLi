import csv
filename1 = "mixed_questions_bal.csv"
filename2 = "mixed_questions_imba_labeled.csv"

count1 = 0
count2 = 0
total1 = 0
total2 = 0

with open(filename1, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        total1 += 1
        if row[-1] == '1':
            count1 += 1

with open(filename2, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip header
    for row in reader:
        total2 += 1
        if row[-1] == '1':
            count2 += 1

print(f"File: {filename1} - Benign: {count1}, Total: {total1}, Percentage: {count1/total1:.2%}")
print(f"File: {filename2} - Benign: {count2}, Total: {total2}, Percentage: {count2/total2:.2%}")