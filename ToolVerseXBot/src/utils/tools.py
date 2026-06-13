import random
import string
import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageColor
import os

def generate_advanced_password(seed, length=12, use_symbols=True, use_numbers=True, use_uppercase=True, style="memorable"):
    """
    Generates an advanced password based on a seed (keyword/name).
    - memorable: translates seed using leetspeak and adds random suffix padding if needed.
    - random: mixes seed letters with random uppercase, numbers, and symbols.
    """
    if style == "memorable":
        # Leetspeak translation table
        leet = {
            'a': '@', 'A': '@', 's': '$', 'S': '$', 'e': '3', 'E': '3',
            'o': '0', 'O': '0', 'i': '1', 'I': '1', 't': '7', 'T': '7',
            'g': '9', 'G': '9', 'b': '8', 'B': '8'
        }
        # Replace characters in seed
        base = "".join(leet.get(c, c) for c in seed)
        
        # Apply casing
        if use_uppercase:
            base = base.capitalize()
        else:
            base = base.lower()
            
        # Accumulate character pool for padding
        pool = string.ascii_lowercase
        if use_uppercase:
            pool += string.ascii_uppercase
        if use_numbers:
            pool += string.digits
        if use_symbols:
            pool += string.punctuation
            
        # If base is shorter than length, pad it
        if len(base) < length:
            padding_length = length - len(base)
            padding = []
            
            # Ensure we include at least one number/symbol in padding if requested and not in base
            if use_numbers and not any(c.isdigit() for c in base):
                padding.append(random.choice(string.digits))
            if use_symbols and not any(c in string.punctuation for c in base):
                padding.append(random.choice(string.punctuation))
            
            while len(padding) < padding_length:
                padding.append(random.choice(pool))
            
            random.shuffle(padding)
            base += "".join(padding)
            
        return base[:length]
        
    else:
        # Random style: Obfuscate the seed by mixing its letters with random characters
        pool = string.ascii_lowercase
        if use_uppercase:
            pool += string.ascii_uppercase
        if use_numbers:
            pool += string.digits
        if use_symbols:
            pool += string.punctuation
        
        seed_chars = list(seed)
        random.shuffle(seed_chars)
        
        password_chars = []
        seed_idx = 0
        while len(password_chars) < length:
            if seed_idx < len(seed_chars) and random.random() > 0.5:
                c = seed_chars[seed_idx]
                # Apply leetspeak subs to seed chars occasionally
                leet_map = {'a': '@', 's': '$', 'e': '3', 'o': '0', 'i': '1', 't': '7'}
                c = leet_map.get(c.lower(), c)
                if use_uppercase and random.random() > 0.5:
                    c = c.upper()
                password_chars.append(c)
                seed_idx += 1
            else:
                password_chars.append(random.choice(pool))
        
        # Ensure we satisfy requirements
        if use_numbers and not any(c.isdigit() for c in password_chars):
            password_chars[random.randint(0, len(password_chars)-1)] = random.choice(string.digits)
        if use_symbols and not any(c in string.punctuation for c in password_chars):
            password_chars[random.randint(0, len(password_chars)-1)] = random.choice(string.punctuation)
        if use_uppercase and not any(c.isupper() for c in password_chars):
            password_chars[random.randint(0, len(password_chars)-1)] = random.choice(string.ascii_uppercase)
            
        return "".join(password_chars[:length])

