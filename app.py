import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import base64

st.title('URL Metadata Extractor')

@st.cache
def extract_metadata(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.RequestException as e:
        st.error(f"Error fetching URL {url}: {e}")
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.title.string if soup.title else None
    meta_description = soup.find('meta', attrs={"name": "description"})
    meta_content = meta_description['content'] if meta_description else None

    return title, meta_content

def get_csv_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="extracted_metadata.csv">Download CSV file</a>'

uploaded_file = st.file_uploader("Upload a CSV file:", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    urls = df.iloc[:, 0].tolist()  # Fetching the first column

    titles = []
    meta_descriptions = []

    for url in urls:
        title, meta_description = extract_metadata(url)
        titles.append(title)
        meta_descriptions.append(meta_description)

    df_output = pd.DataFrame({
        'URL': urls,
        'Title': titles,
        'Meta Description': meta_descriptions
    })

    st.write(df_output)
    st.markdown(get_csv_download_link(df_output), unsafe_allow_html=True)

# About the App section in the sidebar
st.sidebar.header("About the App")
st.sidebar.text("This app extracts the title and meta description for each URL from a CSV file.")
st.sidebar.text("Powered by AI for SEO strategies.")
st.sidebar.markdown("[jonathanboshoff.com](https://jonathanboshoff.com)")
