import feedparser
from datetime import datetime, timedelta
import pytz
import os
import time
import json
import random
import google.generativeai as genai
from dotenv import load_dotenv
from twitter_bot import post_tweet

# Load environment variables
load_dotenv()

# Configure Google Generative AI
API_KEY = os.getenv("API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
else:
    print("⚠️ Warning: API_KEY not found in environment variables")
    model = None

# Constants
POSTED_LINKS_FILE = 'posted_links.txt'
LOG_FILE = 'tweet_log.json'
CONFIG_FILE = 'bot_config.json'

# Time zone
IST = pytz.timezone('Asia/Kolkata')

# Default configuration - can be overridden by config file
DEFAULT_CONFIG = {
    # RSS Feed sources and their categories
    "rss_feeds": [
        {"url": "https://indianexpress.com/section/business/budget/feed/", "category": "business"},
        {"url": "https://indianexpress.com/section/business/feed/", "category": "business"},
        {"url": "https://indianexpress.com/section/world/climate-change/feed/", "category": "world"},
        {"url": "https://indianexpress.com/section/business/companies/feed/", "category": "business"},
        {"url": "https://indianexpress.com/section/business/economy/feed/", "category": "business"},
        {"url": "https://indianexpress.com/elections/feed/", "category": "politics"},
        {"url": "https://indianexpress.com/section/entertainment/feed/", "category": "entertainment"},
        {"url": "https://indianexpress.com/section/education/festivals/feed/", "category": "education"},
        {"url": "https://indianexpress.com/section/india/feed/", "category": "india"},
        {"url": "https://indianexpress.com/section/technology/feed/", "category": "technology"},
        {"url": "https://indianexpress.com/section/trending/feed/", "category": "trending"},
        {"url": "https://indianexpress.com/section/trending/trending-in-india/feed/", "category": "trending"},
        {"url": "https://indianexpress.com/section/trending/trending-globally/feed/", "category": "trending"}
    ],
    
    # Priority keywords for news selection
    "priority_keywords": [
        "Modi", "Donald Trump", "Trump", "Narendra Modi", "Airstrike", "Rahul Gandhi", "stock market", 
        "crash", "earthquake", "crypto", "flood", "AI", "ban", "twitter", "India vs Pakistan", 
        "inflation", "budget", "Elon Musk", "ISRO", "NASA", "Adani", "Ambani", "war", "Boycott", 
        "Supreme Court", "BJP"
    ],
    
    # Weighting for different news categories
    "category_weights": {
        "trending": 5,
        "politics": 5,
        "india": 4,
        "world": 4,
        "business": 4,
        "entertainment": 3,
        "technology": 3,
        "education": 2
    },
    
    # Number of tweets to post per run
    "tweets_per_run": 3,
    
    # Maximum news age in days (1 = today only, 2 = today + yesterday)
    "max_news_age": 2,
    
    # Tweet posting method ('selenium' or 'api')
    "tweet_method": "selenium",
    
    # Time between tweets in seconds
    "tweet_delay": 300  # 5 minutes
}

def load_config():
    """Load configuration from file or use defaults"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                print("✅ Configuration loaded from file")
                return config
        else:
            # Save default config if file doesn't exist
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print("✅ Default configuration saved to file")
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"⚠️ Error loading configuration: {e}")
        return DEFAULT_CONFIG

def load_posted_links():
    """Load previously posted links to avoid duplication"""
    if not os.path.exists(POSTED_LINKS_FILE):
        return set()
    
    today_str = datetime.now(IST).date().isoformat()
    posted = set()
    
    try:
        with open(POSTED_LINKS_FILE, 'r') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                date, link = line.split('|', 1)
                # Keep links from today to avoid duplicates
                if date == today_str:
                    posted.add(link)
            except ValueError:
                # Handle incorrectly formatted lines
                pass
                
        print(f"✅ Loaded {len(posted)} posted links from today")
        return posted
        
    except Exception as e:
        print(f"⚠️ Error loading posted links: {e}")
        return set()

def save_posted_links(new_links, date=None):
    """Save links to the posted links file"""
    if not new_links:
        return
        
    if date is None:
        date = datetime.now(IST).date().isoformat()
        
    try:
        with open(POSTED_LINKS_FILE, 'a') as f:
            for link in new_links:
                f.write(f"{date}|{link}\n")
        print(f"✅ Saved {len(new_links)} new links to posted links file")
    except Exception as e:
        print(f"⚠️ Error saving posted links: {e}")

def log_tweet(news_item, tweet_text, success=True):
    """Log tweet attempts to a file"""
    log_entry = {
        "timestamp": datetime.now(IST).isoformat(),
        "title": news_item.get("title", ""),
        "link": news_item.get("link", ""),
        "tweet": tweet_text,
        "success": success
    }
    
    try:
        # Load existing log
        log_data = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r') as f:
                log_data = json.load(f)
        
        # Add new entry
        log_data.append(log_entry)
        
        # Save updated log
        with open(LOG_FILE, 'w') as f:
            json.dump(log_data, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Error logging tweet: {e}")

def rephrase_for_twitter(title, explanation, category=None):
    """Create an engaging tweet from news content using AI"""
    if not model:
        # Fallback if API key not available
        hashtags = f" #{category.capitalize()}" if category else ""
        return f"{title} — {explanation[:100]}...{hashtags} #News"
    
    try:
        prompt = (
            f"Rephrase the following news for a Twitter post. Make it engaging, informative and include 2-3 relevant hashtags.\n"
            f"- Use **bold** for important keywords (Twitter supports markdown)\n"
            f"- Keep it under 280 characters\n"
            f"- Don't mention 'article' or 'news summary'\n"
            f"- Don't include links\n"
            f"- Category: {category or 'general'}\n\n"
            f"Title: {title}\n"
            f"Summary: {explanation}\n\n"
            f"Twitter Post:"
        )

        response = model.generate_content(prompt)
        tweet_text = response.text.strip()
        
        # Ensure tweet isn't too long (Twitter limit is 280 chars)
        if len(tweet_text) > 280:
            # Truncate tweet and add ellipsis
            tweet_text = tweet_text[:277] + "..."
            
        return tweet_text
        
    except Exception as e:
        print(f"⚠️ Error generating tweet content: {e}")
        # Fallback in case of error
        hashtags = f" #{category.capitalize()}" if category else ""
        tweet = f"{title} — {explanation[:100]}...{hashtags} #News"
        return tweet[:280]  # Ensure we stay under Twitter's character limit

def fetch_and_rank_news(config):
    """Fetch news from RSS feeds and rank them by importance"""
    now = datetime.now(IST)
    today = now.date()
    
    # Calculate the oldest date we'll accept based on config
    max_age = config.get("max_news_age", 2)
    oldest_date = today - timedelta(days=max_age - 1)
    
    # Get category weights from config
    category_weights = config.get("category_weights", {})
    
    # Get already posted links to avoid duplicates
    posted_links = load_posted_links()
    
    # Set to track seen links to avoid duplicates across feeds
    seen_links = set()
    
    # List to store all news items
    all_news = []
    
    # Fetch news from each RSS feed
    for feed_config in config.get("rss_feeds", []):
        feed_url = feed_config.get("url")
        category = feed_config.get("category", "general")
        
        try:
            print(f"📰 Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Get publication date
                pub_date = None
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6]).astimezone(IST).date()
                else:
                    # Skip entries without a date
                    continue

                # Skip old entries
                if pub_date < oldest_date:
                    continue

                # Get link and check for duplicates
                link = getattr(entry, 'link', None)
                if not link or link in seen_links or link in posted_links:
                    continue

                # Get title and summary
                title = getattr(entry, 'title', '').strip()
                summary = getattr(entry, 'summary', '').strip().replace('\n', ' ')
                
                # Use first couple sentences for explanation
                explanation = '. '.join(summary.split('. ')[:2]) + '.' if summary else 'More details in the article.'

                # Score the news item based on keywords and category
                combined_text = (title + ' ' + summary).lower()
                keyword_score = sum(1 for kw in [k.lower() for k in config.get("priority_keywords", [])] 
                                   if kw in combined_text)
                
                # Get category weight (default to 1 if not specified)
                genre_score = category_weights.get(category, 1)
                
                # Calculate total score with keyword score weighted higher
                total_score = keyword_score * 2 + genre_score
                
                # Add random factor to avoid always picking the same feeds
                randomness = random.uniform(0, 0.5)
                total_score += randomness

                # Add news item to list
                all_news.append({
                    'title': title,
                    'explanation': explanation,
                    'link': link,
                    'score': total_score,
                    'category': category,
                    'pub_date': pub_date.isoformat()
                })

                # Mark link as seen
                seen_links.add(link)

        except Exception as e:
            print(f"⚠️ Error parsing feed {feed_url}: {e}")

    # Rank news by score
    ranked_news = sorted(all_news, key=lambda x: x['score'], reverse=True)
    
    print(f"✅ Found {len(ranked_news)} news items")
    return ranked_news

def main():
    """Main function to run the news bot"""
    print("🤖 Starting Indian Express Twitter Bot...")
    
    # Load configuration
    config = load_config()
    
    # Fetch and rank news
    ranked_news = fetch_and_rank_news(config)
    
    # Select top news based on config
    tweets_per_run = config.get("tweets_per_run", 3)
    selected_news = ranked_news[:tweets_per_run]
    
    if not selected_news:
        print("❌ No news items found to tweet")
        return
    
    print(f"📊 Selected {len(selected_news)} news items to tweet")
    
    # Save links that we're about to tweet
    links_to_save = [news['link'] for news in selected_news]
    save_posted_links(links_to_save)
    
    # Post tweets
    tweet_delay = config.get("tweet_delay", 300)  # 5 minutes by default
    tweet_method = config.get("tweet_method", "selenium")
    
    for i, news in enumerate(selected_news, start=1):
        try:
            # Generate tweet content
            tweet = rephrase_for_twitter(news['title'], news['explanation'], news['category'])
                
            print(f"\n📰 News {i}/{len(selected_news)}:")
            print(f"🔗 Link: {news['link']}")
            print(f"📝 Tweet: {tweet}")
            
            # Post tweet
            success = post_tweet(tweet, method=tweet_method)
            
            # Log tweet attempt
            log_tweet(news, tweet, success=success)
            
            if success:
                print(f"✅ Tweet {i}/{len(selected_news)} posted successfully")
            else:
                print(f"❌ Failed to post tweet {i}/{len(selected_news)}")
            
            # Wait between tweets if there are more to post
            if i < len(selected_news):
                print(f"⏱️ Waiting {tweet_delay} seconds before next tweet...")
                time.sleep(tweet_delay)
                
        except Exception as e:
            print(f"❌ Error posting tweet {i}/{len(selected_news)}: {e}")
            log_tweet(news, "ERROR", success=False)

    print("\n✅ Twitter bot run completed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Bot crashed: {e}")