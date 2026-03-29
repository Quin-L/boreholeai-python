# BoreholeAI Python SDK

Python SDK for the [BoreholeAI](https://boreholeai.com) API. Digitise borehole logs programmatically — upload PDFs or images, get structured ground profiles, test data, and annotated PDFs.

## Installation

```bash
pip install boreholeai
```

## Quick Start

```python
from boreholeai import BoreholeAI

client = BoreholeAI(api_key="bhai_your_api_key_here")

# Process a single borehole log
result = client.process_documents("BH01.pdf", output_dir="./results")

print(f"Pages processed: {result.num_pages}")
for f in result.files:
    print(f"  {f.filename}")
```

## Folder Processing

Pass a directory path to process multiple files together. Results are merged into a single ground profile Excel, test data Excel, and AGS file, with one annotated PDF per input file.

```python
result = client.process_documents("./borehole_logs/", output_dir="./results")

# Output:
#   Borehole_ground_profile.xlsx   (merged from all input files)
#   Borehole_test_data.xlsx        (merged from all input files)
#   Borehole_ags4.ags              (merged from all input files)
#   BH01_annotated.pdf             (one per input file)
#   BH02_annotated.pdf
#   BH03_annotated.pdf
```

## Supported File Types

- PDF (`.pdf`)
- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- TIFF (`.tif`, `.tiff`)
- WebP (`.webp`)

## API Key

Get your API key from the [BoreholeAI dashboard](https://boreholeai.com/app/settings/api-keys).

```python
# Pass directly
client = BoreholeAI(api_key="bhai_xxx")

# Or use for local development / testing
client = BoreholeAI(api_key="bhai_xxx", base_url="http://localhost:8000")
```

## Error Handling

```python
from boreholeai import BoreholeAI, InsufficientCreditsError, AuthenticationError

client = BoreholeAI(api_key="bhai_xxx")

try:
    result = client.process_documents("borehole.pdf")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("Not enough credits — buy more at boreholeai.com")
```

## Response

`process_documents()` returns a `JobResult`:

```python
@dataclass
class JobResult:
    job_id: str              # Unique job identifier
    status: str              # "completed"
    num_pages: int           # Total pages processed
    credits_used: int        # Credits consumed
    files: list[FileResult]  # Downloaded result files

@dataclass
class FileResult:
    filename: str            # e.g. "Borehole_ground_profile.xlsx"
    path: Path               # Local path where file was saved
```

## License

MIT
