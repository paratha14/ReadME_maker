document.getElementById('generator').addEventListener('click', async () => {
  const contentDiv = document.getElementById('content');
  const btn = document.getElementById('generator');

  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url;

  const githubRegex = /^https:\/\/github\.com\/([^/]+)\/([^/]+)(\/|$)/;
  const match = url.match(githubRegex);

  if (!match) {
    contentDiv.innerHTML = '<p style="color: red;">Please navigate to a GitHub repository page.</p>';
    return;
  }

  const owner = match[1];
  const repo = match[2].replace(".git", ""); 

  btn.disabled = true;
  btn.innerText = 'Generating... (this might take a few seconds)';
  contentDiv.innerHTML = '<p class="loading">Analyzing file tree & Crafting README...</p>';

  try {
    const response = await fetch(`http://127.0.0.1:8000/generate-readme?owner=${owner}&repo=${repo}`);
    
    if (!response.ok) throw new Error('Failed to fetch from backend');
    
    const data = await response.json();
    contentDiv.innerHTML = `<pre>${data.readme}</pre>`; 

  } catch (error) {
    contentDiv.innerHTML = `<p style="color: red;">Error: ${error.message}. Make sure your FastAPI backend is running.</p>`;
  } finally {
    btn.disabled = false;
    btn.innerText = 'Generate README';
    document.getElementById("copy-button").hidden = false;
  }
});

document.getElementById("copy-button")
  .addEventListener("click", copy);

async function copy() {
  const copyButton = document.getElementById("copy-button");
  const contentElement = document.getElementById("content");

  if (!contentElement) return;

  try {
    await navigator.clipboard.writeText(contentElement.innerText);

    copyButton.innerText = "Copied!";
    copyButton.disabled = true;

    setTimeout(() => {
      copyButton.innerText = "Copy";
      copyButton.disabled = false;
    }, 2000);

  } catch (error) {
    copyButton.innerText = "Failed";
  }
}