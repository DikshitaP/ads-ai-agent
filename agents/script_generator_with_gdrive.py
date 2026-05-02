import os
import json
import requests
import ollama
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

# ========== GOOGLE DRIVE DOWNLOADER (built-in) ==========
class GDriveDownloader:
    def __init__(self):
        self.file_ids = {
            "ndx": "1j5ElESYs4mkQQ-0laPy37ZPgvOLLHyVP",
            "snow": "1oOeLtcCqu73RFQMGaB7kmsBEUNyZEw3W"
        }
        self.data_dir = "data/gdrive"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def download_file_direct(self, file_id, output_name):
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        try:
            response = requests.get(url)
            
            # Handle Google's virus scan warning page
            if "download_warning" in response.text:
                import re
                confirm_match = re.search(r'confirm=([0-9A-Za-z_-]+)', response.text)
                if confirm_match:
                    confirm = confirm_match.group(1)
                    url = f"https://drive.google.com/uc?export=download&confirm={confirm}&id={file_id}"
                    response = requests.get(url)
            
            if response.status_code == 200:
                output_path = f"{self.data_dir}/{output_name}.json"
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"✅ Downloaded: {output_name}")
                return output_path
            else:
                print(f"❌ Failed to download {output_name}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error downloading {output_name}: {e}")
            return None
    
    def load_trading_data(self):
        ndx_path = f"{self.data_dir}/NDX_2026-04-27.json"
        snow_path = f"{self.data_dir}/SNOW_2026-04-27.json"
        
        if not os.path.exists(ndx_path) or not os.path.exists(snow_path):
            self.download_file_direct(self.file_ids["ndx"], "NDX_2026-04-27")
            self.download_file_direct(self.file_ids["snow"], "SNOW_2026-04-27")
        
        try:
            with open(ndx_path, 'r', encoding='utf-8') as f:
                nasdaq = json.load(f)
            with open(snow_path, 'r', encoding='utf-8') as f:
                snow = json.load(f)
            
            return {"nasdaq": nasdaq, "snowflake": snow}
        except Exception as e:
            print(f"❌ Error loading: {e}")
            return None


