import hashlib

def generate_hash(file_path, algorithm="sha256"):
    with open(file_path, "rb") as f:
        data = f.read()

    if algorithm == "sha256":
        obj = hashlib.sha256(data)
    elif algorithm == "md5":
        obj = hashlib.md5(data)
    else:
        raise ValueError("Unsupported algorithm")

    return obj.hexdigest()