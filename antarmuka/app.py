import streamlit as st
import requests
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()
import os

# Page configuration
st.set_page_config(
    page_title="Image Comparator",
    page_icon="🖼️",
    layout="centered"
)

# Header
st.title("🖼️ Image Comparator")
st.markdown("Upload at least 2 images to compare using AI")

# API endpoint
API_URL = os.getenv("COMPARE_ENDPOINT")

st.sidebar.markdown("---")
st.sidebar.markdown("### How to Use")
st.sidebar.markdown("""
1. Upload at least 2 images
2. (Optional) Enter additional instructions
3. Click the **Compare Images** button
4. Wait for the AI comparison results
""")

# Upload images
st.subheader("📤 Upload Images")
uploaded_files = st.file_uploader(
    "Select images (minimum 2)",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True,
    help="Upload at least 2 images to compare"
)

# Preview uploaded images
if uploaded_files:
    st.subheader("👀 Image Preview")
    cols = st.columns(min(len(uploaded_files), 4))
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(file, caption=f"Image {idx + 1}", use_container_width=True)

# Additional user input
st.subheader("💬 Additional Instructions (Optional)")
user_input = st.text_area(
    "Enter specific instructions or questions",
    placeholder="Example: Compare the color quality of both images...",
    help="Provide specific instructions for AI when comparing images"
)

# Compare button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    compare_button = st.button(
        "🔍 Compare Images",
        type="primary",
        use_container_width=True,
        disabled=len(uploaded_files) < 2
    )

# Validation and processing
if len(uploaded_files) < 2:
    st.info("ℹ️ Upload at least 2 images to start comparison")

if compare_button:
    if len(uploaded_files) < 2:
        st.error("❌ Please upload at least 2 images!")
    else:
        with st.spinner("🔄 Comparing images..."):
            try:
                # Prepare files for request
                files = []
                for file in uploaded_files:
                    # Reset file pointer
                    file.seek(0)
                    files.append(
                        ("images", (file.name, file.read(), file.type))
                    )
                
                # Prepare data
                data = {}
                if user_input and user_input.strip():
                    data["user_input"] = user_input.strip()
                
                # Send request to API
                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Comparison complete!")
                    
                    st.subheader("📊 Comparison Results")
                    st.json(result)
                    
                else:
                    st.error(f"❌ Error: {response.status_code}")
                    st.code(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the server is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout. Please try again later.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Image Comparator - Powered by AI"
    "</div>",
    unsafe_allow_html=True
)
