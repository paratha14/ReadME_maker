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
        template = """
You are an elite open-source technical writer who specializes in visually striking, high-impact GitHub READMEs.

Your task is to generate a modern, badge-heavy, visually polished README.md file.

CRITICAL RULES:
- Return ONLY valid Markdown.
- Do NOT include explanations.
- Do NOT wrap output in code fences.
- Do NOT add commentary.
- Output must start directly with a Markdown heading.
- Do NOT use emoji in section headers.
- Do NOT fabricate technologies, tools, badges, or links.
- Do NOT invent files not present in metadata.

-----------------------------------
Repository Metadata:
- Repository Name: {repo_name}
- Languages Used: {languages_used}
- File Structure: {all_files}
-----------------------------------

DESIGN REQUIREMENTS:

1. HERO SECTION

Start with:

# {repo_name}

Below the title:
- Add a strong one-line tagline inferred from the repository purpose.
- Add shields.io bitmap badges (flat style).
- Include language badges for detected languages.
- Include notebook badge if .ipynb files exist.
- Include Python badge if .py files exist.
- Include dataset badge if .csv files exist.
- Include license badge ONLY if a LICENSE file is detected.
- Do NOT include placeholder badges.
- Badge format:
  ![Label](https://img.shields.io/badge/<label>-<value>-<color>?style=flat)

Then add a horizontal divider:
---

2. OVERVIEW SECTION

Create a compelling overview.
Explain what the project achieves and why it matters.
Avoid corporate tone.
Keep it confident and modern.

---

3. FEATURES SECTION

- Use bold feature titles.
- Focus on outcomes and capabilities.
- Use strong action verbs.
- Avoid generic phrases like "This project includes".

---

4. TECH STACK SECTION

Display technologies as badge rows instead of plain bullet points.
Only include technologies that can be confidently inferred.

---

5. ARCHITECTURE / WORKFLOW SECTION

If multiple notebooks, scripts, or stages exist:
- Describe the system as a pipeline.
- Use arrows (→) to represent data flow.
- Clearly show inputs and outputs.
- Mention generated files where applicable.

Keep this structured and readable.

---

6. PROJECT STRUCTURE SECTION

- Show a clean tree block.
- Add concise, modern explanations for key files.
- Avoid over-explaining obvious files.

---

7. USAGE SECTION (IMPORTANT — MUST BE DETAILED AND GUIDED)

This section must:

- Begin with environment setup.
- Provide step-by-step instructions.
- Clearly state the correct execution order.
- Explain what each step produces.
- Mention expected output files.
- Include dependency installation.
- Include optional virtual environment setup.
- Include Jupyter launch instructions if notebooks exist.
- Include customization guidance if configurable parameters are present.

Structure the Usage section like:

- Setup
- Execute Pipeline (numbered steps)
- Customization (if applicable)
- Expected Outputs

The tone must feel guided and smooth — like onboarding documentation.
Avoid being abrupt or minimal.

---

8. CONTRIBUTING SECTION (UPGRADED)

Create a clean, professional Contributing section that includes:

- Fork workflow
- Branch naming example
- Commit clarity guidance
- Pull request instructions
- Optional issue reporting suggestion

Keep it concise but structured.
Avoid being overly corporate.
Avoid unnecessary verbosity.

---

9. LICENSE SECTION

Include only if a license file is detected.
Keep it clean and simple.

---

STYLE RULES:

- No emoji in headers.
- No repetitive sentences.
- No filler text.
- No fake deployment links.
- No fake GitHub URLs.
- No hallucinated badges.
- Keep paragraphs tight and readable.
- Maintain strong visual hierarchy.
- Make it feel like a polished flagship open-source project.

The final README should feel:
- Modern
- Confident
- Visually structured
- Developer-friendly
- Production-ready

Return ONLY the final README content.
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
