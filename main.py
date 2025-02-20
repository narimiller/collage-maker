import streamlit as st
from PIL import Image, ImageOps, ImageFile
from PIL.ExifTags import TAGS
import pillow_heif
import io
import math

st.set_option("client.showErrorDetails", False)

def apply_exif_rotation(image):
    try:
        if hasattr(image, "_getexif"):
            exif = image._getexif()
            if exif is not None:
                for tag, value in exif.items():
                    if TAGS.get(tag) == 'Orientation':
                        # Apply the transformations based on EXIF orientation
                        if value == 2:
                            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        elif value == 3:
                            return image.transpose(Image.Transpose.ROTATE_180)
                        elif value == 4:
                            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                        elif value == 5:
                            return image.transpose(Image.Transpose.ROTATE_270).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        elif value == 6:
                            return image.transpose(Image.Transpose.ROTATE_270)
                        elif value == 7:
                            return image.transpose(Image.Transpose.ROTATE_90).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                        elif value == 8:
                            return image.transpose(Image.Transpose.ROTATE_90)
                        elif value == 3:
                            return image.rotate(180, expand=True)
                        elif value == 6:
                            return image.rotate(270, expand=True)
                        elif value == 8:
                            return image.rotate(90, expand=True)                       
        return image
    except Exception as e:
        st.error(f"Error applying EXIF rotation: {e}")
        return image

ImageFile.LOAD_TRUNCATED_IMAGES = True
MAX_IMAGE_PIXELS = 178956970
pillow_heif.register_heif_opener()

st.title("Collage Maker")
st.write("""This tool will arrange your images into an n-by-3 collage, where the number of rows depends on the number of images. 
         You may upload up to 15 images at a time. Generate as many collages as you need to showcase all your submissions.""")

st.markdown("<br>", unsafe_allow_html=True)

if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "clear_files" not in st.session_state:
    st.session_state.clear_files = False

# Collage layout settings
SCALE_FACTOR = (2000 / 1500)
COLLAGE_WIDTH = int(1500 * SCALE_FACTOR)
GRID_COLUMNS = 3
CELL_SIZE = int(COLLAGE_WIDTH // GRID_COLUMNS)  # Square cells
PADDING = int(10 * SCALE_FACTOR)  # Padding between images
BORDER_SIZE = int(20 * SCALE_FACTOR)
PADDING_COLOR = (40, 40, 40)

uploaded_files = st.file_uploader(
    "Upload up to 15 photos", type=["jpg", "jpeg", "png", "heic", "tiff"], accept_multiple_files=True
)

if uploaded_files:
    st.session_state.uploaded_files = uploaded_files
    st.session_state.clear_files = False

#if st.button("Clear Selection"):
#    st.session_state.uploaded_files = []
#    st.session_state.clear_files = True

st.write("*To clear your selection, please refresh the page.*")

st.markdown("<br>", unsafe_allow_html=True)

if st.session_state.uploaded_files and not st.session_state.clear_files:

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
                    image = Image.open(uploaded_file)
                    image = apply_exif_rotation(image)
                    
                    if uploaded_file.type == "image/tiff":
                        buffer = io.BytesIO()
                        image.convert("RGB").save(buffer, format="JPEG")
                        buffer.seek(0)
                        image = Image.open(buffer)

                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    
                    # Resize and prepare images
                    image.thumbnail((CELL_SIZE - PADDING, CELL_SIZE - PADDING), Image.Resampling.LANCZOS)
                    square_image = ImageOps.pad(image, (CELL_SIZE - PADDING, CELL_SIZE - PADDING), color=(40, 40, 40))
                    images.append(square_image)
                    
                except Exception as e:
                    st.error(f"Could not process image {uploaded_file.name}: {e}")
                    continue

            if not images:
                st.warning("No valid images to create a collage.")
                st.stop()

            collage_with_border = Image.new("RGB", (canvas_width, canvas_height), color=(40, 40, 40))

            # Create canvas
            collage = Image.new("RGB", (COLLAGE_WIDTH, collage_height), (40, 40, 40))

            for idx, image in enumerate(images):
                row = idx // GRID_COLUMNS
                col = idx % GRID_COLUMNS
                x_offset = col * (CELL_SIZE + PADDING)
                y_offset = row * (CELL_SIZE + PADDING)

                collage.paste(PADDING_COLOR, (x_offset, y_offset, x_offset + CELL_SIZE + PADDING, y_offset + CELL_SIZE + PADDING))
                collage.paste(image, (x_offset + PADDING // 2, y_offset + PADDING // 2))

            collage_with_border.paste(collage, (BORDER_SIZE, BORDER_SIZE))

            st.image(collage_with_border, caption=f"{custom_filename}", use_column_width=True)

            buffer = io.BytesIO()
            collage_with_border.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            st.download_button(
                label="Download Collage",
                data=buffer,
                file_name=f"{custom_filename}.jpg",
                mime="image/jpeg"
            )
else:
    st.info("Please upload photos to create a collage.")