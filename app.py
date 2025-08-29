import streamlit as st
import os
from google import genai
from google.genai import types
import PIL.Image
import io

# Configure page for mobile
st.set_page_config(
    page_title="Gemini AI Image Generator",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Mobile-optimized CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100% !important;
        padding: 0.5rem !important;
    }
    
    .stButton > button {
        width: 100% !important;
        height: 56px !important;
        font-size: 1rem !important;
        border-radius: 12px !important;
        margin: 0.5rem 0 !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        font-size: 16px !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    
    .stTextArea > div > div > textarea {
        min-height: 100px !important;
    }
    
    .stFileUploader > div {
        border-radius: 12px !important;
        border: 2px dashed #ccc !important;
        padding: 2rem 1rem !important;
        text-align: center !important;
    }
    
    .main-header {
        text-align: center;
        padding: 1rem 0 2rem 0;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
    }
    
    .main-header h1 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 4px;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .stImage > div {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
        background: #f1f5f9;
    }
    
    @media (max-width: 480px) {
        .main-header h1 {
            font-size: 1.3rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem;
            padding: 0 0.5rem;
        }
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# Initialize Gemini client
@st.cache_resource
def initialize_gemini():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("🔑 Please set your Google API Key in the secrets!")
        st.info("1. Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)")
        st.info("2. Add it as GOOGLE_API_KEY in your environment")
        st.stop()
    
    client = genai.Client(api_key=api_key)
    return client

MODEL_ID = "gemini-2.5-flash-image-preview"

def generate_image(prompt):
    """Generate an image from text prompt"""
    try:
        client = initialize_gemini()
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    )
                ],
                response_modalities=['Text', 'Image']
            )
        )
        
        generated_image = None
        response_text = ""
        
        for part in response.parts:
            if part.text:
                response_text += part.text + "\n"
            elif image := part.as_image():
                generated_image = image
        
        return generated_image, response_text.strip() if response_text else "Image generated successfully!"
        
    except Exception as e:
        return None, f"Error generating image: {str(e)}"

