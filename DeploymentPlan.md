# Deployment Plan: Streamlit Community Cloud

Because we chose Streamlit for our User Interface and Chroma DB for our local vector storage, we can deploy **both the Backend and Frontend together as a single full-stack application** completely for free using [Streamlit Community Cloud](https://streamlit.io/cloud). 

Streamlit's servers will run our Python backend (Groq/RAG integration) and serve the frontend UI simultaneously.

## Phase 11: Production Deployment

### Step 1: Prepare the Repository
Our repository is already 95% ready for production! 
- ✅ The code is pushed to GitHub.
- ✅ `requirements.txt` contains all necessary dependencies.
- ✅ Our `.gitignore` is preventing our private API keys from being leaked.

### Step 2: Create a Streamlit Cloud Account
1. Go to [share.streamlit.io](https://share.streamlit.io/) and click **Continue with GitHub**.
2. Authorize Streamlit to access your GitHub repositories.

### Step 3: Deploy the App
1. Once logged in, click the **"New app"** button.
2. Fill out the deployment form:
   - **Repository**: `faridi16/Mutualfund_FAQ_Assistant`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: You can customize this (e.g., `hdfc-faq-assistant.streamlit.app`)

### Step 4: Inject the API Key (CRITICAL)
Before you click Deploy, we must securely pass our Groq API key into the cloud environment. 
1. Click **Advanced settings** at the bottom of the deployment form.
2. In the **Secrets** text box, paste your API key exactly like this:
```toml
GROQ_API_KEY="your-actual-groq-api-key-here"
```
3. Click **Save**.

### Step 5: Launch!
1. Click the **Deploy!** button. 
2. Streamlit will boot up a cloud server, clone your repository, install everything in `requirements.txt`, and launch your app. 
3. Your Mutual Fund FAQ Assistant will now be live on the internet!

---
> **Note on Architecture**: Our `check_env()` function in `chat.py` uses `os.environ.get("GROQ_API_KEY")`. Streamlit Community Cloud automatically takes whatever you put in the "Secrets" box and injects it into Python's `os.environ`, so **we do not need to rewrite any code for this to work!**
