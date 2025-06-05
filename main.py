import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import cv2
import pandas as pd
import os

v12 = 0.2
v31 = 0.5

def estimate_area_of_potholes(video_path, material_factor):
    output_frames_path = "frames/"
    output_csv_path = "output.csv"
    if not os.path.exists(output_frames_path):
        os.makedirs(output_frames_path)
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    success, frame = cap.read()
    frame_count = 0
    pothole_data = []
    pothole_number = 1
    while success:
        if frame_count % fps == 0:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
            edges = cv2.Canny(blurred_frame, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                if cv2.contourArea(contour) > 500:
                    epsilon = 0.02 * cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, epsilon, True)
                    area = cv2.contourArea(approx)
                    cost_of_repair = area * material_factor
                    frame_path = f"{output_frames_path}pothole_{pothole_number}.jpg"
                    cv2.imwrite(frame_path, frame)
                    pothole_data.append([pothole_number, area, cost_of_repair])
                    pothole_number += 1
        success, frame = cap.read()
        frame_count += 1
    cap.release()
    df = pd.DataFrame(pothole_data, columns=['Pothole_Number', 'Area_pothole', 'Cost_Repair_Pothole'])
    total_cost = df['Cost_Repair_Pothole'].sum()
    total_row = pd.DataFrame([['Total', '', total_cost]], columns=['Pothole_Number', 'Area_pothole', 'Cost_Repair_Pothole'])
    df = pd.concat([df, total_row], ignore_index=True)
    df.to_csv(output_csv_path, index=False)
    # Change directory to the "cpp" folder
    os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop', 'cpp'))

def browse_file():
    filename = filedialog.askopenfilename()
    entry_path.delete(0, tk.END)
    entry_path.insert(0, filename)

def calculate_potholes():
    video_path = entry_path.get()
    material = material_var.get()
    if material == '1':
        factor = v12
    elif material == '2':
        factor = v31
    else:
        factor = 0.1

    if not video_path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    try:
        estimate_area_of_potholes(video_path, factor)
        messagebox.showinfo("Success", "Potholes estimation completed successfully!")
        cpp_folder = os.path.join(os.path.expanduser('~'), 'Desktop', 'cpp')
        os.startfile(cpp_folder)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# GUI setup
root = tk.Tk()
root.title("Pothole Estimation")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

label_path = tk.Label(frame, text="Select Video File:")
label_path.grid(row=0, column=0, sticky="w")

entry_path = tk.Entry(frame, width=50)
entry_path.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame, text="Browse", command=browse_file)
button_browse.grid(row=0, column=2, padx=5, pady=5)

label_material = tk.Label(frame, text="Select Material:")
label_material.grid(row=1, column=0, sticky="w")

material_var = tk.StringVar(value='1')
radio_v12 = tk.Radiobutton(frame, text="Material 1 (v12)", variable=material_var, value='1')
radio_v12.grid(row=1, column=1, sticky="w")

radio_v31 = tk.Radiobutton(frame, text="Material 2 (v31)", variable=material_var, value='2')
radio_v31.grid(row=1, column=2, sticky="w")

button_calculate = tk.Button(frame, text="Calculate Potholes", command=calculate_potholes)
button_calculate.grid(row=2, column=0, columnspan=3, pady=10)

root.mainloop()
