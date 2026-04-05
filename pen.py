
import numpy as np
from matplotlib.textpath import TextPath
from matplotlib.path import Path
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, interp1d

class Pen:
    def __init__(self) -> None:
        pass

    @staticmethod
    def generate_text_targets(text, start_x=0, start_y=0, scale=1.0):
        """
        Generate target points (x,y) for the text given. The function generates 
        the letters in a default sans-serif font. No interpolation is used, as
        the points are generated from the font files themselves.

        Input:
            text: string,           the string of text to write out
            start_x: int,           the x pos of the start of text
            start_y: int,           the y pos of the start of text
            scale: float,           the scale of the text

        Returns:
            (x, y): tuple,          list of target points describing the text
            
        """
        # Create the text path (Matplotlib handles finding a default sans-serif font)
        # size=1 keeps the letters roughly 1 unit tall
        tp = TextPath((start_x, start_y), text, size=1)

        vertices = tp.vertices * scale
        codes = tp.codes

        target_x = []
        target_y = []

        # Loop sequentially through the font's instructions
        for i in range(len(vertices)):
            x, y = vertices[i]

            # Path.MOVETO is Matplotlib's "Pen Up" command
            if codes[i] == Path.MOVETO:
                # 1. Lift the pen (insert NaN)
                if len(target_x) > 0: # Don't insert NaN before the very first point
                    target_x.append(np.nan)
                    target_y.append(np.nan)

                # 2. Move to the new starting coordinate
                target_x.append(x)
                target_y.append(y)

            # Path.LINETO or Path.CURVE
            else:
                # Just keep drawing!
                target_x.append(x)
                target_y.append(y)
        return np.array(target_x), np.array(target_y)



def dynamic_linear_interpolation(text, start_x=0, start_y=0, scale=1.0, density=5.0):
    """
    Interpolate a text target using a linear interpolation.

    Input:
        text: string,                   the string you want to interpolate
        start_x, int                    starting x co-ord of interpolation
        stary_y: int,                   starting y co-ord of interpolation
        scale: float,                   scale or amplitude of finished interpolation
        density: float,                 amount of pts per unit

    Returns
        x, y: np.ndarray,               points representing interpolated string
    """
    return _generate_dense_points(text, 
                                 _dynamic_linear_interp, 
                                 start_x=start_x,
                                 start_y=start_y,
                                 scale=scale,
                                 density=density)

def dynamic_spline_interpolation(text, start_x=0, start_y=0, scale=1.0, density=5.0):
    """
    Interpolate a text target using a spline interpolation. A spline is forced
    to fit all the points in a letter.

    Input:
        text: string,                   the string you want to interpolate
        start_x, int                    starting x co-ord of interpolation
        stary_y: int,                   starting y co-ord of interpolation
        scale: float,                   scale or amplitude of finished interpolation
        density: float,                 amount of pts per unit

    Returns
        x, y: np.ndarray,               points representing interpolated string
    """
    return _generate_dense_points(text, 
                                 _dynamic_spline_interp, 
                                 start_x=start_x,
                                 start_y=start_y,
                                 scale=scale,
                                 density=density)


