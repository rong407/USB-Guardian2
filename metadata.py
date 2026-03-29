import json

def embed_metadata(file_path, fingerprint):

    ext = file_path.split(".")[-1].lower()

    if ext in ["txt"]:
        with open(file_path, "a") as f:
            f.write("\nFP:" + fingerprint)

    elif ext in ["jpg", "png"]:
        try:
            from PIL import Image
            img = Image.open(file_path)
            img.save(file_path, "PNG")
        except:
            pass

    # NOTE: extend สำหรับ pdf/docx/xlsx ได้
