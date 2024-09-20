import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64
from concurrent.futures import ThreadPoolExecutor

st.title('The TitleMetaInator')

MAX_THREADS = 10

def extract_metadata(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.HTTPError as http_err:
        return url, f"HTTP error occurred: {http_err}", None
    except requests.RequestException as e:
        return url, f"Error occurred: {e}", None

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.title.string if soup.title else None
    meta_description = soup.find('meta', attrs={"name": "description"})
    meta_content = meta_description['content'] if meta_description else None

    return url, title, meta_content

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="extracted_metadata.csv">Download CSV file</a>'

# Instructions section
st.header("Instructions")
st.write("""
1. **Upload a CSV file**. The app will automatically extract URLs from the first column.
2. Each row in this column should contain a full URL (including `http` or `https`) from which you want to extract the title and meta description.
3. The app will process these URLs and provide a downloadable CSV file with the extracted metadata.
""")

uploaded_file = st.file_uploader("Upload a CSV file:", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Fetch the first column (ignoring the header)
    urls = df.iloc[:, 0].dropna().tolist()  # Fetching the first column and dropping blank rows

    data = {'URL': [], 'Title': [], 'Meta Description': []}

    with st.spinner("Fetching metadata..."):
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            progress_bar = st.progress(0)
            for i, (url, title, meta_description) in enumerate(executor.map(extract_metadata, urls)):
                data['URL'].append(url)
                data['Title'].append(title)
                data['Meta Description'].append(meta_description)

                # Update the progress bar
                progress = int(100 * (i+1) / len(urls))
                progress_bar.progress(progress)

    st.write(pd.DataFrame(data))
    st.markdown(get_csv_download_link(pd.DataFrame(data)), unsafe_allow_html=True)

# About the App section in the sidebar
st.sidebar.header("About the TitleMetaInator")
st.sidebar.text("This app extracts the title and meta description for each URL from a CSV file.")
st.sidebar.text("Made by Jonathan Boshoff. Get more AI SEO strategies at:")
st.sidebar.markdown("[jonathanboshoff.com](https://jonathanboshoff.com)")
