import streamlit as st
from PIL import Image, ImageOps, ImageFile
import pillow_heif  # Import pillow_heif for HEIC support
import io
import math

# Allow PIL to load large images without decompression error
ImageFile.LOAD_TRUNCATED_IMAGES = True
MAX_IMAGE_PIXELS = 178956970  # Pillow's safe default threshold
pillow_heif.register_heif_opener()  # Enable HEIC support

st.title("Collage Maker")

# Initialize session state variables
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "clear_files" not in st.session_state:
    st.session_state.clear_files = False

# Collage grid settings
COLLAGE_WIDTH = 1500
GRID_COLUMNS = 3
CELL_SIZE = COLLAGE_WIDTH // GRID_COLUMNS  # Square cells of 500x500 pixels each

uploaded_files = st.file_uploader(
    "Upload up to 15 photos", type=["jpg", "jpeg", "png", "heic"], accept_multiple_files=True
)

# Update session state with new uploads
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    st.session_state.clear_files = False

# Clear uploaded files on button press
if st.button("Clear Selection"):
    st.session_state.uploaded_files = None
    st.session_state.clear_files = True

if st.session_state.uploaded_files and not st.session_state.clear_files:
    if st.button("Create Collage"):
        num_images = len(st.session_state.uploaded_files)
        
        if num_images > 15:
            st.error("Please upload up to 15 images only.")
        else:
            images = []
            num_rows = math.ceil(num_images / GRID_COLUMNS)
            collage_height = num_rows * CELL_SIZE

            for uploaded_file in st.session_state.uploaded_files:
                try:
                    # Open and resize each image to fit within a square cell
                    image = Image.open(uploaded_file)
                    image.thumbnail((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
                    square_image = ImageOps.pad(image, (CELL_SIZE, CELL_SIZE), color=(26, 26, 26))
                    images.append(square_image)
                except Exception as e:
                    st.error(f"Could not process image {uploaded_file.name}: {e}")
                    continue

            if not images:
                st.warning("No valid images to create a collage.")
                st.stop()

            # Create canvas and arrange images in grid
            collage = Image.new("RGB", (COLLAGE_WIDTH, collage_height), color="white")
            for idx, image in enumerate(images):
                x_offset = (idx % GRID_COLUMNS) * CELL_SIZE
                y_offset = (idx // GRID_COLUMNS) * CELL_SIZE
                collage.paste(image, (x_offset, y_offset))

            st.image(collage, caption="Your Photo Collage", use_column_width=True)

            # Provide download option for the collage
            buffer = io.BytesIO()
            collage.save(buffer, format="PNG")
            buffer.seek(0)
            st.download_button(
                label="Download Collage",
                data=buffer,
                file_name="collage.png",
                mime="image/png"
            )
else:
    st.info("Please upload photos to create a collage.")


