import mlcroissant as mlc
import itertools

# Fetch the Croissant JSON-LD for the dataset
url = 'https://www.kaggle.com/datasets/utsh0dey/global-medicine-directory-and-healthcare-dataset/croissant/download'
croissant_dataset = mlc.Dataset(url)

# Print available record sets to identify the correct identifier name
record_sets = [rs.id for rs in croissant_dataset.metadata.record_sets]
print("Available Record Sets:", record_sets)

# Use the first available record set automatically (or specify it by name if known)
if record_sets:
    file_path = record_sets[0]
    print(f"Using record set: {file_path}")
    
    # Fetch the records
    record_set = croissant_dataset.records(record_set=file_path)
    print("First 5 records:", list(itertools.islice(record_set, 5)))
else:
    print("No record sets found in the dataset metadata.")
