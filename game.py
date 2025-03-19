import pygame
import math
import time
import numpy as np
from scipy.signal import butter, filtfilt

# 🎮 Initialize game
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG-Controlled Ball Simulation")

# 🎨 Fonts for Display
pygame.font.init()
font = pygame.font.SysFont("Arial", 24, bold=True)

# ⚽ Circle and Ball properties
CENTER = (WIDTH // 2, HEIGHT // 2)  
RADIUS = 200  
ball_radius = 15  
ball_angle = math.pi / 2  
initial_speed = 0.01  
boosted_speed = initial_speed * 3  

ball_speed = 0  
ball_direction = 1  

# 🚀 Speed boost tracking
boost_active = False  
boost_start_time = None  
cooldown_active = False  
cooldown_start_time = None  

# 🛑 Blink Stop Tracking
blink_active = False  
blink_start_time = None  

# 📝 Display Tracking Variables
display_speed = initial_speed  
display_status = "Normal"  

# 🎛 **Apply High-Pass Filter (1 Hz)**
def highpass_filter(data, cutoff=1, fs=250, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return filtfilt(b, a, data, axis=1)

# 🔍 Load EEG Data
eeg_data = np.load("data/misc/eeg_run-1.npy")
filtered_eeg = highpass_filter(eeg_data)  # **Apply high-pass filtering**

fs = 250  
sample_interval = 1 / fs  # **✅ FIX: Define `sample_interval` before using it**
start_idx = fs * 5  # Ignore first 5 seconds
filtered_data = filtered_eeg[:, start_idx:]  # Use only from 5s onward
num_samples = filtered_data.shape[1]  # Update num_samples to match new data size

# 🎯 New EEG Thresholds (from computed values)
MOVEMENT_THRESHOLD = 2.61
BLINK_THRESHOLD = 142.49
FOCUS_THRESHOLD = 44.84

# 🎮 Main Game Loop
running = True
sample_idx = 0  

while running:
    pygame.time.delay(int(sample_interval * 1000))  # **✅ FIX: Now sample_interval is defined**
    screen.fill((255, 255, 255))  

    # 🏀 Draw Circle Border
    pygame.draw.circle(screen, (0, 0, 0), CENTER, RADIUS, 2)

    # 🧠 Get EEG data for the current time step (after filtering)
    left_brain_activity = np.abs(filtered_data[0, sample_idx])  # C3 (Left Brain)
    right_brain_activity = np.abs(filtered_data[1, sample_idx])  # C4 (Right Brain)
    blink_signal = np.abs(filtered_data[2, sample_idx])  # Fp1 (Blink)
    focus_level = np.abs(filtered_data[4, sample_idx])  # Fz (Focus)

    current_time = time.time()

    # 🛑 Blink Detection (Stop for 3 Seconds)
    if blink_signal > BLINK_THRESHOLD and not blink_active:
        blink_active = True
        blink_start_time = current_time  
        ball_speed = 0
        boost_active = False  

    # If 3 seconds have passed, resume movement
    if blink_active and (current_time - blink_start_time >= 1):
        blink_active = False  
        ball_speed = initial_speed  

    # 🔄 Movement Detection (Only if ball is not stopped)
    if ball_speed == 0 and not blink_active:
        if left_brain_activity - right_brain_activity > MOVEMENT_THRESHOLD:
            ball_speed = initial_speed
            ball_direction = 1  
        elif right_brain_activity - left_brain_activity > MOVEMENT_THRESHOLD:
            ball_speed = initial_speed
            ball_direction = -1  

    # 🚀 Focus-Based Speed Boost (Lasts 3 sec, Cooldown for 5 sec)
    if focus_level > FOCUS_THRESHOLD and not boost_active and not cooldown_active and not blink_active:
        boost_active = True
        boost_start_time = current_time  
        ball_speed = boosted_speed  

    # Maintain boost for 3 sec, then reset speed
    if boost_active and (current_time - boost_start_time >= 3):
        ball_speed = initial_speed  
        boost_active = False
        cooldown_active = True
        cooldown_start_time = current_time  

    # Prevent re-boosting for 5 sec
    if cooldown_active and (current_time - cooldown_start_time >= 5):
        cooldown_active = False  
    
    new_status = "Stopped" if blink_active else "Accelerating" if boost_active else "Normal"

    # 🔄 Update Ball Position (Only move if not stopped)
    if ball_speed > 0 and not blink_active:
        ball_angle += ball_direction * ball_speed
        ball_angle %= 2 * math.pi  

    # 🎱 Calculate Ball Position
    ball_x = CENTER[0] + (RADIUS - ball_radius) * math.cos(ball_angle)
    ball_y = CENTER[1] + (RADIUS - ball_radius) * math.sin(ball_angle)

    # 🎱 Draw Ball
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)

    # 📝 Update Display Only When Speed/Status Changes
    new_status = "Accelerating" if boost_active else "Stopped" if blink_active else "Normal"
    new_speed = 0 if blink_active else (boosted_speed if boost_active else initial_speed)

    if new_speed != display_speed or new_status != display_status:
        display_speed = new_speed
        display_status = new_status

    # 📝 Render Speed and Status Text
    speed_text = font.render(f"Speed: {display_speed:.3f}", True, (0, 0, 0))
    status_text = font.render(f"Status: {display_status}", True, (0, 0, 0))

    screen.blit(speed_text, (20, 20))  
    screen.blit(status_text, (20, 50))  

    pygame.display.update()

    # 🔥 Quit condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 📌 Move to the next EEG sample, but loop back if we reach the end
    sample_idx += 1
    if sample_idx >= num_samples:
        sample_idx = 0  # **Ensure looping back correctly!**

    # Print debug info every 250 samples (1-second intervals)
    if sample_idx % 250 == 0:
        print(f"Sample: {sample_idx}/{num_samples} | Ball Speed: {ball_speed:.3f} | Ball Dir: {ball_direction}")
        print(f"EEG: L={left_brain_activity:.2f}, R={right_brain_activity:.2f}, Blink={blink_signal:.2f}, Focus={focus_level:.2f}")
        print(f"Boost Active: {boost_active}, Cooldown Active: {cooldown_active}, Blink Active: {blink_active}")

pygame.quit()
