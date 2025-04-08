import json
import os
import streamlit as st

DATA_FILE = "custom_codes.json"

def load_custom_codes():
    """Load custom codes from the JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_custom_codes(codes):
    """Save custom codes to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(codes, f)

# Default codes dictionary.
default_content = {
    "code1": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/Streamlit_logo.png",
        "info": "This is the Streamlit logo. Streamlit is an open-source app framework for Machine Learning and Data Science projects."
    },
    "code2": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Cat_on_computer.jpg",
        "info": "Here is a playful image of a cat on a computer. Enjoy the charm of our furry friend!"
    },
    "code3": {
        "url": "https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png",
        "info": "This is the famous 'Lenna' image, widely used as a benchmark in image processing."
    }
}

# Load persistent custom codes from file
custom_codes = load_custom_codes()

st.title("Code-Based Image & Information Display with Persistent Storage")

# --- Section to Add Custom Codes ---
with st.expander("Add Custom Code"):
    with st.form("custom_code_form", clear_on_submit=True):
        new_code = st.text_input("Enter new code:")
        new_url = st.text_input("Enter image URL:")
        new_info = st.text_area("Enter information text:")
        submitted = st.form_submit_button("Add Code")
        if submitted:
            if new_code.strip() and new_url.strip() and new_info.strip():
                standardized_code = new_code.strip().lower()
                # Combine default and custom codes for validation
                combined_codes = default_content.copy()
                combined_codes.update(custom_codes)
                
                if standardized_code in combined_codes:
                    st.error("This code already exists. Please try a different code.")
                else:
                    # Save the new code to the custom_codes dictionary and persist it.
                    custom_codes[standardized_code] = {"url": new_url, "info": new_info}
                    save_custom_codes(custom_codes)
                    st.success(f"Code '{standardized_code}' added successfully.")
            else:
                st.error("Please fill in all fields to add a custom code.")

# Combine the default codes with the custom codes
combined_codes = default_content.copy()
combined_codes.update(custom_codes)

# --- Section to Display Content Based on Code ---
user_code = st.text_input("Enter a code to display the corresponding image and information:")
if user_code:
    entered_code = user_code.strip().lower()
    if entered_code in combined_codes:
        col1, col2 = st.columns(2)
        with col1:
            st.image(combined_codes[entered_code]["url"], use_container_width=True)
        with col2:
            st.header("Image Information")
            st.write(combined_codes[entered_code]["info"])
    else:
        st.error("Unrecognized code. Please try again with a valid code.")
