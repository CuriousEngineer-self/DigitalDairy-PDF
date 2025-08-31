#!/usr/bin/env python3
"""
Password and Security Module for PDF Diary Generator
Handles secure password input and PDF encryption setup
"""

import getpass
import hashlib
import secrets
from reportlab.lib import pdfencrypt

class PasswordManager:
    """Handle password operations and validation"""

    @staticmethod
    def get_password(min_length=4, max_attempts=3):
        """
        Get password from user with confirmation and validation

        Args:
            min_length (int): Minimum password length
            max_attempts (int): Maximum number of attempts before giving up

        Returns:
            str: Validated password

        Raises:
            ValueError: If password requirements not met after max attempts
        """
        attempts = 0

        while attempts < max_attempts:
            attempts += 1

            try:
                password = getpass.getpass(f"Enter password for PDF encryption (min {min_length} chars): ")

                # Validate password length
                if len(password) < min_length:
                    print(f"❌ Password must be at least {min_length} characters long.")
                    if attempts < max_attempts:
                        print(f"Please try again ({max_attempts - attempts} attempts remaining)")
                    continue

                # Check for empty password
                if not password.strip():
                    print("❌ Password cannot be empty or just whitespace.")
                    if attempts < max_attempts:
                        print(f"Please try again ({max_attempts - attempts} attempts remaining)")
                    continue

                # Confirm password
                confirm_password = getpass.getpass("Confirm password: ")

                if password != confirm_password:
                    print("❌ Passwords do not match.")
                    if attempts < max_attempts:
                        print(f"Please try again ({max_attempts - attempts} attempts remaining)")
                    continue

                # Password validation passed
                return password

            except KeyboardInterrupt:
                print("\n❌ Password entry cancelled by user.")
                raise ValueError("Password entry cancelled")
            except Exception as e:
                print(f"❌ Error during password entry: {e}")
                if attempts < max_attempts:
                    print(f"Please try again ({max_attempts - attempts} attempts remaining)")
                continue

        # Max attempts reached
        raise ValueError(f"Failed to get valid password after {max_attempts} attempts")

    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength and provide feedback

        Args:
            password (str): Password to validate

        Returns:
            tuple: (is_strong: bool, feedback: list)
        """
        feedback = []
        is_strong = True

        # Check length
        if len(password) < 8:
            feedback.append("⚠️  Consider using at least 8 characters for better security")
            if len(password) < 6:
                is_strong = False

        # Check character variety
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        char_types = sum([has_upper, has_lower, has_digit, has_special])

        if char_types < 2:
            feedback.append("⚠️  Consider mixing letters, numbers, and symbols")
            is_strong = False
        elif char_types < 3:
            feedback.append("💡 Good! Consider adding more character variety for extra security")

        # Check for common patterns
        common_patterns = ['123', 'abc', 'password', 'qwerty', '111', '000']
        if any(pattern in password.lower() for pattern in common_patterns):
            feedback.append("⚠️  Avoid common patterns like '123', 'abc', or 'password'")
            is_strong = False

        return is_strong, feedback

    @staticmethod
    def get_password_with_strength_check():
        """Get password with strength validation and user choice"""
        while True:
            password = PasswordManager.get_password()
            is_strong, feedback = PasswordManager.validate_password_strength(password)

            if is_strong:
                print("✅ Strong password!")
                return password
            else:
                print("🔒 Password Strength Assessment:")
                for item in feedback:
                    print(f"   {item}")

                while True:
                    choice = input("\nContinue with this password? (y/n/r for retry): ").lower().strip()
                    if choice in ['y', 'yes']:
                        return password
                    elif choice in ['n', 'no', 'r', 'retry']:
                        break
                    else:
                        print("Please enter 'y' for yes, 'n' for no, or 'r' for retry")


class PDFSecurity:
    """Handle PDF encryption and security settings"""

    @staticmethod
    def create_encryption(password, allow_printing=True, allow_copying=False,
                         allow_modification=False, allow_annotation=True):
        """
        Create PDF encryption object with specified permissions

        Args:
            password (str): User password for PDF
            allow_printing (bool): Allow printing
            allow_copying (bool): Allow copying text
            allow_modification (bool): Allow document modification
            allow_annotation (bool): Allow adding annotations/forms

        Returns:
            StandardEncryption: Encryption object for ReportLab
        """
        return pdfencrypt.StandardEncryption(
            userPassword=password,
            canPrint=1 if allow_printing else 0,
            canModify=1 if allow_modification else 0,
            canCopy=1 if allow_copying else 0,
            canAnnotate=1 if allow_annotation else 0
        )

    @staticmethod
    def create_high_security_encryption(password):
        """Create high-security encryption (minimal permissions)"""
        return PDFSecurity.create_encryption(
            password=password,
            allow_printing=True,    # Allow printing for backup purposes
            allow_copying=False,    # Prevent copying sensitive info
            allow_modification=False,  # Prevent tampering
            allow_annotation=True   # Allow form filling
        )

    @staticmethod
    def create_standard_encryption(password):
        """Create standard encryption (balanced permissions)"""
        return PDFSecurity.create_encryption(
            password=password,
            allow_printing=True,
            allow_copying=False,    # Still prevent copying for privacy
            allow_modification=False,  # Prevent accidental changes
            allow_annotation=True
        )

    @staticmethod
    def create_low_security_encryption(password):
        """Create low-security encryption (most permissions allowed)"""
        return PDFSecurity.create_encryption(
            password=password,
            allow_printing=True,
            allow_copying=True,
            allow_modification=True,
            allow_annotation=True
        )


def get_secure_password_for_diary():
    """
    Main function to get a secure password for diary generation
    Returns configured encryption object
    """
    print("🔐 PDF Security Setup")
    print("=" * 50)
    print("Your diary will be password-protected to keep your personal information secure.")
    print("")

    # Get password with strength checking
    password = PasswordManager.get_password_with_strength_check()

    encryption = PDFSecurity.create_high_security_encryption(password)
    print("\n🔒 Your PDF will be encrypted and password-protected!")
    return encryption


def hash_password_for_filename(password):
    """
    Create a short hash of password for unique filename generation
    (Not for security - just to create unique filenames)
    """
    return hashlib.md5(password.encode()).hexdigest()[:8]
