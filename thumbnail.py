import os
import requests
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any
from io import BytesIO

class ThumbnailGenerator:
    """Takes AI-generated images and applies The Policy Brief Master Template branding."""
    
    def __init__(self, output_dir: str = "web/public/thumbnails"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Attempt to load a thick, high-impact font suitable for YouTube."""
        # For cross-platform compatibility without manual font downloads,
        # we try standard system fonts or fallback to default
        try:
            # Try Mac impact font
            return ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", size)
        except OSError:
            try:
                # Try generic sans-serif
                return ImageFont.truetype("Arial.ttf", size)
            except OSError:
                # Download a heavy font dynamically for GitHub Actions (Ubuntu/Linux)
                import requests
                font_path = "/tmp/Roboto-Black.ttf"
                if not os.path.exists(font_path):
                    try:
                        print("Downloading Roboto-Black font for Linux compatibility...")
                        response = requests.get("https://github.com/google/fonts/raw/main/apache/robotoblack/Roboto-Black.ttf", timeout=10)
                        if response.status_code == 200:
                            with open(font_path, "wb") as f:
                                f.write(response.content)
                    except Exception as e:
                        print(f"⚠️ Failed to download font: {e}")
                
                try:
                    return ImageFont.truetype(font_path, size)
                except OSError:
                    return ImageFont.load_default()

    def generate_thumbnail(self, audit: Dict[str, Any]) -> str:
        """
        Downloads the AI-generated imagery (if available), or creates a base background.
        Applies a 70/30 or 50/50 split overlay with high-contrast text ("Financial War Room" style).
        """
        bill_id = audit.get("bill_id", "BILL")
        fluff_detected = audit.get("fluff_detected", False)
        
        # Dimensions for a standard 1080p YouTube Thumbnail
        width, height = 1920, 1080
        
        # 1. Base Image Layer
        # If we had a URL from Imagen, we'd fetch it here. For now, create a dark stylistic background.
        base_img_url = audit.get("youtube_metadata", {}).get("thumbnail_url")
        base_image = None
        
        if base_img_url:
            try:
                response = requests.get(base_img_url)
                if response.status_code == 200:
                    base_image = Image.open(BytesIO(response.content)).convert("RGBA")
                    # Resize and crop to fill 1920x1080
                    base_image = base_image.resize((width, height))
            except Exception as e:
                print(f"Failed to fetch base image: {e}")
                
        if not base_image:
            # Fallback War Room background: Dark slate with a subtle tint
            base_bg_color = (20, 20, 25, 255) # Dark slate
            base_image = Image.new("RGBA", (width, height), base_bg_color)
            
        # Create an overlay layer for the split text effect
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 2. Left Side Overlay (The Text Panel)
        # 40% width solid panel with a feathered/gradient edge (simplified to solid with slight opacity)
        panel_width = int(width * 0.45)
        
        # Unified Branding: Dark Blue/Gold
        overlay_color = (10, 25, 50, 230) # Navy Blue, mostly solid
        accent_color = (255, 215, 0, 255) # Gold
        main_text = "BILL\nBRIEF"
        sub_text_color = (200, 220, 255, 255)
            
        # Draw the solid panel on the left
        draw.rectangle([0, 0, panel_width, height], fill=overlay_color)
        
        # Draw a bright accent line separating the panel from the image
        draw.line([(panel_width, 0), (panel_width, height)], fill=accent_color, width=15)
        
        # 3. Add Text content
        font_main = self._get_font(250)
        font_bill_id = self._get_font(120)
        font_sponsor = self._get_font(80)
        font_pork = self._get_font(60)
        
        # Draw Main Status
        draw.multiline_text(
            (80, 100), 
            main_text, 
            font=font_main, 
            fill=accent_color,
            spacing=20,
            align="left"
        )
        
        # Include nickname if provided in the bill_id
        display_bill_id = bill_id.replace(" ", "")
        if " - " in audit.get("historical_context", "")[:30]:
            # Try to grab a descriptive nickname from the context
            nickname = audit.get("historical_context").split(" - ")[0]
            if len(nickname) < 40:
                display_bill_id = f"{display_bill_id} - {nickname}"
        
        # Draw Bill ID
        draw.text(
            (80, 750), 
            display_bill_id, 
            font=font_bill_id, 
            fill=(255, 255, 255, 255)
        )
        
        # Draw Sponsor info
        # Prefer the raw string pulled directly from the Congress API if available (bypasses AI hallucination)
        sponsor_name = audit.get("raw_api_sponsor")
        if not sponsor_name:
            sponsor_name = audit.get("sponsor_contact_info", {}).get("sponsor_name", "UNKNOWN SPONSOR")
            
        draw.text(
            (80, 900), 
            f"SPONSOR: {sponsor_name[:35] + '...' if len(sponsor_name) > 35 else sponsor_name}".upper(), 
            font=font_sponsor, 
            fill=sub_text_color
        )
        
        # 4. Add "The Policy Brief" Branding
        draw.text(
            (width - 400, 50), 
            "THE POLICY BRIEF", 
            font=self._get_font(40), 
            fill=(255, 255, 255, 180)
        )
        
        # Composite the overlay onto the base image
        final_image = Image.alpha_composite(base_image, overlay)
        
        # 5. Add Conditional Pork Stamp (Watermark on the right side)
        if fluff_detected:
            try:
                # Load the pig icon
                pig_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "public", "pig-icon.png")
                if os.path.exists(pig_path):
                    pig_img = Image.open(pig_path).convert("RGBA")
                    
                    # Strip white AND gray checkerboard background pixels
                    # The AI-generated PNG has a fake checkerboard pattern baked in
                    pixels = pig_img.load()
                    for y in range(pig_img.height):
                        for x in range(pig_img.width):
                            r, g, b, a = pixels[x, y]
                            # Remove white-ish pixels
                            if r > 200 and g > 200 and b > 200:
                                pixels[x, y] = (r, g, b, 0)
                            # Remove gray checkerboard pixels (typically ~191 or ~204)
                            elif abs(r - g) < 10 and abs(g - b) < 10 and r > 150:
                                pixels[x, y] = (r, g, b, 0)
                    
                    # Resize icon to 200x200
                    pig_img = pig_img.resize((200, 200))
                    
                    # Position in bottom right, above the edge
                    pig_x = width - 300
                    pig_y = height - 350
                    
                    # Paste pig directly (no circle behind it)
                    final_image.paste(pig_img, (pig_x, pig_y), pig_img)
                    draw_final = ImageDraw.Draw(final_image)
                    
                    # Write "PORK ALERT" directly underneath
                    text_x = pig_x - 50
                    text_y = pig_y + 240
                    
                    # Add black stroke for readability
                    stroke_w = 4
                    for dx in range(-stroke_w, stroke_w+1):
                        for dy in range(-stroke_w, stroke_w+1):
                            draw_final.text((text_x+dx, text_y+dy), "PORK ALERT", font=font_pork, fill=(0, 0, 0, 255))
                    
                    draw_final.text((text_x, text_y), "PORK ALERT", font=font_pork, fill=(255, 50, 50, 255))
            except Exception as e:
                print(f"Failed to add Pork Stamp: {e}")
        
        # Convert back to RGB to save as JPEG
        final_image = final_image.convert("RGB")
        
        # Save to disk
        filename = f"{bill_id.replace(' ', '')}_thumbnail.jpg"
        filepath = os.path.join(self.output_dir, filename)
        final_image.save(filepath, format="JPEG", quality=90)
        
        print(f"🎬 Generated custom YouTube Thumbnail: {filepath}")
        
        return filepath
