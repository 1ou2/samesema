# samesema
Same Semantic

# installation
```python
python3 -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
```

# Data loading
Get wikipedia dump in French from mirror :
```wget https://mirror.accum.se/mirror/wikimedia.org/dumps/frwiki/20240820/frwiki-20240820-pages-articles-multistream.xml.bz2```


## Parse
The raw dump is in XML format, and contains, metadata,links. We use ```wikiextractor``` module to extract the text 
```wikiextractor ./frwiki-latest-pages-articles3.xml-p2550823p2977214.bz2 -o outputdir --json```

