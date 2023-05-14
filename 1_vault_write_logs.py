import subprocess
import re
import csv
from datetime import datetime
from pymongo import MongoClient

log_file = "docker_logs.txt"
csv_file = "parsed_logs.csv"

### Functions Definitions ###
def use_regex(input_text):
    pattern = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?([Zz]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?.*(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|SEVERE|FATAL).*$", re.IGNORECASE)
    return pattern.match(input_text)


### 1 ###
# Run the bash script to save docker logs
subprocess.run(["bash", "-c", "docker logs dotnet-vault_vault_1 > docker_logs.txt 2>&1"])

### 2 ###
# Open input and output files
with open(log_file, 'r') as input_file, open(csv_file, 'w') as output_file:
    # Process each line in the input file
    for line in input_file:
        # Apply regex substitution pattern
        parsed_line = re.sub(r'^([^ ]+) \[([^]]+)\] (.+)', r'\1, \2, \3', line)
        
        # Write parsed line to the output file
        output_file.write(parsed_line)

### 3 ###
def filter_log_file(file_path):
    year_pattern = r'^\d{4}'  # Regular expression pattern for matching a year at the beginning of a line
    filtered_lines = []

    with open(file_path, 'r') as file:
        for line in file:
            if re.match(year_pattern, line):
                filtered_lines.append(line)

    # Write the filtered lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(filtered_lines)

# Usage example
log_file_path = csv_file
filter_log_file(log_file_path)


# Print a success message
print('Parsing completed. Parsed logs saved to', csv_file)

### 4 ###
# Prepare to write to MongoDBs
data = []

with open('parsed_logs.csv', 'r') as file:
    csv_reader = csv.reader(file)
    for row in csv_reader:
        data.append(row)

print(data)

### 5 ###
# Write to MongoDB
def csv_to_mongodb(csv_file_path, mongodb_uri, mongodb_database, mongodb_collection):
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)
    db = client[mongodb_database]
    collection = db[mongodb_collection]

    # Open the CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        
        # Iterate over each row in the CSV file
        for row in reader:
            print(row)
            # Extract the data from each column
            timestamp_str, level, message = row[:3]
            
            # Parse the timestamp string to a datetime object
            timestamp = datetime.fromisoformat(timestamp_str[:-1])
            
            # Create a document to insert into MongoDB
            document = {
                'timestamp': timestamp,
                'level': level.strip(),
                'message': message.strip()
            }
            
            # Insert the document into the MongoDB collection
            collection.insert_one(document)

    # Disconnect from MongoDB
    client.close()

# Usage example
csv_file_path = 'parsed_logs.csv'
mongodb_uri = 'mongodb://34.215.234.156:27017'  # Replace with your MongoDB connection URI
mongodb_database = 'ccf-project'  # Replace with your target database name
mongodb_collection = 'hashicorp-vault-collection'  # Replace with your target collection name

csv_to_mongodb(csv_file_path, mongodb_uri, mongodb_database, mongodb_collection)
