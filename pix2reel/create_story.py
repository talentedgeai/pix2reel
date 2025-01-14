import os
import json

def load_environment_variables():
    """
    Load environment variables from multiple sources with priority:
    1. Cloud environment variables (e.g., Vercel, Heroku)
    2. Local .env.local file
    3. Default to None if not found
    """
    # Check for cloud environment variables first
    cloud_env_vars = [
        'VERCEL_ENV',  # Vercel
        'HEROKU_APP_NAME',  # Heroku
        'RENDER_SERVICE_NAME',  # Render
        'RAILWAY_SERVICE_NAME',  # Railway
    ]
    
    # Prioritize cloud environment variables
    for env_var in cloud_env_vars:
        if os.getenv(env_var):
            return
    
    # If not in cloud, try loading from local .env.local file
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        os.environ[key] = value
        except Exception as e:
            print(f"Warning: Could not load .env.local file: {e}")

# Load environment variables
load_environment_variables()


from openai import OpenAI
from typing import List

class TourStoryGenerator:
    def __init__(self, openai_api_key: str = None):
        """
        Initialize the Tour Story Generator with OpenAI API key.
        
        Args:
            openai_api_key (str, optional): OpenAI API key. 
                                            If not provided, will look for environment variable.
        """
        if openai_api_key:
            self.client = OpenAI(api_key=openai_api_key)
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key must be provided either as argument or in environment variable OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)

    def generate_tour_story(self, tour_schedule: str, tour_notes: str, story_length: int = 100) -> str:
        """
        Generate a story based on tour schedule and notes.
        
        Args:
            tour_schedule (str): Details of the tour schedule
            tour_notes (str): Additional notes about the tour
            story_length (int, optional): Desired story length in words. Defaults to 100.
        
        Returns:
            str: Generated story about the tour
        """
        prompt = f"""Create a precisely {story_length}-word creative story based on the following tour details:

        Tour Schedule: {tour_schedule}
        Tour Notes: {tour_notes}

        Important Guidelines:
        1. Highlight the "Tour Notes" – They’re the star! Don’t miss any key details from this section.
        2. If there were any hiccups during the trip, that’s okay! Share them, but always spin it into a positive or uplifting takeaway.
        3. Stick to the facts in the "Tour Schedule" and "Tour Notes" while keeping the story creative and exciting. Don’t go off-track!
        4. Word limit is {story_length}. Keep it short, snappy, and on point.
        
        Make the story feel real and relatable, like something you'd share on Instagram or TikTok. Use vivid descriptions and keep it fresh, fun, and full of energy!"

        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative storyteller who can weave narratives from travel experiences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150  # Slightly higher to ensure we get close to 100 words
            )
            
            story = response.choices[0].message.content.strip()
            cost = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            return story, cost
        
        except Exception as e:
            print(f"Error generating story: {e}")
            return "", {}

    def generate_story_from_file(self, schedule_file: str, notes_file: str, story_length: int = 100) -> str:
        """
        Generate a story by reading tour schedule and notes from files.
        
        Args:
            schedule_file (str): Path to the file containing tour schedule
            notes_file (str): Path to the file containing tour notes
            story_length (int, optional): Desired story length in words. Defaults to 100.
        
        Returns:
            str: Generated story about the tour
        """
        with open(schedule_file, 'r') as f:
            tour_schedule = f.read().strip()
        
        with open(notes_file, 'r') as f:
            tour_notes = f.read().strip()
        
        return self.generate_tour_story(tour_schedule, tour_notes, story_length)

    def generate_location_stories(self, tour_schedule: str, tour_notes: List[str], story_length: int = 100) -> str:
        """
        Generate each story for many locations.
        
        Args:
            tour_schedule (str): Details of the whole tour schedule
            tour_notes (str): Additional notes about the tour, each line corresponding to a location formatted as location_id;location_notes, each location in a different line
            story_length (int, optional): Desired story length for each location in words. Defaults to 100.
        
        Returns:
            str: Generated story about the tour
        """
        prompt = f"""
        Create a precisely {story_length}-word creative story for each location based on the following tour details:

        Tour Schedule: {tour_schedule}
        Tour Notes: {tour_notes}

        Tour Notes Format:
        Tour Notes is provided as a list of strings. Each string corresponds to a single location and is formatted as:
        location_id;location_name;location_notes
        Example:
        [
            "8bdcbfb6-9b0e-4ca6-92b4-2a3061bbf6ea;Cho Ben Thanh;Ben Thanh photos",
            "d41d8cd9-8f00-3204-a980-98ef41c8e308;Notre Dame Cathedral;Visited the iconic church"
        ]

        location_id: A unique identifier for the location (usually a UUID format).
        location_name: The name of the location (plain text).
        location_notes: Descriptive notes about the location (plain text).

        Important Guidelines:
        1. Generate one story for each location in the "Tour Notes." Treat each item in "Tour Notes" as a single location. IF THERE IS ONLY ONE LOCATION, MAKE SURE THE OUTPUT HAS ONLY ONE LOCATION AS WELL.
            Do not split or combine fields (location_id, location_name, location_notes) into separate locations.
            Use the semicolon (;) as a delimiter within each item, not between two different items in the list.
        2. Highlight the "location_notes" for each location – They’re the star! Don’t miss any key details from this section.
        3. If there were any hiccups at a location, that’s okay! Share them, but always spin it into a positive or uplifting takeaway.
        4. Stick to the facts in the "Tour Schedule" and "location_notes" while keeping each story creative and exciting. Don’t go off-track!
        5. Word limit is {story_length} per location. Keep it short, snappy, and on point.

        Output Format:
        Return the result as a JSON list, where each item is a dictionary with:
        - "locationId": The location_id from the "Tour Notes."
        - "story": A {story_length}-word creative story for the corresponding location.
        This output can have ONLY ONE item if the tour notes only has one location.

        Example Output:
        [
            {{"locationId": 1, "story": "Exploring Hanoi's Old Quarter was a feast for the senses..."}},
            {{"locationId": 2, "story": "A peaceful afternoon in Halong Bay began with a gentle..."}}
        ]

        Make the stories feel real and relatable, like something you'd share on Instagram or TikTok. Use vivid descriptions and keep them fresh, fun, and full of energy!
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a creative storyteller who can weave narratives from travel experiences."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200*len(tour_notes)  # Slightly higher to ensure we get close to 100 words
            )
            
            story = response.choices[0].message.content.strip()
            cost = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            return story, cost
        
        except Exception as e:
            print(f"Error generating story: {e}")
            return "", {}

