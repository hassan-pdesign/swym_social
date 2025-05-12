import os
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import uuid
from app.models.templates import Template, TemplateType
from app.models.content import Post, ContentStatus
from app.config import settings

logger = logging.getLogger(__name__)

class ImageGenerator:
    """Generator for social media post images using templates."""
    
    def __init__(self, output_dir: Optional[str] = None, fonts_dir: str = "app/templates/fonts"):
        """Initialize the image generator.
        
        Args:
            output_dir: Directory to save generated images, defaults to settings
            fonts_dir: Directory containing font files
        """
        self.output_dir = output_dir or settings.IMAGE_OUTPUT_DIR
        self.fonts_dir = fonts_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Default brand colors
        self.colors = {
            "primary": (41, 128, 185),    # Blue
            "secondary": (39, 174, 96),   # Green
            "accent": (230, 126, 34),     # Orange
            "light": (236, 240, 241),     # Light Gray
            "dark": (52, 73, 94),         # Dark Gray
            "white": (255, 255, 255),     # White
            "black": (0, 0, 0)            # Black
        }
        
        # Load default fonts
        self.default_fonts = {
            "title": self._load_font(os.path.join(self.fonts_dir, "OpenSans-Bold.ttf"), 48),
            "subtitle": self._load_font(os.path.join(self.fonts_dir, "OpenSans-SemiBold.ttf"), 36),
            "body": self._load_font(os.path.join(self.fonts_dir, "OpenSans-Regular.ttf"), 24),
            "small": self._load_font(os.path.join(self.fonts_dir, "OpenSans-Regular.ttf"), 18)
        }
    
    def _load_font(self, font_path: str, size: int) -> Optional[ImageFont.FreeTypeFont]:
        """Load a font file.
        
        Args:
            font_path: Path to the font file
            size: Font size
            
        Returns:
            PIL ImageFont object or None if loading fails
        """
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
            else:
                logger.warning(f"Font file not found: {font_path}, using default font")
                return ImageFont.load_default()
        except Exception as e:
            logger.error(f"Error loading font {font_path}: {str(e)}")
            return ImageFont.load_default()
    
    def _create_blank_image(self, width: int, height: int, color: Tuple[int, int, int]) -> Image.Image:
        """Create a blank image with specified dimensions and color.
        
        Args:
            width: Image width
            height: Image height
            color: RGB color tuple
            
        Returns:
            PIL Image object
        """
        return Image.new("RGB", (width, height), color)
    
    def _add_text(self, 
                  draw: ImageDraw.ImageDraw, 
                  text: str, 
                  position: Tuple[int, int], 
                  font: ImageFont.FreeTypeFont, 
                  color: Tuple[int, int, int] = (0, 0, 0),
                  max_width: int = None,
                  alignment: str = "left") -> int:
        """Add text to an image with proper wrapping.
        
        Args:
            draw: PIL ImageDraw object
            text: Text to add
            position: (x, y) position for text
            font: Font to use
            color: RGB color tuple
            max_width: Maximum width in pixels for text wrapping
            alignment: Text alignment (left, center, right)
            
        Returns:
            Y position after adding text (for sequential placement)
        """
        x, y = position
        if not max_width:
            draw.text(position, text, font=font, fill=color)
            return y + font.getbbox(text)[3] + 10
        
        # Wrap text
        lines = textwrap.wrap(text, width=max_width)
        for line in lines:
            line_width = font.getbbox(line)[2]
            
            # Calculate position based on alignment
            if alignment == "center":
                line_x = x - line_width // 2
            elif alignment == "right":
                line_x = x - line_width
            else:  # left alignment
                line_x = x
            
            draw.text((line_x, y), line, font=font, fill=color)
            y += font.getbbox(line)[3] + 5
        
        return y + 10
    
    def _add_overlay(self, image: Image.Image, opacity: float = 0.3) -> Image.Image:
        """Add a semi-transparent overlay to an image.
        
        Args:
            image: PIL Image object
            opacity: Opacity of the overlay (0-1)
            
        Returns:
            PIL Image with overlay
        """
        overlay = Image.new("RGBA", image.size, (0, 0, 0, int(255 * opacity)))
        return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    
    def generate_feature_image(self, post: Post, template: Template) -> str:
        """Generate a feature showcase image.
        
        Args:
            post: Post to generate image for
            template: Template to use
            
        Returns:
            Path to the generated image
        """
        try:
            # Create base image
            width = template.width
            height = template.height
            img = self._create_blank_image(width, height, self.colors["white"])
            draw = ImageDraw.Draw(img)
            
            # Add color background
            draw.rectangle([(0, 0), (width, height)], fill=self.colors["primary"])
            
            # Add accent bar
            bar_width = 20
            draw.rectangle([(0, 0), (bar_width, height)], fill=self.colors["accent"])
            
            # Extract title and short excerpt from post text
            text_parts = post.text_content.split('\n')
            title = text_parts[0] if text_parts else "Feature Highlight"
            
            # Find a good excerpt
            excerpt = ""
            for part in text_parts[1:]:
                if len(part) > 20 and not part.startswith('#'):
                    excerpt = part
                    break
            
            if not excerpt and len(text_parts) > 1:
                excerpt = text_parts[1]
            
            # Add title
            title_y = 60
            title_y = self._add_text(
                draw, 
                title[:70] + ('...' if len(title) > 70 else ''),  # Truncate long titles
                (width // 2, title_y), 
                self.default_fonts["title"], 
                self.colors["white"],
                max_width=30,
                alignment="center"
            )
            
            # Add divider
            divider_padding = 40
            draw.line([(width // 4, title_y + divider_padding), (width * 3 // 4, title_y + divider_padding)], 
                      fill=self.colors["light"], width=3)
            
            # Add excerpt
            excerpt_y = title_y + divider_padding + 40
            if excerpt:
                self._add_text(
                    draw, 
                    excerpt[:200] + ('...' if len(excerpt) > 200 else ''),  # Truncate long excerpts
                    (width // 2, excerpt_y), 
                    self.default_fonts["body"], 
                    self.colors["light"],
                    max_width=40,
                    alignment="center"
                )
            
            # Add branding at bottom
            branding_text = "Your Brand"  # Would come from settings in a real app
            branding_y = height - 60
            self._add_text(
                draw, 
                branding_text,
                (width // 2, branding_y), 
                self.default_fonts["subtitle"], 
                self.colors["white"],
                alignment="center"
            )
            
            # Save the image
            file_name = f"post_{post.id}_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join(self.output_dir, file_name)
            img.save(file_path, "PNG")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating feature image: {str(e)}")
            return ""
    
    def generate_quote_image(self, post: Post, template: Template) -> str:
        """Generate a quote/testimonial image.
        
        Args:
            post: Post to generate image for
            template: Template to use
            
        Returns:
            Path to the generated image
        """
        try:
            # Create base image
            width = template.width
            height = template.height
            img = self._create_blank_image(width, height, self.colors["white"])
            draw = ImageDraw.Draw(img)
            
            # Add background color
            draw.rectangle([(0, 0), (width, height)], fill=self.colors["light"])
            
            # Extract quote from post text
            text_parts = post.text_content.split('\n')
            
            # Try to find a good quote in the post
            quote = ""
            author = "Industry Expert"
            
            for part in text_parts:
                if '"' in part or '"' in part or '"' in part:
                    quote = part.replace('"', '').replace('"', '').replace('"', '').strip()
                    break
            
            if not quote and len(text_parts) > 0:
                quote = text_parts[0]
            
            # Add quotation mark
            quote_mark_size = 120
            quote_mark_font = self._load_font(os.path.join(self.fonts_dir, "OpenSans-Bold.ttf"), quote_mark_size)
            self._add_text(
                draw, 
                '"',
                (width // 2 - 200, 60), 
                quote_mark_font, 
                self.colors["primary"],
                alignment="center"
            )
            
            # Add central quote box
            box_padding = 40
            box_x = width // 8
            box_y = height // 4
            box_width = width * 3 // 4
            box_height = height // 2
            
            draw.rectangle(
                [(box_x, box_y), (box_x + box_width, box_y + box_height)], 
                fill=self.colors["white"],
                outline=self.colors["primary"],
                width=3
            )
            
            # Add quote text
            quote_y = box_y + box_padding
            quote_y = self._add_text(
                draw, 
                quote[:150] + ('...' if len(quote) > 150 else ''),  # Truncate long quotes
                (width // 2, quote_y), 
                self.default_fonts["subtitle"], 
                self.colors["dark"],
                max_width=30,
                alignment="center"
            )
            
            # Add author
            author_y = quote_y + 40
            self._add_text(
                draw, 
                f"— {author}",
                (width // 2, author_y), 
                self.default_fonts["body"], 
                self.colors["primary"],
                alignment="center"
            )
            
            # Add branding at bottom
            branding_text = "Your Brand"  # Would come from settings in a real app
            branding_y = height - 60
            self._add_text(
                draw, 
                branding_text,
                (width // 2, branding_y), 
                self.default_fonts["subtitle"], 
                self.colors["dark"],
                alignment="center"
            )
            
            # Save the image
            file_name = f"quote_{post.id}_{uuid.uuid4().hex[:8]}.png"
            file_path = os.path.join(self.output_dir, file_name)
            img.save(file_path, "PNG")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error generating quote image: {str(e)}")
            return ""
    
    def generate_image_for_post(self, post: Post, template_type: TemplateType = TemplateType.GENERAL) -> str:
        """Generate an image for a post based on template type.
        
        Args:
            post: Post to generate image for
            template_type: Type of template to use
            
        Returns:
            Path to the generated image
        """
        # Create a default template (in a real app, this would come from the database)
        template = Template(
            id=1,
            name="Default Template",
            template_type=template_type,
            width=1200,
            height=630,
            is_active=True
        )
        
        # Generate image based on template type
        if template_type == TemplateType.FEATURE_SHOWCASE:
            return self.generate_feature_image(post, template)
        elif template_type == TemplateType.TESTIMONIAL:
            return self.generate_quote_image(post, template)
        else:
            # Default to feature image for other types
            return self.generate_feature_image(post, template) 