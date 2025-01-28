import os
import re

def process_files_with_regex(input_directory, output_directory):
    """Process .objectTranslation files with regex to handle <value> tags and remove comments."""
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.endswith(".objectTranslation") and "en_US" not in filename:
            # Define file paths
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)
            
            # Extract language code from filename (e.g., 'fr' from 'sqx_c-fr.objectTranslation')
            language_code = filename.split('-')[-1].split('.')[0]
            
            try:
                # Read file content
                with open(input_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                def replace_value_tag(match):
                    """Update <value> tags by appending the language code if not already present."""
                    value_content = match.group(1).strip()

                    # Remove comments if present
                    if value_content.startswith("<!--") and value_content.endswith("-->"):
                        value_content = value_content[4:-3].strip()

                    # Remove [Deprecated] if it exists
                    value_content = value_content.replace("[Deprecated]", "").strip()

                    # Remove the trailing ']' if it exists
                    if value_content.endswith("]"):
                        value_content = value_content.rstrip("]")

                    # Append the language code only if it is not already present
                    if language_code not in value_content:
                        updated_value = f"{value_content} {language_code}" if value_content else language_code
                    else:
                        updated_value = value_content  # No need to append if language code is already in the value

                    return f"<value>{updated_value}</value>"  # Ensure this returns the correct value

                def remove_all_comments(match):
                    """Remove comments for all fields except <value> tags."""
                    tag_name = match.group(1)
                    tag_content = match.group(2).strip()
                    # If content is a comment, strip it
                    if tag_content.startswith("<!--") and tag_content.endswith("-->"):
                        tag_content = tag_content[4:-3].strip()
                    return f"<{tag_name}>{tag_content}</{tag_name}>"

                # Apply regex to update <value> tags
                updated_content = re.sub(r"<value>(.*?)</value>", replace_value_tag, content, flags=re.DOTALL)

                # Apply update to each row for other tags
                updated_content = re.sub(r"<(\w+)>(.*?)</\1>", remove_all_comments, updated_content, flags=re.DOTALL)

                # Write the updated content to the output file
                with open(output_path, 'w', encoding='utf-8') as file:
                    file.write(updated_content)
                
                print(f"Processed and saved: {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Input and output directories
input_directory = "./Test/testy"
output_directory = "./Test/testy"

# Run the script
process_files_with_regex(input_directory, output_directory)
