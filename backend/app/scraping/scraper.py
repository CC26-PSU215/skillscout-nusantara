import requests
from bs4 import BeautifulSoup

def scrape_jobs():
    # 1. Target the URL and download the HTML
    url = "https://realpython.github.io/fake-jobs/"
    print(f"Fetching data from {url}...")
    
    # We use requests to get the page, just like a browser does
    response = requests.get(url)
    
    # 2. Feed the raw HTML into BeautifulSoup to parse it
    soup = BeautifulSoup(response.content, "html.parser")
    
    # 3. Find the data containers
    # If you right-click the website and select "Inspect", you'll see every 
    # job is wrapped in a <div> tag with the class "card-content"
    job_cards = soup.find_all("div", class_="card-content")
    
    print(f"Found {len(job_cards)} jobs! Extracting details...\n")
    print("-" * 40)
    
    # 4. Loop through the containers and extract the specific text we want
    scraped_data = []
    
    for card in job_cards:
        # We use .text to strip away the HTML tags (like <h2>) and .strip() to remove extra whitespace
        title = card.find("h2", class_="title").text.strip()
        company = card.find("h3", class_="company").text.strip()
        location = card.find("p", class_="location").text.strip()
        
        # Save the clean data into a dictionary
        job_info = {
            "title": title,
            "company": company,
            "location": location
        }
        scraped_data.append(job_info)
        
        # Print the first 5 just to see it working
        if len(scraped_data) <= 5:
            print(f"💼 {title}\n🏢 {company}\n📍 {location}\n")
            
    return scraped_data

# Run the function
if __name__ == "__main__":
    scrape_jobs()