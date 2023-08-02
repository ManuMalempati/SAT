from tkinter import *
from PIL import ImageTk, Image
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
import os
from tkinter import filedialog
from Trafficlight import process_signal_footage
import threading


# main window
tkWindow = Tk()
tkWindow.title('Traffic and Speed Violation System')
tkWindow.state('zoomed')
tkWindow.config(bg='black')

# Checking if the XML file already exists
if os.path.isfile("users.xml"):
    # Read the existing XML file via creating a tree
    tree = ET.parse("users.xml")
    # obtain root
    root = tree.getroot()
    # Perform any necessary operations on the tree object
    tree.write("users.xml") 

else:
    # Creating main/head root element
    root = ET.Element("users")
    # Create new XML tree
    tree = ET.ElementTree(root)
    # Writing the modified tree back to the XML file
    tree.write("users.xml")

# Symmetric encryption key generated
# Read the key from the file
with open('mykey.key', 'rb') as mykey:
    key = mykey.read()
# Create a Fernet object with the key
f = Fernet(key)

# Encrypt data from original file with an encryption key
def encrypt_data():
    with open('users.xml', 'rb') as original_file:
        original = original_file.read()
    encrypted = f.encrypt(original)
    with open('enc_users.xml', 'wb') as encrypted_file:
        encrypted_file.write(encrypted)

# Decrypt data from encrypted file
def decrypt_data():
    with open('enc_users.xml', 'rb') as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = f.decrypt(encrypted)
    with open('dec_users.xml', 'wb') as decrypted_file:
        decrypted_file.write(decrypted)

