import streamlit as st
import re

# Function to read teacher names and image URLs from the text file
def load_teachers(file):
    teachers = []
    with open(file, 'r') as f:
        lines = f.readlines()
        teacher_name = None
        image_url = None
        for line in lines:
            if line.startswith("Name:"):
                teacher_name = line.strip().replace("Name: ", "")
            elif line.startswith("Image:"):
                image_url = line.strip().replace("Image: ", "")
                if teacher_name and image_url:
                    teachers.append((teacher_name, image_url))
                    teacher_name, image_url = None, None  # Reset for the next entry
    return teachers

# Clean teacher names for search comparison
def clean_name(name):
    return re.sub(r'^(dr|mr|ms)\s+', '', name.strip().lower())

# Load teachers data
teachers = load_teachers('SCOPE.txt')
teachers_cleaned = [clean_name(teacher[0]) for teacher in teachers]

# Set up Streamlit UI
st.title("Teacher Review System")
st.header("Search for a Teacher")

# Search bar (case insensitive and ignore titles like Dr, Mr, Ms)
search_query = st.text_input("Search for a teacher:")

# Find matching teachers based on the search query
if search_query:
    search_query_cleaned = clean_name(search_query)
    matches = [teachers[i] for i in range(len(teachers_cleaned)) if search_query_cleaned in teachers_cleaned[i]]
else:
    matches = []

# Create a session state to store the reviews and votes
if 'reviews' not in st.session_state:
    st.session_state.reviews = {}

# Display the search results
if matches:
    st.write("Teachers found:")
    for teacher, image_url in matches:
        col1, col2 = st.columns([2, 1])  # Create two columns: one for the name, one for the image

        with col1:
            st.subheader(f"Teacher: {teacher}")

            # Initialize teacher's reviews in session state if not already present
            if teacher not in st.session_state.reviews:
                st.session_state.reviews[teacher] = {
                    'teaching': 0,
                    'leniency': 0,
                    'correction': 0,
                    'da_quiz': 0,
                    'overall': 0,
                    'user_reviews': 0,  # Track total reviews for the teacher
                    'total_reviews': 0  # Track total rating points (teaching + leniency + correction + da_quiz)
                }

            # User input section (ratings for the teacher)
            st.markdown("### **Rate the Teacher**")
            teaching = st.slider("Teaching:", 0, 10, st.session_state.reviews[teacher]['teaching'] if st.session_state.reviews[teacher]['teaching'] > 0 else 0)
            leniency = st.slider("Leniency:", 0, 10, st.session_state.reviews[teacher]['leniency'] if st.session_state.reviews[teacher]['leniency'] > 0 else 0)
            correction = st.slider("Correction:", 0, 10, st.session_state.reviews[teacher]['correction'] if st.session_state.reviews[teacher]['correction'] > 0 else 0)
            da_quiz = st.slider("DA/Quiz:", 0, 10, st.session_state.reviews[teacher]['da_quiz'] if st.session_state.reviews[teacher]['da_quiz'] > 0 else 0)

            # Display the teacher's image in a smaller size
            with col2:
                try:
                    st.image(image_url, caption=f"{teacher}'s Picture", width=150)
                except Exception as e:
                    st.error(f"Error displaying image: {e}")

            # Submit button to save the review
            submit_button = st.button("Submit Review")
            
            if submit_button:
                # Combine new ratings with old data and calculate the new overall score

                # Retrieve previous reviews
                old_teaching = st.session_state.reviews[teacher]['teaching']
                old_leniency = st.session_state.reviews[teacher]['leniency']
                old_correction = st.session_state.reviews[teacher]['correction']
                old_da_quiz = st.session_state.reviews[teacher]['da_quiz']

                # Calculate the average of old and new ratings (normalize to out of 10)
                combined_teaching = (old_teaching + teaching) / 2
                combined_leniency = (old_leniency + leniency) / 2
                combined_correction = (old_correction + correction) / 2
                combined_da_quiz = (old_da_quiz + da_quiz) / 2

                # Update the reviews in session state
                st.session_state.reviews[teacher]['teaching'] = combined_teaching
                st.session_state.reviews[teacher]['leniency'] = combined_leniency
                st.session_state.reviews[teacher]['correction'] = combined_correction
                st.session_state.reviews[teacher]['da_quiz'] = combined_da_quiz

                # Update total reviews and rating points
                st.session_state.reviews[teacher]['user_reviews'] += 1
                st.session_state.reviews[teacher]['total_reviews'] += combined_teaching + combined_leniency + combined_correction + combined_da_quiz

                # Calculate the overall rating
                overall_rating = (combined_teaching + combined_leniency + combined_correction + combined_da_quiz) / 4
                st.session_state.reviews[teacher]['overall'] = overall_rating

                # Display success message
                st.success("Review submitted successfully!")

        # Section 2: Overall Rating and Previous Votes
        if st.session_state.reviews[teacher]['user_reviews'] > 0:
            # Highlighted Section with Overall Rating and Previous Reviews
            st.markdown("---")
            st.markdown("### **Overall Rating**", unsafe_allow_html=True)
            
            # Calculate average overall rating
            total_reviews = st.session_state.reviews[teacher]['user_reviews']
            avg_overall = st.session_state.reviews[teacher]['total_reviews'] / (total_reviews * 4) if total_reviews > 0 else 0
            avg_overall = round(avg_overall, 2)  # Overall rating on 0-10 scale

            # Ensure avg_overall is between 0 and 1 before multiplying by 100
            avg_overall = min(max(avg_overall, 0), 1)

            # Display the overall rating in the overall rating box
            st.markdown(f"**Overall Rating (based on {total_reviews} reviews):**")
            st.markdown(f"{avg_overall * 10} / 10", unsafe_allow_html=True)  # Display on 10-point scale
            
            # Display the progress bar (scaled from 0 to 100)
            st.progress(avg_overall * 100, text="Rating is good" if avg_overall > 0.7 else "Rating is average" if avg_overall > 0.4 else "Rating is poor")

            # Display reviews and their individual ratings with colors based on rating
            st.markdown("### **REVIEWS**")
            st.write("**Teaching:**", f"{st.session_state.reviews[teacher]['teaching']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['teaching'] > 5 else 'red' if st.session_state.reviews[teacher]['teaching'] < 5 else 'yellow'};")
            st.write("**Leniency:**", f"{st.session_state.reviews[teacher]['leniency']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['leniency'] > 5 else 'red' if st.session_state.reviews[teacher]['leniency'] < 5 else 'yellow'};")
            st.write("**Correction:**", f"{st.session_state.reviews[teacher]['correction']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['correction'] > 5 else 'red' if st.session_state.reviews[teacher]['correction'] < 5 else 'yellow'};")
            st.write("**DA/Quiz:**", f"{st.session_state.reviews[teacher]['da_quiz']}/10", style=f"color:{'green' if st.session_state.reviews[teacher]['da_quiz'] > 5 else 'red' if st.session_state.reviews[teacher]['da_quiz'] < 5 else 'yellow'};")
else:
    st.write("No teachers found.")
