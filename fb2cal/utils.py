from .contact import BirthdayContact


def generate_facebook_profile_url_permalink(contact: BirthdayContact) -> str:
    """Build a stable Facebook profile URL from a contact ID."""
    return f"https://www.facebook.com/{contact.id}"


# Facebook prepends an infinite while loop to their API responses as anti hijacking protection
# It must be stripped away before parsing a response as JSON
def remove_anti_hijacking_protection(text: str) -> str:
    return text.removeprefix("for (;;);")
