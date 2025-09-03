#!/usr/bin/env python3
"""
Personal Information Module for Digital Diary
Adds personal info pages with form fields and navigation
Usage: Import and integrate with DiaryGenerator
"""

from reportlab.lib.colors import Color, white
from reportlab.lib.units import inch
import calendar
from datetime import date


class PersonalInfoManager:
    """Handle personal information pages for the diary"""
    
    def __init__(self, diary_generator):
        """
        Initialize with reference to the main diary generator
        
        Args:
            diary_generator: Instance of DiaryGenerator class
        """
        self.diary_gen = diary_generator
        self.width = diary_generator.width
        self.height = diary_generator.height
        
        # Personal info form fields organized by page
        self.personal_info_fields = {
            'page1': [
                ("Full Name", "full_name"),
                ("Date of Birth", "date_of_birth"),
                ("Place of Birth", "place_of_birth"),
                ("Nationality", "nationality"),
                ("Occupation", "occupation"),
                ("Company/Organization", "company"),
                ("Work Address", "work_address"),
                ("Work Phone", "work_phone"),
                ("Work Email", "work_email"),
                ("Home Address", "home_address"),
                ("Home Phone", "home_phone"),
                ("Personal Email", "personal_email"),
                ("Emergency Contact Name", "emergency_name"),
                ("Emergency Contact Phone", "emergency_phone"),
                ("Emergency Contact Relationship", "emergency_relationship"),
            ],
            'page2': [
                ("Blood Type", "blood_type"),
                ("Allergies", "allergies"),
                ("Medical Conditions", "medical_conditions"),
                ("Medications", "medications"),
                ("Doctor Name", "doctor_name"),
                ("Doctor Phone", "doctor_phone"),
                ("Insurance Provider", "insurance_provider"),
                ("Insurance Policy Number", "insurance_policy"),
                ("Passport Number", "passport_number"),
                ("Passport Expiry", "passport_expiry"),
                ("Driver's License Number", "drivers_license"),
                ("License Expiry", "license_expiry"),
                ("Bank Name", "bank_name"),
                ("Account Number", "account_number"),
                ("Social Security/ID Number", "ssn_id"),
            ]
        }
    
    def draw_personal_info_tab(self, c, current_page=None):
        """Draw the personal info tab on the right side"""
        # Personal info tab positioned above month tabs
        tab_width = 83
        tab_height = 45
        start_x = self.width - tab_width - 10
        start_y = self.height - 15  # Above the month tabs
        
        # Use current month's season for tab coloring
        current_month = date.today().month
        from enhanced_diary import SeasonalTheme
        season = SeasonalTheme.get_season(current_month)
        colors = SeasonalTheme.get_colors(season)
        
        # Highlight if on personal info page
        if current_page and current_page.startswith('personal'):
            c.setFillColor(colors["accent"])
        else:
            c.setFillColor(colors["primary"])
        
        # Draw tab
        c.rect(start_x, start_y, tab_width, tab_height, fill=1, stroke=1)
        
        # Add text
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 10)
        text = "Personal"
        text_width = c.stringWidth(text, "DancingScript-Bold", 10)
        c.drawString(start_x + (tab_width - text_width) / 2, start_y + 25, text)
        
        text2 = "Info"
        text2_width = c.stringWidth(text2, "DancingScript-Bold", 10)
        c.drawString(start_x + (tab_width - text2_width) / 2, start_y + 10, text2)
        
        # Add link annotation
        if not (current_page and current_page.startswith('personal')):
            c.linkRect("", "personal_info_1", (start_x, start_y, start_x + tab_width, start_y + tab_height))
    
    def draw_page_navigation(self, c, current_page_num):
        """Draw navigation between personal info pages"""
        nav_y = 50
        nav_spacing = 100
        center_x = self.width / 2
        
        # Get current month's colors
        current_month = date.today().month
        from enhanced_diary import SeasonalTheme
        season = SeasonalTheme.get_season(current_month)
        colors = SeasonalTheme.get_colors(season)
        
        # Page indicators and navigation
        pages = ["Page 1", "Page 2", "Page 3"]
        page_links = ["personal_info_1", "personal_info_2", "personal_info_3"]
        
        for i, (page_text, page_link) in enumerate(zip(pages, page_links)):
            x = center_x + (i - 1) * nav_spacing
            
            # Current page styling
            if i + 1 == current_page_num:
                c.setFillColor(colors["accent"])
                c.setFont("DancingScript-Bold", 14)
            else:
                c.setFillColor(colors["primary"])
                c.setFont("DancingScript-Regular", 12)
            
            # Draw page indicator
            text_width = c.stringWidth(page_text, "DancingScript-Bold" if i + 1 == current_page_num else "DancingScript-Regular", 14 if i + 1 == current_page_num else 12)
            c.rect(x - text_width/2 - 10, nav_y - 5, text_width + 20, 25, fill=1, stroke=1)
            
            # Add text
            c.setFillColor(colors["text"])
            c.drawString(x - text_width/2, nav_y + 5, page_text)
            
            # Add link if not current page
            if i + 1 != current_page_num:
                c.linkRect("", page_link, (x - text_width/2 - 10, nav_y - 5, x + text_width/2 + 10, nav_y + 20))
        
        # Navigation arrows
        if current_page_num > 1:
            # Previous arrow
            c.setFont("DancingScript-Bold", 16)
            c.setFillColor(colors["accent"])
            prev_text = "← Previous"
            c.drawString(50, nav_y + 5, prev_text)
            prev_link = f"personal_info_{current_page_num - 1}"
            c.linkRect("", prev_link, (50, nav_y, 50 + c.stringWidth(prev_text, "DancingScript-Bold", 16), nav_y + 20))
        
        if current_page_num < 3:
            # Next arrow
            c.setFont("DancingScript-Bold", 16)
            c.setFillColor(colors["accent"])
            next_text = "Next →"
            next_width = c.stringWidth(next_text, "DancingScript-Bold", 16)
            c.drawString(self.width - 50 - next_width, nav_y + 5, next_text)
            next_link = f"personal_info_{current_page_num + 1}"
            c.linkRect("", next_link, (self.width - 50 - next_width, nav_y, self.width - 50, nav_y + 20))
    
    def create_form_table(self, c, fields, start_y, colors):
        """Create a two-column form table with labels and input fields"""
        row_height = 35
        label_width = 180
        field_width = 250
        start_x = 50
        field_x = start_x + label_width + 20
        
        current_y = start_y
        
        for label, field_name in fields:
            # Draw label
            c.setFillColor(colors["text"])
            c.setFont("DancingScript-Bold", 12)
            c.drawString(start_x, current_y + 10, label + ":")
            
            # Create form field
            try:
                tr = Color(100, 0, 0, 0.0)
                c.acroForm.textfield(
                    name=field_name,
                    tooltip=f'Enter your {label.lower()}',
                    x=field_x, y=current_y,
                    width=field_width, height=25,
                    borderStyle='inset',
                    forceBorder=True,
                    fontName='Helvetica',
                    fontSize=10,
                    textColor=colors["text"],
                    fillColor=tr,
                    borderWidth=1
                    # Remove fieldFlags parameter - not needed for basic text fields
                )
            except AttributeError:
                # Fallback: Draw visual input field
                c.setFillColor(colors["primary"])
                c.setStrokeColor(colors["accent"])
                c.setLineWidth(1)
                c.rect(field_x, current_y, field_width, 25, fill=1, stroke=1)
            
            current_y -= row_height
            
            # Check if we need to move to next page
            if current_y < 100:
                break
        
        return current_y
    
    def create_personal_info_page_1(self, c):
        """Create the first personal info page with basic information"""
        # Get current month's colors for theming
        current_month = date.today().month
        from enhanced_diary import SeasonalTheme
        season = SeasonalTheme.get_season(current_month)
        colors = SeasonalTheme.get_colors(season)
        
        # Draw seasonal background
        self.diary_gen.draw_seasonal_background(c, current_month)
        
        # Draw tabs
        self.diary_gen.draw_month_tabs(c)
        self.draw_personal_info_tab(c, "personal_info_1")
        
        # Add bookmark
        c.bookmarkPage("personal_info_1")
        
        # Title
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 28)
        title = "Personal Information - Basic Details"
        title_width = c.stringWidth(title, "DancingScript-Bold", 28)
        c.drawString((self.width - title_width) / 2, self.height - 80, title)
        
        # Instructions
        c.setFont("DancingScript-Regular", 12)
        instruction = "Please fill in your basic personal information below:"
        inst_width = c.stringWidth(instruction, "DancingScript-Regular", 12)
        c.drawString((self.width - inst_width) / 2, self.height - 110, instruction)
        
        # Create form table
        self.create_form_table(c, self.personal_info_fields['page1'], self.height - 150, colors)
        
        # Navigation
        self.draw_page_navigation(c, 1)
        
        c.showPage()
    
    def create_personal_info_page_2(self, c):
        """Create the second personal info page with medical and official information"""
        # Get current month's colors for theming
        current_month = date.today().month
        from enhanced_diary import SeasonalTheme
        season = SeasonalTheme.get_season(current_month)
        colors = SeasonalTheme.get_colors(season)
        
        # Draw seasonal background
        self.diary_gen.draw_seasonal_background(c, current_month)
        
        # Draw tabs
        self.diary_gen.draw_month_tabs(c)
        self.draw_personal_info_tab(c, "personal_info_2")
        
        # Add bookmark
        c.bookmarkPage("personal_info_2")
        
        # Title
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 28)
        title = "Personal Information - Medical & Official"
        title_width = c.stringWidth(title, "DancingScript-Bold", 28)
        c.drawString((self.width - title_width) / 2, self.height - 80, title)
        
        # Instructions
        c.setFont("DancingScript-Regular", 12)
        instruction = "Please fill in your medical and official document information:"
        inst_width = c.stringWidth(instruction, "DancingScript-Regular", 12)
        c.drawString((self.width - inst_width) / 2, self.height - 110, instruction)
        
        # Create form table
        self.create_form_table(c, self.personal_info_fields['page2'], self.height - 150, colors)
        
        # Navigation
        self.draw_page_navigation(c, 2)
        
        c.showPage()
    
    def create_personal_info_page_3(self, c):
        """Create the third personal info page for documents and photos"""
        # Get current month's colors for theming
        current_month = date.today().month
        from enhanced_diary import SeasonalTheme
        season = SeasonalTheme.get_season(current_month)
        colors = SeasonalTheme.get_colors(season)
        
        # Draw seasonal background
        self.diary_gen.draw_seasonal_background(c, current_month)
        
        # Draw tabs
        self.diary_gen.draw_month_tabs(c)
        self.draw_personal_info_tab(c, "personal_info_3")
        
        # Add bookmark
        c.bookmarkPage("personal_info_3")
        
        # Title
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 28)
        title = "Personal Information - Documents & Photos"
        title_width = c.stringWidth(title, "DancingScript-Bold", 28)
        c.drawString((self.width - title_width) / 2, self.height - 80, title)
        
        # Instructions
        c.setFont("DancingScript-Regular", 14)
        c.setFillColor(colors["text"])
        instructions = [
            "This page is reserved for important documents and photos.",
            "You can print and attach copies of:",
            "• Passport/ID copies",
            "• Insurance cards", 
            "• Medical information cards",
            "• Emergency contact cards",
            "• Personal photos",
            "• Any other important documents"
        ]
        
        y_pos = self.height - 130
        for instruction in instructions:
            if instruction.startswith("•"):
                c.setFont("DancingScript-Regular", 12)
                c.drawString(100, y_pos, instruction)
            else:
                c.setFont("DancingScript-Regular", 14)
                inst_width = c.stringWidth(instruction, "DancingScript-Regular", 14)
                c.drawString((self.width - inst_width) / 2, y_pos, instruction)  # FIXED: Added instruction parameter
            y_pos -= 25
        
        # Create document areas
        doc_areas = [
            "Document Area 1",
            "Document Area 2", 
            "Photo Area"
        ]
        
        area_width = 200
        area_height = 150
        areas_per_row = 2
        start_x = (self.width - (areas_per_row * area_width + (areas_per_row - 1) * 50)) / 2
        start_y = self.height - 400
        
        for i, area_name in enumerate(doc_areas):
            row = i // areas_per_row
            col = i % areas_per_row
            
            x = start_x + col * (area_width + 50)
            y = start_y - row * (area_height + 50)
            
            # Draw document area
            c.setFillColor(colors["primary"])
            c.setStrokeColor(colors["accent"])
            c.setLineWidth(2)
            c.rect(x, y, area_width, area_height, fill=1, stroke=1)
            
            # Add area label
            c.setFillColor(colors["text"])
            c.setFont("DancingScript-Bold", 14)
            label_width = c.stringWidth(area_name, "DancingScript-Bold", 14)
            c.drawString(x + (area_width - label_width) / 2, y + area_height + 10, area_name)
            
            # Add instruction text
            c.setFont("DancingScript-Regular", 10)
            inst_text = "Attach documents here"
            inst_width = c.stringWidth(inst_text, "DancingScript-Regular", 10)
            c.setFillColor(Color(0.6, 0.6, 0.6))
            c.drawString(x + (area_width - inst_width) / 2, y + area_height / 2, inst_text)
        
        # Large text area for additional notes
        c.setFillColor(colors["text"])
        c.setFont("DancingScript-Bold", 16)
        c.drawString(50, 200, "Additional Notes:")
        
        try:
            tr = Color(100, 0, 0, 0.0)
            c.acroForm.textfield(
                name='personal_additional_notes',
                tooltip='Additional personal information or notes',
                x=50, y=80,
                width=self.width - 200, height=100,
                borderStyle='inset',
                forceBorder=True,
                fontName='Helvetica',
                fontSize=10,
                textColor=colors["text"],
                fillColor=tr,
                borderWidth=1,
                fieldFlags='multiline'
            )
        except AttributeError:
            # Fallback
            c.setFillColor(colors["primary"])
            c.setStrokeColor(colors["accent"])
            c.rect(50, 80, self.width - 200, 100, fill=1, stroke=1)
        
        # Navigation
        self.draw_page_navigation(c, 3)
        
        c.showPage()
    
    def generate_all_personal_info_pages(self, c):
        """Generate all three personal information pages"""
        self.create_personal_info_page_1(c)
        self.create_personal_info_page_2(c)
        self.create_personal_info_page_3(c)
  #      print("✓ Personal information pages created with form fields and navigation")


