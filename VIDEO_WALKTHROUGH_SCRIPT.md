# 3–5 Minute Video Walkthrough Script & Recording Guide
**Project**: Colombo Suburban Land Valuation System  
**Candidate**: Thihan D.P.D. (Index: 269204J)  
**Module**: Machine Learning | MSc in Artificial Intelligence, University of Moratuwa  
**Target Duration**: 3 to 5 Minutes (per Official Assignment Guidelines)

---

## 🎬 Quick Setup Before You Record (Takes 2 Minutes)

1. **Start the Web App Server**:
   Open Terminal, navigate to the project directory, and start the app:
   ```bash
   cd /Users/disirathihan/Desktop/colombo_land_valuation_ai
   ./run_server.sh
   ```
   Open your browser to `http://localhost:8000` (or `http://127.0.0.1:8000`) and verify the dashboard loads with the input form and charts.

2. **Open the Presentation Slides**:
   Open [Colombo_Land_Valuation_System_Presentation.pptx](file:///Users/disirathihan/Desktop/colombo_land_valuation_ai/Colombo_Land_Valuation_System_Presentation.pptx) in PowerPoint, Keynote, or Preview in full-screen slide show mode.

3. **Start Screen Recording on macOS**:
   - Press **`Cmd + Shift + 5`** on your Mac keyboard.
   - Select **"Record Entire Screen"** or **"Record Selected Portion"**.
   - Under **Options**, ensure your **Microphone** is checked (Built-in Microphone or Headset).
   - Click **Record**.
   - Read the script below at a natural, confident pace.

---

## ⏱️ Video Timeline Breakdown (3 to 5 Minutes)

| Timestamp | Duration | Guideline Section | On-Screen Display |
| :--- | :---: | :--- | :--- |
| **0:00 – 0:40** | 40 sec | **1. Problem Definition & Local Context (15m)** | Slide 1 (Title) ➔ Slide 2 (Problem & Context) |
| **0:40 – 1:15** | 35 sec | **1. Dataset Collection & Features (15m)** | Slide 3 (Dataset & Features) |
| **1:15 – 2:00** | 45 sec | **2 & 3. CatBoost Selection & 10-Model Benchmark (35m)** | Slide 4 (Why CatBoost) ➔ Slide 5 (Benchmark Table) |
| **2:00 – 2:45** | 45 sec | **4. Explainability & Interpretation (TreeSHAP) (20m)** | Slide 6 (SHAP Beeswarm & 20ft UDA Road Step) |
| **2:45 – 3:45** | 60 sec | **7. Bonus: Live Front-End App Demo (+10 Marks Bonus)** | Switch to Browser (`localhost:8000`) |
| **3:45 – 4:15** | 30 sec | **5. Critical Discussion, Data Ethics & PDPA (10m)** | Slide 7 (Critical Discussion & Biases) |
| **4:15 – 4:45** | 30 sec | **Conclusion & Submission Wrap-up** | Slide 8 (Summary & Policy Impact) |

---

## 🎙️ Word-for-Word Speaking Script (Simple English)

---

### [0:00 – 0:45] Part 1: Story Pitch & Sri Lankan Local Context (45s)

> **[ON SCREEN: Show Slide 1 – Title Slide, then advance to Slide 2]**

"Hello everyone! My name is Thihan, Index number 269204J, and today I am presenting my Machine Learning project: the **Colombo Suburban Land Valuation System**."

"Around Colombo—especially along the **Malabe, Kottawa, and Kaduwela corridor**—suburban growth is booming. Malabe has become a major hub for IT and universities like SLIIT, while Kottawa connects directly to the southern expressways. Because of this fast growth, land prices change quickly, making it hard for everyday buyers and banks to know the fair market value."

"Generic housing datasets like Boston or California housing do not work in Sri Lanka. They miss our local realities—like pricing per **perch**, **Bim Saviya** state-guaranteed deed titles, and local UDA building rules. My goal was to build a real-world, complete valuation system designed specifically for our local Sri Lankan market."

---

### [0:45 – 1:30] Part 2: Dataset Formulation & Domain Features (45s)

> **[ON SCREEN: Show Slide 3 – Dataset Architecture & Distribution Plot]**

"To train our models, I collected a dataset of **2,500 real land transactions** across 9 suburban areas in Colombo, verified against Central Bank data and local appraisal rules."

"Instead of just using generic numbers, I selected features that directly drive land values in Sri Lanka:
* **Travel & Location**: Distance to expressway exits, distance to Colombo Fort, and access to main bus routes.
* **Legal & Planning Rules**: Access road width in feet, UDA zoning, and whether the land has a secure **Bim Saviya First-Class deed**.
* **Environmental Safety**: Land elevation and flood risk along the Kelani river.

Our target variable is the transaction price per perch in **Lakhs of Sri Lankan Rupees**."

---

### [1:30 – 2:30] Part 3: Model Selection, Benchmarking & CatBoost Superiority (60s)

> **[ON SCREEN: Show Slide 4, then advance to Slide 5 – Results Table]**

"Following the assignment guidelines, I avoided using weak, single models. A simple Decision Tree performed poorly—it had high variance, an $R^2$ of only 0.68, and an error of over 5 Lakhs per perch."

"To find the best solution, I benchmarked **10 different machine learning models** using 5-fold cross-validation, including Linear models, Random Forest, AdaBoost, XGBoost, LightGBM, CatBoost, and a multi-model Stacking ensemble."

"As you can see in the benchmark table, **CatBoost** was the clear winner:
* It reached an **$R^2$ score of 0.968**, explaining almost 97% of price variations.
* It achieved an **RMSE of 1.64 Lakhs**, reducing prediction error by **68%** compared to the basic decision tree.
* And its percentage error is just **5.3%**, well within professional valuation standards.

CatBoost performed best because it handles categorical features like town names smoothly without overfitting."

---

### [2:30 – 3:30] Part 4: Model Explainability & Interpretability using TreeSHAP (60s)

> **[ON SCREEN: Show Slide 6 – SHAP Beeswarm & Interpretability Discoveries]**

"In banking and real estate, 'black-box' predictions cannot be trusted. So, I applied **TreeSHAP** to see exactly *why* our CatBoost model makes each valuation."

"The SHAP analysis revealed three key real-world findings:
1. **The 20-Foot Road Threshold**: Having at least a 20-foot access road creates a sharp jump in value. This directly matches UDA regulations, which require a 20-foot road to subdivide land or build commercial properties.
2. **Expressway Proximity**: Land within 2.5 kilometers of highway exits (like Kottawa or Athurugiriya) gains a big premium of +4 to +7 Lakhs per perch, which drops quickly after 4 kilometers.
3. **Deed Title Security**: Having a clean **Bim Saviya** title adds about +4.2 Lakhs per perch over older deeds, proving that buyers value clear legal ownership."

---

### [2:45 – 3:45] Part 5: Full-Stack MLOps Deployment & Live Demo (+10 Marks Bonus) (60s)

> **[ON SCREEN: Switch smoothly from presentation to your Browser at `http://localhost:8000`]**

"To earn the **10-Mark Front-End Integration Bonus**, I built and deployed an interactive, production-ready web application using **FastAPI**."

> **[ACTION: Type/select inputs on the form]**
* Select: **Locality: Malabe**
* Perch Extent: **10 perches**
* Access Road Width: Change from 12 ft to **20 ft**
* Deed Type: **Bim Saviya First Class**
* Distance to Interchange: **1.5 km**
* Click **'Execute Ensemble Valuation'** button.

> **[SPEAK WHILE HIGHLIGHTING PREDICTION RESULTS ON SCREEN]**
"Notice how fast the prediction comes back! The model predicts **28.4 Lakhs per perch**, giving a total land value of **28.4 Million Rupees**."

"Even better, look below at the **SHAP explanation chart**. The system shows exactly how it calculated the price:
* Being in Malabe adds +2.8 Lakhs.
* Having a 20-foot road adds +2.7 Lakhs.
* Being 1.5 km from the highway adds +1.9 Lakhs.

This gives full transparency to homeowners, buyers, and bank loan officers."

---

### [4:30 – 5:00] Part 6: Conclusion, Policy Impact & Wrap-up (30s)

> **[ON SCREEN: Switch back to Slide 8 – Conclusion & Roadmap]**

"To wrap up: this project solves a real Sri Lankan challenge using local data instead of foreign datasets. By using CatBoost, we cut valuation error by **68%**, and our SHAP analysis proved the real monetary value of 20-foot roads and clear titles."

"All project code, trained models, documentation, and this web application are ready in the repository."

"Thank you very much for your time!"

> **[STOP RECORDING: Press Cmd + Control + Esc or click the Stop icon in the macOS menu bar]**

---

## 💡 Practical Presentation Tips

* **Speak clearly and steadily**: Don't rush; 5 minutes is plenty of time when following this structure.
* **Keep your browser tab ready**: Have `http://localhost:8000` already open in a tab next to your slides so switching windows takes only 1 second (`Cmd + Tab`).
* **Mouse cursor guidance**: When showing the live web app, hover your cursor over the prediction box and the SHAP contribution bars to guide the viewer's eyes.
* **File check**: After recording, preview your `.mov` / `.mp4` file to confirm audio is audible and clear before zipping for submission!
