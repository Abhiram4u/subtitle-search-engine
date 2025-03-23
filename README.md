# Shazam Clone: Subtitle Search Engine and Audio Transcription

This project is a subtitle search engine and audio transcription tool that allows users to search for movie and TV show subtitles by entering a text query or uploading an audio file. The system uses machine learning and natural language processing (NLP) techniques, such as TF-IDF and cosine similarity, to efficiently match the query with relevant subtitles from a large subtitle database.

The project also leverages AssemblyAI's API to transcribe audio files, providing a seamless way to turn spoken content into text for subtitle searching.

## Features:
- **Subtitle Search**: Search for relevant subtitles based on text queries.
- **Audio Transcription**: Upload audio files to transcribe speech into text and search subtitles based on the transcription.
- **Cosine Similarity**: Use cosine similarity to rank subtitles based on their relevance to the user's query.
- **Support for Various Audio Formats**: Works with multiple audio formats, such as MP3, WAV, FLAC, and more.

## Installation Instructions

### Step 1: Clone the repository

To get started, clone the repository to your local machine:


### Step 2: Set up the environment

Create a virtual environment (optional but recommended):



### Step 3: Install dependencies

Install all required Python libraries using the `requirements.txt` file:



### Step 4: API Setup for AssemblyAI

You'll need to sign up for an API key from [AssemblyAI](https://www.assemblyai.com/). Once you have the API key, set it in your environment or directly within the `assemblyai` configuration in the code:

##python
aai.settings.api_key = 'your-api-key-here'



### **Usage**

#markdown
## Usage Instructions

1. **Run the Streamlit App**:

   After installing dependencies, run the Streamlit app:




This will open a local web interface in your browser where you can upload audio files or enter text queries to search for subtitles.

2. **Subtitle Search**:
- Enter your text query in the search bar, and the app will return the most relevant subtitles based on cosine similarity.

3. **Audio Transcription**:
- Upload an audio file (in MP3, WAV, FLAC, or other formats), click "Transcribe," and the app will display the transcription of the audio.
- The transcribed text will be automatically used to search for relevant subtitles.

4. **Subtitle Information**:
- After searching, the app will display the subtitle name, ID, similarity score, and a link to view more details on OpenSubtitles.





# Download the large files from the following links:
- [Download Subtitle Database (SQLite)](https://drive.google.com/file/d/1GS7KvI1z2-5I-oB_x4ik7nrIRuGIgiUC/view?usp=sharing)
- [Download Processed Data (Pickle)](https://drive.google.com/file/d/1v3f5XiigYZ-WfaIlcKeVQMtnkMEmGsgw/view?usp=sharing)


## Contributing

We welcome contributions! If you would like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -am 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Create a new Pull Request with a clear description of your changes.

Please ensure your code follows the existing style and passes all tests before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