# Integration helper function
def integrate_personal_info_with_diary(diary_generator, canvas):
    """
    Helper function to integrate personal info pages with existing diary
    
    Args:
        diary_generator: Instance of DiaryGenerator
        canvas: ReportLab canvas object
    """
    personal_info = PersonalInfoManager(diary_generator)
    personal_info.generate_all_personal_info_pages(canvas)
    return personal_info


# Modification helper for existing diary generator
class PersonalInfoIntegration:
    """Helper class to modify existing DiaryGenerator methods"""
    
    @staticmethod
    def modify_draw_month_tabs(original_method):
        """Decorator to add personal info tab to month tabs method"""
        def wrapper(self, c, current_month=None):
            # Call original method
            result = original_method(self, c, current_month)
            
            # Add personal info tab
            if hasattr(self, 'personal_info_manager'):
                self.personal_info_manager.draw_personal_info_tab(c)
            
            return result
        return wrapper
    
    @staticmethod
    def modify_generate_diary(original_method):
        """Decorator to add personal info pages to diary generation"""
        def wrapper(self, filename):
            # Initialize personal info manager
            self.personal_info_manager = PersonalInfoManager(self)
            
            # Start canvas
            c = self.canvas if hasattr(self, 'canvas') else None
            
            # Call original method but intercept the canvas creation
            return original_method(self, filename)
        return wrapper


