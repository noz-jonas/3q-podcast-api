# 🎙️ Podcast Metadata Management with Streamlit

This Streamlit app allows editors and producers to quickly assign podcast metadata via API requests and image tools.

---

## ✅ Features

- Add episode to podcast (3Q API)
- Set metadata like videotype, category, vertical image, and body text
- Set podcast season (via cookie-authenticated POST request)
- 🆕 Fetch cover image dynamically from `articleId` (Step 4)

---

## ⚙️ Requirements

- Python 3.8+
- [Streamlit](https://docs.streamlit.io/)
- `requests` library

Install dependencies:

```bash
pip install streamlit requests