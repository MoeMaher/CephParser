import cv2  
import os
import sys
import pandas as pd  
import numpy as np
from tkinter import *  
from PIL import Image, ImageTk  
from tkinter import ttk  
import math

def ang(lineA, lineB):
    # Get nicer vector form
    vA = [(lineA[0][0]-lineA[1][0]), (lineA[0][1]-lineA[1][1])]
    vB = [(lineB[0][0]-lineB[1][0]), (lineB[0][1]-lineB[1][1])]
    # Get dot prod
    dot_prod = np.dot(vA, vB)
    # Get magnitudes
    magA = np.dot(vA, vA)**0.5
    magB = np.dot(vB, vB)**0.5
    # Get cosine value
    cos_ = dot_prod/magA/magB
    # Get angle in radians and then convert to degrees
    angle = math.acos(dot_prod/magB/magA)
    # Basically doing angle <- angle mod 360
    ang_deg = math.degrees(angle)

    return ang_deg

if getattr(sys, 'frozen', False):  
    root_folder = os.path.dirname(sys.executable)  
else:  
    root_folder = "./"

def SNA(s,n,a):
    print(s,n,a)
    print(180-ang([s,n], [n,a]))
    return 180-ang([s,n], [n,a])

def SNB(s,n,b):
    return 180-ang([s,n], [n,b])

def ANB(s,a,n,b):
    if SNA(s,n,a)-SNB(s,n,b) >0:
        return (180- ang([n,b],[a,n]))
    else:
        return -1* (180- ang([n,b],[a,n]))

def u1(ans, pns, u_tip, u_apex):
    return 180-ang([ans,pns], [u_tip, u_apex])

def l1(go, mn, l_tip, l_apex):    
    return 180- ang([go,mn], [l_apex,l_tip])

def sn_ans_pns(ans, pns, s, n):
    return 180-ang([s, n],[ans,pns])

def sn_mn_go(go, mn, s, n):  
    return ang([s, n],[go,mn])

# def print_angles(pateinty):
#     print("SNA", SNA(pateinty))
#     print("SNB", SNB(pateinty))
#     print("ANB", ANB(pateinty))
#     print("u1", u1(pateinty))
#     print("l1", l1(pateinty))
#     print("sn_ans_pns", sn_ans_pns(pateinty))
#     print("sn_mn_go", sn_mn_go(pateinty))





def find_red_dots(image_path):
    image = cv2.imread(image_path)  
    red_dots = []  
  
    # Use a mask to find red pixels  
    lower_red = (0, 0, 200)  
    upper_red = (50, 50, 255)
    # print(image)
    mask = cv2.inRange(image, lower_red, upper_red)  

    # Find contours of the red dots  
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
  
    for cnt in contours:  
        # Get the coordinates of the red dot  
        x, y, w, h = cv2.boundingRect(cnt)  
        center_x, center_y = x + w // 2, y + h // 2  
        red_dots.append((center_x, center_y))  
  
    return red_dots 




def extract_all_coordinates():  
    all_coordinates = {  
        "patient": [],  
        "sella_x": [],  
        "sella_y": [],  
        "nasion_x": [],  
        "nasion_y": [],  
        "A point_x": [],  
        "A point_y": [],  
        "B point_x": [],  
        "B point_y": [],  
        "upper 1 tip_x": [],  
        "upper 1 tip_y": [],  
        "upper 1 apex_x": [],  
        "upper 1 apex_y": [],  
        "lower 1 tip_x": [],  
        "lower 1 tip_y": [],  
        "lower 1 apex_x": [],  
        "lower 1 apex_y": [],  
        "ANS_x": [],  
        "ANS_y": [],  
        "PNS_x": [],  
        "PNS_y": [],  
        "Gonion _x": [],  
        "Gonion _y": [],  
        "Menton_x": [],  
        "Menton_y": [],  
        "ST Nasion_x": [],  
        "ST Nasion_y": [],  
        "Tip of the nose_x": [],  
        "Tip of the nose_y": [],  
        "Subnasal_x": [],  
        "Subnasal_y": [],  
        "Upper lip_x": [],  
        "Upper lip_y": [],  
        "Lower lip_x": [],  
        "Lower lip_y": [],  
        "ST Pogonion_x": [],  
        "ST Pogonion_y": []
    }  
  
    for patient in patient_folders:  
        coordinates_file = os.path.join(root_folder, patient, 'coordinates.csv')  
        all_coordinates["patient"].append(patient)  
          
        coord_dict = {key: None for key in all_coordinates.keys() if key != 'patient'}  
          
        if os.path.exists(coordinates_file):  
            patient_coordinates = pd.read_csv(coordinates_file)  
            coord_dict.update({f"{row['dot_name']}_x": row["x"] for _, row in patient_coordinates.iterrows() if f"{row['dot_name']}_x" in coord_dict.keys()})  
            coord_dict.update({f"{row['dot_name']}_y": row["y"] for _, row in patient_coordinates.iterrows() if f"{row['dot_name']}_y" in coord_dict.keys()})  
  
        for key, value in coord_dict.items():  
            all_coordinates[key].append(value)  
  
    all_coordinates_df = pd.DataFrame(all_coordinates)  
    all_coordinates_df.to_excel(os.path.join(root_folder, 'all_coordinates.xlsx'), index=False)  




