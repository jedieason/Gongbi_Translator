import os
from PIL import Image, ImageDraw, ImageOps

def create_rounded_icon(input_path, output_path, size=1024, radius=None):
    if radius is None:
        radius = int(size * 0.22) # Standard iOS/macOS radius ratio

    # Load input
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    img = Image.open(input_path).convert("RGBA")
    
    # 1. Resize/Crop to square
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) / 2
    top = (height - min_dim) / 2
    right = (width + min_dim) / 2
    bottom = (height + min_dim) / 2
    img = img.crop((left, top, right, bottom))
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    # 2. Create the mask for rounded corners
    # We use a larger canvas for anti-aliasing
    mask_size = size * 4
    mask_radius = radius * 4
    mask = Image.new('L', (mask_size, mask_size), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, mask_size, mask_size), radius=mask_radius, fill=255)
    mask = mask.resize((size, size), Image.Resampling.LANCZOS)

    # 3. Apply mask
    output_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    output_img.paste(img, (0, 0), mask=mask)

    # 4. Save
    output_img.save(output_path, "PNG")
    print(f"✅ Created rounded icon: {output_path}")

    # 5. Generate .icns if on macOS
    try:
        if os.name == 'posix':
            print("📦 Generating .icns for macOS...")
            iconset_dir = "icons.iconset"
            if not os.path.exists(iconset_dir):
                os.makedirs(iconset_dir)
            
            # Iconutil needs specific sizes
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            for s in sizes:
                s_half = s // 2
                if s_half >= 16:
                    img_s = output_img.resize((s_half, s_half), Image.Resampling.LANCZOS)
                    img_s.save(f"{iconset_dir}/icon_{s_half}x{s_half}.png")
                    img_s_2x = output_img.resize((s, s), Image.Resampling.LANCZOS)
                    img_s_2x.save(f"{iconset_dir}/icon_{s_half}x{s_half}@2x.png")
                else:
                    img_s = output_img.resize((s, s), Image.Resampling.LANCZOS)
                    img_s.save(f"{iconset_dir}/icon_{s}x{s}.png")

            # Final size for 1024
            output_img.save(f"{iconset_dir}/icon_512x512@2x.png")

            os.system(f"iconutil -c icns {iconset_dir} -o assets/icon.icns")
            os.system(f"rm -rf {iconset_dir}")
            print(f"✅ Generated: assets/icon.icns")
    except Exception as e:
        print(f"⚠️ Could not generate .icns: {e}")

if __name__ == "__main__":
    assets = "/Users/jedieason/Desktop/TranslateGongBi/assets"
    input_p = os.path.join(assets, "icon.png")
    output_p = os.path.join(assets, "icon.png") # Overwrite or rename? Let's overwrite as the user wants a "new" icon.
    
    create_rounded_icon(input_p, output_p)
