import pygame
import math
import time
import numpy as np

# 🎮 Initialize game
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG-Controlled Ball Simulation")

# ⚽ Circle and Ball properties
CENTER = (WIDTH // 2, HEIGHT // 2)  
RADIUS = 200  
ball_radius = 15  
ball_angle = math.pi / 2  
initial_speed = 0.02  
boosted_speed = initial_speed * 2  
ball_speed = 0  
ball_direction = 0  

# 🚀 Speed boost tracking
boost_active = False  
boost_time = 0  

# 🛑 Inertia tracking
slowing_down = False  

# 🔍 Load EEG Data
eeg_data = np.load('data/misc/eeg_run-1.npy')
num_samples = eeg_data.shape[1]  
fs = 250  
sample_interval = 1 / fs  

# 📌 EEG Thresholds (Update these after visualization)
MOVEMENT_THRESHOLD = 15.5
BLINK_THRESHOLD = 100.0
FOCUS_THRESHOLD = 12.8

# 🎮 Main Game Loop
running = True
sample_idx = 0  

while running:
    pygame.time.delay(int(sample_interval * 1000))  
    screen.fill((255, 255, 255))  

    # 🏀 Draw Circle Border
    pygame.draw.circle(screen, (0, 0, 0), CENTER, RADIUS, 2)

    # 🧠 Get EEG data for the current time step
    left_brain_activity = np.mean(np.abs(eeg_data[0, sample_idx]))  
    right_brain_activity = np.mean(np.abs(eeg_data[1, sample_idx]))  
    blink_signal = np.max(np.abs(eeg_data[2, sample_idx]))  
    focus_level = np.mean(np.abs(eeg_data[4, sample_idx]))  

    # 🔄 Movement Detection (Based on EEG Data)
    if ball_speed == 0 and not slowing_down:
        if left_brain_activity - right_brain_activity > MOVEMENT_THRESHOLD:
            ball_speed = initial_speed
            ball_direction = 1  
        elif right_brain_activity - left_brain_activity > MOVEMENT_THRESHOLD:
            ball_speed = initial_speed
            ball_direction = -1  

    # ⏸️ Blink Detection (Stop Movement)
    if blink_signal > BLINK_THRESHOLD:
        slowing_down = True  

    # 🚀 Focus-Based Speed Boost
    current_time = time.time()
    if focus_level > FOCUS_THRESHOLD and not boost_active:
        ball_speed = boosted_speed
        boost_time = current_time
        boost_active = True

    # Reset speed after 5 sec
    if boost_active and (current_time - boost_time >= 5):
        ball_speed = initial_speed
        boost_active = False

    # 🛑 Apply Inertia (Decelerate until fully stopped)
    if slowing_down and ball_speed > 0:
        ball_speed -= 0.002  
        if ball_speed <= 0:
            ball_speed = 0  
            slowing_down = False  
            ball_direction = 0  

    # 🔄 Update Ball Position
    if ball_speed > 0:
        ball_angle += ball_direction * ball_speed
        ball_angle %= 2 * math.pi  

    # 🎱 Calculate Ball Position
    ball_x = CENTER[0] + (RADIUS - ball_radius) * math.cos(ball_angle)
    ball_y = CENTER[1] + (RADIUS - ball_radius) * math.sin(ball_angle)

    # 🎱 Draw Ball
    pygame.draw.circle(screen, (255, 0, 0), (int(ball_x), int(ball_y)), ball_radius)

    pygame.display.update()

    # 🔥 Quit condition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 📌 Move to the next EEG sample, but loop back if we reach the end
    sample_idx += 1
    if sample_idx >= num_samples:
        sample_idx = 0  

    # Print debug info every 250 samples (1-second intervals)
    if sample_idx % 250 == 0:
        print(f"Sample: {sample_idx}/{num_samples} | Ball Speed: {ball_speed:.3f} | Ball Dir: {ball_direction}")
        print(f"EEG: L={left_brain_activity:.2f}, R={right_brain_activity:.2f}, Blink={blink_signal:.2f}, Focus={focus_level:.2f}")

pygame.quit()
