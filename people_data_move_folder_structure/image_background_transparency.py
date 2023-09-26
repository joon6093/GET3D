from PIL import Image

def remove_background(img, threshold=200):
    img = img.convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        if item[0] > threshold and item[1] > threshold and item[2] > threshold:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    return img

image_path = "/home/msjeong/ext_hdd/jysong/get3d_folder/000.png"
image = Image.open(image_path)

transparent_image = remove_background(image)

transparent_image.save("/home/msjeong/ext_hdd/jysong/get3d_folder/new_image.png", "PNG")
