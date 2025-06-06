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
def extract_address2(street):
    # Common patterns: Apt 5, Suite 19, Ste 2, #11, Unit 12, Bldg 4
    match = re.search(r'(Apt|Apartment|Suite|Ste|Unit|#|Bldg|Building|Floor|Fl|Rm|Room|Lot|Space|Dept|Trailer|Trlr|PO Box|P\.O\. Box|POB|Box)\s*[\w\-]+', street, re.IGNORECASE)
    if match:
        # Remove address2 from street
        address2 = match.group(0)
        street_clean = street.replace(address2, '').replace(',', '').strip()
        return street_clean, address2.strip()
    # No address2 found
    return street.strip(), ""
    
def smart_address_split(address: str):
    lines = [l.strip() for l in address.replace('\r\n', '\n').split('\n') if l.strip()]
    # If all on one line, split by comma for possible name presence
    if len(lines) == 1:
        items = [x.strip() for x in lines[0].split(',')]
        if len(items) >= 4:
            name = items[0]
            street = items[1]
            city = items[2]
            state_zip = items[3]
        elif len(items) == 3:
            name = ""
            street = items[0]
            city = items[1]
            state_zip = items[2]
        else:
            name = ""
            street = lines[0]
            city = ""
            state_zip = ""
    else:
        if lines and not any(char.isdigit() for char in lines[0]):
            name = lines[0]
            street = lines[1] if len(lines) > 1 else ""
            city_state_zip = lines[2] if len(lines) > 2 else ""
        else:
            name = ""
            street = lines[0]
            city_state_zip = lines[1] if len(lines) > 1 else ""
        city = ""
        state_zip = ""
        if ',' in city_state_zip:
            parts = city_state_zip.split(',')
            city = parts[0].strip()
            state_zip = parts[1].strip() if len(parts) > 1 else ""
        else:
            city = city_state_zip
            state_zip = ""
    state, zip_code = "", ""
    if 'state_zip' in locals():
        m = re.match(r'([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?', state_zip)
        if m:
            state = m.group(1)
            zip_code = m.group(2) if m.group(2) else ""
        else:
            sz = state_zip.strip().split()
            if len(sz) == 2:
                state, zip_code = sz
            elif len(sz) == 1:
                state = sz[0]
    else:
        state, zip_code = "", ""
    name = name.strip(",")
    street = street.strip(",")
    city = city.strip(",")
    state = state.strip(",")
    zip_code = zip_code.strip(",")

    # --- Address 2 extraction ---
    street_clean, address2 = extract_address2(street)

    return name, street_clean, address2, city, state, zip_code

# ---- Streamlit UI ----
st.set_page_config(page_title="Shipping Tools", layout="centered")
st.title("Shipping Helper Tool")

# --- Packaging Splitter ---
with st.expander("📦 Packaging Splitter", expanded=True):
    weight = st.number_input("Enter total shipment weight (kg):", min_value=0.1, step=0.1, value=25.0, format="%.1f")
    option = st.selectbox("Select Packaging Option:", list(BOX_CONFIGS.keys()))
    box_sizes = BOX_CONFIGS[option]
    split = split_weight(weight, box_sizes)
    st.subheader("Packaging Breakdown")
    st.table({
        "Box #": [f"{i+1}" for i in range(len(split))],
        "Kg": [f"{x:.1f}" for x in split],
        "Lb (1kg=4lb)": [str(format_lb(x)) for x in split]
    })

# --- Address Splitter ---
with st.expander("🏷️ Address Splitter", expanded=True):
    st.write("Paste an address (any format, partial or full, with or without country):")
    address_input = st.text_area(
        "Address Input",
        height=100,
        value="Adam Sanders\n88 Huntoon Memorial Hwy\nRochdale, MA 01542"
    )
    if address_input.strip():
        name, street, address2, city, state, zip_code = smart_address_split(address_input)
        st.subheader("Split Address")
        st.write(f"**Name:** {name}")
        st.write(f"**Street Address:** {street}")
        st.write(f"**Address 2:** {address2}")
        st.write(f"**City:** {city}")
        st.write(f"**State:** {state}")
        st.write(f"**ZIP:** {zip_code}")

        # Tab-separated with blank Address2 if not found
        sheets_row = f"{name}\t\t{street}\t{address2}\t{city}\t{state}\t{zip_code}"

        st.markdown("#### Copy for Google Sheets Row")
        st.code(sheets_row, language="")
        st_copy_to_clipboard(sheets_row, "📋 Copy Row")
        st.caption("Paste into your Google Sheet row (Name | Org | Street Address | Address2 | City | State | ZIP).")
