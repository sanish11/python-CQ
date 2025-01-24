import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Use logging.INFO for less verbose logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("process_stf.log"),  # Log to a file
        logging.StreamHandler()  # Log to the console
    ]
)

# Define constants
REMOVE_KEYWORDS = [
    "SF_Rendition_Provider_Callout",
    "Total_Number_Of_Incomplete_Action_Plans",
    "SQX_User_Job_Function__c.compliancequest__Uniqueness_Constraint.FieldLabel",
    "SQX_SFC_VIEW_URL"
]

RETAIN_METADATA = [
    "Language code: ",
    "Type: Bilingual",
    "Translation type: Metadata",
    "------------------TRANSLATED-------------------",
    "# KEY\tLABEL\tTRANSLATION\tOUT OF DATE",
]

def escape_special_chars(text):
    """
    Escapes special characters in a text string.
    """
    return text.replace("\t", "\\t").replace("\n", "\\n").replace("\r", "\\r")

def process_stf_file(input_file, output_file, language_code, char_limit=255):
    """
    Processes a Salesforce Translation (.stf) file to handle issues such as:
    - Removing unwanted keywords.
    - Retaining necessary metadata.
    - Truncating field lengths based on predefined limits.

    :param input_file: Path to the input .stf file.
    :param output_file: Path to save the processed file.
    :param language_code: Language code to append translations (e.g., 'es', 'fr').
    :param char_limit: Maximum allowed character length for any field.
    """
    try:
        logging.info(f"Starting processing of file: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        processed_lines = []
        key_map = defaultdict(list)
        metadata_retention_active = True

        for line in lines:
            stripped_line = line.strip()

            # Skip lines containing specified keywords
            if any(keyword in stripped_line for keyword in REMOVE_KEYWORDS):
                logging.debug(f"Skipped line due to keyword: {stripped_line}")
                continue

            # Skip flow elements
            if stripped_line.startswith("Flow."):
                logging.debug(f"Skipped flow element: {stripped_line}")
                continue

            # Retain metadata lines
            if metadata_retention_active:
                if any(metadata in stripped_line for metadata in RETAIN_METADATA) or \
                   stripped_line.startswith("#KEY") or \
                   stripped_line.lower().startswith("customfield"):
                    processed_lines.append(stripped_line)
                    logging.debug(f"Retained metadata line: {stripped_line}")
                    
                    # Stop retaining metadata after the first "CustomField" line
                    if stripped_line.lower().startswith("customfield"):
                        metadata_retention_active = False
                    continue

            # Process and transform valid key-value pairs
            match = re.match(r"^([^\t]+)\t([^\t]+)$", stripped_line)
            if match:
                key, label = match.groups()
                translation = f"{escape_special_chars(label)} {language_code}"
                
                # Apply truncation rules based on key types
                if "FieldLabel" in key or "CrtColumn" in key or "WebTab" in key:
                    translation = translation[:39]
                elif "RelatedListLabel" in key:
                    translation = translation[:80]

                replacement = f"{key}\t{escape_special_chars(label)}\t{translation}\t-"
                processed_lines.append(replacement)
                logging.debug(f"Processed and transformed line: {replacement}")

        # Write the processed lines to the output file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("\n".join(processed_lines) + "\n")

        logging.info(f"Processing completed successfully. Output saved to: {output_file}")

    except Exception as e:
        logging.error(f"An error occurred during processing: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Processes Salesforce Translation (.stf) files with issue handling, including "
                    "character limits, keyword removal, and metadata retention."
    )
    parser.add_argument("input_file", help="Path to the input .stf file")
    parser.add_argument("output_file", help="Path to save the processed .stf file")
    parser.add_argument("language_code", help="Language code to append (e.g., 'es', 'fr')")
    parser.add_argument("--char_limit", type=int, default=255, help="Maximum character length for fields (default: 255)")

    args = parser.parse_args()
    process_stf_file(args.input_file, args.output_file, args.language_code, args.char_limit)
