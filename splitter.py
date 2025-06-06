import streamlit as st
import re
from st_copy_to_clipboard import st_copy_to_clipboard

# ---- Packaging Splitter ----
BOX_CONFIGS = {
    "Los Doz": [12, 6, 2],
    "AML (9kg)": [9],
    "AML (10kg)": [10]
}

def split_weight(weight, box_sizes):
    box_sizes = sorted(box_sizes, reverse=True)
    kg_left = weight
    result = []
    for size in box_sizes:
        while kg_left >= size:
            result.append(size)
            kg_left -= size
    if kg_left > 0:
        result.append(round(kg_left, 2))
    return result

def format_lb(kg):
    return int(kg * 4)

# ---- Robust Address Splitter ----
def robust_address_split(address: str):
    lines = [l.strip() for l in address.replace('\r\n', '\n').split('\n') if l.strip()]
    country = ""
    name = ""
    full_address = ", ".join(lines)
    country_match = re.search(r"(USA|United States|Canada|Mexico)$", full_address, re.IGNORECASE)
    if country_match:
        country = country_match.group(0)
        full_address = re.sub(r",?\s*(" + country + r")$", "", full_address)
    else:
        country = ""
    match = re.match(
        r"(?P<street>.+?),\s*(?P<city>[A-Za-z .'-]+),\s*(?P<state>[A-Z]{2})\s*(?P<zip>\d{5}(?:-\d{4})?)",
        full_address
    )
    if match:
        street = match.group("street")
        city = match.group("city")
        state = match.group("state")
        zip_code = match.group("zip")
    else:
        street = full_address
        city = ""
        state = ""
        zip_code = ""
    if len(lines) > 1:
        name = lines[0]
    return {
        "Name": name,
        "Street Address": street,
        "City": city,
        "State": state,
        "ZIP": zip_code,
        "Country": country,
    }

# ---- Address Splitter as before ----
def robust_address_split(address: str):
    lines = [l.strip() for l in address.replace('\r\n', '\n').split('\n') if l.strip()]
    country = ""
    name = ""
    full_address = ", ".join(lines)
    country_match = re.search(r"(USA|United States|Canada|Mexico)$", full_address, re.IGNORECASE)
    if country_match:
        country = country_match.group(0)
        full_address = re.sub(r",?\s*(" + country + r")$", "", full_address)
    else:
        country = ""
    match = re.match(
        r"(?P<street>.+?),\s*(?P<city>[A-Za-z .'-]+),\s*(?P<state>[A-Z]{2})\s*(?P<zip>\d{5}(?:-\d{4})?)",
        full_address
    )
    if match:
        street = match.group("street")
        city = match.group("city")
        state = match.group("state")
        zip_code = match.group("zip")
    else:
        street = full_address
        city = ""
        state = ""
        zip_code = ""
    if len(lines) > 1:
        name = lines[0]
    return {
        "Name": name,
        "Street Address": street,
        "City": city,
        "State": state,
        "ZIP": zip_code,
        "Country": country,
    }

# ---- Streamlit UI ----
st.set_page_config(page_title="Shipping Tools", layout="centered")
st.title("Shipping Helper Tool")

with st.expander("🏷️ Address Splitter", expanded=True):
    st.write("Paste an address (any format, partial or full, with or without country):")
    address_input = st.text_area(
        "Address Input",
        height=100,
        value="4506 Central School Road, St. Charles, MO 63304, USA"
    )
    if address_input.strip():
        parts = robust_address_split(address_input)
        st.subheader("Split Address")

        # Add custom CSS to make button and input align horizontally
        st.markdown("""
            <style>
            .address-row {
                display: flex;
                align-items: center;
                gap: 0.5em;
                margin-bottom: 0.1em;
            }
            .address-row input {
                flex: 1 1 70%;
                margin-bottom: 0 !important;
            }
            </style>
        """, unsafe_allow_html=True)

        for label, value in parts.items():
            row_key = f"row_{label}"
            st.markdown(f'<div class="address-row">', unsafe_allow_html=True)
            st.text_input(label, value, key=label, label_visibility="visible")
            # Insert the clipboard button as raw HTML in the same flex row
            if value:
                st.markdown(
                    st_copy_to_clipboard(value, "📋"),
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
