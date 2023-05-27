"""
This code fetches all of Yu Hua's books from a repo.
Then it uses jieba for word segmentation and frequency count.
The result is a dataframe of the most common substantive words in Yu Hua's books.
"""
#Run in Google Colab

import jieba
import pandas as pd
from collections import defaultdict
import requests
import urllib.parse

# List of main character names in Chinese characters
main_characters = ['余华', '许三观', '许玉兰', '方铁匠']  # Add main character names here

# Create a custom words list and combine it with main character names
custom_words = ['卖血']
custom_words += main_characters

# Load stop words
stop_words_url = "https://raw.githubusercontent.com/goto456/stopwords/master/cn_stopwords.txt"
response = requests.get(stop_words_url)
stop_words = response.text.strip().split("\n")

# List of unwanted words
unwanted_words = ['对许']  # Add unwanted words here

# Combine stop words and unwanted words
stop_words += unwanted_words

def extract_word_frequency_from_file(file_url):
    # Fetch the raw content of the file
    response = requests.get(file_url)
    text = response.text
    
    # Step 2: Add custom words to Jieba dictionary
    for word in custom_words:
        jieba.add_word(word)
    
    # Step 3: Word Segmentation with stop words filtering and unwanted words removal
    tokens = jieba.cut(text)
    filtered_tokens = [
        token for token in tokens if token not in stop_words and len(token) > 1
    ]
    
    # Step 4: Word Frequency Calculation
    word_freq = defaultdict(int)
    for token in filtered_tokens:
        word_freq[token] += 1
    
    return word_freq

# GitHub API URL to retrieve repository contents
api_url = "https://api.github.com/repos/xzs603/books/contents/txt"

# Fetch the repository contents using the GitHub API
response = requests.get(api_url)
contents = response.json()

# List to store the file URLs and names
file_urls = []
file_names = []

# Process each content item
for content in contents:
    if content["type"] == "file" and content["name"].endswith(".txt") and "余华" in content["name"]:
        file_urls.append(content["download_url"])
        file_names.append(urllib.parse.unquote(content["name"]))

# Print the list of file URLs
print("List of File URLs:")
for url in file_urls:
    print(url)

# Create an empty DataFrame to store the results
df_result = pd.DataFrame(columns=['File', 'Word', 'Frequency'])

# Process each file URL
for file_url, file_name in zip(file_urls, file_names):
    # Extract word frequency from the file
    word_frequency = extract_word_frequency_from_file(file_url)
    
    # Create a DataFrame from the word frequency data
    df = pd.DataFrame(word_frequency.items(), columns=['Word', 'Frequency'])
    
    # Add the file name to the DataFrame
    df['File'] = file_name
    
    # Append the DataFrame to the result DataFrame
    df_result = pd.concat([df_result, df], ignore_index=True)

# Sort the result DataFrame by frequency in descending order
df_result_sorted = df_result.sort_values(by='Frequency', ascending=False)

# Show the head 50 rows of the DataFrame
df_result_sorted.head(50)
