import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load the hidden keys from the .env file
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_KEY")

# 2. Build the communication bridge
supabase: Client = create_client(url, key)

def test_database():
    print(f"Attempting to connect to: {url}...\n")
    
    try:
        # 3. Try a simple read operation. 
        # We ask for just 1 row from the table we created earlier.
        response = supabase.table("jobs").select("*").limit(1).execute()
        
        print("✅ Connection Successful!")
        print("Here is the raw data Supabase returned:")
        print(response.data)
        
    except Exception as e:
        print("❌ Connection Failed.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    test_database()