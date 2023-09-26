import os
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

def process_images(input_dir, output_dir):
    # Process images in each sequence directory
    for seq_dir in os.listdir(input_dir):
        seq_dir_path = os.path.join(input_dir, seq_dir,'img')
        
        # Process images in camera directory inside sequence directory
        if os.path.isdir(seq_dir_path):
            img_count = 0
            for cam_dir in os.listdir(seq_dir_path):
                img_path = os.path.join(seq_dir_path, cam_dir, '0000.jpg')
                
                # If image exists, convert to PNG and save
                if os.path.isfile(img_path):
                    # Convert to PNG
                    img = Image.open(img_path)
                    img = img.convert('RGB')
                    
                    # Remove background
                    transparent_img = remove_background(img)
                    
                    # Prepare output directory
                    output_path = os.path.join(output_dir, seq_dir)
                    os.makedirs(output_path, exist_ok=True)
                    
                    # Save the image
                    transparent_img.save(os.path.join(output_path, f'{img_count:03d}.png'))
                                
                    img_count += 1

# Set input and output directory paths
input_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/test_people_data/20230228/'
output_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/out_dir_human_test/img/test_people_data/'

# Call the function
process_images(input_dir, output_dir)  # Uncomment this line to run the function

