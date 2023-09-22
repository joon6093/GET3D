import os
import numpy as np
import json

def rotation_elevation_from_camera_json(json_data):
    camera_count = len(json_data)

    # 빈 리스트를 생성하여 모든 카메라의 rotation과 elevation 값을 저장
    all_rotations = []
    all_elevations = []

    # 모든 카메라에 대한 처리
    for camera in json_data.values():
        # 회전 행렬 추출 및 numpy 배열로 변환
        R = np.array(camera["R"])

        # Yaw, Pitch 계산
        yaw = np.arctan2(R[1, 0], R[0, 0])
        pitch = np.arctan2(-R[2, 0], np.sqrt(R[2, 1]**2 + R[2, 2]**2))

        # 각도를 도(degree) 단위로 변환
        yaw_deg = np.degrees(yaw)
        pitch_deg = np.degrees(pitch)

        # rotation과 elevation 값을 리스트에 추가
        all_rotations.append(yaw_deg)
        all_elevations.append(pitch_deg)

    # Numpy 배열로 변환
    rotation_array = np.array(all_rotations, dtype=np.float32).reshape((camera_count,))
    elevation_array = np.array(all_elevations, dtype=np.float32).reshape((camera_count,))

    return rotation_array, elevation_array

def process_camera_json_files(input_dir, output_dir):
    # 주어진 디렉토리에서 모든 cameras.json 파일 찾기
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file == 'cameras.json':
                # JSON 파일 로드
                with open(os.path.join(root, file), 'r') as f:
                    data = json.load(f)

                # rotation과 elevation 배열 가져오기
                rotation_array, elevation_array = rotation_elevation_from_camera_json(data)

                # 출력 디렉토리 준비
                relative_path = os.path.relpath(root, input_dir)
                output_path = os.path.join(output_dir, relative_path)
                os.makedirs(output_path, exist_ok=True)

                # NPY 파일로 저장
                np.save(os.path.join(output_path, 'rotation.npy'), rotation_array)
                np.save(os.path.join(output_path, 'elevation.npy'), elevation_array)

# 입력과 출력 디렉토리 경로 설정
input_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/test_people_data/20230228/'
output_dir = '/home/msjeong/ext_hdd/jysong/get3d_folder/out_dir_human_test/camera/test_people_data/'

# 함수 호출
process_camera_json_files(input_dir, output_dir)