def on_image_click(event):  
    global current_dot_name, dot_mapping, window, ceph_image  
    x, y = event.x, event.y  
  
    # Find the closest red dot to the click position  
    closest_dot = min(red_dots, key=lambda dot: (x - dot[0]) ** 2 + (y - dot[1]) ** 2)  
    dot_mapping[current_dot_name] = closest_dot  
    red_dots.remove(closest_dot)  
  
    dot_name_index = dot_names.index(current_dot_name)  
    if dot_name_index + 1 < len(dot_names):  
        current_dot_name = dot_names[dot_name_index + 1]  
        dot_name_label.config(text=f"Select {current_dot_name}")  
    else:  
        window.quit()  
  
    update_image(ceph_image) 
    update_angles()  # Add this line to update angles  
 
  
  
def update_image(ceph_image):  
    global image, red_dots  
    image_with_dots = image.copy()  
    for dot in red_dots:  
        cv2.circle(image_with_dots, (dot[0], dot[1]), 3, (0, 255, 0), 2)  
  
    img = cv2.cvtColor(image_with_dots, cv2.COLOR_BGR2RGB)  
    img = Image.fromarray(img)  
      
    # Merge the images before updating the panel  
    merged_image = merge_images_horizontally(img, ceph_image)  
  
    panel.config(image=merged_image)  
    panel.image = merged_image  # Keep a reference to the image object  


def load_ceph_image(patient_folder):  
    ceph_image_path = os.path.join(patient_folder, 'ceph.JPG')  
    if not os.path.exists(ceph_image_path):  
        return None  
  
    ceph_image = cv2.imread(ceph_image_path)  
    ceph_image = cv2.cvtColor(ceph_image, cv2.COLOR_BGR2RGB)  
    ceph_image = Image.fromarray(ceph_image) 
    #resize image to be with the bigger side 600
    width, height = ceph_image.size
    if width > height:
        ceph_image = ceph_image.resize((600, int(600*height/width)))
    else:
        ceph_image = ceph_image.resize((int(600*width/height), 600))
  
    return ceph_image  

def merge_images_horizontally(image1, image2):  
    if image2 is not None:
        print("Merging")
        merged_image = Image.new('RGB', (image1.width + image2.width, max(image1.height, image2.height)))  
        merged_image.paste(image1, (0, 0))  
        merged_image.paste(image2, (image1.width, 0))  
    else:  
        merged_image = image1  
  
    return ImageTk.PhotoImage(merged_image) 

def reset_points_selected():  
    global red_dots, dot_mapping, current_dot_name  
      
    # Return the previously selected dots back to the red_dots list  
    for dot in dot_mapping.values():  
        red_dots.append(dot)  
          
    # Reset the dot_mapping and current_dot_name  
    dot_mapping = {}  
    current_dot_name = dot_names[0]  
      
    # Update the instructions label  
    dot_name_label.config(text=f"Select {current_dot_name}")  
      
    # Refresh the image to show all the red dots  
    update_image(ceph_image)  


