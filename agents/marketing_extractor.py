import os
import json
import ollama
from dotenv import load_dotenv

load_dotenv()

class MarketingExtractorOllama:
    def __init__(self):
        self.model = "llama3.2:3b"  # Small, fast, free
        print(f"🤖 Using local LLM: {self.model}")
    
    def extract_from_ad(self, ad):
        """
        Extract marketing angles, pain points, and concepts from a single ad.
        """
        ad_text = ad.get("adText", "")
        headline = ad.get("headline", "")
        cta = ad.get("cta", "")
        
        combined_text = f"""
Headline: {headline}
Ad Text: {ad_text}
Call to Action: {cta}
"""
        
        prompt = f"""You are an expert marketing analyst specializing in trading/finance ads.

Analyze this ad and extract the following in JSON format:

1. primary_hook: The first sentence or phrase that grabs attention
2. pain_points: List of problems the ad promises to solve (max 3)
3. marketing_concepts: List of techniques used (choose from: scarcity, urgency, social proof, authority, fear of missing out, simplicity, guaranteed results, free trial, limited time, educational, community)
4. target_emotion: One word (fear, greed, hope, frustration, excitement, trust)
5. ad_structure: Short description of how the ad flows (max 10 words)

Here's the ad:
{combined_text}

Return ONLY valid JSON, no other text. Format exactly like this example:
{{
    "primary_hook": "example hook here",
    "pain_points": ["pain1", "pain2"],
    "marketing_concepts": ["concept1", "concept2"],
    "target_emotion": "emotion",
    "ad_structure": "structure description"
}}
"""
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {"role": "user", "content": prompt}
            ])
            
            result_text = response['message']['content'].strip()
            
            # Clean markdown if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing ad: {e}")
            return {
                "primary_hook": "Error extracting",
                "pain_points": [],
                "marketing_concepts": [],
                "target_emotion": "unknown",
                "ad_structure": "error"
            }
    
    def extract_batch(self, ads, save_file="data/marketing_insights.json"):
        """
        Extract insights from multiple ads and save.
        """
        insights = []
        
        for i, ad in enumerate(ads):
            page_name = ad.get('pageName', 'Unknown')[:30]
            print(f"📊 Analyzing ad {i+1}/{len(ads)}: {page_name}...")
            
            insight = self.extract_from_ad(ad)
            insight["original_ad"] = {
                "adText": ad.get("adText", "")[:300],
                "headline": ad.get("headline", ""),
                "pageName": ad.get("pageName", "")
            }
            insights.append(insight)
        
        # Save to file
        os.makedirs("data", exist_ok=True)
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(insights, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(insights)} ad insights to {save_file}")
        
        # Print summary statistics
        from collections import Counter
        
        all_pains = []
        all_concepts = []
        all_emotions = []
        
        for insight in insights:
            all_pains.extend(insight.get("pain_points", []))
            all_concepts.extend(insight.get("marketing_concepts", []))
            all_emotions.append(insight.get("target_emotion", ""))
        
        print("\n📊 SUMMARY OF EXTRACTED INSIGHTS:")
        print("\nTop Pain Points:")
        for pain, count in Counter(all_pains).most_common(5):
            print(f"  • {pain}: {count} ads")
        
        print("\nTop Marketing Concepts:")
        for concept, count in Counter(all_concepts).most_common(5):
            print(f"  • {concept}: {count} ads")
        
        print("\nTarget Emotions:")
        for emotion, count in Counter(all_emotions).most_common(5):
            print(f"  • {emotion}: {count} ads")
        
        return insights


if __name__ == "__main__":
    # Load ads from Step 1
    if not os.path.exists("data/winning_ads.json"):
        print("❌ data/winning_ads.json not found. Run tools/apify_scraper.py first.")
        exit(1)
    
    with open("data/winning_ads.json", "r", encoding="utf-8") as f:
        ads = json.load(f)
    
    print(f"📖 Loaded {len(ads)} ads from data/winning_ads.json")
    
    extractor = MarketingExtractorOllama()
    insights = extractor.extract_batch(ads, "data/marketing_insights.json")
    
    print(f"\n✅ Complete! Insights saved to data/marketing_insights.json")