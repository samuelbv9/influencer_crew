import os
import json
from apify_client import ApifyClient

def apify_scrape(link, username):
    # Initialize the ApifyClient with your Apify API token
    # Replace '<YOUR_API_TOKEN>' with your token.
    client = ApifyClient(os.getenv("APIFY_API_KEY"))

    # # Prepare the Actor input
    profile_run_input = { "usernames": [username] }
    post_run_input = {
        "directUrls": [link],
        "resultsType": "posts",
        "includePinned": True,
        "resultsLimit": 9,
    }

    # Run the Actor and wait for it to finish
    run_profile = client.actor("apify/instagram-profile-scraper").call(run_input=profile_run_input)
    run_posts = client.actor("apify/instagram-scraper").call(run_input=post_run_input)


    dataset_id_profile = run_profile["defaultDatasetId"]
    dataset_id_posts = run_posts["defaultDatasetId"]

    # Fetch all dataset items
    all_profile_data = list(client.dataset(dataset_id_profile).iterate_items())
    all_posts_data = list(client.dataset(dataset_id_posts).iterate_items())

    # Define relevant fields to keep
    profile_relevant_fields = ["fullName", "username", "biography", "postsCount", "followersCount"]
    posts_relevant_fields = ["caption", "commentsCount", "firstComment", 
                            "hashtags", "latestComments", "likesCount",
                            "timestamp", "type", "videoPlayCount"]

    # Extract profile data (should be only one per user)
    profile_info = {k: v for k, v in all_profile_data[0].items() if k in profile_relevant_fields} if all_profile_data else {}

    # Extract posts data
    posts_info = []
    for item in all_posts_data:
        post_details = {k: v for k, v in item.items() if k in posts_relevant_fields}
        
        # Format latest comments to extract only text
        if "latestComments" in post_details and isinstance(post_details["latestComments"], list):
            post_details["latestComments"] = [comment.get("text", "") for comment in post_details["latestComments"]]
        
        posts_info.append(post_details)

    # Store data in JSON format
    result = {
        "profile": profile_info,
        "posts": posts_info
    }

    return json.dumps(result, indent=4)  # Return JSON object