def compute_angles(dot_data):
    angles = []
    try:
        s = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "sella"][0]
    except IndexError:
        s = None
    try:
        n = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "nasion"][0]
    except IndexError:
        n = None
    try:
        a = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "A point"][0]
    except IndexError:
        a = None
    try:
        b = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "B point"][0]
    except IndexError:
        b = None
    try:
        ans = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "ANS"][0]
    except IndexError:
        ans = None
    try:
        pns = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "PNS"][0]
    except IndexError:
        pns = None
    try:
        u_tip = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "upper 1 tip"][0]
    except IndexError:
        u_tip = None
    try:
        u_apex = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "upper 1 apex"][0]
    except IndexError:
        u_apex = None
    try:
        l_tip = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "lower 1 tip"][0]
    except IndexError:
        l_tip = None
    try:
        l_apex = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "lower 1 apex"][0]
    except IndexError:
        l_apex = None
    try:
        go = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "Gonion "][0]
    except IndexError:
        go = None
    try:
        mn = [[dot["x"], dot["y"]] for dot in dot_data if dot["dot_name"] == "Menton"][0]
    except IndexError:
        mn = None

    # s n a b ans pns u_tip u_apex go mn l_tip l_apex 
    if s is not None and n is not None and a is not None:
        angles.append({"dot_name": "SNA", "x": SNA(s,n,a), "y": round(SNA(s,n,a), 1)})
    if s is not None and n is not None and b is not None:
        angles.append({"dot_name": "SNB", "x": SNB(s,n,b), "y": round(SNB(s,n,b), 1)})
    if a is not None and n is not None and b is not None:
        angles.append({"dot_name": "ANB", "x": ANB(s,a,n,b), "y": round(ANB(s,a,n,b), 1)})
    if ans is not None and pns is not None and u_tip is not None and u_apex is not None:
        angles.append({"dot_name": "u1", "x": u1(ans, pns, u_tip, u_apex), "y": round(u1(ans, pns, u_tip, u_apex), 1)})
    if go is not None and mn is not None and l_tip is not None and l_apex is not None:
        angles.append({"dot_name": "l1", "x": l1(go, mn, l_tip, l_apex), "y": round(l1(go, mn, l_tip, l_apex), 1)})
    if ans is not None and pns is not None and s is not None and n is not None:
        angles.append({"dot_name": "sn_ans_pns", "x": sn_ans_pns(ans, pns, s, n), "y": round(sn_ans_pns(ans, pns, s, n), 1)})
    if go is not None and mn is not None and s is not None and n is not None:
        angles.append({"dot_name": "sn_mn_go", "x": sn_mn_go(go, mn, s, n), "y": round(sn_mn_go(go, mn, s, n), 1)})

    return angles

def update_angles():  
    dot_data = [{"dot_name": name, "x": coords[0], "y": coords[1]} for name, coords in dot_mapping.items()]  
    angles = compute_angles(dot_data) 
    angles_from_dolphine = find_angles_from_dolphine(os.path.join(root_folder, patient)) 
    angle_text = "   ".join([f"{angle['dot_name']}: {angle['y']}" for angle in angles])  
    angle_text_from_dolphine = "   ".join([f"{angle_name}: {angle_value}" for angle_name, angle_value in angles_from_dolphine.items()])
    angle_label.config(text=angle_text)  
    angle_label_from_dolphine.config(text=angle_text_from_dolphine)  

import re  
import os  
  
def find_angles_from_dolphine(parent_directory):  
    angle_dict = {}  
  
    # Read ABO.txt  
    abo_file = parent_directory + "/ABO.txt"  
    if os.path.exists(abo_file):  
        with open(abo_file, "r", encoding='ISO-8859-1') as f:  
            text = f.read()  
  
        angle_names = ["SNA", "SNB", "SN - MP", "ANB", "L1 - MP"]  
  
        for angle_name in angle_names:  
            angle_line = re.search(rf"{angle_name}\s*\(º\).*", text)  
            if angle_line:  
                angle_parts = angle_line.group(0).split()  
                try:  
                    angle_value = float(angle_parts[2])  
                except ValueError:  
                    angle_value = float(angle_parts[4])  
                angle_dict[angle_name] = angle_value  
            else:  
                angle_dict[angle_name] = None  
    else:  
        print(f"{abo_file} not found.")  
  
    # Read Bjork.txt  
    bjork_file = parent_directory + '/Bjork.txt'  
    if os.path.exists(bjork_file):  
        with open(bjork_file, 'r', encoding='ISO-8859-1') as file:  
            text = file.read()  
  
        angle_names = ["Cranio-Mx Base/SN-Palatal Plane", "U1 - Palatal Plane/Mx Base"]  
  
        for angle_name in angle_names:  
            angle_line = re.search(rf"{re.escape(angle_name)}\s*\(º\).*", text)  
            if angle_line:  
                angle_parts = angle_line.group(0).split()  
                try:  
                    angle_value = float(angle_parts[4])  
                except:  
                    angle_value = float(angle_parts[6])  
                angle_dict[angle_name] = angle_value  
            else:  
                angle_dict[angle_name] = None  
    else:  
        print(f"{bjork_file} not found.")  
  
    return angle_dict  

window = None
# root_folder = "./"

