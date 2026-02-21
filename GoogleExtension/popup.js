document.getElementById('generator').addEventListener('click', async () => {
  const contentDiv = document.getElementById('content');
  const btn = document.getElementById('generator');

  // 1. Get the URL of the current active tab
  let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url;

  // 2. Validate that we are actually on a GitHub repository
  const githubRegex = /^https:\/\/github\.com\/([^/]+)\/([^/]+)(\/|$)/;
  const match = url.match(githubRegex);

  if (!match) {
    contentDiv.innerHTML = '<p style="color: red;">Please navigate to a GitHub repository page.</p>';
    return;
  }

  const owner = match[1];
  const repo = match[2].replace(".git", ""); 

  // 3. Update UI to loading state
  btn.disabled = true;
  btn.innerText = 'Generating... (this might take a few seconds)';
  contentDiv.innerHTML = '<p class="loading">Analyzing file tree & calling LLM...</p>';

  try {
    // 4. Call your FastAPI Backend (Ensure your FastAPI server has CORS enabled!)
    const response = await fetch(`http://127.0.0.1:8000/generate-readme?owner=${owner}&repo=${repo}`);
    
    if (!response.ok) throw new Error('Failed to fetch from backend');
    
    const data = await response.json();

    // 5. Display the result in the popup
    contentDiv.innerHTML = `<pre>${data.readme}</pre>`; 
    
  } catch (error) {
    contentDiv.innerHTML = `<p style="color: red;">Error: ${error.message}. Make sure your FastAPI backend is running.</p>`;
  } finally {
    btn.disabled = false;
    btn.innerText = 'Generate README';
  }
});