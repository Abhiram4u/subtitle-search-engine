import sqlite3
import re
import random
import pickle
import numpy as np
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
import assemblyai as aai
import tempfile

# Set up AssemblyAI API key
aai.settings.api_key = "426f3fbd27f946dd8e87df11195759d2"
transcriber = aai.Transcriber()

# -----------------------------
# Preprocessing Data (Initial Setup)
# -----------------------------

# Step 1: Connect to the SQLite database
def get_data_from_db():
    conn = sqlite3.connect('eng_subtitles_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT num, name, content FROM zipfiles")  # Include subtitle name
    rows = cursor.fetchall()
    return rows

# Step 2: Clean subtitle content
def clean_subtitle(content):
    text = content.decode('latin-1', errors='ignore')  # Decode binary content

    # Remove timestamps using regular expressions
    text = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', text)
    
    # Remove non-alphanumeric characters (keeping spaces, digits, and letters)
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    
    # Clean up extra spaces, newlines, etc.
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces with one and remove trailing spaces
    text = re.sub(r'\r\n', ' ', text)  # Replace carriage returns/newlines
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Keep only alphabetic characters and spaces
    
    # Replace multiple spaces with a single space and strip leading/trailing spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Optionally, remove unwanted special characters (only keep printable ASCII characters)
    allowed_chars = string.ascii_letters + string.digits + string.punctuation + " "
    text = ''.join([char for char in text if char in allowed_chars])

    return text

# Step 3: Get a sample of subtitles (for large datasets)
def get_sample_data(rows, sample_size=0.2):
    sample_rows = random.sample(rows, int(len(rows) * sample_size))
    return [(num, name, clean_subtitle(content)) for num, name, content in sample_rows]

# Step 4: Vectorization using TF-IDF and save results
def preprocess_and_save_data():
    # Fetch data from the database
    rows = get_data_from_db()
    
    # Sample and clean the data
    subtitles = get_sample_data(rows)

    # Extract subtitle content and IDs
    documents = [content for _, _, content in subtitles]
    subtitle_ids = [num for num, _, _ in subtitles]
    subtitle_names = [name for _, name, _ in subtitles]
    
    # Vectorize the subtitles
    vectorizer = TfidfVectorizer(stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents)
    
    # Save processed data
    with open('processed_data.pkl', 'wb') as f:
        pickle.dump({
            'vectorizer': vectorizer,
            'doc_vectors': doc_vectors,
            'subtitle_ids': subtitle_ids,
            'subtitle_names': subtitle_names,
            'subtitles': subtitles
        }, f)
    
    print("Data preprocessing and saving complete!")

# ---------------------------
# Querying Functionality (for Streamlit UI)
# ---------------------------

# Step 1: Load preprocessed data (stored in pickle file)
def load_preprocessed_data():
    with open('processed_data.pkl', 'rb') as f:
        data = pickle.load(f)
    return data

# Step 2: Vectorize user query and compute similarity
def vectorize_query(query, vectorizer):
    return vectorizer.transform([query])

# Step 3: Compute cosine similarity
def compute_similarity(query_vector, doc_vectors):
    similarities = cosine_similarity(query_vector, doc_vectors)
    return similarities.flatten()

# Step 4: Get top subtitles based on similarity
def get_top_subtitles(similarity_scores, subtitles, subtitle_names, top_n=10):
    top_indices = similarity_scores.argsort()[-top_n:][::-1]  # Get top N
    return [(subtitle_names[i], subtitles[i][0], similarity_scores[i], subtitles[i][2]) for i in top_indices]

# ---------------------------
# Audio Transcription Functionality
# ---------------------------

# Function to transcribe audio using AssemblyAI
def transcribe_audio(uploaded_file):
    with st.spinner('Transcribing your audio...'):
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_audio_path = temp_file.name

        # Transcribe the audio using AssemblyAI
        transcript = transcriber.transcribe(temp_audio_path)

        # Display the transcription result
        st.success("Transcription complete!")
        return transcript.text

# ---------------------------
# Streamlit UI
# ---------------------------

def create_ui():
    st.title("Shazam Clone: Subtitle Search Engine and Audio Transcription")

    # Load preprocessed data
    data = load_preprocessed_data()
    vectorizer = data['vectorizer']
    doc_vectors = data['doc_vectors']
    subtitle_ids = data['subtitle_ids']
    subtitle_names = data['subtitle_names']
    subtitles = data['subtitles']

    # Section for audio upload and transcription
    st.header("Upload Audio for Transcription")
    uploaded_file = st.file_uploader("Choose an audio file (any format)", type=["mp3", "wav", "flac", "m4a", "aac", "ogg"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format=uploaded_file.type)
        
        if st.button("Transcribe"):
            transcribed_text = transcribe_audio(uploaded_file)
            st.text_area("Transcribed Text", transcribed_text, height=200)
            
            # Use the transcribed text as a search query
            user_query = transcribed_text
            st.write(f"Searching for: {user_query}")

            # Vectorize the user query
            query_vector = vectorize_query(user_query, vectorizer)

            # Compute the cosine similarity between the query and subtitles
            similarity_scores = compute_similarity(query_vector, doc_vectors)

            # Get the top subtitles based on similarity scores
            top_subtitles = get_top_subtitles(similarity_scores, subtitles, subtitle_names)

            # Display the results
            if top_subtitles:
                for subtitle_name, subtitle_id, score, content in top_subtitles:
                    # Create the OpenSubtitles link for the subtitle
                    subtitle_link = f"https://www.opensubtitles.org/en/subtitles/{subtitle_id}"

                    # Display the subtitle information
                    st.write(f"**Subtitle Name**: {subtitle_name}")
                    st.write(f"**Subtitle ID**: {subtitle_id}")
                    st.write(f"**Similarity Score**: {score:.4f}")
                    #st.write(f"**Subtitle Text**: {content[:200]}...")  # Show first 200 chars of the subtitle content
                    st.markdown(f"[More details on OpenSubtitles]({subtitle_link})")  # Display the link
                    st.markdown("---")
            else:
                st.write("No relevant subtitles found.")
    else:
        # Regular search query section
        st.header("Search Subtitles")
        user_query = st.text_input("Enter your search query:", "")

        # If the user has entered a query
        if user_query:
            st.write(f"Searching for: {user_query}")

            # Vectorize the user query
            query_vector = vectorize_query(user_query, vectorizer)

            # Compute the cosine similarity between the query and subtitles
            similarity_scores = compute_similarity(query_vector, doc_vectors)

            # Get the top subtitles based on similarity scores
            top_subtitles = get_top_subtitles(similarity_scores, subtitles, subtitle_names)

            # Display the results
            if top_subtitles:
                for subtitle_name, subtitle_id, score, content in top_subtitles:
                    # Create the OpenSubtitles link for the subtitle
                    subtitle_link = f"https://www.opensubtitles.org/en/subtitles/{subtitle_id}"

                    # Display the subtitle information
                    st.write(f"**Subtitle Name**: {subtitle_name}")
                    st.write(f"**Subtitle ID**: {subtitle_id}")
                    st.write(f"**Similarity Score**: {score:.4f}")
                    #st.write(f"**Subtitle Text**: {content[:200]}...")  # Show first 200 chars of the subtitle content
                    st.markdown(f"[More details on OpenSubtitles]({subtitle_link})")  # Display the link
                    st.markdown("---")
            else:
                st.write("No relevant subtitles found.")

# ---------------------------
# Main Function to Run the App
# ---------------------------

if __name__ == "__main__":
    # Run this function once to preprocess data and save it
    #preprocess_and_save_data()  # Uncomment to preprocess and save data (Only once)
    
    create_ui()
