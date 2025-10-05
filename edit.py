import requests
import os
from urllib.parse import urlparse

#Implement precautions that you should  take when downloading files from unknown sources.
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024

#prevent duplicates
HASH_RECORD_FILE = "downloaded_hashes.txt"  # Store hashes of downloaded files

def get_file_hash(filepath):
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def is_duplicate(file_hash):
    """Check if hash is already recorded."""
    if not os.path.exists(HASH_RECORD_FILE):
        return False
    with open(HASH_RECORD_FILE, "r") as f:
        return file_hash in f.read().splitlines()


def record_hash(file_hash):
    """Record hash of a new file."""
    with open(HASH_RECORD_FILE, "a") as f:
        f.write(file_hash + "\n")


#allows users to enter multiple urls 
def download_image(url, folder="Fetched_Images"):
    try:
        os.makedirs(folder, exist_ok=True)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

       
        # --- Check headers before saving ---
        content_type = response.headers.get("Content-Type", "").lower()
        content_length = response.headers.get("Content-Length")
        disposition = response.headers.get("Content-Disposition")

        if not content_type.startswith("image/"):
            print(f"✗ Skipped: {url} (invalid content type: {content_type})")
            return

        if content_length and int(content_length) > MAX_FILE_SIZE:
            print(f"✗ Skipped: {url} (file too large: {content_length} bytes)")
            return

        # --- Decide filename ---
        if disposition and "filename=" in disposition:
            filename = disposition.split("filename=")[-1].strip('"')
        else:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

        if not filename:
            filename = "image_" + str(abs(hash(url))) + ".jpg"
    #check file extensions
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            print(f"✗ Blocked suspicious file type: {filename}")
            return
        
        filepath = os.path.join(folder, filename)
        #save file in chuncks not as whole
        total_size = 0
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE:
                    print(f"✗ File too large: {filename}")
                    f.close()
                    os.remove(filepath)  # remove partial file
                    return
                f.write(chunk)

        print(f"✓ Successfully fetched: {filename}")
        print(f"✓ Image saved to {filepath}\n")

    except requests.exceptions.RequestException as e:
        print(f"✗ Connection error for {url}: {e}")
    except Exception as e:
        print(f"✗ An error occurred for {url}: {e}")

def main():
    print("Welcome to the Ubuntu Image Fetcher")
    print("A tool for mindfully collecting images from the web\n")
    
    # Get URL from multiple users
    urls = input("Please enter image URLs (separated by spaces or commas): ")
    
    # Convert input into a list
    url_list = [u.strip() for u in urls.replace(",", " ").split() if u.strip()]

    if not url_list:
        print("✗ No valid URLs entered.")
        return
    print(f"\nFetching {len(url_list)} images...\n")
    for url in url_list:
        download_image(url)

    print("✓ All done.")
    print("Connection strengthened. Community enriched.")
    


if __name__ == "__main__":
    main()