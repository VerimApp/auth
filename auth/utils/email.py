def safe_email_str(email: str) -> str:
    email, domain = email.split("@")
    if len(email) == 1:
        return "@".join(["*", domain])
    if len(email) == 2:
        return "@".join([f"{email[0]}*", domain])
    hide_len = len(email) - 2
    return "@".join([f"{email[0]}{'*' * hide_len}{email[-1]}", domain])
