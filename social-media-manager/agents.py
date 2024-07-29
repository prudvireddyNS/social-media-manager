from crewai import Agent, Task, Crew
from tools import scrape_website, generate_images_and_add_to_blog, generate_video
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from utils import post_image_and_text



def get_crews():

    llm = ChatGroq(model="llama3-70b-8192", api_key='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')
    # llm = ChatOpenAI(model='gpt-4o-mini')  
    print(llm)

    information_retriever_agent = Agent(
        role="Web Information Retriever",
        goal="To retieve all the information from the website and summarize the information.",
        backstory="You are web information retriever agent. You are expert in scraping websites and summarizing the content.",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    task_scrape = Task(
        description="Scrape all the informatin from the website: {website}.",
        expected_output="Scraped information from the website: {website}",
        agent=information_retriever_agent,
        tools=[scrape_website]
    )

    task_summarize = Task(
        description="provide a neet summary of the company. Do not add up things. ",
        expected_output="Detailed summary of a company web page. "
        # "Start with Company name, Mission and Vision, Leadership. "
        # "Explain it's Products and Services, Market presence, Financial highlights, Recent Developments and Future plans. "
        # "If there are not mentioned, explain they have mentioned."
        "Do not add up things.",
        agent=information_retriever_agent,
        context=[task_scrape]
    )

    blog_agent = Agent(
        role="Blog Writer",
        goal="Create captivating blog that inspire and educate readers.",
        backstory="You are a skilled blog writer for a company, creating insightful and engaging blog posts on various topics. You have a passion for sharing knowledge through writing. With years of experience in the industry, you know how to craft compelling narratives and provide valuable insights to your audience.",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    task_create_blog = Task(
    description=
        "Write a compelling blog on the below topic for the company."
        "Begin by explaining the topic, followed by an introduction to the company. "
        "The blog should cover various aspects relevant to {topic}, ensuring it provides comprehensive insights and value to the readers. "
        "The blog should contain only 1 image, so insert '<-IMAGE->' where image has to be inserted. One image should be after first paragraph. "
        "The blog should not contain author details."
        "**Topic:** \n\n{topic}\n\n"
        "**Company summary:** \n\n{company_summary}\n\n",
    expected_output="A full engaging and informative blog post about the topic: '{topic}'",
    # output_file="topic_blog_post.md",
    agent=blog_agent,
    # context=[task_summarize]
    )

    task_visual_prompts = Task(
        description = "Replace <-IMAGE-> with prompts.There should be only 1 image in the blog. "
        "Every prompt should be enclosed in '<image> prompt </image>' tag. "
        "The image should not contain any form of text, names of persons, company or company logo, etc.  "
        "Prompt is 'What you wish to see in the output image'. "
        "A descriptive prompt that clearly defines elements, colors, and subjects will lead to better results. "
        "For example: The sky was a crisp (blue:0.3) and (green:0.8) would convey a sky that was blue and green, but more green than blue. The weight applies to all words in the prompt. ",
        expected_output= "A full blog with prompts enclosed in '<image> prompt </image>' tag.",
        agent = blog_agent,
        context = [task_create_blog]
    )

    task_add_images = Task(
        description = "Generate images and add to blog using the provided tool. If image generation fails, stop the execution.",
        expected_output= "Path of the blog. ",
        agent = blog_agent,
        # output_file="blog_post.md",
        tools = [generate_images_and_add_to_blog],
        context = [task_visual_prompts]
    )

    content_creation_agent = Agent(
        role="Content Creator",
        goal="To generate accurate and engaging narration and image prompt pairs for video scripts and subsequently generate videos using these pairs.",
        backstory="The agent is designed to assist in creating engaging video content by generating narrations and image prompts, and then compiling them into videos.",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    task_generate_narration_image_pairs = Task(
        description = "Generate narration and image prompt pairs used for video script for the below topic for the company. The number of pairs are limited to two. Total words in video script should be around 200."
        "Image should not contain any form of text, names of persons, company or company logo, etc. "
        "Prompt is 'What you wish to see in the output image'. "
        "A descriptive prompt that clearly defines elements, colors, and subjects will lead to better results. "
        "To control the weight of a given word use the format (word:weight), where word is the word you'd like to control the weight of and weight is a value between 0 and 1. "
        "For example: The sky was a crisp (blue:0.3) and (green:0.8) would convey a sky that was blue and green, but more green than blue. The weight applies to all words in the prompt. "
        "\n\n**Topic:** \n{topic}\n\n"
        "**Company summary:** \n{company_summary}\n\n",
        expected_output="Pairs of sentences. Narrations are enclosed in <narration> narration here </narration> tag. Image prompts are enclosed in <image> image prompt here </image> tag.",
        agent=content_creation_agent,
        # context = [task_video_script]
    )

    task_generate_video = Task(
        description="Generate video using narration and image prompt pairs. If image generation fails, stop the execution.",
        expected_output="Path of the video",
        agent=content_creation_agent,
        context = [task_generate_narration_image_pairs],
        tools=[generate_video]
    )

    LinkedInPosterAgent = Agent(
        role="LinkedIn Poster",
        goal="To post articles on LinkedIn",
        backstory="This agent is responsible for automating the posting of articles on LinkedIn to keep the profile active and engaging.",
        verbose=True,
        llm=llm,
        allow_delegation=False
    )

    BlogtoArticle = Task(
        description="Convert the following blog into engaging LinkedIn post of 200 words. " 
        "Make the post attractive using emojis and symbols ."
        # "Use image path from blog for LinkedIn post, example: tmp/xxxxxxxxx.png "
        "**Blog:** \n\n{blog} ",
        expected_output="A dictionary containing linkedin_post_title, linkedin_post_content. ",
        agent=LinkedInPosterAgent,
        # context = [task_add_images]
    )

    PostArticleToLinkedIn = Task(
        description="""post article on LinkedIn.

        token:
        {token}

        image_path:
        {image_path}
        
        """,
        expected_output="A confirmation that the article was successfully posted on LinkedIn.",
        agent=LinkedInPosterAgent,
        context = [BlogtoArticle],
        tools=[post_image_and_text]
    )

    info_agents = [information_retriever_agent]
    info_tasks = [task_scrape, task_summarize]

    blog_agents = [blog_agent]
    blog_tasks = [task_create_blog, task_visual_prompts]#, task_add_images]

    video_agents = [content_creation_agent]
    video_tasks = [task_generate_narration_image_pairs]#, task_generate_video]

    linkedin_agents = [LinkedInPosterAgent]
    linkedin_tasks = [BlogtoArticle, PostArticleToLinkedIn]

    info_crew = Crew(agents=info_agents, tasks=info_tasks, verbose=2)
    blog_crew = Crew(agents=blog_agents, tasks=blog_tasks, verbose=2)
    video_crew = Crew(agents=video_agents, tasks=video_tasks, verbose=2)
    linkedin_crew = Crew(agents=linkedin_agents, tasks=linkedin_tasks, verbose=2)

    return info_crew, blog_crew, video_crew, linkedin_crew




    # agents = [
    #           information_retriever_agent, 
    #           blog_agent, 
    #           content_creation_agent,
    #           ]
    
    # tasks = [
    #          task_scrape, 
    #          task_summarize, 
    #          task_create_blog,
    #          task_visual_prompts, 
    #          task_add_images, 
    #         # task_summarize_blog,
    #         # task_video_script,
    #          task_generate_narration_image_pairs, 
    #          task_generate_video,
             
    #         ]
    # print(blog_agent.llm)
    
    # if is_token:
    #     agents.append(LinkedInPosterAgent)
    #     tasks.append(BlogtoArticle)
    #     tasks.append(PostArticleToLinkedIn)
    
    # return agents, tasks

# a, b = get_agents_and_tasks(is_token=None)