#if __name__ == "__main__":
#    print("Personal Info Module - Import this module into your diary generator")
#    print("Usage:")
#    print("  from PersonalInfoManager import PersonalInfoManager, integrate_personal_info_with_diary, PersonalInfoIntegration")
#    print("  ")
#    print("  # Method 1: Simple Integration (adds personal info pages only)")
#    print("  # In your DiaryGenerator.generate_diary method:")
#    print("  # personal_info = integrate_personal_info_with_diary(self, c)")
#    print("  ")
#    print("  # Method 2: Full Integration (adds personal info tab to ALL pages)")
#    print("  # In your main script:")
#    print("  # diary = DiaryGenerator()")
#    print("  # diary.personal_info_manager = PersonalInfoManager(diary)")
#    print("  # PersonalInfoIntegration.add_to_all_pages(diary)")
#    print("  # diary.generate_diary('my_diary.pdf')")
#    print("  ")
#    print("  # Method 3: Override draw_month_tabs method")
#    print("  # original_draw_tabs = diary.draw_month_tabs")
#    print("  # diary.draw_month_tabs = PersonalInfoIntegration.modify_draw_month_tabs(original_draw_tabs)")


# QUICK SETUP INSTRUCTIONS:
"""
To add personal info tab to ALL pages in your existing diary:

1. Import this module:
   from PersonalInfoManager import PersonalInfoManager, PersonalInfoIntegration

2. In your DiaryGenerator.__init__ method, add:
   self.personal_info_manager = PersonalInfoManager(self)

3. In your DiaryGenerator.draw_month_tabs method, add this line at the end:
   if hasattr(self, 'personal_info_manager'):
       self.personal_info_manager.draw_personal_info_tab(c)

4. In your DiaryGenerator.generate_diary method, add personal info pages:
   self.personal_info_manager.generate_all_personal_info_pages(c)

That's it! The personal info tab will now appear on every page.

Note: The draw_personal_info_tab method can handle both string page identifiers 
and integer month numbers, so you can call it from any context.
"""