def example_generate_tour_story():
    # Example usage
    generator = TourStoryGenerator()
    
    # Example 1: Direct input
    tour_schedule = """
    Chinatown, Binh Tay Market, Thien Hau Temple and Reunification Palace.

    Start the city tour to head to bustling Chinatown, take a tour of Cholon, HCMC’s Chinatown, see colorful Chinese architecture and traditional medicine shops abound, visit Binh Tay market to experience the vibrant rhythm of one of Ho Chi Minh City’s busiest and most colorful areas. At this major hub for local merchants, watch Vietnamese sellers barter for goods.

    Next stop is Thien Hau Temple, built in the early 19th century. The temple is dedicated to Thien Hau, the goddess of seafarers, for her protection during Chinese migration to Vietnam. Visit the pagoda’s shrines and shops in the center of Chinatown, where the Chinese minority reside.

    Continue to the century-old Reunification Palace, which witnessed the growth of Ho Chi Minh City during peacetime and throughout the Vietnam War until its end in 1975.

    End the tour at your hotel.

    """
    tour_notes = "weather really hot, chinatown street quite small, palace ticket is expensive, good sugarcane juice"
    story, cost = generator.generate_tour_story(tour_schedule, tour_notes)
    print("Generated Story:", story)
    print("Cost:", cost)
    
    # Example 2: From files
    # story = generator.generate_story_from_file('tour_schedule.txt', 'tour_notes.txt')
    # print(story)

