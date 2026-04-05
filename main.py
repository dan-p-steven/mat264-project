import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from robot_arm import RobotArm
from pen import dynamic_bezier_interpolation, dynamic_spline_interpolation, dynamic_linear_interpolation, dynamic_piece_polynomial_interpolation

animation_filename = 'thank_you.mp4'
plot_title = 'Thank You'
# --- 1. PRE-COMPUTATION PHASE ---
# Setup the arm parameters
l1 = 6.0
l2 = 6.0
arm = RobotArm(l1, l2)

# Generate targets using our optimized Bezier approximation
# (Positioned at x=-6, y=3 to fit nicely in the arm's reach)
print("Generating target coordinates...")
target_x, target_y = dynamic_spline_interpolation("Thank You!", start_x=-4, start_y=1, scale=2.5, density=10.0)
num_frames = len(target_x)

theta1_array = []
theta2_array = []

# Initial guess for the Newton Solver (pointing generally up and left)
current_guess = np.array([np.pi/2, 0.0]) 

print(f"Solving Inverse Kinematics sequentially for {num_frames} points...")
for i in range(num_frames):
    tx = target_x[i]
    ty = target_y[i]
    
    # Handle "Pen Up" (NaN values) gracefully
    if np.isnan(tx) or np.isnan(ty):
        theta1_array.append(np.nan)
        theta2_array.append(np.nan)
        # We leave the guess as-is, so the arm remembers its posture for the next stroke
        continue
        
    target_pt = np.array([tx, ty])
    
    print(f"\rSolving point {i + 1}/{num_frames}", end="", flush=True)
    # Solve IK for this specific target
    theta_sol = arm.inverse_k(target_pt, current_guess)
    
    theta1_array.append(theta_sol[0])
    theta2_array.append(theta_sol[1])
    
    # CRUCIAL: Feed the solved angle as the guess for the NEXT point!
    current_guess = theta_sol

print("Calculations complete! Launching animation...")

# --- 2. PLOT SETUP PHASE ---
fig, ax = plt.subplots(figsize=(8, 8))

# Set limits based on max reach (l1 + l2 = 9.0)
ax.set_xlim(-12, 12)
ax.set_ylim(-3, 6)
ax.set_aspect('equal')
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_title(plot_title)

#$ax.plot(target_x, target_y, color='lightgray', lw=3, label='Target Path (Desired)')

# Initialize visual elements
arm_line, = ax.plot([], [], 'o-', lw=5, markersize=8, color='#2c3e50', label='Robot Arm')
trace_line, = ax.plot([], [], '-', lw=2, color='#e74c3c', label='Pen Trace')

tip_history_x = []
tip_history_y = []

# --- 3. THE UPDATE LOOP ---
def update(frame):
    t1 = theta1_array[frame]
    t2 = theta2_array[frame]
    
    # If we hit a NaN, the pen is lifted.
    if np.isnan(t1) or np.isnan(t2):
        tip_history_x.append(np.nan)
        tip_history_y.append(np.nan)
        trace_line.set_data(tip_history_x, tip_history_y)
        
        # Hide the arm for this single frame to simulate lifting
        arm_line.set_data([np.nan], [np.nan])
        return arm_line, trace_line

    # Forward Kinematics to find the joint positions for drawing
    elbow_x = l1 * np.cos(t1)
    elbow_y = l1 * np.sin(t1)
    
    tip_x = elbow_x + l2 * np.cos(t1 + t2)
    tip_y = elbow_y + l2 * np.sin(t1 + t2)
    
    # Update the arm visualization
    arm_line.set_data([0, elbow_x, tip_x], [0, elbow_y, tip_y])
    
    # Update the ink trace
    tip_history_x.append(tip_x)
    tip_history_y.append(tip_y)
    trace_line.set_data(tip_history_x, tip_history_y)
    
    return arm_line, trace_line

# --- 4. RUN THE ANIMATION ---
ani = animation.FuncAnimation(
    fig, 
    update, 
    frames=num_frames, 
    interval=20, # Reduced to 20ms for a smoother, faster drawing speed
    blit=True
)

# Save the animation as an MP4 for PowerPoint
print("Saving animation to MP4... (This might take a minute)")
ani.save(animation_filename, writer='ffmpeg', fps=30, dpi=200)
print("Save complete!")
