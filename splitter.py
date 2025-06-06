import streamlit as st
import re

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

# ---- Address Splitter ----

def robust_address_split(address: str):
    # Tidy up the address
    lines = [l.strip() for l in address.replace("\r\n", "\n").split("\n") if l.strip()]
    name = lines[0] if len(lines) > 1 else ""
    addr_line = lines[1] if len(lines) > 1 else lines[0] if lines else ""
    citystatezip = ""
    country = ""
    if len(lines) > 2:
        addr_line = lines[1]
        citystatezip = lines[2]
        if len(lines) > 3:
            country = lines[3]
    elif ',' in addr_line:
        parts = addr_line.rsplit(',', 1)
        addr_line, citystatezip = parts[0].strip(), parts[1].strip()
    city, state, zipcode = "", "", ""
    match = re.search(r"(.*?),?\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)", citystatezip)
    if match:
        city, state, zipcode = match.group(1), match.group(2), match.group(3)
    else:
        if not name:
            addr_line = address
            city = state = zipcode = ""
    if not country:
        if "USA" in address or "United States" in address:
            country = "USA"
        else:
            country = ""
    return {
        "Name": name,
        "Street Address": addr_line,
        "City": city,
        "State": state,
        "ZIP": zipcode,
        "Country": country,
    }

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
    st.table(
        {
            "Box #": [f"{i+1}" for i in range(len(split))],
            "Kg": [f"{x:.1f}" for x in split],
            "Lb (1kg=4lb)": [str(format_lb(x)) for x in split]
        }
    )

# --- Address Splitter ---
with st.expander("🏷️ Address Splitter", expanded=True):
    st.write("Paste an address (any format, partial or full, with or without country):")
    address_input = st.text_area("Address Input", height=100, value="""Britt Kimmel
15373 E Hinsdale Cir ste a,
Centennial, CO 80112, USA""")
    if address_input.strip():
        parts = robust_address_split(address_input)
        st.subheader("Split Address")
        for label, value in parts.items():
            st.text_input(label, value, key=label)
