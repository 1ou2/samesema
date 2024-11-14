import bz2
import xml.etree.ElementTree as ET
import re,regex
from typing import Iterator
import logging
from pathlib import Path
import os

class WikiXMLProcessor:
    def __init__(self, input_file: str, output_file: str = None):
        """Initialize the Wikipedia XML processor.
        
        Args:
            input_file: Path to the bzip2 compressed XML file
            output_file: Optional path to save extracted text
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file) if output_file else None
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for the processor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    

    def remove_unwanted_sections(self, text):
        # List of section headers to remove (case insensitive)
        sections_to_remove = [
            'bibliographie',
            'liens externes',
            'notes et références',
            'références',  # sometimes used instead of "notes et références"
            'voir aussi'   # optional, if you want to remove "See also" sections too
        ]
        
        # Create pattern to match any of these sections and their content
        pattern = r'(?i)==\s*(?:' + '|'.join(sections_to_remove) + r')\s*==.*?(?=\n==[^=]|\Z)'
        
        # Remove the sections
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        return cleaned_text

    def clean_wikipedia_text(self,text):
        # First remove unwanted sections
        text = self.remove_unwanted_sections(text)
        def remove_nested_braces(text):
            result = ""
            i = 0
            while i < len(text):
                if text[i:i+2] == "{{":
                    count = 2
                    i += 2
                    while i < len(text) and count > 0:
                        if text[i:i+2] == "{{":
                            count += 2
                            i += 2
                        elif text[i:i+2] == "}}":
                            count -= 2
                            i += 2
                        else:
                            i += 1
                else:
                    result += text[i]
                    i += 1
            return result
        
        # Remove nested templates
        text = remove_nested_braces(text)
        # Remove math equations
        text = re.sub(r'<math>.*?</math>', '', text, flags=re.DOTALL)
        # Also remove inline math with dollar signs if present
        text = re.sub(r'\$.*?\$', '', text)
        # Remove displaystyle math if present
        text = re.sub(r'\\displaystyle\{.*?\}', '', text, flags=re.DOTALL)

        # for gallery images , div, timeline, mapframe
        text = re.sub(r'<gallery.*?</gallery>', '', text, flags=re.DOTALL)
        text = re.sub(r'<div.*?</div>', '', text, flags=re.DOTALL)
        text = re.sub(r'<timeline.*?</timeline>', '', text, flags=re.DOTALL)
        text = re.sub(r'<mapframe.*?</mapframe>', '', text, flags=re.DOTALL)

        # Remove escaped quotes pattern \'\' word \'\'
        text = re.sub(r"\\\'\\\'([^\\]*)\\\'\\\'", r'\1', text)
        
        # Remove table patterns with balanced braces
        table_pattern = r'\{\|(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\})*\})*\|\}'
        text = regex.sub(table_pattern, '', text)

        # {| class="wikitable
        text = re.sub(r'\{\| class=.*\|\}', '', text, flags=re.DOTALL)

        # Remove table structures {| ... |}
        text = re.sub(r'\{\|.*?\|\}', '', text, flags=re.DOTALL)
        
        # Remove content between {{ }}
        text = re.sub(r'\{\{[^\}]*\}\}', '', text)

        # Remove File/Image patterns with balanced brackets using recursive regex
        pattern = r'\[\[(?:File|Fichier|Image)\s?:(?:[^[\]]|\[(?:[^[\]]|\[(?:[^[\]]|\[(?:[^[\]]|\[(?:[^[\]]|\[[^[\]]*\])*\])*\])*\])*\])*\]\]'
        text = regex.sub(pattern, '', text,flags=re.IGNORECASE)
    
        
        # Remove wiki links [[text|display]] or [[text]]
        text = re.sub(r'\[\[([^|\]]*\|)?([^\]]+)\]\]', r'\2', text)
        
        # Remove references <ref>...</ref>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove multiple apostrophes (''' or ''''')
        text = re.sub(r"'{2,}", '', text)

        # remove tables <table> ... </table>
        text = re.sub(r'<table[^>]*>.*?</table>', '', text, flags=re.DOTALL)
        
        # remove url [http(s):// description of url]
        # do not be greedy in the regex
        text = re.sub(r'\[http[s]?://[^\]]+\]', '', text)

        # remove section titles === title ===
        text = re.sub(r'=====[^=]+=====', '', text)

        # remove section titles === title ===
        text = re.sub(r'====[^=]+====', '', text)

        # remove section titles === title ===
        text = re.sub(r'===[^=]+===', '', text)

        # remove section subtitles == subtitle ==
        text = re.sub(r'==[^=]+==', '', text)

        # remove lines that are lists, they start with ***
        text = re.sub(r'^\*\*\*.*?\n', '', text, flags=re.MULTILINE)

        # remove lines that are lists, they start with **
        text = re.sub(r'^\*\*.*?\n', '', text, flags=re.MULTILINE)

        # remove lines that are lists, they start with *
        text = re.sub(r'^\*.*?\n', '', text, flags=re.MULTILINE)

        # remove lines that starts with 4 spaces or more
        # used for pseudo code
        text = re.sub(r'\n[ ]{4,}.*(?=\n|$)', '', text)

        # Remove multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = text.replace("\\'\\'", "")

        # remove '\n at begining of text
        text = re.sub(r"^'\n", '', text)
        
        # remove consecutive carriage returns
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()

    
    def extract_pages(self) -> Iterator[tuple[str, str]]:
        """Extract text from Wikipedia XML dump.
        
        Yields:
            Tuple of (title, cleaned text content) for each article
        """
        self.logger.info(f"Starting to process {self.input_file}")
        
        # Parse XML directly from bzip2 file
        with bz2.open(self.input_file, 'rt', encoding='utf-8') as f:
            context = ET.iterparse(f, events=('end',))
            
            # Track progress
            page_count = 0
            
            for event, elem in context:
                if page_count > 10000:
                    break
                if elem.tag.endswith('page'):
                    try:
                        # Find title and text elements
                        title = elem.find('.//{*}title').text
                        # sonic adventure
                        if title.startswith("Hierosonic"):
                            print("Found it")
                        text = elem.find('.//{*}text').text
                        process_page = True
                        # do not process Portail or project pages
                        skip_categories = ["Portail:", "Projet:","Catégorie:","Wikipedia:","Wikipédia:"]
                        for category in skip_categories:
                            if title.startswith(category):
                                process_page = False
                                break

                        if text and not self._is_redirect(text) and process_page:
                            cleaned_text = title + "\n" + self.clean_wikipedia_text(text)
                            # check if text contains the word "width"
                            # it probably means that the cleanup failed and html code is still present
                            black_list = ["width","colspan","valign","align=","upright="]
                            for word in black_list:
                                if word in cleaned_text:
                                    process_page = False
                                    break
                            if cleaned_text and process_page:
                                page_count += 1
                                if page_count % 1000 == 0:
                                    self.logger.info(f"Processed {page_count} pages")
                                yield title, cleaned_text
                    
                    except AttributeError:
                        self.logger.warning(f"Skipping page due to missing title or text")
                    
                    # Clear element to save memory
                    elem.clear()
    
    def _is_redirect(self, text: str) -> bool:
        """Check if page is a redirect."""
        return text.startswith('#REDIRECT') or text.startswith('#redirect')
    
    def process_dump(self, batch_size: int = 1000) -> list[str]:
        """Process the entire dump and optionally save to file.
        
        Args:
            batch_size: Number of articles to process at once
            
        Returns:
            List of processed text documents
        """
        documents = []
        current_batch = []
        
        for title, text in self.extract_pages():
            current_batch.append(text)
            
            if len(current_batch) >= batch_size:
                documents.extend(current_batch)
                if self.output_file:
                    self._save_batch(current_batch)
                current_batch = []
        
        # Handle remaining documents
        if current_batch:
            documents.extend(current_batch)
            if self.output_file:
                self._save_batch(current_batch)
        
        self.logger.info(f"Completed processing {len(documents)} documents")
        return documents
    
    def _save_batch(self, batch: list[str]):
        """Save a batch of documents to file."""
        with open(self.output_file, 'a', encoding='utf-8') as f:
            for doc in batch:
                f.write(doc + '\n\n')

# Example usage
if __name__ == '__main__':

    data_dir = "data/"
    processed_dir = "processed/"
    os.makedirs(processed_dir, exist_ok=True)

    # files are in bzip2 format
    for filename in os.listdir(data_dir):
        if filename.endswith(".bz2"):
            input = data_dir + filename
            print(f"Preprocessing {input}")
            processor = WikiXMLProcessor(
                input_file=input,
                output_file=processed_dir + filename[:-4] + "--.txt"
            )
            
            # Process the dump and get the documents
            documents = processor.process_dump(batch_size=1000)