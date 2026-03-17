# Repo for the MAT264 Group Project

A.6 Robot Arm Calligraphy
A planar robot arm with two rigid segments of lengths l1 and l2 can move in the plane
by rotating two joints with angles θ1 and θ2. The position of the end-effector (the tip of
the robot arm) is given by
x = l1 cos θ1 + l2 cos(θ1 + θ2), y = l1 sin θ1 + l2 sin(θ1 + θ2).
Given a target point (x, y), the robot must determine the joint angles (θ1, θ2) that place
the end-effector at that location. This problem is known as inverse kinematics. Since the
equations are nonlinear, numerical methods are required to compute the angles.
Mission
1. Implement the forward kinematics equations that map (θ1, θ2) to the position (x, y)
of the robot arm.
2. Given a target point (x, y), formulate the inverse kinematics problem as a nonlinear
system and solve it using Newton’s method.
3. Choose several points that trace a curve representing “MAT 264 ROCKS”. Use
interpolation (for example piecewise linear interpolation or spline interpolation) to
generate a smooth sequence of points along the curve.
4. For each point on the curve, compute the corresponding joint angles (θ1, θ2) using
your numerical solver.
5. Simulate the motion of the robot arm and visualize the trajectory of the end-effector.
Verify that the robot arm traces the intended curve.
6. Create a simple animation showing the robot arm moving and writing the curve.
