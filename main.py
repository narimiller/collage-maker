import streamlit as st
from PIL import Image, ImageOps, ImageFile
import pillow_heif
import io
import math

ImageFile.LOAD_TRUNCATED_IMAGES = True
MAX_IMAGE_PIXELS = 178956970
pillow_heif.register_heif_opener()

st.title("Inktober 2024 Collage Maker")
st.write("""Congratulations on completing Inktober at the Movies! This tool will arrange your images into an n-by-3 collage, where the number of rows depends on the number of images. 
         You may upload up to 15 images at a time. Generate as many collages as you need to showcase all your submissions.""")

st.markdown("<br>", unsafe_allow_html=True)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "clear_files" not in st.session_state:
    st.session_state.clear_files = False

# Collage layout settings
COLLAGE_WIDTH = 1500
GRID_COLUMNS = 3
CELL_SIZE = COLLAGE_WIDTH // GRID_COLUMNS  # Square cells of 500x500 pixels each
PADDING = 10  # Padding between images
BORDER_SIZE = 20  
PADDING_COLOR = (40, 40, 40)

uploaded_files = st.file_uploader(
    "Upload up to 15 photos", type=["jpg", "jpeg", "png", "heic"], accept_multiple_files=True
)

if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    st.session_state.clear_files = False

if st.button("Clear Selection"):
    st.session_state.uploaded_files = None
    st.session_state.clear_files = True

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.uploaded_files and not st.session_state.clear_files:
    # Custom filename input
    custom_filename = st.text_input("Enter a filename for your collage (without extension)", "collage")

    if st.button("Create Collage"):
        num_images = len(st.session_state.uploaded_files)
        
        if num_images > 15:
            st.error("Please upload up to 15 images only.")
        else:
            images = []
            num_rows = math.ceil(num_images / GRID_COLUMNS)
            collage_height = num_rows * CELL_SIZE + (num_rows - 1) * PADDING 

            canvas_width = COLLAGE_WIDTH + 2 * BORDER_SIZE
            canvas_height = collage_height + 2 * BORDER_SIZE

            for uploaded_file in st.session_state.uploaded_files:
                try:
                    # Open and resize each image
                    image = Image.open(uploaded_file)
                    image.thumbnail((CELL_SIZE - PADDING, CELL_SIZE - PADDING), Image.Resampling.LANCZOS)
                    square_image = ImageOps.pad(image, (CELL_SIZE - PADDING, CELL_SIZE - PADDING), color=(40,40,40))
                    images.append(square_image)
                except Exception as e:
                    st.error(f"Could not process image {uploaded_file.name}: {e}")
                    continue

            if not images:
                st.warning("No valid images to create a collage.")
                st.stop()

            # Create a black canvas for the border
            collage_with_border = Image.new("RGB", (canvas_width, canvas_height), color=(40,40,40))

            # Create canvas for collage
            collage = Image.new("RGB", (COLLAGE_WIDTH, collage_height), (40,40,40))

            for idx, image in enumerate(images):
                row = idx // GRID_COLUMNS
                col = idx % GRID_COLUMNS
                x_offset = col * (CELL_SIZE + PADDING)
                y_offset = row * (CELL_SIZE + PADDING)

                collage.paste(PADDING_COLOR, (x_offset, y_offset, x_offset + CELL_SIZE + PADDING, y_offset + CELL_SIZE + PADDING))

                collage.paste(image, (x_offset + PADDING // 2, y_offset + PADDING // 2))

            # Paste collage onto black canvas
            collage_with_border.paste(collage, (BORDER_SIZE, BORDER_SIZE))

            # Display collage with border
            st.image(collage_with_border, caption=f"{custom_filename}", use_column_width=True)

            # Download button
            buffer = io.BytesIO()
            collage_with_border.save(buffer, format="PNG")
            buffer.seek(0)
            st.download_button(
                label="Download Collage",
                data=buffer,
                file_name=f"{custom_filename}.png",
                mime="image/png"
            )
else:
    st.info("Please upload photos to create a collage.")