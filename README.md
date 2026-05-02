<h1>📈 CrowdWisdomTrading AI Ad Agent</h1>

<p><span class="badge">Status: Working</span> <span class="badge">Python 3.10+</span> <span class="badge">Ollama</span></p>

<p>This is my submission for the AI Agent Development Internship at CrowdWisdomTrading. I built a system that automatically creates 60-second video ads by scraping successful trading ads, analyzing what makes them work, and generating new ads using the company's proprietary trading data from Google Drive.</p>

<p>Honestly, I started this not knowing if I could finish all 4 steps, but after a lot of debugging and late nights, everything works end-to-end now.</p>

<hr>

<h2>🎯 What This System Does</h2>

<p>Think of it as a robot that watches other ads, learns from them, and then makes a completely new ad using CrowdWisdom's real trading signals. Here's the flow:</p>

<pre>
Step 1: Scrape Meta Ads Library → Find winning trading ads
Step 2: Analyze ads with LLM → Extract pain points &amp; hooks  
Step 3: Combine with GDrive data → Write video script
Step 4: Generate video → MP4 with images + voiceover
</pre>

<p>I didn't use CrewAI or LangChain like the assignment suggested because I wanted to keep things simple and actually understand every line of code. Also, fewer dependencies = fewer things that break.</p>

<hr>

<h2>📂 Project Structure</h2>

<pre>
ads-ai-agent/
│
├── agents/                      # Main logic for each step
│   ├── marketing_extractor_ollama.py   # Step 2: Analyzes ads
│   ├── script_generator_with_gdrive.py # Step 3: Writes script
│   └── video_generator_pexels.py       # Step 4: Creates video
│
├── tools/                       # Helper scripts
│   ├── apify_scraper.py               # Step 1: Fetches ads
│
├── data/                        # All JSON outputs saved here
│   ├── winning_ads.json               # Scraped ads
│   ├── marketing_insights.json        # Pain points &amp; conc
│   ├──script_with_real_data.json     # Final script
│
├── output/                      # Final video + audio files
│   └── videos/
│       ├── final_ad_with_pexels.mp4   # The actual ad
│       └── scene_*_pexels.jpg         # Images from Pexels
│
├── .env                         # API keys (not in repo)
├── requirements_clean.txt       # Minimal dependencies
└── README.html                  # This file
</pre>

<p>I know there are <code>__pycache__</code> folders too but I added them to .gitignore.</p>

<hr>

<h2>🚀 Setup & Installation</h2>

<p>I'm on Windows but the code should work on Mac/Linux too (paths might need changes).</p>

<h3>1. Clone & Virtual Environment</h3>
<pre>
git clone https://github.com/YOUR_USERNAME/ads-ai-agent
cd ads-ai-agent

python -m venv venv
venv\Scripts\activate        # On Windows
source venv/bin/activate   # On Mac/Linux
</pre>

<h3>2. Install Dependencies</h3>
<p>I tried to keep this minimal. No CrewAI, no LangChain — just what's actually used.</p>
<pre>
pip install -r requirements_clean.txt
</pre>

<h3>3. Install Ollama (Local LLM)</h3>
<p>I used Ollama because it's free and I didn't want to burn through OpenAI credits while debugging.</p>
<pre>
# Download from https://ollama.com
ollama pull llama3.2:3b

Keep Ollama running in background
ollama serve
</pre>

<h3>4. API Keys</h3>
<p>Create a <code>.env</code> file in the root directory:</p>
<pre>
APIFY_TOKEN=your_apify_token_here
PEXELS_API_KEY=your_pexels_api_key_here
</pre>
<p><strong>Note:</strong> I tried ElevenLabs first but got quota errors, so I switched to gTTS (free, no key needed). The Pexels API is for real images instead of colored placeholders.</p>

<hr>

<h2>⚙️ Running Each Step</h2>

<p>I've tested this multiple times. Run these commands in order:</p>

<h3>Step 1 — Scrape Winning Ads (Apify)</h3>
<pre>
python tools/apify_scraper.py
</pre>
<p>This pulls ads from Meta Ads Library using "trading signals" as the search term. Saves to <code>data/winning_ads.json</code>. The actor took me a while to figure out — had to find the correct Actor ID.</p>

<h3>Step 2 — Extract Marketing Insights</h3>
<pre>
python agents/marketing_extractor.py
</pre>
<p>Uses Ollama to analyze each ad and find pain points, hooks, and marketing concepts. The output is in <code>data/marketing_insights.json</code>. Some of the pain points it found were pretty dramatic ("betrayal", "exploitation") — that's just what the LLM picked up from real trading ads.</p>

<h3>Step 3 — Generate Script with Real GDrive Data</h3>
<pre>
python agents/script_generator_with_gdrive.py
</pre>
<p>This downloads the actual JSON files from Google Drive (Nasdaq and Snowflake signals) and generates a 60-second script. The script includes real confidence scores (85%) and price targets (27480). Saves to <code>data/script_with_real_data.json</code>.</p>

