import streamlit as st
import re
from st_copy_to_clipboard import st_copy_to_clipboard

def smart_address_split(address: str):
    # Remove country if present
    address = re.sub(r'\b(USA?|United States|US)\b\.?', '', address, flags=re.IGNORECASE).strip(", \n")

    # Split into lines or by comma if single line
    if "\n" in address:
        lines = [x.strip() for x in address.split("\n") if x.strip()]
    else:
        lines = [x.strip() for x in address.split(",")]

    # If first line is clearly a name (no digits), use as name
    if lines and not any(char.isdigit() for char in lines[0]):
        name = lines[0]
        lines = lines[1:]
    else:
        name = ""

    # Now flatten the rest for easier parsing
    rest = ", ".join(lines)

    # Regex: street, optional address2, city, state, zip
    pat = re.compile(
        r"""^
        (?P<street>[\d\w ./\-\#]+?)                                     
        (?:,\s*(?P<address2>(Apt|Apartment|Suite|Ste|Unit|#|Bldg|Building|Floor|Fl|Rm|Room|Lot|Space|Dept|Trailer|Trlr|PO Box|P\.O\. Box|POB|Box)\s*[\w\-]+))?   # optional address2
        ,?\s*(?P<city>[A-Za-z .'-]+)                                   
        ,\s*(?P<state>[A-Z]{2})                                          
        \s+(?P<zip>\d{5}(?:-\d{4})?)                                    
        $""", re.IGNORECASE | re.VERBOSE)

    m = pat.search(rest)
    if m:
        street = m.group("street").strip(", ")
        address2 = m.group("address2") or ""
        city = m.group("city").strip(", ")
        state = m.group("state").strip(", ")
        zip_code = m.group("zip").strip(", ")
    else:
        # Fallback: try to split anyway
        parts = [x.strip() for x in rest.split(",")]
        street = parts[0] if len(parts) > 0 else ""
        address2 = ""
        city = parts[1] if len(parts) > 1 else ""
        state_zip = parts[2] if len(parts) > 2 else ""
        m2 = re.match(r"([A-Z]{2})\s*(\d{5}(?:-\d{4})?)?", state_zip)
        state, zip_code = (m2.groups() if m2 else ("", ""))
        state = state or ""
        zip_code = zip_code or ""

    # Clean
    name = name.strip(", ")
    street = street.strip(", ")
    address2 = address2.strip(", ")
    city = city.strip(", ")
    state = state.strip(", ")
    zip_code = zip_code.strip(", ")

    return name, street, address2, city, state, zip_code

# ---- Streamlit UI ----
st.set_page_config(page_title="Shipping Tools", layout="centered")
st.title("Shipping Helper Tool")

# --- Packaging Splitter ---
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
        value="Adam Sanders\n14828 W 6TH AVE, STE 9B, GOLDEN, CO 80401-5000 US"
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

        # Tab-separated with blank Org column after Name
        sheets_row = f"{name}\t\t{street}\t{address2}\t{city}\t{state}\t{zip_code}"

        st.markdown("#### Copy for Google Sheets Row")
        st.code(sheets_row, language="")
        st_copy_to_clipboard(sheets_row, "📋 Copy Row")
        st.caption("Paste into your Google Sheet row (Name | Org | Street Address | Address2 | City | State | ZIP).")
