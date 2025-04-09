# --- Section to Bulk Upload Codes via Excel ---
with st.expander("Bulk Upload Codes"):
    st.write("""
    Upload an Excel file (.xlsx) with these columns:
    - **code**: 11-digit code
    - **url**: Image URL
    - **media**: e.g., Oil on Canvas
    - **year**: 4-digit year
    - **series**: Primary series
    - **secondary_series**: Optional
    - **length**: in cm
    - **width**: in cm
    - **size_category**: e.g., Small, Medium, Large
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
                "series", "length", "width", "size_category"
            }
            if not required_cols.issubset(set(df.columns)):
                st.error(f"The Excel file must contain these columns: {', '.join(required_cols)}")
            else:
                added = 0
                skipped = 0
                messages = []
                
                # Display available codes horizontally
                if custom_codes:
                    st.write("Existing Codes:")
                    # Create a row of buttons/pills for each code
                    cols = st.columns(8)  # Adjust number of columns as needed
                    col_index = 0
                    for code in custom_codes.keys():
                        with cols[col_index % len(cols)]:
                            st.code(code)
                        col_index += 1
                
                # Process each row
                for idx, row in df.iterrows():
                    code_val = str(row['code']).strip()
                    url_val = str(row['url']).strip()
                    row_number = idx + 2  # Accounting for header row
                    
                    # Validate required fields
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
                    
                    # Prepare details
                    details = {
                        "media": str(row['media']).strip(),
                        "year": str(row['year']).strip(),
                        "series": str(row['series']).strip(),
                        "secondary_series": str(row.get('secondary_series', '')).strip(),
                        "dimensions": {
                            "length": str(row['length']).strip(),
                            "width": str(row['width']).strip(),
                            "size_category": str(row['size_category']).strip()
                        }
                    }
                    
                    if code_val in custom_codes:
                        messages.append(f"Row {row_number}: Code exists - skipped")
                        skipped += 1
                    else:
                        custom_codes[code_val] = {
                            "url": url_val,
                            "details": details
                        }
                        added += 1
                
                save_custom_codes(custom_codes)
                st.success(f"Bulk upload complete. Added {added} codes; skipped {skipped} rows.")
                if messages:
                    with st.expander("View detailed messages"):
                        st.write("\n".join(messages))
