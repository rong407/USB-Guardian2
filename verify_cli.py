import sys
import json
import os

from metadata_tool import extract_metadata
from api_client import search_by_hash
from utils import sha256


def verify_file(file_path):

    if not os.path.exists(file_path):
        print("❌ File not found")
        return

    print(f"\n🔍 Analyzing: {file_path}")

    # 1. Extract metadata
    raw = extract_metadata(file_path)

    if not raw:
        print("❌ No metadata found")
        return

    # 2. Parse JSON
    try:
        fp = json.loads(raw)
    except:
        print("❌ Invalid metadata format")
        return

    # 3. Show fingerprint
    print("\n=== 📌 Fingerprint ===")
    for k, v in fp.items():
        print(f"{k:12}: {v}")

    # 4. Query server
    print("\n🌐 Querying server...")
    result = search_by_hash(fp["hash"])

    # 5. Show result
    print("\n=== 🔎 Trace Result ===")

    current_hash = sha256(file_path)
    if current_hash != fp["hash"]:
    	print("⚠ WARNING: File modified!")


    if result and "status" not in result:
        print("✅ SOURCE FOUND\n")
        for k, v in result.items():
            print(f"{k:12}: {v}")
    else:
        print("❌ NOT FOUND IN SERVER")


def main():

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python verify_cli.py <file>")
        print("  python verify_cli.py <folder>")
        return

    path = sys.argv[1]

    # single file
    if os.path.isfile(path):
        verify_file(path)

    # folder scan
    elif os.path.isdir(path):
        print(f"\n📂 Scanning folder: {path}\n")
        for file in os.listdir(path):
            full_path = os.path.join(path, file)
            if os.path.isfile(full_path):
                verify_file(full_path)

    else:
        print("❌ Invalid path")


if __name__ == "__main__":
    main()
