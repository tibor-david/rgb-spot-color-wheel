from PIL import Image, ImageDraw
import math
from typing import Any


def hsv_to_rgb(h, s, v) -> Any:
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def create_color_wheel(size):
    larger_size = size * 2  # Create a larger image for anti-aliasing
    image = Image.new(
        "RGBA", (larger_size, larger_size), (0, 0, 0, 0)
    )
    draw = ImageDraw.Draw(image)
    radius = larger_size // 2
    center = (radius, radius)

    for y in range(larger_size):
        for x in range(larger_size):
            dx = x - center[0]
            dy = y - center[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance <= radius:
                angle = math.atan2(dy, dx)
                hue = (angle + math.pi) / (2 * math.pi)
                saturation = distance / radius
                r, g, b = hsv_to_rgb(hue, saturation, 1)
                draw.point((x, y), (int(r * 255), int(g * 255), int(b * 255)))
            else:
                draw.point((x, y), (0, 0, 0, 0))

    image = image.resize(
        (size, size), Image.Resampling.LANCZOS
    )
    return image


if __name__ == "__main__":
    size = 250  # Size of the image
    color_wheel_image = create_color_wheel(size)
    color_wheel_image.save("color_wheel.png")
