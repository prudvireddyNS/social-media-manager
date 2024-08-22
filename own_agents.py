from utils import twitter_tweet, post_image_and_text, upload_file, PARENT_FOLDER_ID, send_email
from tools import generate_image_openai, generate_video
import nltk
from nltk.corpus import stopwords
import re
from tools import generate_images_and_add_to_blog, extract_relevant_sections_from_website

# from dotenv import load_dotenv
# load_dotenv()

# llm = ChatOpenAI(model='gpt-4o-mini')

class ResearchAgent():
    def __init__(self, llm, url, topic) -> None:
        self.llm = llm
        self.url = url
        self.topic = topic

        nltk.download('stopwords')
        self.stop_words = set(stopwords.words('english'))

    def select_keywords(self):

        core_terms = [term.strip().lower() for term in self.topic.split() if term.isalpha()]
        filtered_keywords = [keyword for keyword in core_terms if keyword.lower() not in self.stop_words and len(keyword) > 1]

        prompt = (
            f"Generate a list of relevant keywords related to the topic '{self.topic}'. "
            f"These keywords should help in filtering relevant content from a website. "
            f"Keywords from the topic are {filtered_keywords}. Remove useless and add newly generated. "
            f"Output format: A list of keywords, separated by commas."
        )
        response = self.llm.invoke(prompt)
        keywords = response.content.strip()

        keyword_list = [keyword.strip() for keyword in keywords.split(',') if keyword]

        filtered_keywords = [keyword for keyword in keyword_list if keyword.lower() not in self.stop_words and len(keyword) > 1]

        return filtered_keywords

    def scrape_relevant_content(self, keywords):
        try:
            content = extract_relevant_sections_from_website(self.url, keywords)
            return content
        except Exception as e:
            print(f"Error while scraping content: {e}")
            return {}

    def filter_content(self, scraped_content):
        prompt = (
            f"Given the topic '{self.topic}', evaluate the relevance of the following content. "
            f"Content is considered relevant if it partially or slightly related to the topic. "
            f"For each content piece, output 'yes' or 'no' based on this criterion.\n\n"
        )

        filtered_content = {}
        for url, text in scraped_content.items():
            full_prompt = f"{prompt}Content: {text}\n\nRelevance:"
            relevance = self.llm.invoke(full_prompt).content.strip()
            print(relevance, url)
            if "yes" in relevance.lower():
                filtered_content[url] = text

        return filtered_content


    def summarize_content(self, content):
        summarized_content = {}
        for url, text in content.items():
            prompt = (
                f"Summarize how the company contributes to or solves the topic '{self.topic}' using the extracted sections from their website({url}). "
                f"Expected Output: A comprehensive summary explaining the company's role in addressing the topic."
                f"\n{text}\n\nSummary:"
            )
            summary = self.llm.invoke(prompt).content
            summarized_content[url] = summary
        return summarized_content

    def research(self):
        keywords = self.select_keywords()
        print(f"Selected Keywords: {keywords}")
        
        if not keywords:
            print("No keywords generated, stopping research.")
            return {}
        
        scraped_content = self.scrape_relevant_content(keywords)
        print(f"Scraped Content: {scraped_content}")
        
        if not scraped_content:
            print("No content scraped, stopping research.")
            return {}

        filtered_content = self.filter_content(scraped_content)
        print(f"Filtered Content: {filtered_content}")
        
        if not filtered_content:
            print("No relevant content found, stopping research.")
            return {}

        summarized_content = self.summarize_content(filtered_content)
        print(f"Summarized Content: {summarized_content}")
        
        return summarized_content
    
