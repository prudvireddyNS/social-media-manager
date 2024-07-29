from agents import get_crews
from crewai import Crew
from utils import send_email_with_company_details, post_image_and_text
import streamlit as st
from dotenv import load_dotenv
from tools import generate_images_and_add_to_blog, generate_video

load_dotenv()


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