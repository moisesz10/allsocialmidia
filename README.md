# AllSocialMidia - Automated Video Production 🎬

This project is an automated tool for mass creation and publishing of short-form videos (Shorts, Reels, TikTok, Kwai) and long-form videos. It leverages Artificial Intelligence for scriptwriting, voiceovers, and automatic video editing, along with bots to automatically publish the content to social media platforms.

## 🚀 Key Features

- **Viral Script Generation:** Uses the Google Gemini API to create highly optimized scripts.
- **Neural Voices:** Generates realistic voiceovers using Edge-TTS.
- **Smart B-Roll:** Automatically fetches contextual background videos from the Pexels API.
- **Editing & Effects:** Features "Hormozi" style captions with highlight colors, automatic audio ducking, and background soundtracks.
- **Auto-Publishing Bots:** Node.js (Puppeteer) and Python scripts to automatically post content on Instagram, YouTube, and Kwai.

## ⚙️ Prerequisites & Setup

For the system to work properly, you need to configure a `.env` file in the root directory (use `.env.example` as a template) containing your API keys:

```env
GEMINI_API_KEY=your_google_gemini_key
PEXELS_API_KEY=your_pexels_key
```

## 🛠️ How to Use (Video Generation)

You can launch the main system interface in three different ways:

1. **Interactive Mode (CLI):**
   Opens a terminal menu where you can select the niche, topic, format (9:16, 16:9, 1:1), background music, and caption colors.
   ```bash
   python main.py
   ```

2. **Web Mode (GUI):**
   Starts a local server with a web interface to manage video creation.
   ```bash
   python main.py --web
   ```

3. **Batch Generation (Scripts):**
   To generate dozens of videos at once for a specific niche (e.g., stoic philosophy), simply run the pre-configured scripts:
   ```bash
   python scripts/generate_kwai.py
   # or
   python scripts/generate_kwai_remaining.py
   ```
   The finished videos and associated assets will be saved in the `output/` folder.

## 🤖 How to Use (Auto-Publishing)

The project includes pre-mapped commands in `package.json` to make running the publishing bots easier. You can use the following NPM commands:

**Instagram:**
- `npm run bot:instagram` - Publish posts.
- `npm run generate:instagram:reels` - Generate a Reels package.
- *(Includes commands for mass follow/delete: `npm run bot:instagram:follow`)*

**YouTube:**
- `npm run bot:youtube:shorts` - Publish YouTube Shorts.
- `npm run bot:youtube:longs` - Publish long-form videos.
- `npm run bot:youtube:community` - Publish community posts.

**Kwai:**
- `npm run bot:kwai:shorts` - Publish to Kwai.
- `npm run generate:kwai:shorts` - Generate a video package for Kwai.

## 📁 Folder Structure

- `/src/` - Core Python application (content generation, audio, video, media downloads).
- `/bots/` - Automation scripts (Puppeteer/Node.js and Python) to interact with the platforms.
- `/scripts/` - Standalone scripts for mass batch video generation.
- `/assets/` - Static resources (fonts, soundtracks).
- `/output/` - Where the final generated videos and kits are stored.
- `/data/` and `/chrome_profile/` - Local data and browser sessions for bots (keeps logins saved).

---

> **Tip:** Always ensure your virtual environment (`.venv`) is active before running the Python scripts. Use `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows).