def dynamic_bezier_interpolation(text, start_x=0, start_y=0, scale=1.0, density=5.0):
    """
    Interpolate a text target using Bezier curves.

    Input:
        text: string,                   the string you want to interpolate
        start_x, int                    starting x co-ord of interpolation
        stary_y: int,                   starting y co-ord of interpolation
        scale: float,                   scale or amplitude of finished interpolation
        density: float,                 amount of pts per unit

    Returns
        x, y: np.ndarray,               points representing interpolated string
    """
    raw_path = TextPath((start_x, start_y), text, size=1)
    vertices = raw_path.vertices * scale
    codes = raw_path.codes
    
    target_x, target_y = [], []
    current_pos = vertices[0]
    i = 0
    
    while i < len(codes):
        code = codes[i]
        
        if code == Path.MOVETO:
            if len(target_x) > 0:
                target_x.append(np.nan)
                target_y.append(np.nan)
            current_pos = vertices[i]
            target_x.append(current_pos[0])
            target_y.append(current_pos[1])
            i += 1
            
        elif code == Path.LINETO:
            p1 = vertices[i]
            
            # 1. Calculate length using standard Euclidean distance (2-norm)
            length = np.linalg.norm(p1 - current_pos)
            
            # 2. Dynamically calculate steps (minimum of 2 to ensure start and end points exist)
            steps = max(2, int(length * density))
            t_array = np.linspace(0, 1, steps)[:, np.newaxis]
            
            pts = bezier_linear(current_pos, p1, t_array)
            target_x.extend(pts[:, 0])
            target_y.extend(pts[:, 1])
            
            current_pos = p1
            i += 1
            
        elif code == Path.CURVE3:
            p1, p2 = vertices[i], vertices[i+1]
            
            # Approximate length using the control polygon
            length = np.linalg.norm(p1 - current_pos) + np.linalg.norm(p2 - p1)
            steps = max(3, int(length * density))
            t_array = np.linspace(0, 1, steps)[:, np.newaxis]
            
            pts = bezier_quad(current_pos, p1, p2, t_array)
            target_x.extend(pts[:, 0])
            target_y.extend(pts[:, 1])
            
            current_pos = p2
            i += 2
            
        elif code == Path.CURVE4:
            p1, p2, p3 = vertices[i], vertices[i+1], vertices[i+2]
            
            # Approximate length using the control polygon
            length = (np.linalg.norm(p1 - current_pos) + 
                      np.linalg.norm(p2 - p1) + 
                      np.linalg.norm(p3 - p2))
            
            steps = max(4, int(length * density))
            t_array = np.linspace(0, 1, steps)[:, np.newaxis]
            
            pts = bezier_cubic(current_pos, p1, p2, p3, t_array)
            target_x.extend(pts[:, 0])
            target_y.extend(pts[:, 1])
            
            current_pos = p3
            i += 3
            
        else:
            i += 1
            
    return np.array(target_x), np.array(target_y)

def dynamic_piece_polynomial_interpolation(text, start_x=0, start_y=0, scale=1.0, density=5.0):
    """
    Interpolate a text target using a Piecewise Polynomial Curve strategy. For
    straight lines, use a line to interpolate. When a CURVE3 command is seen in
    the text target, using a quadratic to interpolate. When a CURVE4 is seen,
    use a cubic to interpolate.

    Input:
        text: string,                   the string you want to interpolate
        start_x, int                    starting x co-ord of interpolation
        stary_y: int,                   starting y co-ord of interpolation
        scale: float,                   scale or amplitude of finished interpolation
        density: float,                 amount of pts per unit

    Returns
        x, y: np.ndarray,               points representing interpolated string
    """
    raw_path = TextPath((start_x, start_y), text, size=1)
    vertices = raw_path.vertices * scale
    codes = raw_path.codes
    
    target_x, target_y = [], []
    current_pos = vertices[0]
    i = 0
    
    while i < len(codes):
        code = codes[i]
        
        if code == Path.MOVETO:
            if len(target_x) > 0:
                target_x.append(np.nan)
                target_y.append(np.nan)
            current_pos = vertices[i]
            target_x.append(current_pos[0])
            target_y.append(current_pos[1])
            i += 1
            
        elif code == Path.LINETO:
            p1 = vertices[i]
            length = np.linalg.norm(p1 - current_pos)
            steps = max(2, int(length * density))
            
            pts = np.array([current_pos, p1])
            t = np.linspace(0, 1, 2)
            t_dense = np.linspace(0, 1, steps)
            
            fx = interp1d(t, pts[:, 0], kind='linear')
            fy = interp1d(t, pts[:, 1], kind='linear')
            
            target_x.extend(fx(t_dense))
            target_y.extend(fy(t_dense))
            
            current_pos = p1
            i += 1
            
        elif code == Path.CURVE3:
            p1, p2 = vertices[i], vertices[i+1]
            length = np.linalg.norm(p1 - current_pos) + np.linalg.norm(p2 - p1)
            steps = max(3, int(length * density))
            
            pts = np.array([current_pos, p1, p2])
            t = np.linspace(0, 1, 3)
            t_dense = np.linspace(0, 1, steps)
            
            fx = interp1d(t, pts[:, 0], kind='quadratic')
            fy = interp1d(t, pts[:, 1], kind='quadratic')
            
            target_x.extend(fx(t_dense))
            target_y.extend(fy(t_dense))
            
            current_pos = p2
            i += 2
            
        elif code == Path.CURVE4:
            p1, p2, p3 = vertices[i], vertices[i+1], vertices[i+2]
            length = (np.linalg.norm(p1 - current_pos) + 
                      np.linalg.norm(p2 - p1) + 
                      np.linalg.norm(p3 - p2))
            steps = max(4, int(length * density))
            
            pts = np.array([current_pos, p1, p2, p3])
            t = np.linspace(0, 1, 4)
            t_dense = np.linspace(0, 1, steps)
            
            fx = interp1d(t, pts[:, 0], kind='cubic')
            fy = interp1d(t, pts[:, 1], kind='cubic')
            
            target_x.extend(fx(t_dense))
            target_y.extend(fy(t_dense))
            
            current_pos = p3
            i += 3
            
        else:
            i += 1
            
    return np.array(target_x), np.array(target_y)

