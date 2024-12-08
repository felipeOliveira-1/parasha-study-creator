# Guide for Using the Sefaria API with LLMs

This document outlines how to leverage the Sefaria API effectively for generating insights, retrieving text, and building applications. 

## Table of Contents
1. [Key Features](#key-features)
2. [Core API Endpoints](#core-api-endpoints)
3. [Advanced API Endpoints](#advanced-api-endpoints)
4. [Practical Examples](#practical-examples)
5. [Integration Tips](#integration-tips)

## Key Features
1. **Structured Access to Jewish Texts**: Retrieve texts, commentaries, and their relationships.
2. **No Authentication Required**: Most endpoints are publicly accessible.
3. **Customizable Data Retrieval**: Specify text versions, translations, or format outputs.
4. **Versatile Use Cases**: Includes tools for calendars, lexicons, images, and learning schedules.

## Core API Endpoints

### 1. Texts (v3)
- **Purpose**: Fetch text data and metadata.
- **Endpoint**: `https://www.sefaria.org/api/v3/texts/{tref}`
- **Parameters**:
  - `tref`: The specific text reference (e.g., `Genesis.1.1`).
  - `version`: Specify language or text version.
  - `return_format`: Customize text output (e.g., strip footnotes).
- **Example**:
  ```python
  import requests
  response = requests.get("https://www.sefaria.org/api/v3/texts/Genesis.1.1?version=english")
  print(response.json())
  ```

### 2. Versions
- **Purpose**: Retrieve all versions of a text.
- **Endpoint**: `https://www.sefaria.org/api/texts/versions/{index}`
- **Example**:
  ```python
  response = requests.get("https://www.sefaria.org/api/texts/versions/Genesis")
  print(response.json())
  ```

### 3. Calendars
- **Purpose**: Retrieve data for Jewish learning schedules.
- **Endpoint**: `https://www.sefaria.org/api/calendars`
- **Example**:
  ```python
  response = requests.get("https://www.sefaria.org/api/calendars")
  print(response.json())
  ```

## Advanced API Endpoints

### 1. Topic (v2)
- **Purpose**: Retrieve specific topics and their relationships.
- **Endpoint**: `https://www.sefaria.org/api/v2/topics/{topic_slug}`
- **Parameters**:
  - `topic_slug`: *(required)* The slug of the desired topic
  - `annotate_links`: Add extra fields to topic links (0/1)
  - `with_links`: Include intra-topic links (0/1)
  - `annotate_time_period`: Include time period data (0/1)
  - `group_related`: Group related links (0/1)
  - `with_refs`: Include tagged references (0/1)
- **Example**:
  ```python
  url = "https://www.sefaria.org/api/v2/topics/topic_slug"
  headers = {"accept": "application/json"}
  response = requests.get(url, headers=headers)
  ```

### 2. Related Content
- **Purpose**: Find all content related to a reference.
- **Endpoint**: `https://www.sefaria.org/api/related/{tref}`
- **Returns**:
  - Links to other texts
  - User-created sheets
  - Notes and media
  - Manuscripts
  - Webpages
  - Topics
- **Example**:
  ```python
  tref = "Genesis.1.1"
  response = requests.get(f"https://www.sefaria.org/api/related/{tref}")
  related_content = response.json()
  ```

### 3. Lexicon
- **Purpose**: Search dictionary entries.
- **Endpoint**: `https://www.sefaria.org/api/words/{word}`
- **Parameters**:
  - `lookup_ref`: Refine by reference
  - `never_split`: Exact string matching
  - `always_split`: Enable substring matches
  - `always_consonants`: Prioritize consonants
- **Example**:
  ```python
  word = "בראשית"
  response = requests.get(f"https://www.sefaria.org/api/words/{word}")
  entries = response.json().get('entries', [])
  ```

### 4. Word Completion
- **Purpose**: Autocompletion for lexicon entries.
- **Endpoint**: `https://www.sefaria.org/api/words/completion/{word}/{lexicon}`
- **Parameters**:
  - `word`: Text to match
  - `lexicon`: Dictionary to search
  - `limit`: Maximum results
- **Example**:
  ```python
  word = "בר"
  lexicon = "BDB Dictionary"
  response = requests.get(
      f"https://www.sefaria.org/api/words/completion/{word}/{lexicon}",
      params={"limit": 5}
  )
  ```

## Practical Examples

### Retrieving a Weekly Parasha Study
```python
# 1. Get the weekly parasha
url = "https://www.sefaria.org/api/calendars"
response = requests.get(url)
parasha_data = response.json()

# 2. Extract parasha reference
for item in parasha_data['calendar_items']:
    if item['title']['en'] == 'Parashat Hashavua':
        parasha_ref = item['ref'].split("-")[0]

# 3. Get parasha text
text_response = requests.get(f"https://www.sefaria.org/api/v3/texts/{parasha_ref}")
text_data = text_response.json()

# 4. Get related commentaries
related_response = requests.get(f"https://www.sefaria.org/api/related/{parasha_ref}")
commentaries = [
    link['ref'] for link in related_response.json()['links'] 
    if link['type'] == 'commentary'
]

# 5. Fetch commentary text
def get_commentary_text(ref):
    url = f"https://www.sefaria.org/api/v3/texts/{ref}"
    response = requests.get(url)
    data = response.json()
    return data['title'], data['versions'][0]['text']

com1_title, com1_text = get_commentary_text(commentaries[0])
```

## Integration Tips
1. **Caching**: Minimize repeated requests for the same data.
2. **Error Handling**: Use try/except blocks to handle invalid responses.
3. **Data Parsing**: Leverage JSON structures for organized processing.
4. **Rate Limiting**: Implement delays between requests to respect API limits.
5. **Validation**: Always validate text references before making requests.

---

For additional documentation, visit the [Sefaria API reference](https://www.sefaria.org).
