import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

files_map = {
    "01_fund_master.csv": "1vxvhJB2gVKsLfv51pXcLa39hnOr7M6vZ",
    "02_nav_history.csv": "10GfFYNtj-yqUoJ05zxkFhti0DkEW_CuZ",
    "03_aum_by_fund_house.csv": "1SY1wVj6aU3coZcPVE5DuWxUOj5mtUP4T",
    "04_monthly_sip_inflows.csv": "1NoQEbNNZyenLShtBM4CRjrh6c5lhx5Qy",
    "05_category_inflows.csv": "1M-OqSJBEz-so0Q69PzMZBq10ON_WaI17",
    "06_industry_folio_count.csv": "1rgkdnDbv0GcjZgfdczqr7kkVB7cGBz4s",
    "07_scheme_performance.csv": "1N65c5EcrgYQmDJUAs8cxyZnp9WV10izk",
    "08_investor_transactions.csv": "1zRk1hIJ1gF2vmmYbXFuKmpaFDzTiFIFj",
    "09_portfolio_holdings.csv": "1O2cXuQhc8SMOcYY38fCJF7IErOqaP6iv",
    "10_benchmark_indices.csv": "13VZkUoJlyXADh3M9kbaXLi9cVEJs_76s"
}

def download_files():
    for filename, file_id in files_map.items():
        url = f"https://docs.google.com/uc?export=download&id={file_id}"
        dest_path = RAW_DIR / filename
        print(f"Downloading {filename} from Google Drive...")
        try:
            # Simple download using urllib
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read()
                
            # If the response contains a GDrive confirmation/virus scan page, we might need to handle it.
            # But for files < 100MB, uc?export=download works directly.
            with open(dest_path, "wb") as f:
                f.write(content)
            print(f"Saved {filename} to {dest_path}")
        except Exception as e:
            print(f"Error downloading {filename}: {e}")

if __name__ == "__main__":
    download_files()

