Getting Started With The Sefaria API
The Sefaria API
The Sefaria API allows live access to Sefaria's structured database of Jewish texts and their interconnections. It is designed to make getting a new web or mobile app up-and-running as simple as possible.

Welcome to the Sefaria API Reference.
Here you will find documentation and interactive playgrounds for many of our most important API endpoints. Our reference is powered by our OpenAPI spec, which you can see here.

🚧
Work-In-Progress

Please note, this reference is a work-in-progress. We are always striving to refine and improve our API itself, as well as our documentation. We are looking forward to documenting additional endpoints here in the future. Looking for something you can't find? Contact us, we'd love to hear from you.

For additional documentation, check out our technical docs here.

Getting Started
There isn't much needed to get started with our API; all of our currently documented endpoints can be reached without needing any API keys, tokens or authorization.

Need a Simple Example? In this tutorial, we guide you step-by-step through a very simple script that uses a handful of our endpoints.

Looking to Dive Deep? You can jump right into our API Reference here

Still Puzzled? - You can see what others have asked or contact us for help!

API Pathways
Below are a few different pathways through the Sefaria API for individuals seeking to acquaint themselves with specific aspects of our data. Organized by use case, these entry points can assist you in navigating to the data you need as you're learning the API.

Where are the books?
At its core, Sefaria is an open-source digital library of Jewish books. To see all of the books available right now on Sefaria, see the Table of Contents. To retrieve all of the metadata related to a specific book, try out the Index (v2) endpoint.

Ready to dive into some text data?
Start with Texts (v3) to retrieve text editions, along with all of the metadata for that given version. Dive into the Versions endpoint to see all available editions of a given book.

Links, Links, Links
One of the most powerful aspects of Sefaria's data is the links, and other relations, between various texts. To get started with seeing all of the links, check out our very powerful Related API. This is your ticket to retrieve related commentaries on a verse, parallel passages, and more.

Trying to build something based on a learning schedule?
Explore our Calendars API to find data about all of the different study schedules tracked on Sefaria.

Topics
Interested in our Sefaria curation of Topics, and the associated texts? Check out the Topic Graph endpoint to retrieve interrelated topics, and the Ref-Topic-Links endpoint to retrieve all of the topics associated with a given text.

Interested in Images?
Use our Social Media Image endpoint to generate nice graphics based on a segment of text of your choosing.

Alternatively, if you are looking for a manuscript image, see the Manuscripts endpoint to retrieve correlating manuscript pages for a given text.

Need a dictionary?
Check out the Lexicon endpoint and Word Completion endpoint to get started.

Building something for non-English speakers?
Use our Languages API to see all of the various languages on Sefaria, and query Translations to see all text editions available for that language. Then, head over to the Texts (v3) to query the specific text you need.

Random
Need a random text? See Random Text and Random By Topic endpoints.

Updated about 1 month ago

What’s Next
Tutorial: Dvar Torah Outliner

Texts (v3)
get
https://www.sefaria.org/api/v3/texts/{tref}
The most up-to-date way to retrieve texts from Sefaria via the API, with enhanced control over language, language direction, and other parameters.

Log in to see full request history
time	status	user agent	
2m ago	
200

Path Params
tref
string
required
A Sefaria-specific reference, Ref. This should be a segment Ref (the most specific reference possible), or bottom level section Ref (i.e. a section of text one level up. A section is an array of segments). If a Ref which is not a segment or bottom level section is passed, the response will be to the first bottom level section Ref (e.g. Genesis will resolve to the bottom level section Ref of Genesis 1)

Query Params
version
string
There are two possible forms for the string passed as the version:

language
language|versionTitle
When in the form of language, the primary version of that language is returned in the versions field of the response object. When in the form of language|versionTitle, only that specific version is returned in the versions field.

Notes:

language is the full English name of the language. In cases of dialectics with varying sub-specifities, please pass the ‘mother’ language (so for example, arabic rather than judeo-arabic). This field is NOT case sensitive.
versionTitle is the exact English versionTitle of the given version in the Sefaria database.
When only language is passed, the response will return a single version of the text in that language, the one that is highest priority in the Sefaria database.
Requests can have more than one version param. If no version was passed, the API defaults to version=primary.
Special Values
The following values can be passed in as special values to the version parameter.

source: When version=source is passed, it retrieves the text in its "source" language (i.e. the original language the text was written in, versus a translation).
translation: When version=translationis passed, it retrieves a translation of the text.
primary: When version=primary is passed, it retrieves the primary text as per the Sefaria database (i.e. the isPrimary field on the version in the database is set to True). Usually the text returned is identical to what is returned with the special value of source, but it can also include other languages (e.g. Hebrew for the Kuzari, which was originally written in Judeo-Arabic)
all: get all texts in the required language.
If a required version is missing that information will be under the field warnings of the response.

fill_in_missing_segments
string
This parameter is only relevant for cases where the requested text is incomplete (i.e. not all of the segments in the requested version exist in the database for that text, such as a partial translation).

When fill_in_missing_segments=1, the segments of text that are missing in the requested version will be filled by other versions of the same language.

This value defaults to 0.


return_format
string
Defaults to default
This parameter formats the text that will be returned from the v3 texts/ API. It can have one of four values:

text_only - This strips footnotes, inline references, and all HTML tags from the returned text.
strip_only_footnotes - This strips only the footnotes and commentator tags without stripping the other HTML tags.This is useful for the native app, where we do not display footnotes.
wrap_all_entities - This wraps the HTML for links and topic links.
default - This returns the basic text as it is saved in Sefaria’s DB.

import requests

url = "https://www.sefaria.org/api/v3/texts/tref"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)

Translations
get
https://www.sefaria.org/api/texts/translations/{lang}
Returns a dictionary of texts translated into lang, organized by the Sefaria category & secondary category of each title.

Log in to see full request history
time	status	user agent	
Make a request to see history.

Path Params
lang
string
required
An ISO 639-1 language code.

en

import requests

url = "https://www.sefaria.org/api/texts/translations/en"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)