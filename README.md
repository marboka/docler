I reused previous components and decided to have a very similiar setup for uploading and handling synonyms, to uploading and handling the words.  
I created a new page in gradio where you can upload a synonym CSV, which shoud have the following structure: <br />
<pre>word,synonym
Moon,Apollo 11
Moon,Moon Mission</pre>
Words should not have spaces before or after in the CSV. This CSV is case insensitive.  

First you should upload your CSV of words, and then upload your synonym CSV, becuase the synonyms will be checked against the words, and we ignore those which are not present in the words. The user is informed by this, but this functionalty could be improved.  

I created the following endpoints:
- /upload-synonym-csv/
- /purge-synonym/
- /task-synonym-status/

I craeted a new class which handles all the logic regarding synonyms: 'tagmatch/synonym_manager.py'. Also added unit tests to 'test/synonym_manager_test'  
Synonmys are symmetric and transitive in my solution  
In the 'app.py' when we query a word, first we check if we have synonmys defined for it. If we have, we query the synonmys, combine search results, sort by semantic similarity and only show top k resuls. If not, we query the original word.
