from tkinter import *
import xml.etree.ElementTree as ET

def update_all_violations(name):
    all_violations = {}
    # Updating All violations file by retrieving data from speed and traffic files
    temp_tree = ET.parse(f"{name}_traffic_signal.xml")
    violations = temp_tree.getroot()

    for violation in violations:
        reg = violation.find("Reg").text
        time = violation.find("Time").text
        date = violation.find("Date").text
        loc = violation.find("Location").text
                
        if reg not in all_violations:
            all_violations[reg] = {}
                
        violation_num = f"Violation {len(all_violations[reg]) + 1}"
        all_violations[reg][violation_num] = {"Time": time, "Date": date, "Location": loc, "Type": "Signal Violation"}

    temp_tree = ET.parse(f"{name}_speed.xml")
    violations = temp_tree.getroot()

    for violation in violations:
        reg = violation.find("Reg").text
        time = violation.find("Time").text
        date = violation.find("Date").text
        loc = violation.find("Location").text
        speed = violation.find("Recordedspeed").text
                
        if reg not in all_violations:
            all_violations[reg] = {}
                
        violation_num = f"Violation {len(all_violations[reg]) + 1}"
        all_violations[reg][violation_num] = {"Time": time, "Date": date, "Location": loc, "Type": "Speed Violation", "Speed": speed}

    # Load the existing violations file
    existing_violations_tree = ET.parse(f"{name}_all.xml")
    existing_violations_root = existing_violations_tree.getroot()
    existing_violations_root.clear()

    # Iterate through existing registration numbers and violations
    for reg, violations in all_violations.items():
        reg_element = existing_violations_root.find(f".//RegistrationNumber[@number='{reg}']")

        if reg_element is None:
            reg_element = ET.SubElement(existing_violations_root, "RegistrationNumber", {"number": reg})

        for violation_num, violation_data in violations.items():
            violation_element = ET.SubElement(reg_element, "Violation")

            for key, value in violation_data.items():
                ET.SubElement(violation_element, key).text = str(value)

            # Update total violations count
            if "TotalViolations" in reg_element.attrib:
                reg_element.attrib["TotalViolations"] = str(int(reg_element.attrib["TotalViolations"]) + 1)
            else:
                reg_element.attrib["TotalViolations"] = "1"

    # Write the modified ElementTree back to the same file
    existing_violations_tree.write(f"{name}_all.xml")
