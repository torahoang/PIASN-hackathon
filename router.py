from sentence_transformers import SentenceTransformer, util
import numpy as np


def routerdb():
    db_research = ["Hey, I’m really lost—could you walk me through how to start writing an research paper?",
                   "I’ve never done this before—what’s the first step in putting together an paper?",
                   "Can you help me figure out how to format my references the way wants? I’m so confused!",
                   "I’m not sure what should go in each section of an paper. Could you explain what’s expected in the introduction and abstract?",
                   "English isn’t my first language, so I’m worried my writing on this research paper won’t sound academic enough. Can you help guide me make it better?",
                   "How do I organize my ideas so my paper flows the way papers are supposed to?",
                   "I keep getting stuck on how to write about my results. Can you show me how to do that in the style?",
                   "Is there an easy way to check if I’m following all the formatting rules? I don’t want to miss anything important.",
                   "please guide me through the process of writing an research paper",
                   "I am unsure how to summarize my research findings in the abstract and conclusion sections for journals."]  # db for research

    db_resume = ["I need help creating my first resume for internships—what should I include as a freshman?",
                 "Can you show me how to list my high school achievements on a CV for university applications?",
                 "My English isn’t perfect, so I’m not sure how to describe my skills professionally on my resume. Can you help?",
                 "What’s the difference between a CV and a resume, and which one should I use for jobs in the US?",
                 "I don’t have much work experience yet—how can I make my resume stand out?",
                 "How should I format my contact information and education section on my CV?",
                 "Can you help me write a summary statement for my resume that sounds confident but not arrogant?",
                 "I’m confused about how to organize my extracurricular activities and volunteer work on my resume.",
                 "Is there a specific way to write about my language skills and certifications in a CV for international students?",
                 "Could you review my resume and suggest improvements so it looks more professional to employers?"]  # db for the resume
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # load the model once on start up

    db_research_embeddings = model.encode(db_research)
    db_resume_embeddings = model.encode(db_resume)

    return db_research_embeddings, db_resume_embeddings, model


def router_func(input):
    model_name = ""
    db_research_embeddings, db_resume_embeddings, model = routerdb()
    input_embedding = model.encode([input])[0]  # encode the user input
    similarities_research = util.cos_sim(input_embedding, db_research_embeddings)[
        0].cpu().numpy()  # get the cosine matrix compare to the research db
    similarities_resume = util.cos_sim(input_embedding, db_resume_embeddings)[
        0].cpu().numpy()  # get the cosine matrix compare to the resume db

    average_similarity_research = np.mean(similarities_research)  # get the avg score
    average_similarity_resume = np.mean(similarities_resume)

    if average_similarity_research > average_similarity_resume:
        model_name = "research"
    else:
        model_name = "resume"

    return model_name
