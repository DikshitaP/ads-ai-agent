import os
import json
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load API token from .env file
load_dotenv()

def fetch_trading_ads(search_term="trading signals", max_results=25):
    """
    Fetch ads from Meta Ads Library using Apify.
    
    Args:
        search_term: Keyword to search for (e.g., "trading signals")
        max_results: Number of ads to fetch
    
    Returns:
        List of ad objects
    """
    token = os.getenv("APIFY_TOKEN")
    
    if not token:
        raise ValueError("APIFY_TOKEN not found in .env file")
    
    # Initialize Apify client
    client = ApifyClient(token)
    
    # Actor ID for Meta Ads Library Scraper
    actor_id = "ZQyDz7154hrOfrDMK"
    
    # Facebook Ads Library URL with search term
    search_url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&q={search_term.replace(' ', '%20')}"
    
    # Run the actor
    run_input = {
        "startUrls": [search_url],
        "maxResults": max_results,
        "includeAdvertiserPageInfo": True,
        "scrapeCreativeDetails": True,
        "onlyTotalCount": False
    }
    
    print(f"🚀 Running Apify actor with search: '{search_term}'...")
    
    # Call the actor
    run = client.actor(actor_id).call(run_input=run_input)
    
    # Fetch results from the dataset
    dataset = client.dataset(run["defaultDatasetId"])
    items = dataset.list_items().items
    
    print(f"✅ Fetched {len(items)} ads")
    
    return items

def filter_best_ads(ads, top_n=15):
    """
    Filter the best performing ads based on heuristic:
    - Ads with both text and page info are more complete
    - Prioritize ads with more data fields filled
    
    Args:
        ads: List of ad objects from Apify
        top_n: Number of top ads to return
    
    Returns:
        Filtered list of best ads
    """
    def score_ad(ad):
        score = 0
        # Ads with ad text are valuable
        if ad.get("adText"):
            score += 10
        # Ads with headlines
        if ad.get("headline"):
            score += 5
        # Ads with call to action
        if ad.get("cta"):
            score += 3
        # Pages with more likes = more established advertisers
        likes = ad.get("pageLikes", 0)
        if likes:
            score += min(likes // 100, 20)  # Max 20 points from likes
        return score
    
    # Filter ads that have at least some content
    valid_ads = [ad for ad in ads if ad.get("adText") or ad.get("adArchiveID")]
    
    # Sort by score (higher = better)
    sorted_ads = sorted(valid_ads, key=score_ad, reverse=True)
    
    return sorted_ads[:top_n]


def save_ads_to_json(ads, filename="winning_ads.json"):
    """
    Save ads list to JSON file.
    """
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    filepath = f"data/{filename}"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(ads, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved {len(ads)} ads to {filepath}")
    return filepath


if __name__ == "__main__":
    # Step 1: Fetch ads
    raw_ads = fetch_trading_ads("trading signals", 25)
    
    if not raw_ads:
        print("❌ No ads fetched. Check your search term or API token.")
    else:
        # Step 2: Filter best working ads
        best_ads = filter_best_ads(raw_ads, top_n=15)
        
        # Step 3: Save to JSON
        save_ads_to_json(best_ads, "winning_ads.json")
        
        print(f"\n📊 Summary:")
        print(f"   Raw ads fetched: {len(raw_ads)}")
        print(f"   Best ads selected: {len(best_ads)}")
        print(f"   Saved to: data/winning_ads.json")
        
        # Step 4: Print a quick preview
        print(f"\n📝 Top ad preview:")
        if best_ads:
            top_ad = best_ads[0]
            print(f"   Page: {top_ad.get('pageName', 'Unknown')}")
            print(f"   Ad text: {top_ad.get('adText', 'No text')[:100]}...")