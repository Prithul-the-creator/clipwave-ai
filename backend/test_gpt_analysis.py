#!/usr/bin/env python3
"""
Test script to verify GPT analysis is working properly
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

async def test_gpt_analysis():
    """Test GPT analysis with a sample transcript"""
    
    # Sample transcript (similar to what we get from Whisper)
    sample_transcript = [
        ("And video loves this coding interview question.", 0.0, 2.32),
        ("We are given a string of parentheses and we want to determine if it is valid.", 2.32, 5.96),
        ("A parentheses string is valid if it satisfies these three rules.", 5.96, 9.56),
        ("Number one, open brackets must be closed by the same type of brackets.", 9.56, 13.84),
        ("Number two, open brackets must be closed in the correct order.", 13.84, 17.44),
        ("And number three, every closing bracket has a corresponding open bracket of the same type.", 17.44, 22.64),
        ("So to verify if this is valid, we would use a stack.", 22.64, 25.48),
        ("Now, when we see an open bracket, we need to place that onto the stack.", 25.48, 28.92),
        ("But when we see a closing bracket, we need to make sure that the top of the stack is the matching open.", 28.92, 34.28),
        ("Now, luckily that is the case.", 34.28, 35.64),
        ("So we pop this off the stack and keep going.", 35.64, 37.92),
        ("So we see this open, we place it on the stack.", 37.92, 40.16),
        ("We see this bracket and we again pop this one off because it matches.", 40.16, 44.2),
        ("Now, we've reached the end of the string, but we need to make sure our stack is empty.", 44.2, 47.92),
        ("Because if it wasn't, we might have had something like this.", 47.92, 50.84),
        ("And this is an invalid string and a great data structure to find the mapping of the brackets would be a hash map.", 50.84, 57.04),
        ("Here's my Python code. Follow me for more.", 57.04, 59.04)
    ]
    
    instructions = "Find the most engaging and important moments in this video"
    
    print("🧪 Testing GPT Analysis...")
    print(f"📝 Transcript segments: {len(sample_transcript)}")
    print(f"🎯 Instructions: '{instructions}'")
    
    # Create the prompt (same as in video_processor.py)
    prompt = f"""
    Here is the transcript of the video: {sample_transcript}
    
    Instructions: {instructions}
    
    Please identify the most relevant time intervals in the video based on the instructions.
    Return only the timestamps in this exact format: [{{'start': 12.4, 'end': 54.6}}, ...]
    """
    
    try:
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        print("🔑 API Key loaded successfully")
        client = OpenAI(api_key=api_key)
        
        print("🤖 Making GPT API call...")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """
You are a precise and efficient video clipping assistant.

Given a transcript of a video and a user request, your job is to extract the most relevant time intervals that match the intent of the request.

Provide just enough context for the user to understand what's happening, but avoid unnecessary filler. Be decisive—separate clips only when the topic, speaker, or scene clearly shifts. Minimize the number of clips while maintaining clarity.

Return only a list of timestamp dictionaries in this exact format:
[{'start': 12.4, 'end': 54.6}, {'start': 110.2, 'end': 132.0}]

Do not include any explanation or commentary—just the list of relevant timestamp ranges.
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        response = completion.choices[0].message.content
        print(f"✅ GPT Response: {response}")
        
        # Extract timestamps
        import re
        import ast
        
        match = re.search(r"\[\s*{.*?}\s*\]", response, re.DOTALL)
        if not match:
            raise ValueError("No valid timestamp list found in GPT response")
        
        timestamps = ast.literal_eval(match.group(0))
        print(f"🎬 Extracted {len(timestamps)} timestamp ranges:")
        for i, ts in enumerate(timestamps):
            duration = ts['end'] - ts['start']
            print(f"  📹 Clip {i+1}: {ts['start']:.1f}s - {ts['end']:.1f}s (duration: {duration:.1f}s)")
        
        print("🎉 GPT Analysis test completed successfully!")
        return timestamps
        
    except Exception as e:
        print(f"❌ Error during GPT analysis: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(test_gpt_analysis())
