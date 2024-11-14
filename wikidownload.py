import requests
from tqdm import tqdm
import re
import os

base_url = "https://dumps.wikimedia.org/frwiki/latest/"
data_dir = "data/"

os.makedirs(data_dir, exist_ok=True)

response = requests.get(base_url)

# search all dumps
# example : https://dumps.wikimedia.org/frwiki/latest/frwiki-latest-pages-articles3.xml-p2550823p2977214.bz2
pattern = r'frwiki-latest-pages-articles\w+.xml-\w+.bz2'
re.compile(pattern)
files = list(set(re.findall(pattern, response.text)))

# list all files in data dir
for f in os.listdir(data_dir):
    if f in files:
        print(f"File {f} already downloaded")
        files.remove(f)


# print(search)
for filename in files:
    # check if file was already downloaded


    url = base_url + filename
    print(url)

    # Streaming, so we can iterate over the response.
    response = requests.get(url, stream=True)

    # Sizes in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
        with open(data_dir + filename, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

    if total_size != 0 and progress_bar.n != total_size:
        raise RuntimeError("Could not download file")
    print("Download complete")
    print("Stopping after 1 iter")
    break