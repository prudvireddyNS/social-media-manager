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
    "project_id": os.getenv('project_id'),
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


import streamlit as st
from own_agents import ResearchAgent, BlogAgent, VideoAgent, LinkedinAgent, TwitterAgent, EmailAgent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

blog_status = None
video_status = None
linkedin_status = None
twitter_status = None

st.title("Social Media Manager")

# Inputs for the topic and URL
topic = st.text_input("Enter the topic")
url = st.text_input("Enter the URL")
to_mail = st.text_input("Enter your Email")

# Options to generate content
options = st.multiselect("Select what to generate", ["Blog", "Video", "LinkedIn Post", "Twitter Tweet"])

# Conditional display for LinkedIn credentials
if "LinkedIn Post" in options:
    st.subheader("LinkedIn Credentials")
    linkedin_token = st.text_input("LinkedIn Access Token", type="password")

# Conditional display for Twitter credentials
if "Twitter Tweet" in options:
    st.subheader("Twitter Credentials")
    twitter_consumer_key = st.text_input("Twitter Consumer Key", type="password")
    twitter_consumer_secret = st.text_input("Twitter Consumer Secret", type="password")
    twitter_access_token = st.text_input("Twitter Access Token", type="password")
    twitter_access_token_secret = st.text_input("Twitter Access Token Secret", type="password")

if st.button("Generate"):
    if topic and url and options:
        if "LinkedIn Post" in options and not linkedin_token:
            st.warning("Please enter the LinkedIn Access Token.")
        elif "Twitter Tweet" in options and not all([twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret]):
            st.warning("Please enter all Twitter credentials.")
        else:
            llm = ChatOpenAI(model='gpt-4o-mini')
            research_agent = ResearchAgent(llm, url, topic)

            with st.spinner("Researching content..."):
                summarized_content = research_agent.research()

            if "Blog" in options:
                with st.spinner("Creating Blog..."):
                    with st.expander("Blog"):
                        blog_agent = BlogAgent(llm, topic, url, summarized_content)
                        blog_status = blog_agent.generate_blog()
                        st.markdown(blog_status)

            if "Video" in options:
                with st.spinner("Creating Video..."):
                    with st.expander("Video"):
                        video_agent = VideoAgent(llm, topic, summarized_content)
                        video_status = video_agent.create_video()
                        st.write(video_status)  

            if "LinkedIn Post" in options:
                with st.spinner("Creating LinkedIn Post..."):
                    with st.expander("LinkedIn Post"):
                        linkedin_agent = LinkedinAgent(llm, topic, url, summarized_content)
                        linkedin_status = linkedin_agent.post_on_linkedin(linkedin_token)
                        st.write(linkedin_status)

            if "Twitter Tweet" in options:
                with st.spinner("Creating Twitter Tweet..."):
                    with st.expander("Twitter Tweet"):
                        twitter_agent = TwitterAgent(llm, topic, url, summarized_content)
                        twitter_status = twitter_agent.post_on_twitter(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)
                        st.write(twitter_status)
            
            email_agent = EmailAgent(llm, to_mail)
            mail = email_agent.send_email(to_mail, blog_status, video_status, linkedin_status, twitter_status)
                    
    else:
        st.warning("Please enter a topic, URL, and select at least one option.")













# from agents import get_crews
# from crewai import Crew
# from utils import send_email_with_company_details, post_image_and_text
# import streamlit as st
# from dotenv import load_dotenv
# from tools import generate_images_and_add_to_blog, generate_video

# load_dotenv()




# info_crew, blog_crew, video_crew, linkedin_crew = get_crews()

# def info(website_url):
#     company_summary = info_crew.kickoff(inputs={'website':website_url})
#     return company_summary

# def blog(topic, company_summary):
#     blog_content = blog_crew.kickoff(inputs={'topic': topic, 'company_summary':company_summary})
#     md_file_path, docx_file_path, img_path = generate_images_and_add_to_blog(blog_content)
#     return blog_content, md_file_path, docx_file_path, img_path

# def video(topic, company_summary):
#     pairs = video_crew.kickoff(inputs={'topic':topic, 'company_summary':company_summary})
#     video_path = generate_video(pairs, topic)
#     return video_path

# def linkedin(blog_content, image_path, token):
#     linkedin_confirmation = linkedin_crew.kickoff(inputs={'blog':blog_content, 'image_path':image_path, 'token':token})
#     # linkedin_confirmation = post_image_and_text(token, title, article, image_path)
#     return linkedin_confirmation

# def Main(topic, website_url, token, email):

#     company_summary = info(website_url)
#     print(company_summary)

#     blog_content, md_file_path, docx_file_path, img_path = blog(topic, company_summary)
#     print(blog_content)
#     print(md_file_path)
#     print(docx_file_path)
#     print(img_path)

#     video_path = video(topic, company_summary)
#     print(video_path)

#     if token is not None:
#         linkedin_confirmation = linkedin(blog_content, img_path, token)
#         print(linkedin_confirmation)

#     send_email_with_company_details(email, 'DIGIOTAI SOLUTIONS', title) 

# st.title("Social Media Manager")

# logo_url = 'https://www.digiotai.com/wp-content/uploads/2018/08/Digotai-Logo-Mobile.png'
# st.sidebar.image(logo_url)

# title = st.text_input("Topic")
# url = st.text_input("Social Media Url")
# email = st.text_input("Email ID")

# token = None
# if st.checkbox(label='LinkedIn'):
#     token = st.text_input('Enter you LinkedIn access token')


# if st.button("Generate"):
#     if title and url and email:

#         st.success("Blog and Video will be sent to your email.")
        
#         Main(title, url, token, email)

#         # send_email_with_company_details(email, 'DIGIOTAI SOLUTIONS', title)
        

#     else:
#         st.error("Please provide all inputs.")