def bezier_linear(p0, p1, t): 
    return (1-t)*p0 + t*p1
def bezier_quad(p0, p1, p2, t): 
    return (1-t)**2*p0 + 2*(1-t)*t*p1 + t**2*p2
def bezier_cubic(p0, p1, p2, p3, t): 
    return (1-t)**3*p0 + 3*(1-t)**2*t*p1 + 3*(1-t)*t**2*p2 + t**3*p3


# -------------------------- HELPER FUNCTIONS ---------------------------------

def get_chord_parameterization(vertices):
    """
    Returns the normalized physical parameter 'u' (0.0 to 1.0) based on actual distance,
    and the total length of the stroke.
    """
    if len(vertices) < 2:
        return np.zeros(len(vertices)), 0
        
    # Subtract consecutive points to get the physical vector between them
    diffs = np.diff(vertices, axis=0)
    
    # Calculate the physical length of each segment
    distances = np.linalg.norm(diffs, axis=1)
    
    # Calculate cumulative distance (starts at 0)
    # e.g., if segment lengths are [2, 3], cumulative is [0, 2, 5]
    cum_dist = np.insert(np.cumsum(distances), 0, 0)
    
    total_length = cum_dist[-1]
    
    if total_length == 0:
        return np.zeros(len(vertices)), 0
        
    # Normalize from [0, total_length] to [0.0, 1.0]
    u = cum_dist / total_length
    
    return u, total_length

# --- 2. The Corrected Dynamic Interpolators ---
def _dynamic_spline_interp(vertices, codes, density):
    # Get the physically accurate parameterization
    u, length = get_chord_parameterization(vertices)
    
    total_steps = max(len(vertices), int(length * density))
    u_dense = np.linspace(0, 1, total_steps)
    
    # Now the Spline knows exactly how far apart the control points actually are!
    cs_x = CubicSpline(u, vertices[:, 0])
    cs_y = CubicSpline(u, vertices[:, 1])
    
    return cs_x(u_dense), cs_y(u_dense)


def _dynamic_linear_interp(vertices, codes, density):
    u, length = get_chord_parameterization(vertices)
    
    total_steps = max(len(vertices), int(length * density))
    u_dense = np.linspace(0, 1, total_steps)
    
    lin_x = interp1d(u, vertices[:, 0], kind='linear')
    lin_y = interp1d(u, vertices[:, 1], kind='linear')
    
    return lin_x(u_dense), lin_y(u_dense)

