import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from robot_arm import RobotArm

# --- 1. PRE-COMPUTATION PHASE ---
# (This is where you will plug in your SciPy and IK code)

# TODO: Use scipy.interpolate to generate a smooth array of (x, y) target points.
# target_x = [...] 
# target_y = [...]
num_frames = 100 # Example length of your trajectory

# TODO: Loop through your targets, pass them into your InverseKinematics solver, 
# and store the resulting angles in arrays.
# theta1_array = [...] 
# theta2_array = [...]

# For the skeleton, let's assume l1 and l2 are defined
l1 = 5.0
l2 = 4.0


# --- 2. PLOT SETUP PHASE ---
# Create the figure and the axis
fig, ax = plt.subplots()

# Set the limits of the whiteboard (adjust these based on your arm length!)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect('equal') # Keeps the aspect ratio 1:1 so circles don't look like ovals
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_title("Robot Arm Writing Simulation")

# Initialize the visual elements (they start empty)
# arm_line: Connects Origin -> Elbow -> Tip
arm_line, = ax.plot([], [], 'o-', lw=4, markersize=8, color='blue', label='Robot Arm')

# trace_line: The "ink" left behind by the tip
trace_line, = ax.plot([], [], '-', lw=2, color='red', label='Pen Trace')

ax.legend()

# Arrays to store the history of the tip's (x, y) coordinates for drawing the trace
tip_history_x = []
tip_history_y = []


# --- 3. THE UPDATE LOOP ---
def update(frame):
    """
    This function is called automatically by FuncAnimation for every frame.
    'frame' is just an integer index (0, 1, 2, ..., num_frames - 1).
    """
    
    # 1. Grab the angles for this specific frame
    # t1 = theta1_array[frame]
    # t2 = theta2_array[frame]
    
    # (Placeholder math for the skeleton so it doesn't crash)
    t1 = np.sin(frame * 0.1) 
    t2 = np.cos(frame * 0.1)

    # 2. Calculate the joint positions using Forward Kinematics
    # Origin is always at (0, 0)
    elbow_x = l1 * np.cos(t1)
    elbow_y = l1 * np.sin(t1)
    
    tip_x = elbow_x + l2 * np.cos(t1 + t2)
    tip_y = elbow_y + l2 * np.sin(t1 + t2)
    
    # 3. Update the arm's visual line (passing the 3 X coords, then the 3 Y coords)
    arm_line.set_data([0, elbow_x, tip_x], [0, elbow_y, tip_y])
    
    # 4. Update the pen trace
    tip_history_x.append(tip_x)
    tip_history_y.append(tip_y)
    trace_line.set_data(tip_history_x, tip_history_y)
    
    # Return the graphical elements that have changed
    return arm_line, trace_line

# --- 4. RUN THE ANIMATION ---
# interval=50 means 50 milliseconds per frame (20 frames per second)
# blit=True optimizes rendering by only redrawing the moving parts
ani = animation.FuncAnimation(
    fig, 
    update, 
    frames=num_frames, 
    interval=50, 
    blit=True
)

# Show the interactive plot!
plt.show()
