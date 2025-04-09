import json
import os
import streamlit as st
import pandas as pd

DATA_FILE = "custom_codes.json"

def load_custom_codes():
    """Load custom codes from the JSON file."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_custom_codes(codes):
    """Save custom codes to the JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(codes, f, indent=4)

# Default codes dictionary (cannot be edited or deleted).
default_content = {
    "12345678901": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/3/38/Streamlit_logo.png",
        "info": "This is the Streamlit logo. Streamlit is an open-source app framework for Machine Learning and Data Science projects."
    },
    "23456789012": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/4/4f/Cat_on_computer.jpg",
        "info": "Here is a playful image of a cat on a computer. Enjoy the charm of our furry friend!"
    },
    "34567890123": {
        "url": "https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png",
        "info": "This is the famous 'Lenna' image, widely used as a benchmark in image processing."
    }
}

# Load persistent custom codes from file.
custom_codes = load_custom_codes()

st.title("Art Catalogue")

# --- Section to Add a Single Custom Code ---
with st.expander("Add Custom Code"):
    with st.form("custom_code_form", clear_on_submit=True):
        new_code = st.text_input("Enter new 11-digit code:", max_chars=11)
        new_url = st.text_input("Enter image URL:")
        new_info = st.text_area("Enter information text:")
        submitted = st.form_submit_button("Add Code")
        if submitted:
            if new_code.strip() and new_url.strip() and new_info.strip():
                if not new_code.strip().isdigit() or len(new_code.strip()) != 11:
                    st.error("Code must be exactly 11 numerical digits.")
                else:
                    standardized_code = new_code.strip()
                    # Combine default and custom codes for validation.
                    combined_codes = default_content.copy()
                    combined_codes.update(custom_codes)
                    
                    if standardized_code in combined_codes:
                        st.error("This code already exists. Please try a different code.")
                    else:
                        custom_codes[standardized_code] = {"url": new_url.strip(), "info": new_info.strip()}
                        save_custom_codes(custom_codes)
                        st.success(f"Code '{standardized_code}' added successfully.")
            else:
                st.error("Please fill in all fields to add a custom code.")

# --- Section to Manage (Edit/Delete) Existing Codes ---
with st.expander("Manage Existing Codes"):
    # Combine default and custom codes.
    combined_codes = default_content.copy()
    combined_codes.update(custom_codes)
    
    if not combined_codes:
        st.write("No codes available to manage.")
    else:
        selected_code = st.selectbox(
            "Select a code to manage:",
            options=list(combined_codes.keys()),
            format_func=lambda x: f"{x} - {combined_codes[x]['info'][:50]}..."
        )
        
        if selected_code:
            st.write(f"**Current URL:** {combined_codes[selected_code]['url']}")
            st.write(f"**Current Info:** {combined_codes[selected_code]['info']}")
            
            # Provide an edit form.
            with st.form(f"edit_form_{selected_code}"):
                new_url = st.text_input("New URL:", value=combined_codes[selected_code]["url"])
                new_info = st.text_area("New Info:", value=combined_codes[selected_code]["info"])
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Code"):
                        if selected_code in default_content:
                            st.error("Cannot edit default codes. Please add a custom code to edit.")
                        else:
                            custom_codes[selected_code] = {"url": new_url.strip(), "info": new_info.strip()}
                            save_custom_codes(custom_codes)
                            st.success("Code updated successfully!")
                with col2:
                    if st.form_submit_button("Delete Code"):
                        if selected_code in default_content:
                            st.error("Cannot delete default codes.")
                        else:
                            del custom_codes[selected_code]
                            save_custom_codes(custom_codes)
                            st.success("Code deleted successfully!")
                            st.experimental_rerun()

# --- Section to Bulk Upload Codes via Excel ---
with st.expander("Bulk Upload Codes"):
    st.write("Upload an Excel file (.xlsx) with columns: **code**, **url**, **info**.")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
        else:
            required_cols = {"code", "url", "info"}
            if not required_cols.issubset(set(df.columns)):
                st.error("The Excel file must contain the columns: 'code', 'url', 'info'.")
            else:
                added = 0
                skipped = 0
                messages = []
                # Process each row.
                for idx, row in df.iterrows():
                    code_val = str(row['code']).strip()
                    url_val = str(row['url']).strip()
                    info_val = str(row['info']).strip()
                    row_number = idx + 2  # Accounting for header row.
                    if len(code_val) != 11 or not code_val.isdigit():
                        messages.append(f"Row {row_number}: Code '{code_val}' is invalid (must be 11 numerical digits). Skipped.")
                        skipped += 1
                        continue
                    if not url_val or not info_val:
                        messages.append(f"Row {row_number}: URL or Info is missing. Skipped.")
                        skipped += 1
                        continue
                    combined_codes = default_content.copy()
                    combined_codes.update(custom_codes)
                    if code_val in combined_codes:
                        messages.append(f"Row {row_number}: Code '{code_val}' already exists. Skipped.")
                        skipped += 1
                    else:
                        custom_codes[code_val] = {"url": url_val, "info": info_val}
                        added += 1
                save_custom_codes(custom_codes)
                st.success(f"Bulk upload complete. Added {added} codes; skipped {skipped} rows.")
                if messages:
                    st.info("\n".join(messages))

# --- Section to Display Content Based on Code ---
st.header("View Art by Code")
user_code = st.text_input("Enter an 11-digit code to display the corresponding image and information:", key="view_code")
if user_code:
    entered_code = user_code.strip()
    if not entered_code.isdigit() or len(entered_code) != 11:
        st.error("Please enter exactly 11 numerical digits.")
    else:
        combined_codes = default_content.copy()
        combined_codes.update(custom_codes)
        if entered_code in combined_codes:
            col1, col2 = st.columns(2)
            with col1:
                st.image(combined_codes[entered_code]["url"], use_container_width=True)
            with col2:
                st.header("Image Information")
                st.write(combined_codes[entered_code]["info"])
        else:
            st.error("Unrecognized code. Please try again with a valid code.")
