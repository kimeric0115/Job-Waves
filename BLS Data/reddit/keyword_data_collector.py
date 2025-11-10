import praw
import json
import os
from dotenv import load_dotenv 
from datetime import datetime, timezone
import time

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
)

SECTOR_SUBREDDITS_KEYWORDS = {
    "mining and logging": {
        "Agriculture": [
            "farming jobs", "agricultural engineer", "forestry careers",
            "fishing industry", "ranching jobs", "agriculture technology",
            "farm management", "crop production", "environmental science",
            "conservation jobs"
        ],
        "Forestry": [
            "forester jobs", "wildlife conservation", "logging industry",
            "forest management", "environmental science", "tree planting",
            "national parks jobs", "firefighting (forest service)",
            "sustainability", "land management"
        ],
        "Fishing": [
            "fishing jobs", "commercial fishing", "fisheries management",
            "aquaculture careers", "marine biology", "boat crew jobs",
            "seafood industry", "coastal conservation", "marine science",
            "ocean sustainability"
        ],
        "Mining": [
            "mining engineering", "geology jobs", "oil and gas careers",
            "petroleum engineering", "drilling jobs", "geophysics careers",
            "underground mining", "safety inspector", "quarrying industry",
            "natural resources management"
        ],
        "Utilities": [
            "power plant jobs", "electrical engineering", "renewable energy",
            "grid management", "water treatment careers", "nuclear energy",
            "wind turbine technician", "solar panel installation",
            "hydroelectric jobs", "energy sector careers"
        ],
    },
    "construction": {
        "Construction": [
            "construction management", "civil engineering jobs",
            "electrician careers", "carpentry jobs", "plumbing careers",
            "heavy equipment operator", "project management",
            "construction technology", "welding jobs", "building inspection"
        ],
    },
    "manufacturing": {
        "Manufacturing": [
            "factory jobs", "machinist careers", "industrial engineering",
            "assembly line jobs", "quality control", "robotics technician",
            "process engineering", "lean manufacturing", "welding jobs",
            "production management"
        ]
    },
    "trade, transportation, and utilities": {
        "Logistics": [
            "truck driving jobs", "logistics careers", "aviation industry",
            "railroad jobs", "maritime careers", "public transit jobs",
            "freight and cargo", "supply chain management",
            "transportation engineering", "delivery services"
        ],
        "Retail": [
            "retail management", "customer service jobs", "store manager",
            "e-commerce careers", "cashier jobs", "merchandising",
            "fashion retail", "inventory control", "franchise ownership",
            "retail sales"
        ]
    },
    "information": {
        "cscareerquestions": [
            "software engineering", "data science jobs", "tech industry",
            "cybersecurity careers", "IT support jobs", "web development",
            "cloud computing", "telecommunications", "network engineering",
            "UX/UI design"
        ],
        "jobs": [
            "operations management", "business administration",
            "corporate strategy", "executive leadership", "HR management",
            "project management", "financial management", "business analyst",
            "team leadership", "organizational development"
        ]
    },
    "financial activities": {
        "FinancialCareers": [
            "investment banking", "financial analyst", "accounting careers",
            "auditing jobs", "tax consulting", "wealth management",
            "risk management", "credit analyst", "financial planning",
            "stock market jobs"
        ]
    },
    "professional and business services": {
        "consulting": [
            "consulting jobs", "marketing careers", "legal industry",
            "scientific research", "engineering consulting",
            "business strategy", "paralegal jobs", "architecture careers",
            "management consulting", "data analytics"
        ],
        "office": [
            "office administration", "clerical jobs", "executive assistant",
            "customer service", "data entry jobs", "office management",
            "human resources", "call center jobs", "document processing",
            "event coordination"
        ]
    },
    "private education and health services": {
        "education": [
            "teaching jobs", "professor careers", "curriculum development",
            "education policy", "K-12 education", "higher education jobs",
            "student advising", "special education", "edtech industry",
            "school administration"
        ],
        "healthcare": [
            "nursing jobs", "physician careers", "medical research",
            "healthcare administration", "pharmaceutical careers",
            "physical therapy", "mental health professionals",
            "medical technology", "public health", "dental industry"
        ]
    },
    "leisure and hospitality": {
        "entertainment": [
            "graphic design jobs", "music industry careers", "acting jobs",
            "film production", "game development", "theater careers",
            "animation industry", "photography", "digital marketing",
            "content creation"
        ],
        "hospitality": [
            "hotel management", "restaurant industry", "tourism careers",
            "event planning", "catering jobs", "food and beverage management",
            "travel industry", "casino jobs", "customer service",
            "resort management"
        ]
    },
    "government": {
        "PublicPolicy": [
            "government jobs", "policy analysis", "public relations",
            "law enforcement careers", "city planning", "social work",
            "nonprofit management", "community development",
            "environmental policy", "federal agency jobs"
        ]
    }
}

