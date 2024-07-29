from agents import get_crews
from crewai import Crew
from utils import send_email_with_company_details, post_image_and_text
import streamlit as st
from dotenv import load_dotenv
from tools import generate_images_and_add_to_blog, generate_video

load_dotenv()


import json
import os
from pprint import pprint

private_key_id = os.getenv('private_key_id')
private_key = os.getenv('private_key')
client_email = os.getenv('client_email')
client_id = os.getenv('client_id')
auth_uri = os.getenv('auth_uri')
token_uri = os.getenv('token_uri')
auth_provider_x509_cert_url = os.getenv('auth_provider_x509_cert_url')
client_x509_cert_url = os.getenv('client_x509_cert_url')
universe_domain =  os.getenv("universe_domain")

service_account_info = {
    "type": "service_account",
    "project_id": os.getenv('PROJECT_ID'),
    "private_key_id": private_key_id,
    "private_key": private_key,
    "client_email": client_email,
    "client_id": client_id,
    "auth_uri": auth_uri,
    "token_uri": token_uri,
    "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
    "client_x509_cert_url": client_x509_cert_url,
    "universe_domain": universe_domain
}
pprint(service_account_info)

with open('service_account.json', 'w') as f:
    json.dump(service_account_info, f, indent=2)

token = os.getenv('token')
refresh_token = os.getenv('refresh_token')
token_uri = os.getenv('token_uri')
client_id_mail = os.getenv('client_id_mail')
client_secret = os.getenv('client_secret')
scopes = os.getenv('scopes')
universe_domain = os.getenv('universe_domain')
account = os.getenv('account')
expiry = os.getenv('expiry')

token_info = {
    "token": token,
    "refresh_token": refresh_token,
    "token_uri": token_uri,
    "client_id": client_id_mail,
    "client_secret": client_secret,
    "scopes": ["https://www.googleapis.com/auth/gmail.send"],
    "universe_domain": universe_domain,
    "account": account,
    "expiry": expiry
}
pprint(token_info)

with open('token.json', 'w') as f:
    json.dump(token_info, f)

info_crew, blog_crew, video_crew, linkedin_crew = get_crews()

def info(website_url):
    company_summary = info_crew.kickoff(inputs={'website':website_url})
    return company_summary

def blog(topic, company_summary):
    blog_content = blog_crew.kickoff(inputs={'topic': topic, 'company_summary':company_summary})
    md_file_path, docx_file_path, img_path = generate_images_and_add_to_blog(blog_content)
    return blog_content, md_file_path, docx_file_path, img_path

def video(topic, company_summary):
    pairs = video_crew.kickoff(inputs={'topic':topic, 'company_summary':company_summary})
    video_path = generate_video(pairs, topic)
    return video_path

def linkedin(blog_content, image_path, token):
    linkedin_confirmation = linkedin_crew.kickoff(inputs={'blog':blog_content, 'image_path':image_path, 'token':token})
    # linkedin_confirmation = post_image_and_text(token, title, article, image_path)
    return linkedin_confirmation

def Main(topic, website_url, token, email):

    company_summary = info(website_url)
    print(company_summary)

    blog_content, md_file_path, docx_file_path, img_path = blog(topic, company_summary)
    print(blog_content)
    print(md_file_path)
    print(docx_file_path)
    print(img_path)

    video_path = video(topic, company_summary)
    print(video_path)

    if token is not None:
        linkedin_confirmation = linkedin(blog_content, img_path, token)
        print(linkedin_confirmation)

    send_email_with_company_details(email, 'DIGIOTAI SOLUTIONS', title) 

st.title("Social Media Manager")

logo_url = 'https://www.digiotai.com/wp-content/uploads/2018/08/Digotai-Logo-Mobile.png'
st.sidebar.image(logo_url)

title = st.text_input("Topic")
url = st.text_input("Social Media Url")
email = st.text_input("Email ID")

token = None
if st.checkbox(label='LinkedIn'):
    token = st.text_input('Enter you LinkedIn access token')


if st.button("Generate"):
    if title and url and email:

        st.success("Blog and Video will be sent to your email.")
        
        Main(title, url, token, email)

        # send_email_with_company_details(email, 'DIGIOTAI SOLUTIONS', title)
        

    else:
        st.error("Please provide all inputs.")