def example_generate_location_stories():
    # Example usage
    generator = TourStoryGenerator()
    tour_schedule = """
    Hanoi Vespa Food Tour Itinerary
    8:30 AM: Hotel pick-up. Your guide arrives on a vintage Vespa to start your culinary journey through Hanoi’s vibrant streets. Brief introduction and safety instructions before departing.
    9:00 AM: Pho Ba Muoi on Hang Bai Street. There will be Pho Bo (beef pho) and Pho Ga (chicken pho). Pho Ga will is light-hearted, while Pho Bo is more savory. Guests can enjoy the hot bowl of pho, drink one cup of tea, and soak in the morning atmosphere of Hanoi.
    10:30 AM: Bun Cha Huong Lien. Famed for being Obama's lunch spot with Anthony Bourdain when he visited Hanoi for a business trip. Relish a plate of Hanoi's iconic Bun Cha with grilled pork patties, fresh vermicelli, and dipping sauce at a family-run restaurant.
    12:00 PM: Hotel drop-off. Return safely to your hotel with a heart full of memories and a belly full of Hanoi's finest flavors.
    """

    user_challenges = [
        {
            "index": 0,
            "locationId": "efb4d749-35e5-4296-9b99-092a7270db73",
            "locationName": "Street food Pho",
            "userMediaSubmission": [
                "https://kkhkvzjpcnivhhutxled.supabase.co/storage/v1/object/sign/challenge/88c59643-d03e-466b-a64a-2eaba98d75d4/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=0/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=0_47ae2ad00b41c14d782744a11d1e73ef.jpg?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGFsbGVuZ2UvODhjNTk2NDMtZDAzZS00NjZiLWE2NGEtMmVhYmE5OGQ3NWQ0L2UyZDM1N2JjLTAyNDMtNGI5Yy05YzVlLTBjMjk0MGZlZTU4N2lkPTAvZTJkMzU3YmMtMDI0My00YjljLTljNWUtMGMyOTQwZmVlNTg3aWQ9MF80N2FlMmFkMDBiNDFjMTRkNzgyNzQ0YTExZDFlNzNlZi5qcGciLCJpYXQiOjE3MzYzMzU1NzcsImV4cCI6MTc2Nzg3MTU3N30.3-o8mGzwj8SOy8VjCe2fw5gsckXK0gmuFN9xlculQSQ",
                "https://kkhkvzjpcnivhhutxled.supabase.co/storage/v1/object/sign/challenge/88c59643-d03e-466b-a64a-2eaba98d75d4/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=1/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=1_5c4730da0710b8e0848fbca112224331.jpg?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGFsbGVuZ2UvODhjNTk2NDMtZDAzZS00NjZiLWE2NGEtMmVhYmE5OGQ3NWQ0L2UyZDM1N2JjLTAyNDMtNGI5Yy05YzVlLTBjMjk0MGZlZTU4N2lkPTEvZTJkMzU3YmMtMDI0My00YjljLTljNWUtMGMyOTQwZmVlNTg3aWQ9MV81YzQ3MzBkYTA3MTBiOGUwODQ4ZmJjYTExMjIyNDMzMS5qcGciLCJpYXQiOjE3MzYzMzU1ODIsImV4cCI6MTc2Nzg3MTU4Mn0.J3y8rIS1dCrHu3AhrivtlJ26XjB_h1fG8rjXpDjcHBM"
            ],
            "userQuestionSubmission": "I tried Beef pho. Broth was amazing. The soup was spicy. Seating was limited. The street is too noisy."
        },
        {
            "index": 1,
            "locationId": "c871230b-43a8-4fa0-be7c-bce82442216f",
            "locationName": "Bun Cha Obama",
            "userMediaSubmission": [
                "https://kkhkvzjpcnivhhutxled.supabase.co/storage/v1/object/sign/challenge/88c59643-d03e-466b-a64a-2eaba98d75d4/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=0/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=0_02828672f14ad20ee6a454b220ffcd70.jpg?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGFsbGVuZ2UvODhjNTk2NDMtZDAzZS00NjZiLWE2NGEtMmVhYmE5OGQ3NWQ0L2UyZDM1N2JjLTAyNDMtNGI5Yy05YzVlLTBjMjk0MGZlZTU4N2lkPTAvZTJkMzU3YmMtMDI0My00YjljLTljNWUtMGMyOTQwZmVlNTg3aWQ9MF8wMjgyODY3MmYxNGFkMjBlZTZhNDU0YjIyMGZmY2Q3MC5qcGciLCJpYXQiOjE3MzYzMzU1MzUsImV4cCI6MTc2Nzg3MTUzNX0.LIx4kZcjAzp2xI_MHJ2dJwj25KeaKifs6KPOX_Wd2Ok",
                "https://kkhkvzjpcnivhhutxled.supabase.co/storage/v1/object/sign/challenge/88c59643-d03e-466b-a64a-2eaba98d75d4/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=1/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=1_0c67973d2dc9b06d10784e2c4f06e25e.jpg?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGFsbGVuZ2UvODhjNTk2NDMtZDAzZS00NjZiLWE2NGEtMmVhYmE5OGQ3NWQ0L2UyZDM1N2JjLTAyNDMtNGI5Yy05YzVlLTBjMjk0MGZlZTU4N2lkPTEvZTJkMzU3YmMtMDI0My00YjljLTljNWUtMGMyOTQwZmVlNTg3aWQ9MV8wYzY3OTczZDJkYzliMDZkMTA3ODRlMmM0ZjA2ZTI1ZS5qcGciLCJpYXQiOjE3MzYzMzU1NDEsImV4cCI6MTc2Nzg3MTU0MX0.BeOoue6jh7qEXS-vZY_TyTMEsOweHIo93-V-1hBq9uk",
                "https://kkhkvzjpcnivhhutxled.supabase.co/storage/v1/object/sign/challenge/88c59643-d03e-466b-a64a-2eaba98d75d4/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=2/e2d357bc-0243-4b9c-9c5e-0c2940fee587id=2_e473989a489f57aa5e0c8b42896211fb.jpg?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1cmwiOiJjaGFsbGVuZ2UvODhjNTk2NDMtZDAzZS00NjZiLWE2NGEtMmVhYmE5OGQ3NWQ0L2UyZDM1N2JjLTAyNDMtNGI5Yy05YzVlLTBjMjk0MGZlZTU4N2lkPTIvZTJkMzU3YmMtMDI0My00YjljLTljNWUtMGMyOTQwZmVlNTg3aWQ9Ml9lNDczOTg5YTQ4OWY1N2FhNWUwYzhiNDI4OTYyMTFmYi5qcGciLCJpYXQiOjE3MzYzMzU1NDUsImV4cCI6MTc2Nzg3MTU0NX0.WJ6atZmZfa30oX3PeSHTJ1r_uCexvkv39dy3-8xxDyQ"
            ],
            "userQuestionSubmission": "The shop is too small. The taste is not my liking."
        }
    ]

    tour_notes = []
    for challenge in user_challenges:
        str_to_pass = ";".join([
            str(challenge["locationId"]),
            challenge["locationName"],
            challenge["userQuestionSubmission"]
        ])
        tour_notes.append(str_to_pass)
        
    story, cost = generator.generate_location_stories(tour_schedule, tour_notes)
    print("Generated Story:", story)
    print("Cost:", cost)
    
    # Example 2: From files
    # story = generator.generate_story_from_file('tour_schedule.txt', 'tour_notes.txt')
    # print(story)
