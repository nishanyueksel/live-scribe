from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv(".env.local")
openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

transcript = "We'll start again. This is the meeting for the Army Springfield special meeting to discuss our 2025 financial plan. Today's date is April 29th at 2025 and the time is exactly 6 p.m. I'm Mayor Patrick Terriam for the Army Springfield. All council is present to my right. The sending order is Glenn Fuel, Andy Kaczynski, Mark Miller and Melinda Warren. If I can get a adoption of the agenda there, move on to seconder please. Melinda and Glenn. I'll give you an additional edition from council at all. I see none. If I can get a mover or those in support of the adoption of the agenda. Andy, that would be unanimous and is there for or past. We'll get into 4.1 that's adoption of the 2025 financial plan. We're in a seconder for that as well please. Melinda and Patrick. The year is all that council of the Army Springfield adopt the 2025 financial plan consisting of one and operating budget to a capital budget. Three and estimate of operating revenue and expenditures for the following fiscal year and four or five year capital expenditure programs. Thank you. Questions. Councillor Miller. I'll do that."

prompt = f"""
You are a hyper-efficient AI executive assistant specializing in meeting analysis. 
Return a JSON object with 'summary' and 'action_items'.
Transcript: \"\"\"{transcript}\"\"\"
"""

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

content = response.choices[0].message.content
print(content)