# ========== SCRIPT GENERATOR ==========
class ScriptGenerator:
    def __init__(self):
        self.model = "llama3.2:3b"
    
    def load_insights(self, insights_file="data/marketing_insights.json"):
        with open(insights_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def extract_top_pains(self, insights, top_n=3):
        all_pains = []
        for insight in insights:
            all_pains.extend(insight.get("pain_points", []))
        top_pains = Counter(all_pains).most_common(top_n)
        return [pain for pain, count in top_pains]
    
    def extract_top_concepts(self, insights, top_n=3):
        all_concepts = []
        for insight in insights:
            all_concepts.extend(insight.get("marketing_concepts", []))
        top_concepts = Counter(all_concepts).most_common(top_n)
        return [concept for concept, count in top_concepts]
    
    def load_gdrive_data(self):
        """Load REAL data from Google Drive"""
        downloader = GDriveDownloader()
        trading_data = downloader.load_trading_data()
        
        if trading_data:
            nasdaq = trading_data['nasdaq']
            snow = trading_data['snowflake']
            
            return {
                "company": "CrowdWisdomTrading",
                "unique_selling_points": [
                    f"AI-powered trading signals with {nasdaq['confidence level']}% confidence on Nasdaq-100",
                    f"Real-time sentiment from professional traders on YouTube, X, Reddit, and Groq",
                    f"Clear entry and exit levels: first target {nasdaq['target 1']}, second target {nasdaq['target 2']}",
                    f"Stop-loss protection at {nasdaq['stop 1']}",
                    f"Snowflake breakout signal targeting ${snow['target 1']}"
                ],
                "testimonials": [
                    "The AI caught the Nasdaq move before it happened",
                    "Professional traders are aligned - unified consensus across all platforms",
                    "This is the most accurate trading data I've ever seen"
                ],
                "statistics": [
                    f"Nasdaq-100 current price: {nasdaq['current price']}",
                    f"Confidence score: {nasdaq['confidence level']}% based on multi-source analysis",
                    f"AI infrastructure spending driving megacap tech momentum"
                ],
                "current_signals": {
                    "nasdaq": {
                        "direction": nasdaq['direction'],
                        "confidence": nasdaq['confidence level'],
                        "target": nasdaq['target 1'],
                        "reasoning": nasdaq['Wisdom of Professional Traders'][:300]
                    }
                }
            }
        
        return self.get_fallback_data()
    
    def get_fallback_data(self):
        return {
            "company": "CrowdWisdomTrading",
            "unique_selling_points": [
                "AI-powered trading signals with high accuracy",
                "Real-time crowd sentiment analysis",
                "Clear entry and exit levels"
            ],
            "testimonials": ["Traders love our signals"],
            "statistics": ["Thousands of active users"]
        }
    
    def generate_script(self, pain_points, marketing_concepts, gdrive_data):
        prompt = f"""
    You are a professional copywriter for trading/finance video ads.

    Create a **60-second video script** (approximately 150-180 words) for CrowdWisdomTrading.

    **Pain points to address:**
    {json.dumps(pain_points, indent=2)}

    **Marketing concepts to use:**
    {json.dumps(marketing_concepts, indent=2)}

    **Our REAL proprietary trading data (from Google Drive):**
    {json.dumps(gdrive_data['unique_selling_points'], indent=2)}
    {json.dumps(gdrive_data['current_signals'], indent=2)}

    **Script format requirements:**
    1. Divide into scenes: [SCENE 1], [SCENE 2], etc. (5-8 scenes total)
    2. Each scene has: Visual description + Voiceover text
    3. Include a strong hook in first 5 seconds using REAL data (confidence score, specific targets)
    4. Include a clear Call to Action at the end
    5. Keep voiceover conversational and urgent

    **Output format (JSON):**
    {{
        "hook": "First 5-second attention grabber using specific data like '85% confidence'",
        "scenes": [
            {{
                "scene": 1,
                "visual": "What appears on screen",
                "voiceover": "Words spoken (5-15 seconds each)"
            }}
        ],
        "cta": "Final call to action",
        "total_duration_seconds": 60
    }}

    Return ONLY valid JSON. No other text, no explanations.
    """
        
        response = ollama.chat(model=self.model, messages=[
            {"role": "user", "content": prompt}
        ])
        
        result_text = response['message']['content'].strip()
        
        # Clean the response - remove markdown and trailing commas
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        # Remove trailing commas (common JSON error from LLMs)
        import re
        result_text = re.sub(r',\s*}', '}', result_text)
        result_text = re.sub(r',\s*]', ']', result_text)
        
        # Try to parse JSON
        try:
            return json.loads(result_text)
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed, using fallback script")
            print(f"   Error: {e}")
            print(f"   Attempting to extract JSON from response...")
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            # Return fallback script
            return self.get_fallback_script(gdrive_data)

    def get_fallback_script(self, gdrive_data):
        """Fallback script with real GDrive data"""
        nasdaq_signal = gdrive_data.get('current_signals', {}).get('nasdaq', {})
        confidence = nasdaq_signal.get('confidence', 'high')
        target = nasdaq_signal.get('target', 'next level')
        
        return {
            "hook": f"Tired of losing money? Our AI just issued an {confidence}% confidence LONG signal!",
            "scenes": [
                {
                    "scene": 1,
                    "visual": "Nasdaq chart showing upward momentum",
                    "voiceover": f"Most traders miss the big moves. But CrowdWisdomTrading's AI caught the Nasdaq breakout with {confidence}% confidence."
                },
                {
                    "scene": 2,
                    "visual": "Trading dashboard with target levels",
                    "voiceover": f"Our system analyzes professional traders on YouTube, X, Reddit, and Groq to find the exact entry points."
                },
                {
                    "scene": 3,
                    "visual": "Price target on screen",
                    "voiceover": f"First target: {target}. Second target: higher. Stop-loss automatically calculated."
                },
                {
                    "scene": 4,
                    "visual": "Signal success rate",
                    "voiceover": "Unified consensus across all platforms. No more guessing where the market goes."
                },
                {
                    "scene": 5,
                    "visual": "Call to action button",
                    "voiceover": "Join CrowdWisdomTrading today. Get your first 14 days free. No credit card required."
                }
            ],
            "cta": "Visit CrowdWisdomTrading.com and start winning trades with real AI signals.",
            "total_duration_seconds": 60
        }
    
    def save_script(self, script, filename="data/script.json"):
        os.makedirs("data", exist_ok=True)
        with open(f"data/{filename}", "w", encoding="utf-8") as f:
            json.dump(script, f, indent=2, ensure_ascii=False)
        print(f"💾 Script saved to data/{filename}")


if __name__ == "__main__":
    generator = ScriptGenerator()
    
    print("📖 Loading marketing insights...")
    try:
        insights = generator.load_insights("data/marketing_insights.json")
        pain_points = generator.extract_top_pains(insights, top_n=3)
        concepts = generator.extract_top_concepts(insights, top_n=3)
        print(f"🎯 Top pains: {pain_points}")
        print(f"🎨 Top concepts: {concepts}")
    except Exception as e:
        print(f"⚠️  Could not load insights: {e}")
        pain_points = ["losing money", "missing trades", "complicated platforms"]
        concepts = ["social proof", "urgency", "authority"]
    
    print("📊 Loading real Google Drive trading data...")
    gdrive_data = generator.load_gdrive_data()
    
    print("🔨 Generating script with REAL data...")
    script = generator.generate_script(pain_points, concepts, gdrive_data)
    
    generator.save_script(script, "script_with_real_data.json")
    
    print("\n✅ Script generated with REAL CrowdWisdom trading data!")
    if 'current_signals' in gdrive_data:
        print(f"   Using Nasdaq confidence: {gdrive_data['current_signals']['nasdaq']['confidence']}%")
        print(f"   Target price: {gdrive_data['current_signals']['nasdaq']['target']}")
    
    # Preview the script
    print("\n" + "="*60)
    print("📝 SCRIPT PREVIEW (first 3 scenes)")
    print("="*60)
    print(f"\n🎯 HOOK: {script.get('hook', 'N/A')}\n")
    for scene in script.get('scenes', [])[:3]:
        print(f"[SCENE {scene['scene']}]")
        print(f"  VISUAL: {scene['visual']}")
        print(f"  VOICEOVER: {scene['voiceover'][:100]}...\n")
    print(f"📢 CTA: {script.get('cta', 'N/A')}")