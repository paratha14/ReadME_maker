from fastapi import FastAPI, Request, HTTPException
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
app= FastAPI()


async def fetch_data(owner: str, repo: str, branch: str = "main"):
    url_tree= f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    url_language= f"https://api.github.com/repos/{owner}/{repo}/languages"

    async with httpx.AsyncClient() as client:
        response_tree= await client.get(url_tree)
        response_languages= await client.get(url_language)
    
    if response_tree.status_code != 200:
        raise HTTPException(f"Failed to fetch tree data: {response_tree.status_code}")
    
    data= response_tree.json()
    files = [item['path'] for item in data.get('tree', [])]

    if response_languages.status_code != 200:
        raise HTTPException(f"Failed to fetch language data: {response_languages.status_code}")
    languages = response_languages.json()
    
    content={}
    content['all_files']= files
    content['languages_used']= languages
    
    return content

async def LLM_pass(metadata: dict, repo_name: str):
    api_key= os.getenv("GOOGLE_API_KEY")
    ChatLLM= ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.6, api_key=api_key)
    parser= StrOutputParser()

    prompt= PromptTemplate(
        template= """Generate a proper markdown based README.md file for a GitHub repository with the following metadata:
        - Repository Name: {repo_name}
        - Languages Used: {languages_used}
        - File Structure: {all_files}
        """,
        input_variables= ["repo_name", "languages_used", "all_files"],
    
        )

    chain= prompt | ChatLLM | parser

    result = await chain.ainvoke({
    "repo_name": repo_name,
    "languages_used": metadata.get("languages_used", {}),
    "all_files": metadata.get("all_files", [])
    })
    return result

async def main(owner: str, repo: str, branch: str = "main"):
    metadata= await fetch_data(owner, repo, branch)
    readme_content= await LLM_pass(metadata, repo)
    return readme_content


@app.get("/generate_readme")
async def generate_readme(owner: str = None, repo: str = None, branch: str = "main"):
    
    if not owner or not repo:
        raise HTTPException(status_code=400, detail="Missing 'owner' or 'repo' query parameters.")
    
    try:
        readme_content= await main(owner, repo, branch)
        return {"readme_content": readme_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
