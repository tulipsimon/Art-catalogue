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

# Load persistent custom codes from file.
custom_codes = load_custom_codes()

st.title("Art Catalogue")

# --- Section to Add a Single Custom Code ---
with st.expander("Add Custom Code"):
    with st.form("custom_code_form", clear_on_submit=True):
        new_code = st.text_input("Enter new 11-digit code:", max_chars=11)
        new_url = st.text_input("Enter image URL:")
        name = st.text_input("Name (optional):")
        
        # Split info into categories
        col1, col2 = st.columns(2)
        with col1:
            media = st.text_input("Media (e.g., Oil on Canvas):")
            year = st.text_input("Year:", max_chars=4)
            series = st.text_input("Series:")
        with col2:
            secondary_series = st.text_input("Secondary Series (optional):")
            length = st.text_input("Length (cm):")
            width = st.text_input("Width (cm):")
            area = st.text_input("Area (cm²):")
        
        submitted = st.form_submit_button("Add Code")
        if submitted:
            if (new_code.strip() and new_url.strip() and media and year and 
                series and length and width and area):
                if not new_code.strip().isdigit() or len(new_code.strip()) != 11:
                    st.error("Code must be exactly 11 numerical digits.")
                elif not year.isdigit() or len(year) != 4:
                    st.error("Year must be a 4-digit number.")
                else:
                    standardized_code = new_code.strip()
                    if standardized_code in custom_codes:
                        st.error("This code already exists. Please try a different code.")
                    else:
                        custom_codes[standardized_code] = {
                            "url": new_url.strip(),
                            "name": name.strip(),
                            "details": {
                                "media": media.strip(),
                                "year": year.strip(),
                                "series": series.strip(),
                                "secondary_series": secondary_series.strip(),
                                "dimensions": {
                                    "length": length.strip(),
                                    "width": width.strip(),
                                    "area": f"{area.strip()} cm²"
                                }
                            }
                        }
                        save_custom_codes(custom_codes)
                        st.success(f"Code '{standardized_code}' added successfully.")
            else:
                st.error("Please fill in all required fields (except name and secondary series).")

# --- Section to Manage (Edit/Delete) Existing Codes ---
with st.expander("Manage Existing Codes"):
    if not custom_codes:
        st.write("No codes available to manage.")
    else:
        st.write("Available codes:")
        st.write(list(custom_codes.keys()))
        
        selected_code = st.text_input(
            "Enter the 11-digit code you want to manage:",
            key="manage_code"
        )
        
        if selected_code:
            entered_code = selected_code.strip()
            if not entered_code.isdigit() or len(entered_code) != 11:
                st.error("Please enter exactly 11 numerical digits.")
            elif entered_code not in custom_codes:
                st.error("Code not found. Please enter a valid code.")
            else:
                st.write(f"**Current URL:** {custom_codes[entered_code]['url']}")
                if custom_codes[entered_code].get('name'):
                    st.write(f"**Name:** {custom_codes[entered_code]['name']}")
                details = custom_codes[entered_code]['details']
                
                with st.form(f"edit_form_{entered_code}"):
                    new_url = st.text_input("New URL:", value=custom_codes[entered_code]["url"])
                    new_name = st.text_input("Name:", value=custom_codes[entered_code].get('name', ''))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_media = st.text_input("Media:", value=details["media"])
                        new_year = st.text_input("Year:", value=details["year"], max_chars=4)
                        new_series = st.text_input("Series:", value=details["series"])
                    with col2:
                        new_secondary_series = st.text_input("Secondary Series:", 
                                            value=details["secondary_series"])
                        new_length = st.text_input("Length (cm):", 
                                        value=details["dimensions"]["length"].replace(' cm²', '').split(' ')[0])
                        new_width = st.text_input("Width (cm):", 
                                       value=details["dimensions"]["width"].replace(' cm²', '').split(' ')[0])
                        new_area = st.text_input("Area (cm²):", 
                                   value=details["dimensions"]["area"].replace(' cm²', '').split(' ')[0])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update Code"):
                            if not new_year.isdigit() or len(new_year) != 4:
                                st.error("Year must be a 4-digit number.")
                            else:
                                custom_codes[entered_code] = {
                                    "url": new_url.strip(),
                                    "name": new_name.strip(),
                                    "details": {
                                        "media": new_media.strip(),
                                        "year": new_year.strip(),
                                        "series": new_series.strip(),
                                        "secondary_series": new_secondary_series.strip(),
                                        "dimensions": {
                                            "length": new_length.strip(),
                                            "width": new_width.strip(),
                                            "area": f"{new_area.strip()} cm²"
                                        }
                                    }
                                }
                                save_custom_codes(custom_codes)
                                st.success("Code updated successfully!")
                    with col2:
                        if st.form_submit_button("Delete Code"):
                            del custom_codes[entered_code]
                            save_custom_codes(custom_codes)
                            st.success("Code deleted successfully!")
                            st.experimental_rerun()