# Signup screen
def signup_frame():
    # switches to login frame
    def switch_to_login(login_frame):
        signup_frame.pack_forget()
        login_frame()
    
    # Create signup frame
    signup_frame = Frame(tkWindow, bg='black', width=950, height=600)
    signup_frame.place(x=200, y=70)

    # Side image
    login_image = Image.open("login image.png")
    photo1 = ImageTk.PhotoImage(login_image)
    login_image_label = Label(signup_frame, image=photo1, bg='black')
    login_image_label.image = photo1  # referencing image object
    login_image_label.place(x=5, y=100)

    # User image
    user_image = Image.open("user image.png")
    photo2 = ImageTk.PhotoImage(user_image)
    user_image_label = Label(signup_frame, image=photo2, bg='black')
    user_image_label.image = photo2  # Keep a referencing to the image object
    user_image_label.place(x=620, y=40)

    # Signup label
    signup_label = Label(signup_frame, text="Register", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    signup_label.place(x=660, y=150)

    # Organisation
    organisation_label = Label(signup_frame, text="Organisation", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    organisation_label.place(x=530, y=190)
    organisation_entry = Entry(signup_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white')
    organisation_entry.place(x=535, y=220, width=270)
    organisation_line = Canvas(signup_frame, width=300, height=2, bg='white', highlightthickness=0)
    organisation_line.place(x=530, y=249)

    # Username
    username_label = Label(signup_frame, text="Username", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    username_label.place(x=530, y=270)
    username_entry = Entry(signup_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white')
    username_entry.place(x=535, y=300, width=270)
    username_line = Canvas(signup_frame, width=300, height=2, bg='white', highlightthickness=0)
    username_line.place(x=530, y=329)

    # Password
    password_label = Label(signup_frame, text="Password", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    password_label.place(x=530, y=355)
    password_entry = Entry(signup_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white', show='*')
    password_entry.place(x=535, y=385, width=270)
    password_line = Canvas(signup_frame, width=300, height=2, bg='white', highlightthickness=0)
    password_line.place(x=530, y=414)

    # Password re-enter
    password2_label = Label(signup_frame, text="Re-enter password", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    password2_label.place(x=530, y=440)
    password2_entry = Entry(signup_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white', show='*')
    password2_entry.place(x=535, y=470, width=270)
    password2_line = Canvas(signup_frame, width=300, height=2, bg='white', highlightthickness=0)
    password2_line.place(x=530, y=500)

    # Status label shows the status of account creation
    status_label = Label(signup_frame, bg='black', fg='white')
    status_label.place(x=640, y=180)

    # Validates and creates new account
    def activate(status_label, organisation_entry, username_entry, password_entry, password2_entry):
        organisation = organisation_entry.get()
        username = username_entry.get()
        password = password_entry.get()
        password2 = password2_entry.get()

        # Check if an account with the same username already exists
        for account in root.findall("account"):
            existing_username = account.find("username").text
            if existing_username == username:
                status_label.config(text="Username already exists")
                status_label.place(x=630, y=180)
                organisation_entry.delete(0, 'end')
                username_entry.delete(0, 'end')
                password_entry.delete(0, 'end')
                password2_entry.delete(0, 'end')
                return
        
        # Blank fields error
        if (len(username) <= 0) or (len(organisation) <= 0) or (len(password) <= 0) or (len(password) <= 0):
            status_label.config(text="Blank fields detected")
            status_label.place(x=640, y=180)
            return
        
        # Password validation
        if len(password) < 8:
            status_label.config(text="Password needs to contain a minimum of 8 characters")
            status_label.place(x=550, y=175)
            return
        
        # Password match
        if password != password2:
            status_label.config(text="Passwords do not match")
            status_label.place(x=640, y=180)
            return
        
        # All checks passed, account creation finalised
        # On each account
        new_account = ET.SubElement(root, "account")

        # Under each account, there will be all of these details stored
        new_organisation = ET.SubElement(new_account, "organisation")
        new_username = ET.SubElement(new_account, "username")
        new_password = ET.SubElement(new_account, "password")
        new_footage = ET.SubElement(new_account, "footage")
        new_traffic_signal_file = ET.SubElement(new_account, "traffic_signal_file")
        new_speed_file = ET.SubElement(new_account, "speed_file")
        new_all_file = ET.SubElement(new_account, "all_file")
        new_organisation.text = organisation
        new_username.text = username
        new_password.text = password
        new_traffic_signal_file.text = f"{username}_traffic_signal.xml"
        new_speed_file.text = f"{username}_speed.xml"
        new_all_file.text = f"{username}_traffic_signal.xml"

        # Write the XML tree to a file
        tree.write("users.xml")

        # encrypt updated data from original file
        encrypt_data()

        # decrypt updated data
        decrypt_data()

        status_label.config(text="Succesfully created account")
        status_label.place(x=620, y=175)
        organisation_entry.delete(0, 'end')
        username_entry.delete(0, 'end')
        password_entry.delete(0, 'end')
        password2_entry.delete(0, 'end')

        # Creating 3 new files for details storage of the new account user.
        root2 = ET.Element("violations")
        tree2 = ET.ElementTree(root2)
        tree2.write(f"{username}_traffic_signal.xml")
        root3 = ET.Element("violations")
        tree3 = ET.ElementTree(root3)
        tree3.write(f"{username}_speed.xml")
        root4 = ET.Element("violations")
        tree4 = ET.ElementTree(root4)
        tree4.write(f"{username}_all.xml")

    # Sign up button
    signup_button = Image.open("login button.png")
    photo4 = ImageTk.PhotoImage(signup_button)
    signup_image_label = Label(signup_frame, image=photo4, bg='black')
    signup_image_label.place(x=530, y=520)
    signup = Button(signup_frame, text='SIGN UP', font=('yu gothic ui', 13, 'bold'), width=25, bd=0, bg='#3047ff', cursor='hand2', activebackground="#3047ff", fg='white', command=lambda: activate(status_label, organisation_entry, username_entry, password_entry, password2_entry))
    signup.place(x=550, y=530)

    # Back button
    back = Button(signup_frame, text='Back', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: switch_to_login(login_frame))
    back.place(x=625, y=570)

    return signup_frame

# Login screen
def login_frame():
    global current_account
    # Switches to signup frame
    def switch_to_signup(signup_frame):
        login_frame.pack_forget()
        signup_frame()

    # Create login frame
    login_frame = Frame(tkWindow, bg='black', width=950, height=600)
    login_frame.place(x=200, y=70)

    # Side image
    login_image = Image.open("login image.png")
    photo1 = ImageTk.PhotoImage(login_image)
    login_image_label = Label(login_frame, image=photo1, bg='black')
    login_image_label.image = photo1  # referencing image object
    login_image_label.place(x=5, y=100)

    # User image
    user_image = Image.open("user image.png")
    photo2 = ImageTk.PhotoImage(user_image)
    user_image_label = Label(login_frame, image=photo2, bg='black')
    user_image_label.image = photo2  # Keep a referencing to the image object
    user_image_label.place(x=620, y=130)

    # Login label
    login_label = Label(login_frame, text="Log in", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    login_label.place(x=668, y=240)

    # Username
    username_label = Label(login_frame, text="Username", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    username_label.place(x=530, y=300)
    username_entry = Entry(login_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white')
    username_entry.place(x=535, y=330, width=270)
    username_line = Canvas(login_frame, width=300, height=2, bg='white', highlightthickness=0)
    username_line.place(x=530, y=359)

    # Password
    password_label = Label(login_frame, text="Password", bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'))
    password_label.place(x=530, y=385)
    password_entry = Entry(login_frame, highlightthickness=0, relief=FLAT, bg='black', fg='#4f4e4d', font=('yu gothic ui', 13, 'bold'), insertbackground='white', show='*')
    password_entry.place(x=535, y=415, width=270)
    password_line = Canvas(login_frame, width=300, height=2, bg='white', highlightthickness=0)
    password_line.place(x=530, y=444)

    # Hiding/unhiding password
    show = Image.open("eye open.png").resize((40, 27))
    hide = Image.open("eye closed.png").resize((38, 27))
    show_photo = ImageTk.PhotoImage(show)
    hide_photo = ImageTk.PhotoImage(hide)
    show_password = False

    # shift password visibility status
    def toggle_password():
        nonlocal show_password
        if not show_password:
            password_entry.config(show='')
            show_button.config(image=show_photo)
            show_password = True
        else:
            password_entry.config(show='*')
            show_button.config(image=hide_photo)
            show_password = False

    show_button = Button(login_frame, image=hide_photo, bg='black', relief=FLAT, activebackground='black', cursor='hand2', command=toggle_password)
    show_button.place(x=790, y=410)

    # Validates and loggs in the user
    status_label = Label(login_frame, bg='black', fg='white')
    status_label.place(x=640, y=270)

    # Credentials validation
    def validate(status_label): 
        global current_account
        username = username_entry.get()
        password = password_entry.get()
        status_label.config(text="Incorrect credentials")
        status_label.place(x=640, y=270)
        for account in root.findall("account"):
            if (account.find("username").text == username) and (account.find("password").text == password):
                current_account = account
                home()
                status_label.config(text="Success")
                status_label.place(x=670, y=270)

    # Login button
    login_button = Image.open("login button.png")
    photo3 = ImageTk.PhotoImage(login_button)
    login_image_label = Label(login_frame, image=photo3, bg='black')
    login_image_label.place(x=530, y=480)
    login = Button(login_frame, text='LOGIN', font=('yu gothic ui', 13, 'bold'), width=25, bd=0, bg='#3047ff', cursor='hand2', activebackground="#3047ff", fg='white', command=lambda: validate(status_label))
    login.place(x=550, y=490)

    # Sign in button
    signin = Button(login_frame, text='New? Sign up', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: switch_to_signup(signup_frame))
    signin.place(x=530, y=550)

    # Deleting user, only if correct username and password entered
    def delete_user(status_label, username_entry, password_entry):
        username = username_entry.get()
        password = password_entry.get()
        # Find account with matching username
        account_to_remove = None
        for account in root.findall("account"):
            if (account.find("username").text == username) and (account.find("password").text == password):
                account_to_remove = account
                break

        if account_to_remove is not None:
            # Remove the account element from the XML tree
            root.remove(account_to_remove)
            tree.write("users.xml")
            xml_file_path = f"{username}_traffic_signal.xml"
            deleted_addresses = [evidence.text for evidence in ET.parse(xml_file_path).iter('Evidence') if os.path.exists(evidence.text)]
            [os.remove(evidence) for evidence in deleted_addresses]

            # Removing all associated files of the user
            os.remove(f"{username}_traffic_signal.xml")
            os.remove(f"{username}_speed.xml")
            os.remove(f"{username}_all.xml")
            status_label.config(text="Successfully removed user")
            status_label.place(x=620, y=270)
            username_entry.delete(0, 'end')
            password_entry.delete(0, 'end')

            # encrypt updated XML content
            encrypt_data()

            # decrypt updated XML content
            decrypt_data()
        else:
            status_label.config(text="Incorrect credentials")
            status_label.place(x=640, y=270)

    # Delete user button
    delete = Button(login_frame, text='Delete user', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: delete_user(status_label, username_entry, password_entry))
    delete.place(x=750, y=550)

    return login_frame

# home screen
def home():
    global current_account
    def switch_to_login(home):
        current_account = None
        home.pack_forget()
        login_frame()
    
    def switch_to_traffic_signal(home):
        home.pack_forget()
        traffic_signal_frame()

    def switch_to_speed(home):
        home.pack_forget()
        speed_frame()
    
    def switch_to_all(home):
        home.pack_forget()
        all_frame()

    def upload_footage(footage_label):
        global current_account, tree

        def process_and_update_footage():
            # Update the footage attribute in the current_account
            current_account.attrib["footage"] = file_path
            tree.write("users.xml")
            encrypt_data()
            decrypt_data()

            # Calling Trafficlight.py file to process and retrieve violations
            name = current_account.find("username").text
            footage_file = current_account.attrib.get("footage")
            # Pass the footage that the user has selected and wants to process and their name in order to update the associated traffic signal file
            process_signal_footage(name, footage_file)

            # Update the footage label after processing is done
            footage_label.config(text="Uploaded footage: " + os.path.basename(file_path))

        # Prompt the user to select a new file path
        file_path = filedialog.askopenfilename()

        if file_path and file_path.lower().endswith('.mp4'):
            footage_label.config(text="Processing footage, please wait...")

            # Start a new thread to handle the footage processing
            processing_thread = threading.Thread(target=process_and_update_footage)
            processing_thread.start()

        elif file_path:
            footage_label.config(text="Please select an MP4 file")
        else:
            footage_label.config(text="No file selected")

    home = Frame(tkWindow, bg='black', width=950, height=600)
    home.place(x=200, y=70)

    name = current_account.find("username").text

    welcome_label = Label(home, text="Welcome " + name + "!", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    welcome_label.place(x=420, y=100)

    Traffic_signal_button = Button(home, text='Traffic signal violations', font=('yu gothic ui', 13, 'bold'), width=20, bd=0, bg='blue', cursor='hand2', fg='white', command=lambda: switch_to_traffic_signal(home))
    Traffic_signal_button.place(x=380, y=170)

    speed_button = Button(home, text='Speed violations', font=('yu gothic ui', 13, 'bold'), width=20, bd=0, bg='blue', cursor='hand2', fg='white', command=lambda: switch_to_speed(home))
    speed_button.place(x=380, y=240)

    all_violations_button = Button(home, text='All violations', font=('yu gothic ui', 13, 'bold'), width=20, bd=0, bg='blue', cursor='hand2', fg='white', command=lambda: switch_to_all(home))
    all_violations_button.place(x=380, y=310)

    upload_button = Button(home, text='Upload footage', font=('yu gothic ui', 13, 'bold'), width=20, bd=0, bg='blue', cursor='hand2', fg='white', command=lambda: upload_footage(footage_label))
    upload_button.place(x=380, y=380)

    footage_label = Label(home, text="Uploaded footage: " + os.path.basename(current_account.attrib.get("footage", "")), bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    footage_label.place(x=367, y=432)

    log_out = Button(home, text='Log out', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: switch_to_login(home))
    log_out.place(x=430, y=470)

# Traffic violations frame
def traffic_signal_frame():
    def switch_to_home():
        traffic_signal_frame.pack_forget()
        home()

    name = current_account.find("username").text

    traffic_signal_frame = Frame(tkWindow, bg='black', width=950, height=600)
    traffic_signal_frame.place(x=200, y=70)

    title_label = Label(traffic_signal_frame, text="Traffic Signal Violations", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    title_label.place(x=420, y=100)

    # creating a canvas to display violation details
    canvas = Canvas(tkWindow, bg='black', bd=0, highlightthickness=0)
    canvas.place(x=600, y=230, width=470, height=270)

    # scrollbar, vertical view control
    scrollbar = Scrollbar(tkWindow, command=canvas.yview)
    scrollbar.place(x=910, y=230, height=270)

    canvas.config(yscrollcommand=scrollbar.set)

    violations_frame = Frame(canvas, bg='black')
    canvas.create_window((0,0), window=violations_frame, anchor=NW)

    # Read the existing XML file via creating a tree
    tree = ET.parse(f"{name}_traffic_signal.xml")
    # obtain root
    violations = tree.getroot()

    # Clear any existing labels in the violations_frame
    for widget in violations_frame.winfo_children():
        widget.destroy()

    # Add text labels for each violation in violations
    for row_num, violation in enumerate(violations.findall("violation")):
        label_texts = [f"{child.tag}: {child.text}" for child in violation]
        labels_text = "\n".join(label_texts)
        label = Label(violations_frame, text=labels_text, bg='black', fg='white')
        label.grid(row=row_num, column=0, padx=10, pady=5, sticky='w')

    # Updating the scroll region when the content changes
    violations_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    back = Button(traffic_signal_frame, text='Back', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=switch_to_home)
    back.place(x=445, y=500)

# speed violations frame
def speed_frame():
    def switch_to_home(speed_frame):
        speed_frame.pack_forget()
        home()
    
    speed_frame = Frame(tkWindow, bg='black', width=950, height=600)
    speed_frame.place(x=200, y=70)

    title_label = Label(speed_frame, text="Speed Violations", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    title_label.place(x=420, y=100)

    # Create a canvas with a vertical scrollbar
    canvas = Canvas(tkWindow, bg='black', bd=0, highlightthickness=0)
    canvas.place(x=440, y=230, width=470, height=270)

    scrollbar = Scrollbar(tkWindow, command=canvas.yview)
    scrollbar.place(x=910, y=230, height=270)

    # Link the scrollbar to the canvas
    canvas.config(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the traffic signal violations content
    violations_frame = Frame(canvas, bg='black')
    canvas.create_window((0, 0), window=violations_frame, anchor=NW)

    # Example: Add some labels to simulate content
    for i in range(20):
        label = Label(violations_frame, text=f"Violation {i}", bg='black', fg='white')
        label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

    # Update the scroll region when the content changes
    violations_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    back = Button(speed_frame, text='Back', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: switch_to_home(speed_frame))
    back.place(x=445, y=500) 

# all violations frame
def all_frame():
    def switch_to_home(all_frame):
        all_frame.pack_forget()
        home()
    
    all_frame = Frame(tkWindow, bg='black', width=950, height=600)
    all_frame.place(x=200, y=70)

    title_label = Label(all_frame, text="All Violations", bg='black', fg='white', font=('yu gothic ui', 13, 'bold'))
    title_label.place(x=420, y=100)

    # Create a canvas with a vertical scrollbar
    canvas = Canvas(tkWindow, bg='black', bd=0, highlightthickness=0)
    canvas.place(x=440, y=230, width=470, height=270)

    scrollbar = Scrollbar(tkWindow, command=canvas.yview)
    scrollbar.place(x=910, y=230, height=270)

    # Link the scrollbar to the canvas
    canvas.config(yscrollcommand=scrollbar.set)

    # Create a frame inside the canvas to hold the traffic signal violations content
    violations_frame = Frame(canvas, bg='black')
    canvas.create_window((0, 0), window=violations_frame, anchor=NW)

    # Example: Add some labels to simulate content
    for i in range(20):
        label = Label(violations_frame, text=f"Violation {i}", bg='black', fg='white')
        label.grid(row=i, column=0, padx=10, pady=5, sticky='w')

    # Update the scroll region when the content changes
    violations_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    
    back = Button(all_frame, text='Back', font=('yu gothic ui', 13, 'bold'), width=10, bd=0, bg='black', cursor='hand2', fg='white', command=lambda: switch_to_home(all_frame))
    back.place(x=445, y=500)  

# First display login frame
login_frame()

# for account in root.findall("account"):
#     if (account.find("username").text == "Manu") and (account.find("password").text == "12345678"):
#         current_account = account
#         home()

# Run
tkWindow.mainloop()