def generate_advanced_qr(data, theme="neon_cyan", glow=True, center_icon="none"):
    """
    Generates a high-quality styled QR code image.
    - theme: neon_cyan, neon_pink, neon_green, luxury_gold, classic_dark, plain
    - glow: adds a blurred neon glow outline around the QR modules
    - center_icon: none, lock, link (draws a customized icon in the center)
    """
    if theme == "plain":
        glow = False
        center_icon = "none"

    # Create high-res QR code
    qr = qrcode.QRCode(version=1, box_size=15, border=6)
    qr.add_data(data)
    qr.make(fit=True)
    
    # Theme configuration
    colors = {
        "neon_cyan": ("#00FFFF", "#000000"),
        "neon_pink": ("#FF1493", "#000000"),
        "neon_green": ("#39FF14", "#000000"),
        "luxury_gold": ("#D4AF37", "#121212"),
        "classic_dark": ("#FFFFFF", "#000000"),
        "plain": ("#000000", "#FFFFFF")
    }
    fill_color, back_color = colors.get(theme, ("#00FFFF", "#000000"))
    
    # Generate the base QR image in RGBA
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    bg_r, bg_g, bg_b = ImageColor.getrgb(back_color)
    
    # Apply glow effect
    if glow:
        # Isolate modules by making background pixels transparent
        datas = qr_img.getdata()
        new_data = []
        for item in datas:
            if item[0] == bg_r and item[1] == bg_g and item[2] == bg_b:
                new_data.append((bg_r, bg_g, bg_b, 0)) # transparent background
            else:
                new_data.append(item)
                
        # Create a new glow layer and draw the transparent modules onto it
        glow_layer = Image.new("RGBA", qr_img.size, (bg_r, bg_g, bg_b, 0))
        glow_layer.putdata(new_data)
        
        # Apply Gaussian blur to create the soft neon light aura
        glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=8))
        
        # Merge the glow effect on top of background
        final_img = Image.new("RGBA", qr_img.size, (bg_r, bg_g, bg_b, 255))
        final_img.paste(glow_layer, (0, 0), glow_layer)
        final_img.paste(glow_layer, (0, 0), glow_layer) # Intensify the glow
        
        # Paste crisp original modules on top of the glowing background
        crisp_modules = Image.new("RGBA", qr_img.size, (bg_r, bg_g, bg_b, 0))
        crisp_modules.putdata(new_data)
        final_img.paste(crisp_modules, (0, 0), crisp_modules)
        
        qr_img = final_img.convert("RGBA")
    
    # Draw center icon if requested
    if center_icon != "none":
        draw = ImageDraw.Draw(qr_img)
        w, h = qr_img.size
        
        # Define center box size (approx 16% of total QR size)
        box_w = int(w * 0.16)
        box_h = int(h * 0.16)
        left = (w - box_w) // 2
        top = (h - box_h) // 2
        right = left + box_w
        bottom = top + box_h
        
        # Clear the center area (draw background color block)
        draw.rounded_rectangle([left - 4, top - 4, right + 4, bottom + 4], radius=8, fill=back_color)
        
        # Draw icon container outline
        draw.rounded_rectangle([left, top, right, bottom], radius=6, outline=fill_color, width=2)
        
        # Define icon drawing boundaries
        icon_left = left + int(box_w * 0.22)
        icon_top = top + int(box_h * 0.22)
        icon_right = right - int(box_w * 0.22)
        icon_bottom = bottom - int(box_h * 0.22)
        
        if center_icon == "lock":
            # Draw padlock body
            body_top = icon_top + int((icon_bottom - icon_top) * 0.45)
            draw.rounded_rectangle([icon_left, body_top, icon_right, icon_bottom], radius=2, fill=fill_color)
            
            # Draw padlock shackle (arch)
            shackle_w = icon_right - icon_left
            shackle_left = icon_left + int(shackle_w * 0.15)
            shackle_right = icon_right - int(shackle_w * 0.15)
            shackle_top = icon_top + int((icon_bottom - icon_top) * 0.08)
            shackle_bottom = body_top + int((icon_bottom - icon_top) * 0.22)
            draw.arc([shackle_left, shackle_top, shackle_right, shackle_bottom], start=180, end=360, fill=fill_color, width=2)
            
            # Draw keyhole circle
            dot_x = (icon_left + icon_right) // 2
            dot_y = (body_top + icon_bottom) // 2
            draw.ellipse([dot_x - 2, dot_y - 2, dot_x + 2, dot_y + 2], fill=back_color)
            
        elif center_icon == "link":
            # Draw chain link symbol (interlocking diagonal rings)
            cx, cy = (left + right) // 2, (top + bottom) // 2
            # Ring 1
            draw.ellipse([cx - 2, cy - 8, cx + 8, cy + 2], outline=fill_color, width=2)
            # Ring 2
            draw.ellipse([cx - 8, cy - 2, cx + 2, cy + 8], outline=fill_color, width=2)
            # Diagonal connection link
            draw.line([cx - 3, cy + 3, cx + 3, cy - 3], fill=fill_color, width=2)
            
    # Save image and return file path
    os.makedirs("temp_qr", exist_ok=True)
    file_path = f"temp_qr/qr_{random.randint(1000, 9999)}.png"
    qr_img.convert("RGB").save(file_path)
    return file_path
