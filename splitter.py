import streamlit as st
import re
import html

# -------------------
# Packaging Splitter
# -------------------
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

# -------------------
# Robust Address Splitter
# -------------------
def robust_address_split(address: str):
    # Remove trailing/leading whitespace and split into lines
    lines = [l.strip() for l in address.replace('\r\n', '\n').split('\n') if l.strip()]
    country = ""
    name = ""

    # Combine all lines for parsing
    full_address = ", ".join(lines)
    
    # Guess and remove country if present
    country_match = re.search(r"(USA|United States|Canada|Mexico)$", full_address, re.IGNORECASE)
    if country_match:
        country = country_match.group(0)
        full_address = re.sub(r",?\s*(" + country + r")$", "", full_address)
    else:
        country = ""
    
    # Try: street, city, state zip (eg: 4506 Central School Road, St. Charles, MO 63304)
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
        # fallback: try to guess parts
        street = full_address
        city = ""
        state = ""
        zip_code = ""

    # If name is present, it's probably the first line, if >1 line in original input
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

# -------------------
# Click-to-Copy Button
# -------------------
def copy_button(label, value, key=None):
    # Escape single quotes and HTML chars for JS/HTML
    safe_value = html.escape(value).replace("\n", "\\n").replace("'", "\\'")
    btn_id = f"copy-btn-{label.replace(' ', '-')}-{key or ''}"
    js = f"""
    <script>
    function copyToClipboard_{btn_id}() {{
        navigator.clipboard.writeText('{safe_value}');
        var btn = document.getElementById('{btn_id}');
        if(btn) {{
            var orig = btn.innerText;
            btn.innerText = 'Copied!';
            setTimeout(function(){{ btn.innerText=orig; }}, 1200);
        }}
    }}
    </script>
    """
    html_block = f"""
    {js}
    <button id="{btn_id}" onclick="copyToClipboard_{btn_id}()" style="margin-left:8px; margin-top: 5px;">Copy</button>
    """
    st.markdown(html_block, unsafe_allow_html=True)

# -------------------
# Streamlit UI
# -------------------
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
    address_input = st.text_area("Address Input", height=100, value="""4506 Central School Road, St. Charles, MO 63304, USA""")
    if address_input.strip():
        parts = robust_address_split(address_input)
        st.subheader("Split Address")
        for label, value in parts.items():
            col1, col2 = st.columns([3,1])
            col1.text_input(label, value, key=label)
            if value:
                copy_button(label, value, key=label)
