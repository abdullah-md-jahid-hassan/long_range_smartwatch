"""
Utilities for file manipulation.
"""
import os

def copy_env_keys_only(source_file: str, destination_file: str, with_values: bool = False) -> None:
    """
    Copy the environment variables from a .env style file.
    
    Reads a source file and writes out the content. If `with_values` is False,
    only the key portion up to the first '=' character is written.
    
    Args:
        source_file (str): The path to the source .env file.
        destination_file (str): The path to the destination file.
        with_values (bool): If True, copy the entire key=value line. Default is False.
    """
    if not os.path.exists(source_file):
        raise FileNotFoundError(f"Source file not found: {source_file}")
        
    with open(source_file, "r", encoding="utf-8") as src:
        lines = src.readlines()
        
    # Ensure the destination directory exists
    dest_dir = os.path.dirname(destination_file)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)
        
    with open(destination_file, "w", encoding="utf-8") as dest:
        for line in lines:
            line_stripped = line.strip()
            
            # If a line does not contain "=", preserve it as is (comments, empty lines)
            if "=" not in line_stripped:
                dest.write(line)
                continue
                
            if with_values:
                # Copy the entire line exactly as it is
                dest.write(line)
            else:
                # Copy characters only until the first "=" and do not copy the value
                # Preserves line order
                key = line_stripped.split("=", 1)[0]
                dest.write(f"{key}=\n")
