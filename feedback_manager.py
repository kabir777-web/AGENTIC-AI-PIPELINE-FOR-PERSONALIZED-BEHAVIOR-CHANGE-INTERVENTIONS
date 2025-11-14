# feedback_manager.py
# This saves user ratings to a CSV file (like Excel)

import csv  # Tool for working with CSV files
import os  # Tool for checking if files exist
from datetime import datetime  # Tool for timestamps

class FeedbackManager:
    """
    This class manages user feedback
    Think of it as a notebook where we write down:
    - What goal they had
    - What advice we gave
    - How helpful it was (1-5 stars)
    """
    
    def __init__(self, filename='feedback_data.csv'):
        """
        Initialize: Create the CSV file if it doesn't exist
        """
        self.filename = filename
        self._initialize_csv()
    
    def _initialize_csv(self):
        """
        Create CSV file with column headers if file doesn't exist yet
        """
        if not os.path.exists(self.filename):
            # File doesn't exist, so create it
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write the header row (column names)
                writer.writerow([
                    'timestamp',  # When feedback was given
                    'user_goal',  # What they wanted to achieve
                    'user_barrier',  # What was stopping them
                    'target_component',  # capability/opportunity/motivation
                    'technique_used',  # Which technique we recommended
                    'theory',  # Which psychology theory
                    'rating',  # 1-5 stars
                    'would_try',  # Yes/Maybe/No
                    'feedback_text'  # Optional comments
                ])
            print(f"✅ Created {self.filename}")
    
    def save_feedback(self, user_goal, user_barrier, target_component, 
                     technique_name, theory, rating, would_try, feedback_text=""):
        """
        Save one piece of feedback to the CSV file
        
        Think of it as adding a new row to an Excel spreadsheet
        """
        try:
            # Open file in "append" mode (add to end)
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Write a new row with all the data
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Current time
                    user_goal,
                    user_barrier,
                    target_component,
                    technique_name,
                    theory,
                    rating,
                    would_try,
                    feedback_text
                ])
            return True  # Success!
        except Exception as e:
            print(f"⚠️ Error saving feedback: {e}")
            return False
    
    def get_statistics(self):
        """
        Calculate statistics from all feedback
        
        Like calculating:
        - Average rating (e.g., 4.2 out of 5)
        - Percentage who would try it
        - Which techniques work best
        """
        if not os.path.exists(self.filename):
            return None  # No data yet
        
        try:
            # Read all rows from CSV
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)  # Reads rows as dictionaries
                rows = list(reader)
            
            if len(rows) == 0:
                return None  # No feedback yet
            
            # Calculate total responses
            total_responses = len(rows)
            
            # Calculate average rating
            total_rating = sum(float(row['rating']) for row in rows)
            avg_rating = total_rating / total_responses
            
            # Calculate percentage who would try
            would_try_count = sum(1 for row in rows 
                                if row['would_try'].lower() in ['yes', 'maybe'])
            would_try_percent = (would_try_count / total_responses) * 100
            
            # Calculate performance per technique
            technique_ratings = {}
            for row in rows:
                tech = row['technique_used']
                if tech not in technique_ratings:
                    technique_ratings[tech] = []
                technique_ratings[tech].append(float(row['rating']))
            
            # Calculate average per technique
            technique_avg = {
                tech: sum(ratings)/len(ratings) 
                for tech, ratings in technique_ratings.items()
            }
            
            # Count component distribution
            component_count = {}
            for row in rows:
                comp = row['target_component']
                component_count[comp] = component_count.get(comp, 0) + 1
            
            # Return all statistics
            return {
                'total_responses': total_responses,
                'average_rating': avg_rating,
                'would_try_percent': would_try_percent,
                'technique_performance': technique_avg,
                'component_distribution': component_count
            }
        
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return None


# TESTING
if __name__ == "__main__":
    # Create feedback manager
    fm = FeedbackManager()
    
    # Test: Add sample feedback
    fm.save_feedback(
        user_goal="exercise more",
        user_barrier="too tired",
        target_component="motivation",
        technique_name="Temptation Bundling",
        theory="Behavioral Economics",
        rating=4,
        would_try="yes",
        feedback_text="This sounds fun!"
    )
    
    # Get statistics
    stats = fm.get_statistics()
    if stats:
        print("\n📊 Feedback Statistics:")
        print(f"Total Responses: {stats['total_responses']}")
        print(f"Average Rating: {stats['average_rating']:.2f}/5")
        print(f"Would Try: {stats['would_try_percent']:.1f}%")
