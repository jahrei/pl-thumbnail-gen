from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

app = Flask(__name__)

# Function to process the image
def add_text_to_image(image, weight_number):
    draw = ImageDraw.Draw(image)
    
    # Define the font sizes and paths
    try:
        font_bold = ImageFont.truetype("Helvetica-Bold.ttf", 320)
        font_regular = ImageFont.truetype("Helvetica-Bold.ttf", 50)
    except IOError:
        raise IOError("Helvetica font files not found. Please ensure 'Helvetica-Bold.ttf' is in the same directory as the script.")
    
    # Text to display
    text_number = f"{weight_number}"
    text_lb = "lb"
    
    # Calculate the size of each text part
    size_number = draw.textbbox((0, 0), text_number, font=font_bold)  # Bounding box of the number
    size_lb = draw.textbbox((0, 0), text_lb, font=font_regular)      # Bounding box of "lb"
    
    number_width = size_number[2] - size_number[0]  # Width of the bounding box
    number_height = size_number[3] - size_number[1]  # Height of the bounding box
    lb_width = size_lb[2] - size_lb[0]
    lb_height = size_lb[3] - size_lb[1]
    
    # Calculate total width and height
    total_width = number_width + lb_width
    total_height = max(number_height, lb_height)
    
    # Calculate position to center the text
    image_width, image_height = image.size
    x = (image_width - total_width) // 2
    y = (image_height - total_height) // 2
    
    # Draw the bold number
    draw.text((x, y), text_number, font=font_bold, fill="white")
    # Draw the "lb" slightly offset to the right of the number
    draw.text((x + number_width, y + (number_height - lb_height)), text_lb, font=font_regular, fill="white")
    
    return image

# Routes
@app.route("/")
def upload_form():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files or "weight" not in request.form:
        return "Please upload an image and enter a weight or text.", 400

    image_file = request.files["image"]
    weight = request.form["weight"]
    add_lb = "add_lb" in request.form  # Check if the checkbox was selected

    try:
        # Open the image
        image = Image.open(image_file.stream)

        # Convert to RGB mode if the image has an alpha channel
        if image.mode == "RGBA":
            image = image.convert("RGB")
        
        # Add text to the image
        draw = ImageDraw.Draw(image)
        
        font_bold = ImageFont.truetype("Helvetica-Bold.ttf", 320)
        font_regular = ImageFont.truetype("Helvetica-Bold.ttf", 50)
        
        # Prepare text
        text_number = weight
        text_lb = "lb" if add_lb else ""
        
        size_number = draw.textbbox((0, 0), text_number, font=font_bold)
        size_lb = draw.textbbox((0, 0), text_lb, font=font_regular)
        
        number_width = size_number[2] - size_number[0]
        number_height = size_number[3] - size_number[1]
        lb_width = size_lb[2] - size_lb[0]
        lb_height = size_lb[3] - size_lb[1]
        
        total_width = number_width + (lb_width if add_lb else 0)
        total_height = max(number_height, lb_height if add_lb else 0)
        
        image_width, image_height = image.size
        x = (image_width - total_width) // 2
        y = (image_height - total_height) // 2
        
        draw.text((x, y), text_number, font=font_bold, fill="white")
        if add_lb:
            draw.text((x + number_width, y + (number_height - lb_height)), text_lb, font=font_regular, fill="white")
        
        # Save and send the file
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")  # Ensure we save as JPEG
        image_io.seek(0)
        filename = f"output_{weight}_lb.jpg" if add_lb else f"output_{weight}.jpg"
        return send_file(image_io, mimetype="image/jpeg", as_attachment=True, download_name=filename)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
