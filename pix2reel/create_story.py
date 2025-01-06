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

        1. Place greater emphasis on the details in the "Tour Notes," ensuring that no critical information from this section is missed.\n
        2. While it's acceptable to incorporate moments of negativity (e.g., challenges or setbacks during the trip), always find a way to twist these into a positive, inspiring, or uplifting resolution.\n
        3. Stay within the scope of the provided "Tour Schedule" and "Tour Notes," ensuring creativity enhances the narrative without deviating from the core details provided.\n
        4. Adhere strictly to the word limit of {story_length} words. The story should not exceed or fall short of this limit. Focus on concise and impactful descriptions to maintain brevity while capturing the essence of the experience.\n

        The story should vividly capture the essence of the tour experience, engaging the reader with immersive descriptions and emotions while remaining grounded in the details."

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

def main():
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

if __name__ == "__main__":
    main()