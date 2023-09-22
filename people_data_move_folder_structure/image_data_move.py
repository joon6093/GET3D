import os
from PIL import Image

def process_images(input_dir, output_dir):
    # 각 시퀀스 디렉토리에서 이미지 처리
    for seq_dir in os.listdir(input_dir):
        seq_dir_path = os.path.join(input_dir, seq_dir,'img')
        
        # 시퀀스 디렉토리 내의 카메라 디렉토리에서 이미지 처리
        if os.path.isdir(seq_dir_path):
            img_count = 0
            for cam_dir in os.listdir(seq_dir_path):
                img_path = os.path.join(seq_dir_path, cam_dir, '0000.jpg')
                
                # 이미지가 있는 경우 PNG로 변환 및 저장
                if os.path.isfile(img_path):
                    # PNG로 변환
                    img = Image.open(img_path)
                    img = img.convert('RGB')
                    
                    # 출력 디렉토리 준비
                    output_path = os.path.join(output_dir, seq_dir)
                    os.makedirs(output_path, exist_ok=True)
                    
                    # 이미지 저장
                    img.save(os.path.join(output_path, f'{img_count:03d}.png'))
                    img_count += 1

# 입력과 출력 디렉토리 경로 설정
input_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/test_people_data/20230228/'
output_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/out_dir_human_test/img/test_people_data/'

# 함수 호출
process_images(input_dir, output_dir)