def _generate_dense_points(text, interp_func, start_x=0, start_y=0, scale=1.0, density=5.0):
    raw_path = TextPath((start_x, start_y), text, size=1)
    vertices = raw_path.vertices * scale
    codes = raw_path.codes
    
    target_x, target_y = [], []
    strokes = []
    current_stroke_verts, current_stroke_codes = [], []
    
    # --- 1. Parse the commands ---
    for i in range(len(codes)):
        if codes[i] == Path.MOVETO and len(current_stroke_verts) > 0:
            strokes.append((np.array(current_stroke_verts), current_stroke_codes))
            current_stroke_verts, current_stroke_codes = [], []
            
        if codes[i] == Path.CLOSEPOLY:
            if len(current_stroke_verts) > 0:
                current_stroke_verts.append(current_stroke_verts[0])
                current_stroke_codes.append(codes[i])
        else:
            current_stroke_verts.append(vertices[i])
            current_stroke_codes.append(codes[i])
            
    if len(current_stroke_verts) > 0:
        strokes.append((np.array(current_stroke_verts), current_stroke_codes))
        
    # --- 2. Process the Strokes ---
    for verts, cds in strokes:
        if len(verts) > 1: 
            
            # --- 3. THE FIX: Clean consecutive duplicates ---
            # We always keep the first point
            clean_verts = [verts[0]]
            clean_cds = [cds[0]]
            
            # Only keep subsequent points if they are physically different from the last one
            for j in range(1, len(verts)):
                # np.allclose checks if the two coordinates are essentially identical
                if not np.allclose(verts[j], clean_verts[-1]):
                    clean_verts.append(verts[j])
                    clean_cds.append(cds[j])
            
            clean_verts = np.array(clean_verts)
            
            # Only interpolate if we still have at least 2 unique points left
            if len(clean_verts) > 1:
                x_dense, y_dense = interp_func(clean_verts, clean_cds, density)
                target_x.extend(x_dense)
                target_y.extend(y_dense)
                
                # PEN UP between strokes
                target_x.append(np.nan)
                target_y.append(np.nan)
            
    return np.array(target_x), np.array(target_y)

scale = 4.0
density = 64.0
w = 8
h = 8
#
#
#    # --- Test the Dynamic Piecewise Output ---
#    x_dyn_poly, y_dyn_poly = piecewise_dynamic_interp("MAT264 Rocks!", scale=scale, density=density)
#
#    plt.figure(figsize=(w, h))
#    plt.title("Dynamic Piecewise Polynomial Interpolation", fontsize=14)
#    plt.scatter(x_dyn_poly, y_dyn_poly, color='purple', s=4, alpha=0.8)
#    plt.axis('equal')
#    plt.grid(True, linestyle='--', alpha=0.5)
#    plt.savefig('dynamic_piecewise_polynomial_mat264_rocks.png')
#
#x_bez, y_bez = dynamic_bezier_interpolation("MAT264 Rocks!", scale=scale, density=density)
x_vert, y_vert = dynamic_piece_polynomial_interpolation("R", scale=scale, density=density)
plt.figure(figsize=(w, h))
plt.title("Piecewise Polynomial Interpolation", fontsize=14)
plt.scatter(x_vert, y_vert, color='magenta', s=24, alpha=0.8)
plt.axis('equal')
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('poly_r.png')
#
#    x_spl, y_spl = generate_dense_points("MAT264 Rocks!", dynamic_spline_interp, scale=scale, density=density)
#    plt.figure(figsize=(w, h))
#    plt.title("Dynamic Spline Interpolation", fontsize=14)
#    plt.scatter(x_spl, y_spl, color='green', s=4, alpha=0.8)
#    plt.axis('equal')
#    plt.grid(True, linestyle='--', alpha=0.5)
#    plt.savefig('dynamic_spline_mat264_rocks.png')
#
#    x_lin, y_lin = generate_dense_points("MAT264 Rocks!", dynamic_linear_interp, scale=scale, density=density)
#    plt.figure(figsize=(w, h))
#    plt.title("Dynamic Linear Interpolation", fontsize=14)
#    plt.scatter(x_lin, y_lin, color='red', s=4, alpha=0.8)
#    plt.axis('equal')
#    plt.grid(True, linestyle='--', alpha=0.5)
#    plt.savefig('dynamic_linear_mat264_rocks.png')
#
