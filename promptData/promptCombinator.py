import json
import random

prefixes = []
suffixes = []
payloads = []

table_names = ["users", "passwords", "credentials"]
database_names = ["customer_db", "employee_db", "finance_db"]
column_names = ["username", "password", "email", "ssn"]
file_paths = ["/etc/passwd", "/var/log/syslog", "/home/user/.ssh/id_rsa"]
role_names = ["admin", "root"]


with open("promptData/malicious_prompts_generated.json", "r") as f:
    data = json.load(f)
    prompts = data["prompts"]
    for prompt in prompts:
        full_payload = prompt
        if "<table_name>" in full_payload:
            table_name = random.choice(table_names)
            full_payload = full_payload.replace("<table_name>", table_name)
        if "<database_name>" in full_payload:
            database_name = random.choice(database_names)
            full_payload = full_payload.replace("<database_name>", database_name)
        if "<column_name>" in full_payload:
            column_name = random.choice(column_names)
            full_payload = full_payload.replace("<column_name>", column_name)
        if "<file_path>" in full_payload:
            file_path = random.choice(file_paths)
            full_payload = full_payload.replace("<file_path>", file_path)
        if "<role_name>" in full_payload:
            role_name = random.choice(role_names)
            full_payload = full_payload.replace("<role_name>", role_name)
        payloads.append(full_payload)

with open("promptData/prefix.txt", "r") as f:
    prefixes = [line.strip() for line in f if line.strip()]

with open("promptData/suffix.txt", "r") as f:
    suffixes = [line.strip() for line in f if line.strip()]

composite_prompts = []
for payload in payloads:
    prefix_list = random.sample(prefixes, k=3)
    suffix_list = random.sample(suffixes, k=3)
    #generate all combinations of the selected prefixes and suffixes with the payload
    for prefix in prefix_list:
        for suffix in suffix_list:
            composite_prompt = f"{prefix} {payload} {suffix}"
            composite_prompts.append(composite_prompt)

with open("promptData/composite_malicious_prompts.txt", "w") as f:
    for prompt in composite_prompts:
        f.write(prompt + "\n")