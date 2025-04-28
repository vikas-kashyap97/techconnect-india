import tempfile
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import streamlit as st

# List of tech-related keywords to look for in resumes
TECH_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift", "kotlin",
    "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel",
    "aws", "azure", "gcp", "cloud", "devops", "docker", "kubernetes", "jenkins", "ci/cd",
    "sql", "mysql", "postgresql", "mongodb", "nosql", "database", "redis", "elasticsearch",
    "machine learning", "artificial intelligence", "data science", "big data", "analytics",
    "software engineer", "developer", "programmer", "sde", "web developer", "full stack",
    "frontend", "backend", "mobile developer", "ios developer", "android developer",
    "qa", "quality assurance", "testing", "test automation", "selenium", "cypress",
    "product manager", "project manager", "scrum master", "agile", "jira", "confluence",
    "git", "github", "gitlab", "bitbucket", "version control", "svn", "cybersecurity",
    "network", "system administrator", "linux", "unix", "windows server", "powershell",
    "bash", "shell scripting", "api", "rest", "graphql", "microservices", "soa",
    "html", "css", "sass", "less", "bootstrap", "tailwind", "material ui", "responsive design",
    "ux", "ui", "user experience", "user interface", "figma", "sketch", "adobe xd",
    "data engineer", "etl", "hadoop", "spark", "kafka", "airflow", "tableau", "power bi",
    "blockchain", "cryptocurrency", "smart contracts", "solidity", "web3", "ethereum",
    "iot", "embedded systems", "firmware", "hardware", "raspberry pi", "arduino",
    "game development", "unity", "unreal engine", "3d modeling", "animation",
    "technical lead", "team lead", "engineering manager", "cto", "chief technology officer",
    "it support", "helpdesk", "technical support", "systems analyst", "business analyst"
]

def parse_resume(uploaded_file):
    """
    Parse a resume PDF file and check if it belongs to a tech professional
    Returns a tuple of (is_tech_professional, skills_found)
    """
    try:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        # Load the PDF
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        
        # Split the document into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(documents)
        
        # Extract text from all chunks
        full_text = " ".join([chunk.page_content.lower() for chunk in chunks])
        
        # Count tech keywords
        skills_found = []
        keyword_count = 0
        
        for keyword in TECH_KEYWORDS:
            if keyword in full_text:
                keyword_count += 1
                skills_found.append(keyword.title())  # Capitalize for display
        
        # Clean up the temporary file
        os.unlink(temp_path)
        
        # Determine if this is a tech professional
        # Threshold: At least 5 tech keywords found
        is_tech_professional = keyword_count >= 5
        
        # Limit to top 10 skills for display
        skills_found = list(set(skills_found))[:10]
        
        return is_tech_professional, skills_found
    
    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}")
        return False, []
