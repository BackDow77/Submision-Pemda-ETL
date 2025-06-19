import pandas as pd
import logging
from utils.extract import scrape_main, parse_data
from utils.transform import transform_data
from utils.load import load_data, save_to_google_sheets
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_first_sheet_name(spreadsheet_id: str, creds_file: str) -> str:
    """Get the name of the first sheet/tab from the spreadsheet."""
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    creds_path = os.path.join(BASE_DIR, creds_file)

    creds = Credentials.from_service_account_file(
        creds_path, scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"]
    )
    service = build('sheets', 'v4', credentials=creds)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = sheet_metadata.get('sheets', [])
    first_sheet_title = sheets[0]['properties']['title']
    logging.info(f"📄 Detected sheet/tab name: '{first_sheet_title}'")
    return first_sheet_title

def main():
    output_file = "cleaned_products.csv"
    creds_file = "google-sheets-api.json"
    spreadsheet_id = "1auX4EssPpV-hpMycDyKVODwLz0_GzrLEDoH-B7Z-OMo"

    try:
        # Deteksi nama sheet pertama secara otomatis
        sheet_name = get_first_sheet_name(spreadsheet_id, creds_file)
        range_name = f"{sheet_name}!A1"

        logging.info("📤 Extracting data from website...")
        df = scrape_main()

        if df.empty:
            logging.warning("⚠️ Extracted DataFrame is empty. Skipping transformation and loading.")
            return

        logging.info("🧼 Transforming and cleaning data...")
        cleaned_df = transform_data(df)

        if cleaned_df.empty:
            logging.warning("⚠️ Cleaned DataFrame is empty. No output file or upload will be created.")
        else:
            logging.info("💾 Saving cleaned data locally...")
            load_data(cleaned_df, output_file)

            logging.info(f"📤 Uploading cleaned data to Google Sheets at {range_name}...")
            save_to_google_sheets(cleaned_df, spreadsheet_id, range_name, creds_file)

    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
