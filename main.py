import numpy as np
TOLERANCE = 0.00001

class RobotArm:

    def __init__(self, l1, l2):
        self.l1 = l1
        self.l2 = l2


    def jacobian(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute the Jacobian of the robot arm kinematics.

        Input: 
            theta: 1x2 vector,       the angles of the two joints of the robot
        Returns: 
            J: 2x2 matrix,           jacobian matrix of kinematics of arm
        """
        t1, t2 = theta

        J = np.array([
            [-self.l1 * np.sin(t1) - self.l2 * np.sin(t1 + t2), -self.l2 * np.sin(t1 + t2)],
            [self.l1 * np.cos(t1) + self.l2 * np.cos(t1 + t2), self.l2 * np.cos(t1 + t2)]
            ])

        return J

    def forward_k(self, theta: np.ndarray) -> np.ndarray:
        """
        Compute the forward kinematics of the robot arm given theta.

        Input:
            theta: 1x2 vector,      the angles of the joints of the robot
        Returns:
            p: 1x2 vector,          the end position (x,y) of the tip of robot
        """
        t1, t2 = theta

        x = self.l1 * np.cos(t1) + self.l2 * np.cos(t1 + t2)
        y = self.l1 * np.sin(t1) + self.l2 * np.sin(t1 + t2)
        return np.array([x, y])


    def inverse_k(self, target: np.ndarray, guess: np.ndarray) -> np.ndarray:
        """
        Solve the inverse kinematics of the robot arm using Newtons Method. Start
        with a target position (x,y) and initial guess theta (t1, t2). Then using
        Newton's method, find candidate positions (x,y) until they are within the
        tolerance TOLERANCE.
        
        Input:
            target: 1x2 vector,     position vector you want to find theta for
            guess: 1x2,             initial guess of angles theta

        Returns:
            theta: 1x2,             theta angles (t1, t2) that generate target
                                    position within tolerance
        """

        # Initial guess of angles theta.
        theta = guess.astype(float)

        # Get our (x,y) from initial theta then difference the target.
        # This is our F function, for which we will find the roots.
        F = self.forward_k(theta) - target

        # Check if our guess is close enough to target, "closeness" in this 
        # context is 2D norm, or euclidean distance.
        while np.linalg.norm(F) > TOLERANCE:

            # Compute Jacobian pesudo-inverse for our guess.
            J = self.jacobian(theta)
            J_pinv = np.linalg.pinv(J)

            # Update theta according to Newton Method in 2D.
            theta = theta - (J_pinv @ F)

            # Recompute the error.
            F = self.forward_k(theta) - target

        return theta
