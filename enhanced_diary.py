#!/usr/bin/env python3
"""
Enhanced Digital Diary Generator - With Seasonal Backgrounds and Holidays
Creates an interactive PDF diary with seasonal themes, backgrounds, and holiday support
Usage: python enhanced_diary.py <year>
"""

import sys
import calendar
from datetime import datetime, date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch, mm
import random

from PasswordManager import get_secure_password_for_diary
import os


# Register multiple variants

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Holiday definitions

def get_us_holidays(year):
    """Get US Federal Holidays for a given year"""
    holidays = {}

    # Fixed date holidays
    holidays[date(year, 1, 1)] = "New Year's Day"
    holidays[date(year, 7, 4)] = "Independence Day"
    holidays[date(year, 11, 11)] = "Veterans Day"
    holidays[date(year, 12, 25)] = "Christmas Day"

    # MLK Day - Third Monday in January
    jan_1 = date(year, 1, 1)
    days_to_monday = (7 - jan_1.weekday()) % 7
    first_monday = jan_1.replace(day=1 + days_to_monday)
    mlk_day = first_monday.replace(day=first_monday.day + 14)  # Third Monday
    holidays[mlk_day] = "Martin Luther King Jr. Day"

    # Presidents Day - Third Monday in February
    feb_1 = date(year, 2, 1)
    days_to_monday = (7 - feb_1.weekday()) % 7
    first_monday = feb_1.replace(day=1 + days_to_monday)
    presidents_day = first_monday.replace(day=first_monday.day + 14)  # Third Monday
    holidays[presidents_day] = "Presidents Day"

    # Memorial Day - Last Monday in May
    may_31 = date(year, 5, 31)
    days_back_to_monday = (may_31.weekday() + 1) % 7
    memorial_day = may_31.replace(day=31 - days_back_to_monday)
    holidays[memorial_day] = "Memorial Day"

    # Labor Day - First Monday in September
    sep_1 = date(year, 9, 1)
    days_to_monday = (7 - sep_1.weekday()) % 7
    labor_day = sep_1.replace(day=1 + days_to_monday)
    holidays[labor_day] = "Labor Day"

    # Columbus Day - Second Monday in October
    oct_1 = date(year, 10, 1)
    days_to_monday = (7 - oct_1.weekday()) % 7
    first_monday = oct_1.replace(day=1 + days_to_monday)
    columbus_day = first_monday.replace(day=first_monday.day + 7)  # Second Monday
    holidays[columbus_day] = "Columbus Day"

    # Thanksgiving - Fourth Thursday in November
    nov_1 = date(year, 11, 1)
    days_to_thursday = (3 - nov_1.weekday()) % 7
    first_thursday = nov_1.replace(day=1 + days_to_thursday)
    thanksgiving = first_thursday.replace(day=first_thursday.day + 21)  # Fourth Thursday
    holidays[thanksgiving] = "Thanksgiving Day"

    return holidays

def is_weekend(date_obj):
    """Check if a date is a weekend (Saturday=5, Sunday=6)"""
    return date_obj.weekday() >= 5

# Wisdom quotes for different contexts
WISDOM_QUOTES = [
    "The journey of a thousand miles begins with one step. - Lao Tzu",
    "In the middle of difficulty lies opportunity. - Albert Einstein",
    "Life is what happens when you're busy making other plans. - John Lennon",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "Be yourself; everyone else is already taken. - Oscar Wilde",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "The best time to plant a tree was 20 years ago. The second best time is now. - Chinese Proverb",
    "Your time is limited, don't waste it living someone else's life. - Steve Jobs",
    "The only impossible journey is the one you never begin. - Tony Robbins",
    "In the end, we will remember not the words of our enemies, but the silence of our friends. - Martin Luther King Jr.",
    "The greatest glory in living lies not in never falling, but in rising every time we fall. - Nelson Mandela",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Life is really simple, but we insist on making it complicated. - Confucius",
    "May you live in interesting times. - Ancient Curse",
    "The only true wisdom is in knowing you know nothing. - Socrates",
    "Yesterday is history, tomorrow is a mystery, today is a gift. - Eleanor Roosevelt",
    "Do not go where the path may lead, go instead where there is no path and leave a trail. - Ralph Waldo Emerson",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The mind is everything. What you think you become. - Buddha",
    "A person who never made a mistake never tried anything new. - Albert Einstein",
    "Happiness is not something ready made. It comes from your own actions. - Dalai Lama",
    "The purpose of our lives is to be happy. - Dalai Lama",
    "Life is 10% what happens to you and 90% how you react to it. - Charles R. Swindoll",
    "The only way out is through. - Robert Frost",
    "What lies behind us and what lies before us are tiny matters compared to what lies within us. - Ralph Waldo Emerson",
    "You miss 100% of the shots you don't take. - Wayne Gretzky",
    "Whether you think you can or you think you can't, you're right. - Henry Ford",
    "The best revenge is massive success. - Frank Sinatra",
    "Do something today that your future self will thank you for. - Sean Patrick Flanery",
    "The secret of change is to focus all of your energy on building the new, not fighting the old. - Socrates",
    "The most difficult thing is the decision to act, the rest is merely tenacity. - Amelia Earhart",
    "Every moment is a fresh beginning. - T.S. Eliot",
    "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
    "Success is walking from failure to failure with no loss of enthusiasm. - Winston Churchill",
    "The difference between ordinary and extraordinary is that little extra. - Jimmy Johnson",
    "Don't count the days, make the days count. - Muhammad Ali",
    "If you want to live a happy life, tie it to a goal, not to people or things. - Albert Einstein",
    "Everything you've ever wanted is on the other side of fear. - George Addair"
]

