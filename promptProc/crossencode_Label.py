from transformers import pipeline
from datasets import load_dataset
from transformers.pipelines.pt_utils import KeyDataset # Import KeyDataset
import argparse
import pathlib
import csv

def parse_args():
    parser = argparse.ArgumentParser(description="Zero-shot classification using Hugging Face transformers.")
    parser.add_argument("--file", type=str, required=True, help="Input the file to classify")
    return parser.parse_args()

def process_file(file_path:pathlib.Path):
    output_csv = file_path.stem + "_labeled.csv"
    output_filepath = pathlib.Path(output_csv)
    print(f"Output will be saved to: {output_filepath}")
    classes_verbalized = ["Reconnaissance", "Credential and Data Exfiltration", "Unauthorized Manipulation", "Privilege Escalation", "Denial of Service"]
    hypothesis_template = "This is a text about {}"
    zeroshot_classifier = pipeline("zero-shot-classification", model="MoritzLaurer/deberta-v3-large-zeroshot-v2.0", device=0)

    #Write header and create dataset
    with open(output_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['text', 'label'] + classes_verbalized)
    
    dataset = load_dataset('csv', 
                           data_files=str(file_path))['train']
    
    results = zeroshot_classifier(KeyDataset(dataset, "text"), 
                                  classes_verbalized, 
                                  hypothesis_template=hypothesis_template, 
                                  multi_label=True,
                                  batch_size=16)

    print(results)

    if isinstance(results, dict):
        results = [results]

    # Append results to CSV
    with open(output_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        for i, result in enumerate(results):
            text = dataset[i]['text']
            label = dataset[i]['label']
            preprocessed_scores = {cls: score for cls, score in zip(result['labels'], result['scores'])}
            preprocessed_scores_in_order = [preprocessed_scores[cls] for cls in classes_verbalized]
            csvwriter.writerow([text, label] + preprocessed_scores_in_order)
            print(f"Processed line {i+1}: True label: {label}, Scores: {preprocessed_scores_in_order}")

if __name__ == "__main__":
    args = parse_args()
    file_path = pathlib.Path(args.file)
    process_file(file_path)