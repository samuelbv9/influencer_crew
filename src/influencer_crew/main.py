#!/usr/bin/env python
import sys
import warnings
import json
import re

from crew import InfluencerCrew
from knowledge.influencers import influencers
from process_influencers import process_influencers

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    results = []

    for i in range(0, len(influencers)):
        print(i)
        input = {"influencer_data": influencers[i]}

        result = InfluencerCrew().crew().kickoff(inputs=input)
                # Check if result.raw contains "NULL" (skip invalid results)
        if result.raw.strip().upper() == "NULL":
            continue  # Skip this iteration

        # Step 1: Extract exactly 4 fields
        influencer_data = result.raw.strip().split(", ")[:4]

        # Step 2: Ensure the last element (follower count) is a valid number
        if len(influencer_data) == 4:
            influencer_data[3] = re.sub(r"[^\d]", "", influencer_data[3])  # Remove non-numeric characters from follower count

        # Step 3: Remove stray quotes and whitespace
        influencer_data = [item.strip().strip('"') for item in influencer_data]

        results.append(influencer_data)  # Append as a normal list

    process_influencers(results)

    # with open("results.py", "a") as file:
    #     formatted_results = [result.raw for result in results]  # Extract raw field
    #     file.write(f"results = {formatted_results}")  # Write as a JSON array

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        InfluencerCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        InfluencerCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        InfluencerCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