class SeasonalTheme:
    """Define seasonal color themes"""

    @staticmethod
    def get_season(month):
        """Get season based on month (Northern Hemisphere)"""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    @staticmethod
    def get_colors(season):
        """Get color palette for season"""
        themes = {
            "winter": {
                "primary": Color(0.8, 0.9, 1.0),      # Light blue
                "secondary": Color(0.9, 0.95, 1.0),   # Very light blue
                "accent": Color(0.4, 0.6, 0.9),       # Medium blue
                "text": Color(0.2, 0.3, 0.5)          # Dark blue
            },
            "spring": {
                "primary": Color(0.9, 1.0, 0.9),      # Light green
                "secondary": Color(0.95, 1.0, 0.95),  # Very light green
                "accent": Color(0.5, 0.8, 0.5),       # Medium green
                "text": Color(0.2, 0.5, 0.3)          # Dark green
            },
            "summer": {
                "primary": Color(1.0, 0.95, 0.8),     # Light yellow
                "secondary": Color(1.0, 0.98, 0.9),   # Very light yellow
                "accent": Color(1.0, 0.7, 0.3),       # Orange
                "text": Color(0.6, 0.4, 0.2)          # Brown
            },
            "autumn": {
                "primary": Color(1.0, 0.9, 0.8),      # Light orange
                "secondary": Color(1.0, 0.95, 0.9),   # Very light orange
                "accent": Color(0.9, 0.5, 0.3),       # Dark orange
                "text": Color(0.5, 0.3, 0.2)          # Dark brown
            }
        }
        return themes[season]

# Define seasonal background image paths
SEASON_BACKGROUNDS = {
    'winter': 'images/winter_bg.jpg',
    'spring': 'images/spring_bg.jpg',
    'summer': 'images/summer_bg.jpg',
    'autumn': 'images/autumn_bg.jpg'
}

