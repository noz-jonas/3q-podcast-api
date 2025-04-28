# 🎙️ Podcast Metadata Management with Streamlit

This Streamlit app helps editors and producers easily assign podcast metadata using 3Q API calls, image tools, and article-based automation. It supports live and staging environments.

---

## ✅ Features

- Toggle between **Live** and **Staging** environments
- Add a 3Q file to a podcast episode (3Q API)
- Set metadata:
  - Videotype
  - Category
  - Vertical image
  - Subtitle
  - Body text
  # Podcast season (via cookie-authenticated POST) -- removed, as setting season is deactivated
- Default podcast cover image (Step 3.4)
- 🆕 Fetch and upload cover image dynamically from `articleId` (Step 4)
- Error messages with detailed debugging in staging mode
- Version info shown in the interface

---

## ⚙️ Requirements

- Python 3.8+
- [Streamlit](https://docs.streamlit.io/)
- `requests` library

Install dependencies:

```bash
pip install streamlit requests
```

---

## 🔐 Configuration

Create a `.streamlit/secrets.toml` file with the following structure:

```toml
# Live environment
live_project_id = "..."
live_api_key = "..."
live_podcast_id = "..."
live_season_id = "..."

# Staging environment
staging_project_id = "..."
staging_api_key = "..."
staging_podcast_id = "..."
staging_season_id = "..."

# Shared secrets
sdnSessionRemember = "..."
imgaccess_token = "..."
image_clientId_token = "..."
```

---

## 🚀 Usage

Start the app locally:

```bash
streamlit run streamlit_app.py
```

Then open `http://localhost:8501` in your browser.

### Workflow

1. Enter both a `File ID` and `Article ID`
2. Select **Live** or **Staging** environment
3. Click **Start Processing**
4. The app:
   - Adds the file to a podcast
   - Applies metadata
   - Uploads vertical image and body text
   - Sets the podcast season
   - Uses a default cover image
  - Optionally replaces the cover with an article-based image (if found)
  - Final success message when processing is complete

---

## 🧪 Debugging & Notes

- In **Staging** mode, additional debug info and API responses are shown.
- Errors are handled per-step; one failure doesn't stop the entire flow unless 2+ critical metadata requests fail.

---

## 🧑‍💼 Who Is It For?

- Podcast editors working with the 3Q video system and shz.de articles
- Teams managing multiple environments and testing integration

---

## 📬 Support

Contact your Product Manager or Tech Lead for API keys, cookie session info, and onboarding help.