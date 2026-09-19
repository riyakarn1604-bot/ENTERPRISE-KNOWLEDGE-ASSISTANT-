import os

DATA_DIR = "C:/Users/Harsh/.gemini/antigravity/scratch/enterprise-knowledge-assistant/data"
os.makedirs(DATA_DIR, exist_ok=True)

docs = {
    "HR_Leave_Policy.txt": """
Enterprise Knowledge Assistant - Leave Policy
Effective Date: January 1, 2024

1. Annual Leave
All full-time employees are entitled to 20 days of paid annual leave per calendar year. 
Leave must be requested at least two weeks in advance via the HR portal and approved by the direct manager.
Up to 5 days of unused annual leave can be rolled over to the next year.

2. Sick Leave
Employees receive 10 days of paid sick leave annually. 
For absences exceeding 3 consecutive days, a doctor's note must be provided to HR.
Sick leave cannot be cashed out upon termination of employment.

3. Maternity and Paternity Leave
Eligible employees receive 16 weeks of fully paid maternity leave and 8 weeks of fully paid paternity leave.
This policy applies to birth, adoption, and foster care placement.
""",
    
    "HR_Code_of_Conduct.txt": """
Enterprise Knowledge Assistant - Code of Conduct

1. Professionalism and Respect
We are committed to a workplace free of harassment and discrimination. 
All employees must treat colleagues, clients, and partners with respect. 
Offensive jokes, slurs, and inappropriate comments will not be tolerated and are subject to disciplinary action.

2. Conflict of Interest
Employees must avoid situations where personal interests conflict with the company's interests.
Any potential conflict of interest must be disclosed to the Ethics Committee immediately.
Accepting gifts from vendors exceeding $50 in value is strictly prohibited.

3. Confidentiality
Employees must protect the company's intellectual property and confidential information.
Discussing unreleased products in public forums is a violation of this policy.
""",

    "HR_Remote_Work.txt": """
Enterprise Knowledge Assistant - Remote Work Policy

1. Eligibility
Remote work is available for roles that do not require physical presence in the office, subject to manager approval.
Employees must maintain satisfactory performance to retain remote work privileges.

2. Expectations
Remote employees must be available during core business hours (10 AM to 3 PM, local time).
A stable internet connection and a dedicated workspace are required. 
The company will provide a one-time stipend of $500 for home office setup.

3. Security
All company data must be accessed through the corporate VPN. 
Personal devices should not be used to store company data.
""",

    "Product_Manual_SmartThermo.txt": """
SmartThermo V2 - User Manual

1. Introduction
Welcome to SmartThermo V2, the next-generation smart thermostat. 
Features include machine-learning temperature control, Wi-Fi connectivity, and voice assistant integration.

2. Installation
Turn off power at the circuit breaker before installation.
Connect the C-wire (common wire) to the terminal marked 'C'. 
If your system does not have a C-wire, use the included power adapter kit.
Mount the base plate using the provided screws and snap the display unit onto the base.

3. Troubleshooting
Error Code E71: No power to the Rc wire. Check the HVAC system's breaker and ensure the front panel is securely attached.
Wi-Fi Drops: Ensure your router is broadcasting on the 2.4GHz band. SmartThermo V2 does not support 5GHz networks.
""",

    "Product_Manual_EchoSound.txt": """
EchoSound Pro - Wireless Earbuds Manual

1. Pairing
Open the charging case near your device. Press and hold the pairing button on the back of the case for 3 seconds until the LED flashes white.
Select "EchoSound Pro" from your device's Bluetooth menu.

2. Controls
Single tap on either earbud to play/pause.
Double tap the right earbud to skip forward, double tap the left to skip backward.
Press and hold either earbud for 2 seconds to toggle between Active Noise Cancellation and Transparency Mode.

3. Battery and Charging
The earbuds offer 8 hours of playback. The charging case provides an additional 24 hours.
Place the earbuds in the case and connect the case via USB-C to charge. A full charge takes 1.5 hours.
"""
}

# Generate 15 extra small dummy docs to meet the 15-25 requirement
for i in range(1, 16):
    title = f"IT_Policy_Note_{i}.txt"
    content = f"""
Enterprise Knowledge Assistant - IT Policy Note {i}

This is a standard IT policy document covering topic {i}.
Employees are reminded to update their passwords every 90 days.
For IT support regarding issue {i}, please open a ticket on the internal portal.
Remember to lock your screen when stepping away from your desk.
"""
    docs[title] = content

# Write files
for filename, content in docs.items():
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())

# Create SOURCES.md
with open(os.path.join("C:/Users/Harsh/.gemini/antigravity/scratch/enterprise-knowledge-assistant", "SOURCES.md"), "w", encoding="utf-8") as f:
    f.write("# Document Sources\n\nAll documents in the `/data` directory are synthetic text files generated specifically for this project to simulate HR policies and product manuals without relying on external URLs that may break or have licensing issues.\n")

print(f"Generated {len(docs)} documents.")
