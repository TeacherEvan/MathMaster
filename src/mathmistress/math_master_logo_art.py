import math
import tkinter as tk

def draw_algebra_logo(canvas, center_x, center_y, base_size, get_hex_with_alpha_func):
    """
    Draws a stylized 'Math Master Algebra' logo using X, Y, and =.
    Includes Roman numeral X, internal shading for Y, and a laurel wreath.

    Args:
        canvas: The Tkinter canvas object.
        center_x: The x-coordinate for the center of the logo.
        center_y: The y-coordinate for the center of the logo.
        base_size: A general size factor for the logo.
        get_hex_with_alpha_func: A function to convert hex color and alpha to a Tkinter-compatible color string.
    """

    # --- Colors ---
    matrix_green_bright = "#00FF00"
    matrix_green_medium = "#00DD00"
    matrix_green_dark = "#00AA00"
    gold_bright = "#FFD700"
    gold_medium = "#FFA500"
    gold_dark = "#CC8400" # For Y shading
    dark_shadow_bg = "#003300"
    black = "#000000"
    grey = "#888888"
    x_fill_alpha = 0.7 # Transparency for X

    # --- Helper for scaling ---
    def s(value):
        return value * base_size / 100

    # --- Background Elements (Energy Field / Shield) ---
    num_bg_circles = 3
    for i in range(num_bg_circles, 0, -1):
        radius = s(60 + i * 15)
        alpha = 0.05 + (i / num_bg_circles) * 0.1
        stipple_pattern = 'gray25' if i % 2 == 0 else 'gray12'
        canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=matrix_green_medium,
            width=s(1.5),
            fill=get_hex_with_alpha_func(dark_shadow_bg, alpha * 0.5),
            stipple=stipple_pattern,
            tags="logo_bg_circle"
        )

    # --- Stylized 'Y' with Internal Shading ---
    y_stem_width = s(12)
    y_arm_width = s(10)
    y_height = s(70)
    y_arm_length = s(45)
    y_arm_angle = math.radians(30)
    y_shading_offset = s(2)

    # Shadow for Y stem (outer shadow)
    canvas.create_line(
        center_x + s(2), center_y - y_height / 2 + s(2),
        center_x + s(2), center_y + y_height / 3 + s(2),
        fill=get_hex_with_alpha_func(black, 0.4),
        width=y_stem_width,
        capstyle=tk.ROUND,
        tags="logo_y_outer_shadow"
    )
    # Main Y Stem (brightest part)
    canvas.create_line(
        center_x, center_y - y_height / 2,
        center_x, center_y + y_height / 3,
        fill=gold_bright,
        width=y_stem_width,
        capstyle=tk.ROUND,
        tags="logo_y_stem_main"
    )
    # Internal shading for Y Stem
    canvas.create_line(
        center_x + y_shading_offset / 2, center_y - y_height / 2 + y_shading_offset,
        center_x + y_shading_offset / 2, center_y + y_height / 3 - y_shading_offset / 2,
        fill=gold_dark, 
        width=y_stem_width - y_shading_offset * 1.5, # Thinner shading line
        capstyle=tk.ROUND,
        tags="logo_y_stem_shade"
    )
    canvas.tag_lower("logo_y_outer_shadow", "logo_y_stem_main")

    y_arm_start_y = center_y - y_height / 4
    # Left Arm of Y (Main)
    lx_end = center_x - y_arm_length * math.sin(y_arm_angle)
    ly_end = y_arm_start_y - y_arm_length * math.cos(y_arm_angle)
    canvas.create_line(center_x, y_arm_start_y, lx_end, ly_end, fill=gold_medium, width=y_arm_width, capstyle=tk.ROUND, tags="logo_y_arm_left_main")
    # Left Arm Shading
    canvas.create_line(
        center_x + y_shading_offset * math.cos(math.radians(135)), y_arm_start_y + y_shading_offset * math.sin(math.radians(135)),
        lx_end + y_shading_offset * math.cos(math.radians(135)), ly_end + y_shading_offset * math.sin(math.radians(135)),
        fill=gold_dark, width=y_arm_width - y_shading_offset * 1.5, capstyle=tk.ROUND, tags="logo_y_arm_left_shade"
    )

    # Right Arm of Y (Main)
    rx_end = center_x + y_arm_length * math.sin(y_arm_angle)
    ry_end = y_arm_start_y - y_arm_length * math.cos(y_arm_angle)
    canvas.create_line(center_x, y_arm_start_y, rx_end, ry_end, fill=gold_medium, width=y_arm_width, capstyle=tk.ROUND, tags="logo_y_arm_right_main")
    # Right Arm Shading
    canvas.create_line(
        center_x + y_shading_offset * math.cos(math.radians(45)), y_arm_start_y + y_shading_offset * math.sin(math.radians(45)),
        rx_end + y_shading_offset * math.cos(math.radians(45)), ry_end + y_shading_offset * math.sin(math.radians(45)),
        fill=gold_dark, width=y_arm_width - y_shading_offset * 1.5, capstyle=tk.ROUND, tags="logo_y_arm_right_shade"
    )

    # --- Roman Numeral 'X' (Slightly Transparent) ---
    x_stroke_thickness = s(10) # Thickness of each bar of the X
    x_bar_length = s(45)    # Length of one bar from center to tip
    x_half_width_at_tip = s(8) # Gives it a slightly flared/serif look
    x_color = get_hex_with_alpha_func(matrix_green_bright, x_fill_alpha)

    # Define 4 points for each of the 4 bars of X, meeting at center_x, center_y
    # Top-left bar
    p_tl1 = (center_x - x_half_width_at_tip, center_y - x_bar_length)
    p_tl2 = (center_x + x_half_width_at_tip, center_y - x_bar_length)
    # Top-right bar
    p_tr1 = (center_x + x_bar_length, center_y - x_half_width_at_tip)
    p_tr2 = (center_x + x_bar_length, center_y + x_half_width_at_tip)
    # Bottom-left bar
    p_bl1 = (center_x - x_bar_length, center_y + x_half_width_at_tip)
    p_bl2 = (center_x - x_bar_length, center_y - x_half_width_at_tip)
    # Bottom-right bar
    p_br1 = (center_x + x_half_width_at_tip, center_y + x_bar_length)
    p_br2 = (center_x - x_half_width_at_tip, center_y + x_bar_length)

    # Central meeting point (slightly adjusted for thickness)
    cx_adj, cy_adj = center_x, center_y

    # Create the 4 polygons for the X
    # Top-left to center, center to bottom-right (diagonal 1)
    canvas.create_polygon(p_tl1, p_tl2, (cx_adj + s(1), cy_adj - s(1)), (cx_adj - s(1), cy_adj + s(1)), fill=x_color, outline=matrix_green_medium, width=s(1), tags="logo_x_roman")
    canvas.create_polygon(p_br1, p_br2, (cx_adj - s(1), cy_adj + s(1)), (cx_adj + s(1), cy_adj - s(1)), fill=x_color, outline=matrix_green_medium, width=s(1), tags="logo_x_roman")
    # Top-right to center, center to bottom-left (diagonal 2)
    canvas.create_polygon(p_tr1, p_tr2, (cx_adj + s(1), cy_adj + s(1)), (cx_adj - s(1), cy_adj - s(1)), fill=x_color, outline=matrix_green_medium, width=s(1), tags="logo_x_roman")
    canvas.create_polygon(p_bl1, p_bl2, (cx_adj - s(1), cy_adj - s(1)), (cx_adj + s(1), cy_adj + s(1)), fill=x_color, outline=matrix_green_medium, width=s(1), tags="logo_x_roman")

    # Ensure Y elements are on top of X strokes
    canvas.tag_raise("logo_y_stem_main")
    canvas.tag_raise("logo_y_stem_shade")
    canvas.tag_raise("logo_y_arm_left_main")
    canvas.tag_raise("logo_y_arm_left_shade")
    canvas.tag_raise("logo_y_arm_right_main")
    canvas.tag_raise("logo_y_arm_right_shade")

    # --- '=' Sign (Foundation) ---
    eq_width = s(60)
    eq_stroke_width = s(10)
    eq_spacing = s(15)
    eq_y_offset = y_height / 2.2 # Adjusted to sit well with new X and Y
    eq_y1 = center_y + eq_y_offset - eq_spacing / 2
    eq_y2 = center_y + eq_y_offset + eq_spacing / 2

    canvas.create_line(center_x - eq_width / 2 + s(2), eq_y1 + s(2), center_x + eq_width / 2 + s(2), eq_y1 + s(2), fill=get_hex_with_alpha_func(black, 0.4), width=eq_stroke_width, capstyle=tk.ROUND, tags="logo_eq_shadow")
    canvas.create_line(center_x - eq_width / 2 + s(2), eq_y2 + s(2), center_x + eq_width / 2 + s(2), eq_y2 + s(2), fill=get_hex_with_alpha_func(black, 0.4), width=eq_stroke_width, capstyle=tk.ROUND, tags="logo_eq_shadow")
    canvas.create_line(center_x - eq_width / 2, eq_y1, center_x + eq_width / 2, eq_y1, fill=grey, width=eq_stroke_width, capstyle=tk.ROUND, tags="logo_eq_top_bar")
    canvas.create_line(center_x - eq_width / 2, eq_y2, center_x + eq_width / 2, eq_y2, fill=grey, width=eq_stroke_width, capstyle=tk.ROUND, tags="logo_eq_bottom_bar")
    canvas.tag_lower("logo_eq_shadow", "logo_eq_top_bar")
    canvas.tag_lower("logo_eq_shadow", "logo_eq_bottom_bar")

    # --- Laurel Wreath (Greek Leafy Head Thingy) ---
    laurel_y_center = eq_y2 + s(35) # Position below the '=' sign
    laurel_radius_x = s(50)
    laurel_radius_y = s(25)
    num_leaves_per_side = 7
    leaf_length = s(15)
    leaf_width = s(6)
    leaf_color = matrix_green_dark

    for side in [-1, 1]: # -1 for left, 1 for right
        for i in range(num_leaves_per_side):
            angle_rad = (i / (num_leaves_per_side -1)) * (math.pi / 1.8) - (math.pi / 3.6) # Spread leaves over an arc
            
            # Calculate base of leaf on the elliptical path
            bx = center_x + side * laurel_radius_x * math.cos(angle_rad)
            by = laurel_y_center + laurel_radius_y * math.sin(angle_rad)
            
            # Tip of leaf (points outwards and slightly upwards/downwards depending on position)
            tip_angle_offset = math.pi / 2 if side == -1 else -math.pi / 2
            tx = bx + leaf_length * math.cos(angle_rad + side * math.pi / 6 + tip_angle_offset)
            ty = by + leaf_length * math.sin(angle_rad + side * math.pi / 6 + tip_angle_offset)

            # Control points for curve (making it leaf-like)
            # For simplicity, using a polygon for a basic leaf shape
            c1x = bx + (tx-bx)*0.3 - side * leaf_width * math.sin(angle_rad)
            c1y = by + (ty-by)*0.3 + side * leaf_width * math.cos(angle_rad)
            c2x = bx + (tx-bx)*0.7 + side * leaf_width * math.sin(angle_rad)
            c2y = by + (ty-by)*0.7 - side * leaf_width * math.cos(angle_rad)

            canvas.create_polygon(bx, by, c1x, c1y, tx, ty, c2x, c2y, 
                                  fill=leaf_color, 
                                  outline=get_hex_with_alpha_func(black, 0.3),
                                  smooth=True, 
                                  tags="logo_laurel_leaf")
    canvas.tag_lower("logo_laurel_leaf") # Ensure leaves are behind X,Y,=

    # --- Opposing Triangles (Static Implication of Rotation) ---
    tri_radius_outer = s(45)
    tri_radius_inner = s(38)
    tri_line_width = s(1.5)
    tri_color_outer = gold_medium
    tri_color_inner = matrix_green_medium

    # Outer triangle (pointing up, slightly rotated clockwise)
    angle_offset_outer = math.radians(5) 
    points_outer = []
    for i in range(3):
        angle = (math.pi / 2) + (i * 2 * math.pi / 3) + angle_offset_outer # Start pointing up
        points_outer.extend([
            center_x + tri_radius_outer * math.cos(angle),
            center_y + tri_radius_outer * math.sin(angle)
        ])
    canvas.create_polygon(points_outer, outline=tri_color_outer, fill="", width=tri_line_width, tags="logo_triangle_outer")

    # Inner triangle (pointing down, slightly rotated counter-clockwise)
    angle_offset_inner = math.radians(-5)
    points_inner = []
    for i in range(3):
        angle = (3 * math.pi / 2) + (i * 2 * math.pi / 3) + angle_offset_inner # Start pointing down
        points_inner.extend([
            center_x + tri_radius_inner * math.cos(angle),
            center_y + tri_radius_inner * math.sin(angle)
        ])
    canvas.create_polygon(points_inner, outline=tri_color_inner, fill="", width=tri_line_width, tags="logo_triangle_inner")

    # Ensure triangles are behind the main X, Y, = but above background circles
    canvas.tag_lower("logo_triangle_outer", "logo_x_roman")
    canvas.tag_lower("logo_triangle_inner", "logo_x_roman")
    canvas.tag_raise("logo_triangle_outer", "logo_bg_circle")
    canvas.tag_raise("logo_triangle_inner", "logo_bg_circle")

    # Highlights for Y arms (ensure they are on top of everything else)
    highlight_radius = s(3)
    canvas.create_oval(lx_end - highlight_radius, ly_end - highlight_radius, lx_end + highlight_radius, ly_end + highlight_radius, fill=get_hex_with_alpha_func(gold_bright, 0.9), outline="", tags="logo_highlight_y_left")
    canvas.create_oval(rx_end - highlight_radius, ry_end - highlight_radius, rx_end + highlight_radius, ry_end + highlight_radius, fill=get_hex_with_alpha_func(gold_bright, 0.9), outline="", tags="logo_highlight_y_right")
    canvas.tag_raise("logo_highlight_y_left")
    canvas.tag_raise("logo_highlight_y_right")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Logo Test V2")
    canvas_width = 450
    canvas_height = 550 # Increased height to see laurel
    test_canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#111111")
    test_canvas.pack()

    def _get_hex_with_alpha_dummy(hex_color, alpha):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r_final = int(r * alpha)
        g_final = int(g * alpha)
        b_final = int(b * alpha)
        return f"#{r_final:02x}{g_final:02x}{b_final:02x}"

    draw_algebra_logo(test_canvas, canvas_width / 2, canvas_height / 2 - 20, 100, _get_hex_with_alpha_dummy) 
    root.mainloop() 