class BackgroundGenerator:
    """Generate seasonal background illustrations"""

    def __init__(self):
        self.use_images = self.check_image_files()
        if self.use_images:
            print("✓ Using external image files for backgrounds")
        else:
            print("! External images not found, using generated backgrounds")

    def check_image_files(self):
        """Check if all seasonal background images exist"""
        return all(os.path.exists(path) for path in SEASON_BACKGROUNDS.values())

    def draw_background_image(self, c, image_path, width, height):
        """Draw an external image file as background"""
        try:
            # Draw image with low opacity for subtle background effect
            c.saveState()
            c.setFillColorRGB(1, 1, 1, alpha=0.7)  # White overlay for transparency effect
            c.drawImage(image_path, 0, 0, width=width, height=height,
                       preserveAspectRatio=True, mask='auto')
            c.restoreState()
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")
            # Fallback to generated background
            self.use_images = False
            return False
        return True

    def get_season_from_month(self, month):
        """Get season string from month number"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'

    def draw_seasonal_background(self, c, width, height, month):
        """Draw seasonal background - either from image file or generated"""
        season = self.get_season_from_month(month)

        if self.use_images:
            # Try to use external image file
            image_path = SEASON_BACKGROUNDS[season]
            if self.draw_background_image(c, image_path, width, height):
                return
            # If image loading fails, fall back to generated backgrounds

        # Generate backgrounds programmatically
        if season == "winter":
            self.draw_winter_background(c, width, height)
        elif season == "spring":
            self.draw_spring_background(c, width, height)
        elif season == "summer":
            self.draw_summer_background(c, width, height)
        else:  # autumn
            self.draw_autumn_background(c, width, height)

    @staticmethod
    def draw_winter_background(c, width, height):
        """Draw winter themed background with snow and trees"""
        # Gradient sky
        for i in range(50):
            alpha = i / 50.0
            sky_color = Color(0.7 + alpha * 0.2, 0.8 + alpha * 0.15, 0.9 + alpha * 0.1, alpha=0.1)
            c.setFillColor(sky_color)
            c.rect(0, height - i * 8, width, 8, fill=1, stroke=0)

        # Snow-covered ground
        c.setFillColor(Color(0.95, 0.97, 1.0, alpha=0.3))
        c.rect(0, 0, width, height * 0.2, fill=1, stroke=0)

        # Simple evergreen trees
        tree_positions = [100, 200, width-150, width-50]
        for x in tree_positions:
            # Tree trunk
            c.setFillColor(Color(0.3, 0.2, 0.1, alpha=0.2))
            c.rect(x-5, height*0.1, 10, height*0.15, fill=1, stroke=0)

            # Tree layers
            for layer in range(3):
                y_offset = height * (0.2 + layer * 0.08)
                tree_width = 30 - layer * 5
                c.setFillColor(Color(0.1, 0.3, 0.1, alpha=0.15))
                # Simple triangle for tree layer
                c.beginPath()
                c.moveTo(x, y_offset)
                c.lineTo(x - tree_width//2, y_offset - 30)
                c.lineTo(x + tree_width//2, y_offset - 30)
                c.closePath()
                c.drawPath(fill=1, stroke=0)

        # Falling snowflakes
        for i in range(20):
            snow_x = random.uniform(0, width)
            snow_y = random.uniform(height*0.3, height*0.9)
            c.setFillColor(Color(1, 1, 1, alpha=0.4))
            c.circle(snow_x, snow_y, 2, fill=1, stroke=0)

    @staticmethod
    def draw_spring_background(c, width, height):
        """Draw spring themed background with flowers and new growth"""
        # Gradient sky
        for i in range(50):
            alpha = i / 50.0
            sky_color = Color(0.8 + alpha * 0.1, 0.9 + alpha * 0.05, 0.8 + alpha * 0.1, alpha=0.1)
            c.setFillColor(sky_color)
            c.rect(0, height - i * 8, width, 8, fill=1, stroke=0)

        # Green meadow
        c.setFillColor(Color(0.7, 0.9, 0.7, alpha=0.3))
        c.rect(0, 0, width, height * 0.25, fill=1, stroke=0)

        # Blooming trees
        tree_positions = [80, 180, width-120, width-40]
        for x in tree_positions:
            # Tree trunk
            c.setFillColor(Color(0.4, 0.3, 0.2, alpha=0.2))
            c.rect(x-8, height*0.15, 16, height*0.2, fill=1, stroke=0)

            # Blooming canopy
            c.setFillColor(Color(0.9, 0.95, 0.9, alpha=0.2))
            c.circle(x, height*0.4, 40, fill=1, stroke=0)

            # Pink blossoms
            for j in range(8):
                blossom_x = x + random.uniform(-35, 35)
                blossom_y = height*0.4 + random.uniform(-35, 35)
                c.setFillColor(Color(1.0, 0.8, 0.9, alpha=0.3))
                c.circle(blossom_x, blossom_y, 3, fill=1, stroke=0)

        # Scattered flowers
        for i in range(15):
            flower_x = random.uniform(50, width-50)
            flower_y = random.uniform(height*0.1, height*0.25)
            # Simple flower
            c.setFillColor(Color(1.0, 0.9, 0.3, alpha=0.4))
            c.circle(flower_x, flower_y, 4, fill=1, stroke=0)
            c.setFillColor(Color(0.9, 0.3, 0.5, alpha=0.3))
            for petal in range(5):
                angle = petal * 72 * 3.14159 / 180
                petal_x = flower_x + 6 * (angle / 3.14159)
                petal_y = flower_y + 6 * (1 - angle / 3.14159)
                c.circle(petal_x, petal_y, 2, fill=1, stroke=0)

    @staticmethod
    def draw_summer_background(c, width, height):
        """Draw summer themed background with sun and lush landscape"""
        # Gradient sky
        for i in range(50):
            alpha = i / 50.0
            sky_color = Color(0.9, 0.85 + alpha * 0.1, 0.7 + alpha * 0.2, alpha=0.1)
            c.setFillColor(sky_color)
            c.rect(0, height - i * 8, width, 8, fill=1, stroke=0)

        # Sun
        c.setFillColor(Color(1.0, 0.9, 0.3, alpha=0.3))
        c.circle(width*0.8, height*0.8, 35, fill=1, stroke=0)

        # Sun rays
        c.setStrokeColor(Color(1.0, 0.9, 0.3, alpha=0.2))
        c.setLineWidth(3)
        for angle in range(0, 360, 45):
            rad = angle * 3.14159 / 180
            x1 = width*0.8 + 45 * (angle / 180)
            y1 = height*0.8 + 45 * (1 - angle / 180)
            x2 = width*0.8 + 65 * (angle / 180)
            y2 = height*0.8 + 65 * (1 - angle / 180)
            c.line(x1, y1, x2, y2)

        # Rolling hills
        c.setFillColor(Color(0.6, 0.8, 0.4, alpha=0.3))
        # Simple hill curve using multiple rectangles
        for i in range(0, int(width), 20):
            hill_height = height * 0.3 + 30 * abs((i - width/2) / (width/4))
            c.rect(i, 0, 20, hill_height, fill=1, stroke=0)

        # Tall summer grass
        c.setStrokeColor(Color(0.4, 0.7, 0.3, alpha=0.4))
        c.setLineWidth(2)
        for i in range(30):
            grass_x = random.uniform(0, width)
            grass_height = random.uniform(height*0.1, height*0.25)
            c.line(grass_x, height*0.05, grass_x, grass_height)

    @staticmethod
    def draw_autumn_background(c, width, height):
        """Draw autumn themed background with falling leaves"""
        # Gradient sky
        for i in range(50):
            alpha = i / 50.0
            sky_color = Color(0.9, 0.8 + alpha * 0.1, 0.7 + alpha * 0.1, alpha=0.1)
            c.setFillColor(sky_color)
            c.rect(0, height - i * 8, width, 8, fill=1, stroke=0)

        # Ground with fallen leaves
        c.setFillColor(Color(0.8, 0.7, 0.5, alpha=0.3))
        c.rect(0, 0, width, height * 0.2, fill=1, stroke=0)

        # Deciduous trees with autumn colors
        tree_positions = [90, 170, width-130, width-60]
        autumn_colors = [
            Color(0.9, 0.6, 0.2, alpha=0.3),  # Orange
            Color(0.9, 0.8, 0.3, alpha=0.3),  # Yellow
            Color(0.8, 0.3, 0.2, alpha=0.3),  # Red
            Color(0.7, 0.5, 0.2, alpha=0.3)   # Brown
        ]

        for i, x in enumerate(tree_positions):
            # Tree trunk
            c.setFillColor(Color(0.4, 0.3, 0.2, alpha=0.3))
            c.rect(x-8, height*0.12, 16, height*0.25, fill=1, stroke=0)

            # Autumn canopy
            canopy_color = autumn_colors[i % len(autumn_colors)]
            c.setFillColor(canopy_color)
            c.circle(x, height*0.45, 45, fill=1, stroke=0)

        # Falling autumn leaves
        leaf_colors = [
            Color(0.9, 0.6, 0.2, alpha=0.5),  # Orange
            Color(0.9, 0.8, 0.3, alpha=0.5),  # Yellow
            Color(0.8, 0.3, 0.2, alpha=0.5),  # Red
        ]

        for i in range(25):
            leaf_x = random.uniform(0, width)
            leaf_y = random.uniform(height*0.3, height*0.8)
            leaf_color = random.choice(leaf_colors)
            c.setFillColor(leaf_color)
            # Simple leaf shape (oval)
            c.ellipse(leaf_x-3, leaf_y-2, leaf_x+3, leaf_y+2, fill=1, stroke=0)

class DiaryGenerator:
    def __init__(self, year,enc):
        self.year = year
        self.enc = enc
        self.width, self.height = A4
        self.quotes_used = set()
        self.holidays = get_us_holidays(year)
        self.background_gen = BackgroundGenerator()

    def get_unique_quote(self):
        """Get a unique wisdom quote"""
        available_quotes = [q for q in WISDOM_QUOTES if q not in self.quotes_used]
        if not available_quotes:
            # Reset if we've used all quotes
            self.quotes_used.clear()
            available_quotes = WISDOM_QUOTES

        quote = random.choice(available_quotes)
        self.quotes_used.add(quote)
        return quote

    def draw_seasonal_background(self, c, month_num):
        """Draw seasonal background based on month"""
        self.background_gen.draw_seasonal_background(c, self.width, self.height, month_num)

    def draw_month_tabs(self, c, current_month=None):
        """Draw month tabs on the right side of the page"""
        tab_width = 83
        tab_height = 65
        start_x = self.width - tab_width - 10
        start_y = self.height - 50

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        for i, month in enumerate(months):
            y = start_y - (i * (tab_height + 2))

            # Determine colors based on season
            season = SeasonalTheme.get_season(i + 1)
            colors = SeasonalTheme.get_colors(season)

            # Highlight current month
            if current_month == i + 1:
                c.setFillColor(colors["accent"])
            else:
                c.setFillColor(colors["primary"])

            # Draw tab
            c.rect(start_x, y, tab_width, tab_height, fill=1, stroke=1)

            # Add month text
            c.setFillColor(colors["text"])
            c.setFont("DancingScript-Bold", 30)
            text_width = c.stringWidth(month, "DancingScript-Bold", 15)
            c.drawString(start_x + (tab_width - text_width) / 2, y + 8, month)

            # Add link annotation for navigation (to month view)
            if current_month != i + 1:  # Don't link to current page
                # Create internal document link
                c.linkRect("", f"month_{i+1}", (start_x, y, start_x + tab_width, y + tab_height))

    def create_cover_page(self, c):
        """Create the cover page"""
        # Background
        c.setFillColor(Color(0.95, 0.98, 1.0))
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)

        # Draw a general seasonal background
        self.draw_seasonal_background(c, 6)  # Use summer theme for cover

        # Draw month tabs
        self.draw_month_tabs(c)

        # Title
        c.setFillColor(Color(0.2, 0.3, 0.6))
        c.setFont("DancingScript-Bold", 36)
        title = f"Personal Diary {self.year}"
        title_width = c.stringWidth(title, "DancingScript-Bold", 36)
        c.drawString((self.width - title_width) / 2, self.height - 150, title)

        # Decorative elements
        c.setFillColor(Color(0.4, 0.6, 0.9))
        c.setFont("DancingScript-Regular", 18)
        subtitle = "A Journey Through Time"
        subtitle_width = c.stringWidth(subtitle, "DancingScript-Regular", 18)
        c.drawString((self.width - subtitle_width) / 2, self.height - 200, subtitle)

        # Year in large decorative font
        c.setFont("DancingScript-Bold", 72)
        year_str = str(self.year)
        year_width = c.stringWidth(year_str, "DancingScript-Bold", 72)
        c.drawString((self.width - year_width) / 2, self.height / 2, year_str)

        # Bottom quote
        quote = self.get_unique_quote()
        c.setFont("DancingScript-Bold", 12)
        c.setFillColor(Color(0.3, 0.4, 0.6))
        quote_lines = self.wrap_text(quote, 400, "DancingScript-Regular", 12)
        y_pos = 100
        for line in quote_lines:
            line_width = c.stringWidth(line, "DancingScript-Regular", 12)
            c.drawString((self.width - line_width) / 2, y_pos, line)
            y_pos -= 15

        c.showPage()

    def wrap_text(self, text, max_width, font_name, font_size):
        """Wrap text to fit within specified width"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) * font_size * 0.6 <= max_width:  # Rough approximation
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def create_month_page(self, c, month_num):
        """Create a month view page"""
        season = SeasonalTheme.get_season(month_num)
        colors = SeasonalTheme.get_colors(season)

        # Draw seasonal background first
        self.draw_seasonal_background(c, month_num)

        # Draw month tabs
        self.draw_month_tabs(c, month_num)

        # Add bookmark for this month
        c.bookmarkPage(f"month_{month_num}")

        # Month title
        month_name = calendar.month_name[month_num]
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 38)
        title = f"{month_name} {self.year}"
        title_width = c.stringWidth(title, "DancingScript-Bold", 38)
        c.drawString((self.width - title_width) / 2, self.height - 80, title)

        # Calendar grid
        cal = calendar.monthcalendar(self.year, month_num)

        # Days of week header
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        start_x = 50
        start_y = self.height - 180
        cell_width = (self.width - 160) / 7
        cell_height = 70

        # Draw header
        c.setFillColor(colors["accent"])
        c.rect(start_x, start_y, cell_width * 7, cell_height, fill=1, stroke=1)

        c.setFillColor(white)
        c.setFont("DancingScript-Bold", 12)
        for i, day in enumerate(days):
            x = start_x + i * cell_width + cell_width / 2
            day_width = c.stringWidth(day, "DancingScript-Bold", 12)
            c.drawString(x - day_width / 2, start_y + 15, day)

        # Draw calendar days
        for week_num, week in enumerate(cal):
            y = start_y - (week_num + 1) * cell_height

            for day_num, day in enumerate(week):
                x = start_x + day_num * cell_width

                if day == 0:
                    continue

                # Check if this day is a holiday or weekend
                current_date = date(self.year, month_num, day)
                is_holiday = current_date in self.holidays
                is_wknd = is_weekend(current_date)

                # Choose cell color based on day type
                if is_holiday:
                    c.setFillColor(Color(1.0, 0.8, 0.8))  # Light red for holidays
                elif is_wknd:
                    c.setFillColor(Color(0.9, 0.9, 1.0))  # Light blue for weekends
                else:
                    c.setFillColor(colors["primary"])

                # Draw cell
                c.rect(x, y, cell_width, cell_height, fill=1, stroke=1)

                # Draw day number
                c.setFillColor(colors["text"])
                c.setFont("DancingScript-Bold", 21)
                day_str = str(day)
                day_width = c.stringWidth(day_str, "DancingScript-Bold", 11)
                c.drawString(x + 5, y + cell_height - 20, day_str)

                # Add holiday name if applicable (abbreviated)
                if is_holiday:
                    holiday_name = self.holidays[current_date]
                    # Abbreviate long holiday names
                    if len(holiday_name) > 15:
                        holiday_name = holiday_name[:12] + "..."
                    c.setFont("DancingScript-Regular", 7)
                    c.setFillColor(Color(0.6, 0.0, 0.0))
                    c.drawString(x + 2, y + 5, holiday_name)
                elif is_wknd:
                    c.setFont("DancingScript-Regular", 8)
                    c.setFillColor(Color(0.0, 0.0, 0.6))
                    weekend_label = "Sat" if current_date.weekday() == 5 else "Sun"
                    c.drawString(x + 2, y + 5, weekend_label)

                # Add link to day page
                c.linkRect("", f"day_{month_num}_{day}", (x, y, x + cell_width, y + cell_height))

        # Add wisdom quote at bottom
        quote = self.get_unique_quote()
        c.setFont("DancingScript-Regular", 10)
        c.setFillColor(colors["text"])
        quote_lines = self.wrap_text(quote, 400, "DancingScript-Regular", 10)
        y_pos = 80
        for line in quote_lines:
            line_width = c.stringWidth(line, "DancingScript-Regular", 10)
            c.drawString((self.width - line_width) / 2, y_pos, line)
            y_pos -= 12

        c.showPage()

    def create_day_page(self, c, month_num, day_num):
        """Create a day view page with interactive form fields"""
        season = SeasonalTheme.get_season(month_num)
        colors = SeasonalTheme.get_colors(season)

        # Draw seasonal background first
        self.draw_seasonal_background(c, month_num)

        # Draw month tabs
        self.draw_month_tabs(c, month_num)

        # Add bookmark for this day
        c.bookmarkPage(f"day_{month_num}_{day_num}")

        # Date and day of week
        date_obj = date(self.year, month_num, day_num)
        day_name = date_obj.strftime("%A")
        month_name = calendar.month_name[month_num]

        # Check if this day is special
        is_holiday = date_obj in self.holidays
        is_wknd = is_weekend(date_obj)

        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 24)
        title = f"{day_name}, {month_name} {day_num}, {self.year}"
        title_width = c.stringWidth(title, "DancingScript-Bold", 24)
        c.drawString((self.width - title_width) / 2, self.height - 80, title)

        # Add holiday/weekend indicator
        if is_holiday:
            holiday_text = f"🎉 {self.holidays[date_obj]} 🎉"
            c.setFont("DancingScript-Bold", 14)
            c.setFillColor(Color(0.8, 0.2, 0.2))
            holiday_width = c.stringWidth(holiday_text, "DancingScript-Bold", 14)
            c.drawString((self.width - holiday_width) / 2, self.height - 110, holiday_text)
        elif is_wknd:
            weekend_text = "🌟 Weekend! 🌟"
            c.setFont("DancingScript-Bold", 14)
            c.setFillColor(Color(0.2, 0.2, 0.8))
            weekend_width = c.stringWidth(weekend_text, "DancingScript-Bold", 14)
            c.drawString((self.width - weekend_width) / 2, self.height - 110, weekend_text)

        # Activities section
        y_offset = -140 if (is_holiday or is_wknd) else -120
        c.setFont("DancingScript-Bold", 25)
        c.setFillColor(colors["text"])
        c.drawString(50, self.height + y_offset, "Activities:")

        # Create interactive text field for activities
        activities_x, activities_y = 50, self.height + y_offset - 160
        activities_w, activities_h = self.width - 150, 150

        try:
            # Try to create an interactive form field
            tr = Color(100, 0, 0, 0.0)
            c.acroForm.textfield(
                name=f'activities_{month_num:02d}{day_num:02d}',
                tooltip='Enter your activities for this day',
                x=activities_x, y=activities_y,
                width=activities_w, height=activities_h,
                borderStyle='inset',
                forceBorder=True,
                fontName='Helvetica',
                fontSize=10,
                textColor=colors["text"],
#                fillColor=colors["primary"],
                fillColor=tr,
                borderWidth=1,
                fieldFlags='multiline'
            )
        except AttributeError:
            # Fallback: Draw visual text area if acroForm not available
            c.setFillColor(colors["primary"])
            c.setStrokeColor(colors["accent"])
            c.setLineWidth(1)
            c.rect(activities_x, activities_y, activities_w, activities_h, fill=1, stroke=1)

            # Add lines for writing
            c.setStrokeColor(colors["accent"])
            c.setLineWidth(0.5)
            line_spacing = 15
            for i in range(1, int(activities_h / line_spacing)):
                y = activities_y + activities_h - (i * line_spacing)
                c.line(activities_x + 10, y, activities_x + activities_w - 10, y)

            # Add placeholder text
            c.setFillColor(Color(0.6, 0.6, 0.6))
            c.setFont("DancingScript-Bold", 10)
            c.drawString(activities_x + 15, activities_y + activities_h - 15, "Write your activities here...")

        # Notes section
        notes_y_offset = y_offset - 240
        c.setFont("DancingScript-Bold", 25)
        c.setFillColor(colors["text"])
        c.drawString(50, self.height + notes_y_offset, "Notes:")

        # Create interactive text field for notes
        notes_x, notes_y = 50, self.height + notes_y_offset - 160
        notes_w, notes_h = self.width - 150, 150

        try:
            # Try to create an interactive form field
            tr=Color(100,0,0,0.0)
            c.acroForm.textfield(
                name=f'notes_{month_num:02d}{day_num:02d}',
                tooltip='Enter your notes for this day',
                x=notes_x, y=notes_y,
                width=notes_w, height=notes_h,
                borderStyle='inset',
                forceBorder=True,
                fontName='Helvetica',
                fontSize=20,
                textColor=colors["text"],
#                fillColor=colors["primary"],
                fillColor=tr,
                borderWidth=1,
                fieldFlags='multiline'
            )
        except AttributeError:
            # Fallback: Draw visual text area if acroForm not available
            c.setFillColor(colors["primary"])
            c.setStrokeColor(colors["accent"])
            c.setLineWidth(1)
            c.rect(notes_x, notes_y, notes_w, notes_h, fill=1, stroke=1)

            # Add lines for writing
            c.setStrokeColor(colors["accent"])
            c.setLineWidth(0.5)
            line_spacing = 15
            for i in range(1, int(notes_h / line_spacing)):
                y = notes_y + notes_h - (i * line_spacing)
                c.line(notes_x + 10, y, notes_x + notes_w - 10, y)

            # Add placeholder text
            c.setFillColor(Color(0.6, 0.6, 0.6))
            c.setFont("DancingScript-Regular", 10)
            c.drawString(notes_x + 15, notes_y + notes_h - 15, "Write your notes here...")

        # Add wisdom quote at bottom
        quote = self.get_unique_quote()
        c.setFont("DancingScript-Regular", 12)
        c.setFillColor(colors["text"])
        quote_lines = self.wrap_text(quote, 400, "DancingScript-Regular", 10)
        y_pos = 80
        for line in quote_lines:
            line_width = c.stringWidth(line, "DancingScript-Regular", 10)
            c.drawString((self.width - line_width) / 2, y_pos, line)
            y_pos -= 12

        c.showPage()

    def generate_diary(self, filename):
        enc=self.enc
        """Generate the complete diary PDF"""
        c = canvas.Canvas(filename, pagesize=A4,encrypt=enc)

        print(f"Generating enhanced diary for {self.year}...")
        print(f"Holidays included: {len(self.holidays)} US Federal Holidays")
        print("Weekend support: All Saturdays and Sundays marked")

        # Create cover page
        print("Creating cover page with seasonal background...")
        self.create_cover_page(c)

        # Create month pages
        for month in range(1, 13):
            season = SeasonalTheme.get_season(month)
            print(f"Creating {season} themed page for {calendar.month_name[month]}...")
            self.create_month_page(c, month)

        # Create day pages
        total_days = 366 if calendar.isleap(self.year) else 365
        day_count = 0

        for month in range(1, 13):
            days_in_month = calendar.monthrange(self.year, month)[1]
            for day in range(1, days_in_month + 1):
                day_count += 1
                if day_count % 50 == 0:
                    print(f"Creating day pages with seasonal backgrounds... ({day_count}/{total_days})")
                self.create_day_page(c, month, day)

        c.save()
        print(f"\n✨ Enhanced Diary generated successfully: {filename}")
        print(f"📊 Total pages: {1 + 12 + total_days}")
        print(f"🎨 Features included:")
        print(f"   • Seasonal backgrounds for all 12 months")
        print(f"   • {len(self.holidays)} US Federal Holidays marked")
        print(f"   • All weekends (Saturdays & Sundays) highlighted")
        print(f"   • Interactive navigation between months and days")
        print(f"   • Fillable form fields for activities and notes")

        # Show background mode used
        if self.background_gen.use_images:
            print(f"   • External image backgrounds from 'images/' folder")
        else:
            print(f"   • Generated programmatic backgrounds")

        print(f"\n🖥️  To use the clickable navigation:")
        print("   1. Open the PDF in Firefox: firefox diary_2025.pdf")
        print("   2. Or use Chrome: google-chrome diary_2025.pdf")
        print("   3. Click on month tabs to navigate between months")
        print("   4. Click on calendar dates to jump to specific days")
        print("   5. Holidays shown in red, weekends in blue")

