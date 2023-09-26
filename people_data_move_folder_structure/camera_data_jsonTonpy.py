import os
import numpy as np
import json

def process_camera_json_files(input_dir, output_dir):
    # 주어진 디렉토리에서 모든 cameras.json 파일 찾기
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file == 'cameras.json':
                # JSON 파일 로드
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)

                # 카메라 회전 각도 설정
                views = 36  # 이미지 수
                rotation_step = 10  # 회전 각도 간격 (도)
                rotation_angles = np.array([i * rotation_step for i in range(views)], dtype=np.float32)

                # 카메라 고도 각도 설정 (정면으로 고정)
                elevation_angles = np.zeros(views, dtype=np.float32)  # 모든 각도가 0도로 설정

                # 출력 디렉토리 준비
                relative_path = os.path.relpath(root, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(output_path, exist_ok=True)

                # NPY 파일로 저장
                np.save(os.path.join(output_path, 'rotation.npy'), rotation_angles)
                np.save(os.path.join(output_path, 'elevation.npy'), elevation_angles)

# 입력과 출력 디렉토리 경로 설정
input_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/test_people_data/20230228/'
output_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/out_dir_human_test/camera/test_people_data/'

# 함수 호출
process_camera_json_files(input_dir, output_dir)
