# 🍬 CandyBot – System Architecture & Materials

# 🧠 High-Level Architecture

The system is divided into three main subsystems:

1. **Sorting System (Input + Classification)**
2. **Storage & Dispensing System**
3. **User Interaction & Control System**

All subsystems are orchestrated by a central controller:
- :contentReference[oaicite:0]{index=0}

---

# 🔧 Hardware Components

## 🖥️ Core Controller
- Raspberry Pi 4 (4GB RAM)
- Responsibilities:
  - Image processing (camera input)
  - Decision making (color classification, stock tracking)
  - Motor control (via GPIO PWM)
  - Running user interface (web app or display)

---

## 📷 Vision System
- Camera Module:
  - Raspberry Pi Camera Module v2
- Purpose:
  - Capture images of individual Skittles
  - Detect color using software (e.g., OpenCV)

---

## ⚙️ Actuation System

### Servo Inventory
- 7 × :contentReference[oaicite:2]{index=2}
- 1 × Continuous rotation servo (360°)

---

# ⚙️ Subsystem Breakdown

---

## 🟡 1. Sorting System

### Components:
- 1 × Continuous rotation servo
- 1 × SG90 servo
- Camera module

### Functionality:

#### 🔄 Rotating Disk (Motor 1)
- Type: Continuous servo (360°)
- Purpose:
  - Rotate a horizontal platform
  - Feed Skittles one by one into the camera view

- Control:
  - Speed and direction only (no positional control)
  - Timing-based stopping or guided mechanical positioning required

---

#### 🎯 Directional Ramp (Motor 2)
- Type: SG90 servo
- Purpose:
  - Adjust ramp angle to route Skittles into the correct container

- Positions:
  - 5 discrete angles → 5 color outputs

Example mapping:
| Angle | Color |
|------|------|
| 0°   | Red |
| 30°  | Green |
| 60°  | Yellow |
| 90°  | Orange |
| 120° | Purple |

---

#### 📷 Color Detection Flow
1. Disk rotates → Skittle reaches camera zone
2. System pauses movement
3. Camera captures image
4. Software classifies color
5. Ramp moves to correct position
6. Skittle is released into storage

---

## 🏪 2. Storage & Dispensing System

### Structure:
- 5 vertical cylinders (one per color)

---

### 🔴 Dispenser Motors (Motors 3–7)
- Type: 5 × SG90 servos
- One per cylinder

#### Function:
- Release Skittles individually from storage

#### Mechanism Options:
- Rotating wheel with cavities (recommended)
- Flap/gate system
- Mini screw conveyor

#### Requirement:
- Must ensure **1 Skittle per activation**
- Critical for accurate stock control

---

### 📦 Inventory Tracking

Maintained in software