general_keywords = ["post grad", "hire", "fire" "accepted", "rejected", "results", "job openings", "hiring freeze", "income", "salary", "pay", "interview", "career", "career advice", "job advice", "job help", "apply", "applying"]

# Parameters
POSTS_PER_KEYWORD = 100  # Number of posts to fetch per keyword
REQUEST_DELAY = 5  # Delay between requests to avoid rate limits
MAX_RETRIES = 5  # Max retries for failed requests
START_YEAR = 2018  # Start year for date range
END_YEAR = 2020  # End year for date range

# Convert years to timestamps
start_timestamp = int(datetime(START_YEAR, 1, 1).timestamp())
end_timestamp = int(datetime(END_YEAR, 12, 31).timestamp())

# JSON file for incremental writing
JSON_FILE = "reddit/reddit_post_grad_data_2018_2020_final.json"

def fetch_posts_with_reddit(subreddit, keyword, limit):
    """
    Fetch posts from a subreddit using Reddit API.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            print(f"Searching for posts in r/{subreddit} with keyword: {keyword}...")
            query = f'"{keyword}"'
            posts = subreddit.search(query, limit=limit, sort="new")
            return list(posts)
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                print(f"Rate limit exceeded. Waiting for {REQUEST_DELAY * (retries + 1)} seconds...")
                time.sleep(REQUEST_DELAY * (retries + 1))
                retries += 1
            else:
                raise e
    raise Exception(f"Max retries exceeded for keyword {keyword}.")

def fetch_comments(post, comment_limit=10):
    """
    Fetch comments for a post using Reddit API.
    """
    retries = 0
    while retries < MAX_RETRIES:
        try:
            post.comments.replace_more(limit=0)  # Avoid infinite comment expansion
            comments = post.comments[:comment_limit]
            return comments
        except praw.exceptions.APIException as e:
            if e.error_type == "RATELIMIT":
                print(f"Rate limit exceeded while fetching comments for {post.title}. Retrying...")
                time.sleep(REQUEST_DELAY * (retries + 1))
                retries += 1
            else:
                raise e
    raise Exception(f"Max retries exceeded for post {post.id}.")

def append_to_json(data, file_path):
    """
    Append data to a JSON file.
    """
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
        existing_data.extend(data)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, indent=4)
    else:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

for sector_name, values in SECTOR_SUBREDDITS_KEYWORDS.items():
    for subreddit_name, keywords in values.items():
        print(f"Fetching data from r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        all_keywords = keywords + general_keywords

        for keyword in all_keywords:
            print(f"Searching for keyword: {keyword}")
            posts = fetch_posts_with_reddit(subreddit, keyword, POSTS_PER_KEYWORD)

            batch_data = []
            for post in posts:
                post_timestamp = post.created_utc
                if start_timestamp <= post_timestamp <= end_timestamp:
                    timestamp = datetime.fromtimestamp(post_timestamp, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    post_data = {
                        "sector": sector_name,
                        "subreddit": subreddit_name,
                        "type": "post",
                        "timestamp": timestamp,
                        "content": post.title + "\n" + (post.selftext if post.selftext else ""),
                        "upvotes": post.score,
                        "url": post.url,
                        "comments": []
                    }

                    # Fetch comments
                    comments = fetch_comments(post)
                    for comment in comments:
                        if any((k.lower() in comment.body.lower()) for k in all_keywords):
                            comment_timestamp = datetime.fromtimestamp(comment.created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                            post_data["comments"].append({
                                "type": "comment",
                                "timestamp": comment_timestamp,
                                "content": comment.body,
                                "upvotes": comment.score
                            })

                    batch_data.append(post_data)
                    print(f"Fetched post: {post.title}")  # Print post title for monitoring
                    time.sleep(REQUEST_DELAY)

            # Append batch data to JSON file
            append_to_json(batch_data, JSON_FILE)
            print(f"Appended {len(batch_data)} posts to {JSON_FILE}")

print(f"Data collection complete. Saved to {JSON_FILE}")