def custom_sort_key(s):  
    parts = s.split(' - ')  
    if parts[0].isdigit():  
        return int(parts[0])  
    else:  
        return float('inf')  

patient_folders = sorted([f for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))], key=custom_sort_key)  
print(patient_folders)
dot_names = ["sella", "nasion", "A point", "B point", "upper 1 tip", "upper 1 apex", "lower 1 tip", "lower 1 apex", "ANS", "PNS", "Gonion ", "Menton", "ST Nasion", "Tip of the nose", "Subnasal", "Upper lip", "Lower lip", "ST Pogonion"]  
  
if not patient_folders:  
    print("No patient folders found. Exiting.")  
    sys.exit(0) 


for patient in patient_folders:  
    image_path = os.path.join(root_folder, patient, 'reddots.JPG')  
    coordinates_file = os.path.join(root_folder, patient, 'coordinates.csv')  
    ceph_image = load_ceph_image(os.path.join(root_folder, patient))  

    if not os.path.exists(image_path):  
        print(f"No 'reddots.JPG' found for patient {patient}. Skipping.")  
        continue  

    # Check if the coordinates file exists, if so, skip the patient  
    if os.path.exists(coordinates_file):  
        continue  
  

    red_dots = find_red_dots(image_path)  
    image = cv2.imread(image_path)  
  
    window = Tk()  
    window.title("Dot Labeling")
    window.geometry('1300x750+0+0')
    # window.attributes('-topmost', True) 
    
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  
    img = ImageTk.PhotoImage(Image.fromarray(img))
    # print(img)
    
    # Merge the two images  
    merged_image = merge_images_horizontally(Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)), ceph_image)  
      
    # Display the merged image  
    panel = Label(window, image=merged_image)  
    panel.image = merged_image  
    panel.pack(side="top", padx=5, pady=5)

    panel.bind("<Button-1>", on_image_click)  
    print(patient)
    current_dot_name = dot_names[0]  
    dot_mapping = {}  
  
    patient_dot_name_frame = Frame(window)  
    patient_dot_name_frame.pack(side="top", padx=5, pady=5)  

    dot_name_label = Label(patient_dot_name_frame, text=f"Select {current_dot_name}", font=("Arial", 14))
    patient_name_label = Label(patient_dot_name_frame, text="", font=("Arial", 14))  

    dot_name_label.grid(row=0, column=0, padx=5, pady=5)  
    patient_name_label.grid(row=0, column=1, padx=5, pady=5)  
    patient_name_label.config(text=f"|  for Patient: {patient}")  # Add this line to update the patient's name  
    # dot_name_label.pack(side="top", padx=5, pady=5)  
  
    angle_label = Label(window, text="", font=("Arial", 11))  
    angle_label.pack(side="top", padx=0, pady=0) 
    angle_label_from_dolphine = Label(window, text="", font=("Arial", 11))  
    angle_label_from_dolphine.pack(side="top", padx=0, pady=0)  

    


    button_frame = Frame(window)  
    button_frame.pack(side="top", padx=5, pady=5)  

    extract_button = ttk.Button(button_frame, text="Extract All Coordinates", command=extract_all_coordinates)  
    reset_button = ttk.Button(button_frame, text="Reset", command=reset_points_selected)  

    extract_button.grid(row=0, column=0, padx=5, pady=5)  
    reset_button.grid(row=0, column=1, padx=5, pady=5)  



    update_image(ceph_image)  
    window.mainloop()  
  
    # Save the coordinates to a CSV file in the patient's folder  
    dot_data = [{"dot_name": name, "x": coords[0], "y": coords[1]} for name, coords in dot_mapping.items()]
    angles = compute_angles(dot_data)
    angles_from_dolphine = find_angles_from_dolphine(os.path.join(root_folder, patient))
    dot_data = dot_data + angles + [{"dot_name": angle_name +"_from_dolphine", "x": angle_value, "y": 0} for angle_name, angle_value in angles_from_dolphine.items()]
    print(dot_data)
    pd.DataFrame(dot_data).to_csv(coordinates_file, index=False, columns=["dot_name", "x", "y"])  

    window.destroy()
    window = None

if window is None:  
    window = Tk()  
    window.title("No more patients")  

    extract_button = ttk.Button(window, text="Extract All Coordinates", command=extract_all_coordinates)  
    extract_button.pack(side="top", padx=5, pady=5)  
    message_label = Label(window, text="You have finished processing all patients in the root directory.", font=("Arial", 14))  
    message_label.pack(side="top", padx=5, pady=5)
    window.mainloop()  