def edit_image(input_image, edit_prompt):
    """Edit an uploaded image based on text prompt"""
    try:
        client = initialize_gemini()
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[edit_prompt, input_image],
            config=types.GenerateContentConfig(
                safety_settings=[
                    types.SafetySetting(
                        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                        threshold=types.HarmBlockThreshold.BLOCK_NONE,
                    )
                ]
            )
        )
        
        edited_image = None
        response_text = ""
        
        for part in response.parts:
            if part.text:
                response_text += part.text + "\n"
            elif image := part.as_image():
                edited_image = image
        
        return edited_image, response_text.strip() if response_text else "Image edited successfully!"
        
    except Exception as e:
        return None, f"Error editing image: {str(e)}"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Gemini AI Image Generator</h1>
        <p>Generate & edit images with AI - Private Version</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🎭 Generate", "✏️ Edit", "📖 Help"])
    
    with tab1:
        st.subheader("Generate Images from Text")
        
        gen_prompt = st.text_area(
            "Describe your image:",
            value="Create a photorealistic image of people travelling in Metro train",
            height=100,
            placeholder="A futuristic city at sunset with flying cars..."
        )
        
        st.markdown("**Quick examples:**")
        
        col1, col2 = st.columns(2)
        
        example_prompts = [
            ("🏔️ Mountain sunrise", "A serene mountain landscape at dawn with morning mist"),
            ("🌃 Cyberpunk street", "A cyberpunk street scene with neon lights and rain"),
            ("🤖 Robot in library", "A cute robot reading a book in a cozy library"),
            ("🧚 Magic forest", "A magical forest with glowing mushrooms and fairy lights")
        ]
        
        for i, (label, prompt) in enumerate(example_prompts):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(label, key=f"gen_example_{i}", use_container_width=True):
                    st.session_state.gen_prompt = prompt
                    st.rerun()
        
        if 'gen_prompt' in st.session_state:
            gen_prompt = st.session_state.gen_prompt
            del st.session_state.gen_prompt
        
        if st.button("🎨 Generate Image", type="primary", use_container_width=True):
            if gen_prompt.strip():
                with st.spinner("Generating your image... This may take a moment."):
                    generated_image, status_text = generate_image(gen_prompt)
                    
                    if generated_image:
                        st.image(generated_image, caption="Generated Image", use_column_width=True)
                        
                        img_buffer = io.BytesIO()
                        generated_image.save(img_buffer, format="PNG")
                        st.download_button(
                            label="📥 Download Image",
                            data=img_buffer.getvalue(),
                            file_name="generated_image.png",
                            mime="image/png",
                            use_container_width=True
                        )
                    
                    st.markdown(f"""
                    <div class="status-box">
                        {status_text}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please enter a description for your image.")
    
    with tab2:
        st.subheader("Edit Existing Images")
        
        uploaded_file = st.file_uploader(
            "Upload an image to edit:",
            type=['png', 'jpg', 'jpeg'],
            help="Upload the image you want to edit"
        )
        
        if uploaded_file:
            image = PIL.Image.open(uploaded_file)
            st.image(image, caption="Original Image", use_column_width=True)
            
            edit_prompt = st.text_area(
                "How to edit the image:",
                value="Change all the people to animals wearing suits like Zootopia",
                height=100,
                placeholder="Change the sky to sunset colors with dramatic clouds..."
            )
            
            st.markdown("**Edit ideas:**")
            
            col1, col2 = st.columns(2)
            
            edit_examples = [
                ("❄️ Snowy weather", "Change the weather to snowy winter with falling snow"),
                ("🌸 Add flowers", "Add colorful flowers in the foreground"),
                ("📸 Vintage style", "Make it look like a vintage photograph from the 1950s"),
                ("🎨 Cartoon style", "Transform the scene into a cartoon animation style")
            ]
            
            for i, (label, prompt) in enumerate(edit_examples):
                col = col1 if i % 2 == 0 else col2
                with col:
                    if st.button(label, key=f"edit_example_{i}", use_container_width=True):
                        st.session_state.edit_prompt = prompt
                        st.rerun()
            
            if 'edit_prompt' in st.session_state:
                edit_prompt = st.session_state.edit_prompt
                del st.session_state.edit_prompt
            
            if st.button("✏️ Edit Image", type="primary", use_container_width=True):
                if edit_prompt.strip():
                    with st.spinner("Editing your image... This may take a moment."):
                        edited_image, status_text = edit_image(image, edit_prompt)
                        
                        if edited_image:
                            st.image(edited_image, caption="Edited Image", use_column_width=True)
                            
                            img_buffer = io.BytesIO()
                            edited_image.save(img_buffer, format="PNG")
                            st.download_button(
                                label="📥 Download Edited Image",
                                data=img_buffer.getvalue(),
                                file_name="edited_image.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        
                        st.markdown(f"""
                        <div class="status-box">
                            {status_text}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("Please describe how you want to edit the image.")
        else:
            st.info("👆 Please upload an image to get started!")
    
    with tab3:
        st.markdown("""
        ## 🚀 How to Use
        
        ### Generate Images
        1. **Write what you want to see** in the text box
        2. **Click "Generate Image"** and wait for the AI
        3. **Download your result** using the download button
        
        ### Edit Images  
        1. **Upload a photo** you want to edit
        2. **Describe the changes** you want to make
        3. **Click "Edit Image"** and wait for processing
        4. **Download the result** when ready
        
        ## 💡 Tips for Better Results
        - **Be specific and descriptive** in your prompts
        - Include details about **style, mood, and composition**
        - Mention **lighting, colors, and atmosphere**
        - Try the **example buttons** for inspiration
        - **Wait patiently** for processing to complete
        
        ## 🎨 Perfect For
        - Creative projects and artwork
        - Social media content creation  
        - Photo enhancement and stylization
        - Concept visualization and mockups
        
        ---
        
        ### 🔧 Setup Instructions
        1. Get your Google API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Set it as environment variable: `export GOOGLE_API_KEY="your_key_here"`
        3. Install dependencies: `pip install -r requirements.txt`
        4. Run the app: `streamlit run app.py`
        """)

if __name__ == "__main__":
    main()
