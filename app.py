import streamlit as st
import openai
from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os

load_dotenv()

firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')
firecrawl_app = FirecrawlApp(api_key=firecrawl_api_key)

openai.api_key = os.getenv('OPENAI_API_KEY')

st.title("FAQ Generator for Websites")

url = st.text_input("Enter the URL of the website:")
action = st.selectbox("Choose Action", ["scrape", "crawl"])

if st.button("Generate FAQ"):
    if not url:
        st.error("Please enter a URL.")
    else:
        try:
            if action == "scrape":
                scrape_result = firecrawl_app.scrape_url(url, params={'formats': ['markdown']})
                content = scrape_result.get('markdown', '')
            else:
                crawl_status = firecrawl_app.crawl_url(
                    url, 
                    params={'limit': 100, 'scrapeOptions': {'formats': ['markdown']}}
                )
                content = crawl_status.get('markdown', '')

            if content:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                              {"role": "user", "content": f"Generate a FAQ section based on the following content:\n\n{content}"}],
                    max_tokens=500
                )
                faq = response['choices'][0]['message']['content'].strip()
                st.subheader("Generated FAQ")
                st.write(faq)
                st.download_button("Download FAQ as Text", faq, file_name="faq.txt")

            else:
                st.error("No content found in the scrape/crawl result.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")