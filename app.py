from fastapi import FastAPI, Request, HTTPException
import httpx
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app= FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_data(owner: str, repo: str):
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"

    async with httpx.AsyncClient() as client:
        repo_response = await client.get(repo_url)

    if repo_response.status_code != 200:
        raise HTTPException(status_code=repo_response.status_code,
                            detail="Failed to fetch repository info")

    repo_data = repo_response.json()
    default_branch = repo_data.get("default_branch", "main")

    url_tree = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
    url_language = f"https://api.github.com/repos/{owner}/{repo}/languages"

    async with httpx.AsyncClient() as client:
        response_tree = await client.get(url_tree)
        response_languages = await client.get(url_language)

    if response_tree.status_code != 200:
        raise HTTPException(status_code=response_tree.status_code,
                            detail="Failed to fetch tree data")

    files = [item['path'] for item in response_tree.json().get('tree', [])]

    if response_languages.status_code != 200:
        raise HTTPException(status_code=response_languages.status_code,
                            detail="Failed to fetch language data")

    languages = response_languages.json()

    return {
        "all_files": files,
        "languages_used": languages
    }

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

async def main(owner: str, repo: str):
    metadata= await fetch_data(owner, repo)
    readme_content= await LLM_pass(metadata, repo)
    return readme_content


@app.get("/generate-readme")
async def generate_readme(owner: str, repo: str):

    if not owner or not repo:
        raise HTTPException(status_code=400,
                            detail="Missing owner or repo")

    readme_content = await main(owner, repo)

    return {"readme": readme_content}
