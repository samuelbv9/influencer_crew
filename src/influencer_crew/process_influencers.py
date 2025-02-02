from supabase import create_client, Client
import os

supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))

def process_influencers(influencers):
    for influencer in influencers:
        print(influencer)
        username, name, link, followers = influencer

        try:
            followers = int(followers)
        except ValueError:
            print(f"Invalid follower count: {followers}")
            continue  # Skip if followers is not a valid number

        # Check if username already exists in the influencers table
        existing_user = supabase.from_("influencers").select("username").eq("username", username).execute()

        if existing_user.data:
            print(f"Skipping {username}, already exists in influencers table.")
            continue  # Skip this influencer

        data = {
            "username": username,
            "name": name,
            "social_media_link": link,
            "followers": followers,
        }

        response = supabase.table("potential_influencers").insert(data).execute()

        if response.data:
            print(f"Successfully uploaded: {username}")
        else:
            print(f"Error uploading {username}: {response.error}")