<h3>Step 4 — Create the Video</h3>
<pre>
python agents/video_generator.py
</pre>
<p>This fetches real images from Pexels based on the scene descriptions, generates voiceover using gTTS, stitches everything together with MoviePy. Output is <code>output/videos/final_ad_with_pexels.mp4</code>. Takes about 2-3 minutes.</p>

<hr>

<h2>🎬 Sample Output</h2>

<p>Here's what the generated script looks like (first scene only):</p>

<pre>
Hook: "Tired of losing money? Our AI just issued an 85% confidence LONG signal!"

Scene 1:
  Visual: Person sitting in front of computer screen
  Voiceover: Most traders miss the big moves. But CrowdWisdomTrading's AI caught 
            the Nasdaq breakout with 85% confidence from YouTube, X, Reddit, 
            and Groq analysis.
</pre>

<p>The actual video uses real images from Pexels (not placeholders) and has voiceover throughout. I attached a sample video in the submission email.</p>

<hr>

<h2>🧠 Technical Decisions </h2>

<table>
    <thead>
        <tr><th>Challenge</th><th>My Solution</th><th>Why</th></tr>
    </thead>
    <tbody>
        <tr>
            <td>Scraping Meta Ads</td>
            <td>Apify Actor</td>
            <td>Building a custom scraper would take too long and break when Facebook changes HTML structure.</td>
        </tr>
        <tr>
            <td>LLM API Costs</td>
            <td>Ollama (Local)</td>
            <td>I ran out of OpenAI credits. Ollama is free and runs entirely on my laptop.</td>
        </tr>
        <tr>
            <td>Voiceover</td>
            <td>gTTS</td>
            <td>ElevenLabs gave me 401 errors. gTTS works out of the box with zero configuration.</td>
        </tr>
        <tr>
            <td>Images</td>
            <td>Pexels API</td>
            <td>Real stock photos look better than colored boxes. Free tier is 200 requests/hour.</td>
        </tr>
        <tr>
            <td>Video Assembly</td>
            <td>MoviePy</td>
            <td>Remotion requires Node.js and is more complex. MoviePy does everything I need in Python.</td>
        </tr>
    </tbody>
</table>

<hr>

<h2>🐛 Known Issues & Workarounds</h2>

<ul>
    <li><strong>MoviePy import error:</strong> Version 2.0+ changed the import syntax. I fixed by using <code>from moviepy import ImageClip</code> instead of <code>from moviepy.editor import *</code>.</li>
    <li><strong>ElevenLabs 401:</strong> Their free tier flagged my account for unusual activity. Switched to gTTS as fallback.</li>
    <li><strong>JSON parsing from Ollama:</strong> The LLM sometimes adds extra commas or markdown. I added regex cleaning and a fallback script.</li>
    <li><strong>Google Drive download warning:</strong> Some links have a virus scan interstitial. My code handles the confirm= token redirection.</li>
</ul>

<hr>

<h2>📝 What I'd Improve Given More Time</h2>

<p>If I had another week, I would:</p>
<ul>
    <li>Add real subtitles to the video (requires ImageMagick which was a pain to set up on Windows)</li>
    <li>Implement ElevenLabs with a paid tier for better voice quality</li>
    <li>Use DALL-E or Stable Diffusion instead of Pexels for completely unique images</li>
    <li>Add a CLI with <code>--step [1-4]</code> flags to run individual steps</li>
    <li>Better error recovery when Apify returns 0 results</li>
</ul>

<hr>

<h2>✅ Testing Checklist</h2>

<p>I manually verified:</p>

<table>
    <tr><th>Step</th><th>Status</th><th>Notes</th></tr>
    <tr><td>Apify returns ads</td><td>✓</td><td>10-15 ads per run</td></tr>
    <tr><td>Ollama analyzes ads</td><td>✓</td><td>Takes ~3 seconds per ad</td></tr>
    <tr><td>GDrive downloads</td><td>✓</td><td>NDX and SNOW JSON files</td></tr>
    <tr><td>Script generation</td><td>✓</td><td>Uses real 85% confidence data</td></tr>
    <tr><td>Video with audio</td><td>✓</td><td>MP4 plays correctly</td></tr>
    <tr><td>Pexels images</td><td>✓</td><td>Fetches real stock photos</td></tr>
</table>

<hr>

<p><strong>— Dikshita Pimpale</strong><br>
dikshitapimpale14@gmail.com<br>
https://www.linkedin.com/in/dikshitapimpale/</p>

<hr>

<p><em>Built with Python, Ollama, Apify, MoviePy, and too much lemonade ˙ ✩°˖🍋⋆｡˚꩜</em></p>

</body>
</html>