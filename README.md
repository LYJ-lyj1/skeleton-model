# 🦴 3D Human Skeleton Joint Angle Visualization System

**A web-based interactive tool for visualizing human skeletal kinematics based on joint angle input.**

---

### 📅 Project Status
- **Last Updated:** May 16, 2026
- **Version:** 2.0
- **Location:** Anshun, Guizhou, China

---

### 🚀 Live Demo
**Click the button below to view the interactive application:**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-deployed-link-here.streamlit.app)
> *Note: Replace the link above with your actual Streamlit Community Cloud URL after deployment.*

---

### 📋 Features
- **3D Skeleton Visualization:** Real-time rendering of human skeleton based on angle data.
- **Comprehensive Input:** 
  - 25 Spine segments (Cervical, Thoracic, Lumbar, Sacrum)
  - 8 Major Joints (Shoulders, Elbows, Hips, Knees)
- **Anatomy Integration:** Interactive pop-up windows showing anatomical diagrams for each joint.
- **Data Management:** 
  - Input validation (-180° ~ 180°)
  - CSV data export
  - Reset and Preview functions
- **Responsive Design:** Works on both desktop and mobile browsers.

---

### 🛠️ How to Use

#### Option 1: Web Version (Recommended for Sharing)
1.  Click the **Live Demo** badge above.
2.  Input joint angles in the sidebar.
3.  Click **Preview** to generate the 3D model.
4.  Click **Save** to export data as CSV.

#### Option 2: Local Development
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```
4.  Open your browser and navigate to `http://localhost:8501`.

---

### 📂 Project Structure
```plaintext
SkeletonVisualizer/
├── app.py                  # Main Streamlit interface
├── skeleton_model.py       # 3D skeleton calculation & plotting
├── data_processor.py       # Data validation & storage
├── requirements.txt        # Python dependencies
├── anatomy_images/         # Joint anatomy diagrams
└── README.md               # Project documentation