def main():

    # Register the fonts correctly
    try:
        # Register regular font
        pdfmetrics.registerFont(TTFont('DancingScript-Regular', 'myfonts/static/DancingScript-Regular.ttf'))
        print("✓ Registered DancingScript-Regular")

        # Try to register bold font if it exists
        try:
            pdfmetrics.registerFont(TTFont('DancingScript-Bold', 'myfonts/static/DancingScript-Bold.ttf'))
            print("✓ Registered DancingScript-Bold")

            # Register font family with both variants
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily('DancingScript',
                           normal='DancingScript-Regular',
                           bold='DancingScript-Bold')
            print("✓ Registered DancingScript font family")

        except Exception as e:
            print(f"! Bold font not found: {e}")
            print("! Using regular font for all text")
            # Register family with just regular font
            from reportlab.pdfbase.pdfmetrics import registerFontFamily
            registerFontFamily('DancingScript',
                           normal='DancingScript-Regular',
                           bold='DancingScript-Regular')  # Use regular for bold too

    except Exception as e:
        print(f"Error registering fonts: {e}")
        print("Please check that 'myfonts/static/DancingScript-Regular.ttf' exists")
        sys.exit(1)
#==============================================================================================================================================

    if len(sys.argv) != 2:
        print("Usage: python enhanced_diary.py <year>")
        print("Example: python enhanced_diary.py 2025")
        print("\nOptional: Place seasonal background images in 'images/' folder:")
        print("  - images/winter_bg.jpg")
        print("  - images/spring_bg.jpg")
        print("  - images/summer_bg.jpg")
        print("  - images/autumn_bg.jpg")
        print("If images are not found, beautiful generated backgrounds will be used instead.")
        sys.exit(1)

    try:
        year = int(sys.argv[1])
        if year < 1900 or year > 2100:
            print("Please enter a year between 1900 and 2100")
            sys.exit(1)
    except ValueError:
        print("Please enter a valid year")
        sys.exit(1)

    # Get password for enccryption

    enc=get_secure_password_for_diary()
    # Generate diary
    generator = DiaryGenerator(year,enc)
    filename = f"diary_{year}.pdf"
    generator.generate_diary(filename)

if __name__ == "__main__":
    main()