class BlogAgent():
    def __init__(self, llm, topic, url, summarized_content) -> None:
        self.llm = llm
        self.topic = topic
        self.url = url
        self.summarized_content = summarized_content

    def generate_text(self):
        prompt = (
            f"Write a comprehensive blog post based on the following details:\n\n"
            f"Topic: {self.topic}\n"
            f"Company's website: {self.url}\n"
            f"Summarized content:\n{self.summarized_content}\n\n"
            f"The blog should include an engaging introduction, detailed sections about how the company addresses the topic, "
            f"and a conclusion summarizing the key points. Structure the blog with clear headings, and write it in a conversational style."
            f"Use '<-IMAGE->' placeholders: one after the introduction and another at a point where it would enhance the narrative."
            f"Output the blog in markdown format, including a title, introduction, body sections, and conclusion."
        )

        blog_content = self.llm.invoke(prompt).content.strip()

        return blog_content

    def save_blog(self, blog_content, filename="blog.md"):
        with open(filename, "w") as file:
            file.write(blog_content)
        print(f"Blog saved to {filename}")

    def add_image_prompts(self, blog_content):
        prompt = (
            "Please replace all instances of '<-IMAGE->' with specific image prompts. "
            "Each image prompt should be enclosed within '<image>' and '</image>' tags. "
            "Ensure that the image prompts avoid including any text, names of individuals, company names, logos, or other identifiable information. "
            "Think of the image prompt as 'what you want to see in the final image.' "
            "Provide a descriptive prompt that clearly defines the elements, colors, and subjects. "
            "For instance: 'The sky was a crisp (blue:0.3) and (green:0.8)' indicates a sky that is predominantly green with a hint of blue. "
            "The weights (e.g., 0.3 and 0.8) apply to all words in the prompt, guiding the emphasis of the colors and elements. "
            "While you may reduce the number of images, ensure that no two image prompts are identical."
            f"context:\n{blog_content}"
            "Expected Output: A complete blog with image prompts enclosed in <image> tags."
        )

        blog_content = self.llm.invoke(prompt).content.strip()

        return blog_content

    def add_images(self, blog_content):
        md_file, docx_file, imgs_path = generate_images_and_add_to_blog(blog_content)
        return md_file, docx_file, imgs_path
    
    def upload_to_drive(self, docx_file_path):
        blog_id = upload_file(docx_file_path, 'blog post', PARENT_FOLDER_ID)
        blog_link = f"https://drive.google.com/file/d/{blog_id}/view?usp=sharing"
        blog_status = f'Blog generated, link to blog: {blog_link}'
        return blog_status

    def generate_blog(self):
        blog_content = self.generate_text()
        self.save_blog(blog_content)
        blog_with_prompts = self.add_image_prompts(blog_content)
        blog_md, blog_doc, imgs_path = self.add_images(blog_with_prompts)
        akg = self.upload_to_drive(blog_doc)
        return akg

class VideoAgent:
    def __init__(self, llm, topic, summary) -> None:
        self.llm = llm
        self.topic = topic
        self.summary = summary

    def generate_script(self):
        prompt = (
            "Generate a video script with two narration and image prompt pairs for the following topic, focusing on the company's expertise related to the topic. "
            "The script should contain around 200 words total. Start by explaining the topic and then highlight the company's role or expertise in relation to it. "
            "Ensure that the image prompts do not include any text, names, logos, or other identifying features. "
            "Provide a descriptive image prompt that clearly defines elements, colors, and subjects. For instance, 'The sky was a crisp blue with green hues' is more descriptive than just 'blue sky'."
            f"\n\n**Topic:** \n{self.topic}\n\n"
            f"**Summary:** \n{self.summary}\n\n"
            "Expected Output: Two pairs of sentences. Enclose narration in <narration> narration here </narration> tags and image prompts in <image> image prompt here </image> tags."
        )

        script = self.llm.invoke(prompt).content.strip()
        return script
    
    def upload_to_drive(self, video_file_path):
        video_id = upload_file(video_file_path, 'video', PARENT_FOLDER_ID)
        video_link = f"https://drive.google.com/file/d/{video_id}/view?usp=sharing"
        video_status = f'Video generated, link to video: {video_link}'
        return video_status
    
    def create_video(self):
        script = self.generate_script()
        video_path = generate_video(script, self.topic)
        akg = self.upload_to_drive(video_path)
        return akg
    
class LinkedinAgent:
    def __init__(self, llm, topic, url, summary) -> None:
        self.llm = llm
        self.topic = topic
        self.summary = summary
        self.url = url

    def generate_text(self):
        prompt = (
            "Create a LinkedIn post based on the following topic and summary. The post should be professional, engaging, and suitable for a LinkedIn audience. "
            "It should introduce the topic, provide a brief summary, and include a call-to-action if relevant. The text should be concise yet informative."
            f"Topic: {self.topic}\n"
            f"Company's website: {self.url}\n"
            f"Summarized content:\n{self.summary}\n\n"
            "Expected Output: A well-structured LinkedIn post(around 250 words)."
        )
        
        post_text = self.llm.invoke(prompt).content.strip()
        return post_text
    
    def generate_image(self, post_content):
        prompt = (
            "Generate concise image prompt for the below LinkedIn Post. "
            "Think of the image prompt as 'what you want to see in the final image.' "
            "Provide a descriptive prompt that clearly defines the elements, colors, and subjects. "
            "For instance: 'The sky was a crisp (blue:0.3) and (green:0.8)' indicates a sky that is predominantly green with a hint of blue. "
            "The weights (e.g., 0.3 and 0.8) apply to all words in the prompt, guiding the emphasis of the colors and elements. "
            f"Title: {self.topic}\n"
            f"LinkedIn Post: {post_content}\n"
            "Expected Output: A concise prompt used to generate image in <image></image> tag."
        )
        response = self.llm.invoke(prompt).content.strip()
        img_prompt = re.findall(r'<image>(.*?)</?image>', response, re.DOTALL)[0]
        img_path = generate_image_openai(img_prompt, 0)
        return img_path
    
    def post_on_linkedin(self, token):
        post_content = self.generate_text()
        img_path = self.generate_image(post_content)
        akg = post_image_and_text(token, self.topic, post_content, img_path)
        return akg

