"""Shared constants used across the project."""

BLOOD_GROUPS = [
    ("A+", "A+"), ("A-", "A-"),
    ("B+", "B+"), ("B-", "B-"),
    ("AB+", "AB+"), ("AB-", "AB-"),
    ("O+", "O+"), ("O-", "O-"),
]

# Districts of Kerala (extend or replace for your region)
DISTRICTS = [
    ("Thiruvananthapuram", "Thiruvananthapuram"),
    ("Kollam", "Kollam"),
    ("Pathanamthitta", "Pathanamthitta"),
    ("Alappuzha", "Alappuzha"),
    ("Kottayam", "Kottayam"),
    ("Idukki", "Idukki"),
    ("Ernakulam", "Ernakulam"),
    ("Thrissur", "Thrissur"),
    ("Palakkad", "Palakkad"),
    ("Malappuram", "Malappuram"),
    ("Kozhikode", "Kozhikode"),
    ("Wayanad", "Wayanad"),
    ("Kannur", "Kannur"),
    ("Kasaragod", "Kasaragod"),
]

GENDER_CHOICES = [
    ("M", "Male"),
    ("F", "Female"),
    ("O", "Other"),
]

# Blood compatibility: which donor groups can give to a recipient group
COMPATIBILITY = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "AB+": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "AB-": ["A-", "B-", "AB-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
}
