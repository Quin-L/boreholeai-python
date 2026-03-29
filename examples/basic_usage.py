"""Basic usage example for the BoreholeAI Python SDK."""

from boreholeai import BoreholeAI

# Initialize client with your API key
client = BoreholeAI(api_key="bhai_your_api_key_here")

# Process a single PDF
result = client.process_documents("path/to/borehole.pdf", output_dir="./results")

print(f"Job ID: {result.job_id}")
print(f"Pages processed: {result.num_pages}")
print(f"Credits used: {result.credits_used}")
print(f"Output files:")
for f in result.files:
    print(f"  {f.filename} → {f.path}")


# Process a folder of PDFs and images (merged output)
result = client.process_documents("path/to/logs/", output_dir="./results")

print(f"\nBatch job ID: {result.job_id}")
print(f"Total pages: {result.num_pages}")
for f in result.files:
    print(f"  {f.filename} → {f.path}")