# --- Section to Bulk Upload Codes via Excel ---
with st.expander("Bulk Upload Codes"):
    st.write("""
    Upload an Excel file (.xlsx) with these columns:
    - **code**: 11-digit code
    - **url**: Image URL
    - **name**: Optional artwork name
    - **media**: e.g., Oil on Canvas
    - **year**: 4-digit year
    - **series**: Primary series
    - **secondary_series**: Optional
    - **length**: in cm
    - **width**: in cm
    - **area**: in cm²
    """)
    
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
        else:
            required_cols = {
                "code", "url", "media", "year", 
                "series", "length", "width", "area"
            }
            if not required_cols.issubset(set(df.columns)):
                st.error(f"The Excel file must contain these columns: {', '.join(required_cols)}")
            else:
                added = 0
                skipped = 0
                messages = []
                
                # Reverted to vertical code list display
                if custom_codes:
                    st.write("Existing Codes:")
                    st.write(list(custom_codes.keys()))
                
                for idx, row in df.iterrows():
                    code_val = str(row['code']).strip()
                    url_val = str(row['url']).strip()
                    row_number = idx + 2
                    
                    if len(code_val) != 11 or not code_val.isdigit():
                        messages.append(f"Row {row_number}: Invalid code (must be 11 digits)")
                        skipped += 1
                        continue
                    if not url_val:
                        messages.append(f"Row {row_number}: Missing URL")
                        skipped += 1
                        continue
                    if not str(row['year']).strip().isdigit() or len(str(row['year']).strip()) != 4:
                        messages.append(f"Row {row_number}: Year must be 4 digits")
                        skipped += 1
                        continue
                    
                    details = {
                        "media": str(row['media']).strip(),
                        "year": str(row['year']).strip(),
                        "series": str(row['series']).strip(),
                        "secondary_series": str(row.get('secondary_series', '')).strip(),
                        "dimensions": {
                            "length": str(row['length']).strip(),
                            "width": str(row['width']).strip(),
                            "area": f"{str(row['area']).strip()} cm²"
                        }
                    }
                    
                    if code_val in custom_codes:
                        messages.append(f"Row {row_number}: Code exists - skipped")
                        skipped += 1
                    else:
                        custom_codes[code_val] = {
                            "url": url_val,
                            "name": str(row.get('name', '')).strip(),
                            "details": details
                        }
                        added += 1
                
                save_custom_codes(custom_codes)
                st.success(f"Bulk upload complete. Added {added} codes; skipped {skipped} rows.")
                if messages:
                    with st.expander("View detailed messages"):
                        st.write("\n".join(messages))

# --- Section to Display Content Based on Code ---
st.header("View Art by Code")
user_code = st.text_input("Enter an 11-digit code to display the corresponding image and information:", 
                         key="view_code")
if user_code:
    entered_code = user_code.strip()
    if not entered_code.isdigit() or len(entered_code) != 11:
        st.error("Please enter exactly 11 numerical digits.")
    else:
        if entered_code in custom_codes:
            artwork = custom_codes[entered_code]
            col1, col2 = st.columns(2)
            with col1:
                st.image(artwork["url"], use_container_width=True)
            with col2:
                st.header("Artwork Details")
                if artwork.get('name'):
                    st.subheader(artwork['name'])
                
                st.write(f"**Code:** {entered_code}")
                details = artwork["details"]
                
                st.subheader("Basic Information")
                st.write(f"**Media:** {details['media']}")
                st.write(f"**Year:** {details['year']}")
                st.write(f"**Series:** {details['series']}")
                if details['secondary_series']:
                    st.write(f"**Secondary Series:** {details['secondary_series']}")
                
                st.subheader("Dimensions")
                st.write(f"**Length:** {details['dimensions']['length']} cm")
                st.write(f"**Width:** {details['dimensions']['width']} cm")
                st.write(f"**Area:** {details['dimensions']['area']}")
        else:
            st.error("Unrecognized code. Please try again with a valid code.")
