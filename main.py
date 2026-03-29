import numpy as np
TOLERENCE = 0.00001

class InverseKinematics:

    def __init__(self, l1, l2):
        self.l1 = l1
        self.l2 = l2

# for jacobian
    #def _dx_dt1(self, t1, t2):
    #    return -self.l1 * np.sin(t1) - self.l2 * np.sin(t1 + t2)
    #
    #def _dx_dt2(self, t1, t2):
    #    return -self.l2 * np.sin(t1 + t2)
    #
    #def _dy_dt1(self, t1, t2):
    #    return self.l1 * np.cos(t1) + self.l2 * np.cos(t1 + t2)
    #
    #def _dy_dt2(self, t1, t2):
    #    return self.l2 * np.cos(t1 + t2)

    def forward_k(self, t1, t2):
        """
        input angles t1 and t2
        return x and y coordinates of the end effector
        """
        x = self.l1 * np.cos(t1) + self.l2 * np.cos(t1 + t2)
        y = self.l1 * np.sin(t1) + self.l2 * np.sin(t1 + t2)
        return x, y

    #def inverse_k(self, x, y, t1, t2) -> tuple(float, float):
    #    """
    #    input x and y coordinates of the end effector, initial guess of t1 and t2
    #    return angles t1 and t2
    #    """
    #    X_orig = np.array([x, y])

    #    t_new = np.array([t1, t2])
    #    x_n, y_n = self.forward_k(t_new[0], t_new[1])
    #    X_new = np.array([x_n, y_n])

    #    while np.linalg.norm(X_new - X_orig) > TOLERENCE: # use 2-norm

    #        # t1_n, t2_n
    #        t = t_new
    #        # x_n, y_n
    #        F_n = X_new
    #        # pseudo inverse jacobian
    #        J = np.array([[self._dx_dt1(t[0], t[1]), self._dx_dt2(t[0], t[1])], [self._dy_dt1(t[0], t[1]), self._dy_dt2(t[0], t[1])]])
    #        J_pinv = np.linalg.pinv(J)

    #        # update t1_n, t2_n
    #        t_new = t - np.linalg.matmul(J_pinv, F_n)
    #        # update x_n, y_n
    #        x_n, y_n = self.forward_k(t_new[0], t_new[1])
    #        X_new = np.array([x_n, y_n])
    #    return t_new[0], t_new[1]

        
