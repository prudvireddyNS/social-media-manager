from crewai import Agent, Task, Crew
from langchain_groq import ChatGroq


llm = ChatGroq(model="llama3-70b-8192", api_key='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')

linkedin_post_rewriter_agent = Agent(
    role="LinkedIn Post Rewriter",
    goal="To revise and generate a new LinkedIn post based on user feedback.",
    backstory="You are a LinkedIn post rewriter agent, skilled in improving and generating engaging posts based on user preferences and feedback.",
    verbose=True,
    llm=llm,
    allow_delegation=False
)

task_rewrite_linkedin_post = Task(
    description="Revise the LinkedIn post provided by another agent based on user feedback and generate a new version. "
    "\nPost: \n\n{post}\n",
    expected_output="Revised LinkedIn post based on user feedback.",
    agent=linkedin_post_rewriter_agent,
)

crew = Crew(agents=[linkedin_post_rewriter_agent],
            tasks=[task_rewrite_linkedin_post],
            verbose=2)

post = """
Deep learning, a subset of machine learning, has taken the world of artificial intelligence by storm! 🌪️ This technology has enabled machines to think, learn, and act like humans, transforming the way we live and work. 🤖 From virtual assistants to self-driving cars, deep learning has become an integral part of our daily lives. 🚗


At DIGIOTAI, we are committed to helping companies navigate the complexities of digital transformation. 💻 As a leading DX enablement partner, we provide cutting-edge solutions in IoT, Data Science, Blockchain, AR/VR/MR, AI/GenAI, Cloud Enablement, and Mobility. 📈


Deep learning has numerous applications across various industries, including Computer Vision, Natural Language Processing, and Speech Recognition. 📊 It offers numerous benefits, including Improved Accuracy, Increased Efficiency, and Enhanced Customer Experience. 📈


However, deep learning is not without its challenges and limitations. 🤔 Some of the key challenges include Data Quality, Computational Power, and Interpretability. 💡


At DIGIOTAI, we are committed to helping companies harness the power of deep learning to drive innovation and excellence in the digital economy. 🚀 Whether you're looking to develop a chatbot, create a self-driving car, or simply improve your customer experience, our team of experts can help you unlock the full potential of deep learning. 💡 Contact us today to learn more about our deep learning solutions and how we can help you achieve your digital transformation goals! 📲
"""
res = crew.kickoff(inputs={'post':post})
print(res)