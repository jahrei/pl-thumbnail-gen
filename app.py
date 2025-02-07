from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

# Function to process the image
def add_text_to_image(image, weight_number, unit, color, font_path, font_size):
    draw = ImageDraw.Draw(image)

    # Define fonts for the weight and unit
    try:
        font_weight = ImageFont.truetype(font_path, font_size)
        font_unit = ImageFont.truetype(font_path, int(font_size * 0.3))  # Unit font size is 30% of the main font
    except IOError:
        raise IOError(f"Font file '{font_path}' not found. Please ensure it is in the correct directory.")

    # Calculate text dimensions
    weight_text = f"{weight_number}"
    unit_text = unit

    size_weight = draw.textbbox((0, 0), weight_text, font=font_weight)
    size_unit = draw.textbbox((0, 0), unit_text, font=font_unit)

    weight_width = size_weight[2] - size_weight[0]
    weight_height = size_weight[3] - size_weight[1]
    unit_width = size_unit[2] - size_unit[0]
    unit_height = size_unit[3] - size_unit[1]

    # Calculate total width and alignment
    total_width = weight_width + unit_width
    total_height = max(weight_height, unit_height)

    image_width, image_height = image.size
    x = (image_width - total_width) // 2
    y = (image_height - total_height) // 2

    # Draw weight and unit text
    draw.text((x, y), weight_text, font=font_weight, fill=color)
    draw.text((x + weight_width, y + (weight_height - unit_height)), unit_text, font=font_unit, fill=color)

    return image


def apply_bodybuilding_mode(image):
    # Convert to black and white
    image = image.convert("L")  # L mode is grayscale

    # Adjust exposure and contrast
    exposure_offset = -2.6
    contrast_boost = 50

    # Apply exposure offset
    image = Image.eval(image, lambda p: max(0, min(255, p + int(exposure_offset * 10))))

    # Apply contrast boost
    factor = (259 * (contrast_boost + 255)) / (255 * (259 - contrast_boost))
    image = Image.eval(image, lambda p: max(0, min(255, int(factor * (p - 128) + 128))))

    return image

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files or "weight" not in request.form:
        return "Please upload an image and enter a weight or text.", 400

    image_file = request.files["image"]
    weight = request.form["weight"]
    unit = request.form["unit"]
    unit = "" if unit == "none" else unit
    color = "#FFD700" if request.form.get("color") == "gold" else "#f94449" if request.form.get("color") == "red" else "#FFFFFF"
    bodybuilding_mode = "bodybuilding" in request.form

    try:
        # Open the image
        image = Image.open(image_file.stream)

        # Convert to RGB mode if the image has an alpha channel
        if image.mode == "RGBA":
            image = image.convert("RGB")

        # Apply bodybuilding mode if selected
        if bodybuilding_mode:
            image = apply_bodybuilding_mode(image)
            font_path = "OldEnglish.ttf"
            font_size = 320
        else:
            font_path = "NimbusSanL-Bol.otf"
            font_size = 320

        # Add text to the image
        image = add_text_to_image(image, weight, unit, color, font_path, font_size)

        # Save and send the file
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        filename = f"output_{weight}_{unit if unit else 'no_unit'}{'_bodybuilding' if bodybuilding_mode else ''}.jpg"
        return send_file(image_io, mimetype="image/jpeg", as_attachment=True, download_name=filename)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
