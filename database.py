import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

key = os.getenv("SUPABASE_KEY")
url = os.getenv("SUPABASE_URL")

try:
    supabase: Client = create_client(url, key)
    print("Supabase client created successfully.")

except Exception as e:
    print(f"Error creating Supabase client: {e}")


response = supabase.table("tasks").insert({
    "title":"Sample Task 3",
    "description":"This is a sample task description.",
}).execute()

print(response.data)