class TwitterAgent:
    def __init__(self, llm, topic, url, summary) -> None:
        self.llm = llm
        self.topic = topic
        self.summary = summary
        self.url = url

    def generate_tweet(self):
        prompt = (
            "Create a short tweet of 200 characters based on the following topic and summary. The tweet should be concise, engaging, and suitable for a Twitter audience. "
            "It should introduce the topic, provide a brief summary, and include a call-to-action if relevant. "
            f"Topic: {self.topic}\n"
            f"Company's website: {self.url}\n"
            f"Summarized content:\n{self.summary}\n\n"
            "Expected Output: A well-crafted tweet. "
        )
                    # "The characters in the tweet are limited to 220. "
                    #(strictly within 250 characters)."

        tweet_text = self.llm.invoke(prompt).content.strip()
        return tweet_text
    
    def twitter_tweet(self, tweet, consumer_key, consumer_secret, access_token, access_token_secret):

        try:
            import tweepy
            print(tweet, consumer_key, consumer_secret, access_token, access_token_secret)
            client = tweepy.Client(consumer_key=consumer_key, consumer_secret=consumer_secret, 
                            access_token=access_token, access_token_secret=access_token_secret)
        
            tweet = tweet.strip('"')
            res = client.create_tweet(text=tweet)
            print(res)
            return 'Twitter tweet generated and posted to user twitter account successfully'
        except Exception as e:
            return Exception(f"Failed to tweet: {e}")

    def post_on_twitter(self, consumer_key, consumer_secret, access_token, access_token_secret):
        tweet = self.generate_tweet()
        print(len(tweet))
        akg = self.twitter_tweet(tweet, consumer_key, consumer_secret, access_token, access_token_secret)
        return akg

class EmailAgent:
    def __init__(self, llm, to_mail):
        self.llm = llm
        self.to_mail = to_mail

    def write_email(self, name, blog_status=None, video_status=None, linkedin_status=None, twitter_status=None):
        email_body_template = (
            f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; margin: 0; padding: 20px;">
                    <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">
                        <div style="text-align: center; padding-bottom: 20px; border-bottom: 1px solid #eeeeee;">
                            <h1 style="color: #333333; margin: 0;">Social Media Manager</h1>
                        </div>
                        <div style="padding: 20px;">
                            <p style="font-size: 16px; color: #333333;">Hello {name},</p>
                            <p style="font-size: 16px; color: #555555;">We’re excited to share your latest updates with you. Here’s a summary of what we’ve prepared:</p>

                            <div style="margin-top: 20px;">
                                <h3 style="color: #007BFF; font-size: 18px;">Blog Update</h3>
                                <p style="font-size: 16px; color: #555555;">{blog_status or 'No blog content available.'}</p>
                            </div>

                            <div style="margin-top: 20px;">
                                <h3 style="color: #007BFF; font-size: 18px;">Video Update</h3>
                                <p style="font-size: 16px; color: #555555;">{video_status or 'No video content available.'}</p>
                            </div>

                            <div style="margin-top: 20px;">
                                <h3 style="color: #007BFF; font-size: 18px;">LinkedIn Post Update</h3>
                                <p style="font-size: 16px; color: #555555;">{linkedin_status or 'No LinkedIn content available.'}</p>
                            </div>

                            <div style="margin-top: 20px;">
                                <h3 style="color: #007BFF; font-size: 18px;">Twitter Tweet Update</h3>
                                <p style="font-size: 16px; color: #555555;">{twitter_status or 'No Twitter content available.'}</p>
                            </div>
                        </div>
                        <div style="padding-top: 20px; border-top: 1px solid #eeeeee; text-align: center;">
                            <p style="font-size: 16px; color: #555555; margin: 0;">Thank you for using our service!</p>
                            <p style="font-size: 16px; color: #555555; margin: 0;">Best regards,<br>Your Content Team</p>
                        </div>
                    </div>
                </body>
            </html>
            """
        )
        return email_body_template

    def send_email(self, name, blog_status=None, video_status=None, linkedin_status=None, twitter_status=None):
        name = name.split('@')[0]
        email_body = self.write_email(name, blog_status, video_status, linkedin_status, twitter_status)
        subject = "Your Generated Content Update"
        send_email(self.to_mail, subject, email_body)
        return f"Email sent to {self.to_mail}!"
