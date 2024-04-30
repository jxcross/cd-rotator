import streamlit as st
st.set_page_config(layout="wide")
from PIL import Image
import os
import numpy as np
import math
import cv2

def rotate_cd(cd_image, patch_image, angle):
    # CD 이미지를 numpy 배열로 변환
    cd_array = np.array(cd_image)
    
    # Patch 이미지를 numpy 배열로 변환
    patch_array = np.array(patch_image)
    
    # 회전 중심점 계산
    center = (cd_array.shape[1] // 2, cd_array.shape[0] // 2)
    
    # 회전 변환 행렬 계산
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # CD 이미지를 회전시킴
    rotated_cd_array = cv2.warpAffine(cd_array, rotation_matrix, (cd_array.shape[1], cd_array.shape[0]))
    
    # Patch 이미지를 CD 이미지에 적용
    rotated_cd_array[50:50+patch_array.shape[0], 50:50+patch_array.shape[1]] = patch_array
    
    # 회전된 배열을 이미지로 변환
    rotated_cd_image = Image.fromarray(rotated_cd_array)
    
    return rotated_cd_image

def rotate_image(image, angle):
    # 이미지를 numpy 배열로 변환
    image_array = np.array(image)
    
    # 회전 중심점 계산
    center = (image_array.shape[1] / 2, image_array.shape[0] / 2)
    
    # 회전 변환 행렬 계산
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # 이미지를 회전시킴
    rotated_array = cv2.warpAffine(image_array, rotation_matrix, (image_array.shape[1], image_array.shape[0]))
    
    # 회전된 배열을 이미지로 변환
    rotated_image = Image.fromarray(rotated_array)
    
    return rotated_image

def merge_images(background_image, patch_image, position):   
    p_w, p_h = patch_image.size
    c_w, c_h = (int(p_w/2), int(p_h/2))
    new_position = (position[0]-c_w, position[1]-c_h)
    merged_image = background_image.copy()
    merged_image.paste(patch_image, new_position)

    return merged_image


def get_image(title, id):
    # background 이미지 업로드
    img_file = st.file_uploader(title, type=["jpg", "jpeg", "png"], key=f"file_uploader_{id}")
    if img_file:
        img_pil = Image.open(img_file)
        #bg_width, bg_height = img_pil.size
        #st.image(img_pil)
        return img_pil

def resize_image(image, id):
    width, height = image.size
    new_width = st.text_input("WIDTH", value=width, key=f"new_width_{id}")
    new_height = st.text_input("HEIGHT", value=height, key=f"new_height_{id}")
    resize_button = st.button("RESIZE", key=f"resize_button_{id}")
    if resize_button:
        resized_image = image.resize((int(new_width), int(new_height)))
        return resized_image

def main():
    st.title("이미지 합치기")
    
    col1, col2 = st.columns(2)
    with col1:
        bg_img = get_image("배경 이미지", id=1)
        if bg_img:
            st.image(bg_img)
            resized_bg_img = resize_image(bg_img, id=1)
            if resized_bg_img:
                st.session_state["resized_bg_img"] = resized_bg_img
        if "resized_bg_img" in st.session_state:
            st.image(st.session_state["resized_bg_img"])
    with col2:
        patch_img = get_image("패치 이미지", id=2)
        if patch_img:
            st.image(patch_img)
            resized_patch_img = resize_image(patch_img, id=2)
            if resized_patch_img:
                st.session_state["resized_patch_img"] = resized_patch_img
        if "resized_patch_img" in st.session_state:
            st.image(st.session_state["resized_patch_img"])


    # 백그라운드 이미지 정보
    if "resized_bg_img" in st.session_state and "resized_patch_img" in st.session_state:
        st.markdown("### 이미지 합치기")
        bg_img_w, bg_img_h = st.session_state["resized_bg_img"].size
        st.write("Left Top (x1,y1)=(0, 0)")
        center_x, center_y = (int(bg_img_w/2), int(bg_img_h/2))
        st.write(f"Center (c1, c2) = ({center_x}, {center_y})")
        st.write(f"Right Bottom (x2, y2) = ({bg_img_w-1}, {bg_img_h-1})")
        # patch 이미지 정보
        patch_img_w, patch_img_h = st.session_state["resized_patch_img"].size
        patch_cx, patch_cy = (int(patch_img_w/2), int(patch_img_h/2))
        st.write(f"패치 이미지 중심점 = ({patch_cx}, {patch_cy})")
    
        st.markdown("**붙일 위치**")
        patch_x = st.text_input("X 위치", value=center_x)
        patch_y = st.text_input("Y 위치", value=center_y)
        patch_button = st.button("MERGE")
        if patch_button:
            merged_image = merge_images(st.session_state["resized_bg_img"], st.session_state["resized_patch_img"], (int(patch_x), int(patch_y)))
            st.session_state["merged_image"] = merged_image
        if "merged_image" in st.session_state:
            st.image(st.session_state["merged_image"])
    
    # save
    if "merged_image" in st.session_state:
        merged_image_path = st.text_input("파일 저장 위치 및 이름", value="./merged_image.jpg")
        save_button = st.button("SAVE")
        if save_button:
            # 파일 저장 다이얼로그 열기
            #file_path = "./merged_image.jpg" #st.sidebar.text_input("저장 경로", value="merged_image.jpg")  # 저장할 파일 경로와 이름 입력 필드
            save_dir, save_file = os.path.split(merged_image_path)  # 경로와 파일 이름 분리

            if save_dir and save_file:  # 경로와 파일 이름이 모두 입력되었을 경우에만 저장 수행
                st.session_state["merged_image"].save(merged_image_path)  # 이미지 파일로 저장
                st.success(f"이미지가 성공적으로 저장되었습니다. 파일 경로: {merged_image_path}")
                
                # 다운로드 버튼 생성
                st.markdown(
                    f'<a href="{merged_image_path}" download="{save_file}">Download Image</a>',
                    unsafe_allow_html=True
                )
            else:
                st.warning("저장 경로와 파일 이름을 입력해주세요.")
    
    
    
# def get_image(title, id):
#     # background 이미지 업로드
#     img_file = st.file_uploader("배경 이미지 업로드", type=["jpg", "jpeg", "png"], key=f"file_uploader_{id}")
#     if img_file:
#         img_pil = Image.open(img_file)
#         bg_width, bg_height = img_pil.size
#         st.image(img_pil)
#         width_text = st.text_input("WIDTH", value=bg_width, key=f"width_text_{id}")
#         height_text = st.text_input("HEIGHT", value=bg_height, key=f"height_text_{id}")
#         resize_button = st.button("RESIZE", key=f"resize_button_{id}")

#         if resize_button:
#             try:
#                 new_width = int(width_text)
#                 new_height = int(height_text)
#                 resized_pil = resize_image(img_pil, new_width, new_height)
#                 #st.image(resized_pil, caption="Resized Image")
#                 return resized_pil
#             except ValueError:
#                 st.error("Invalid input. Please enter numbers for width and height.")


# def main():
#     st.title("이미지 합치기")
    
#     col1, col2 = st.columns(2)
#     with col1:
#         bg_img = get_image(title="배경 이미지", id=1)
#         if bg_img:
#             st.image(bg_img)
#     with col2:
#         patch_img = get_image(title="패치 이미지", id=2)
#         if patch_img:
#             st.image(patch_img)



            
        
        


    # # patch 이미지 업로드
    # patch_image = st.file_uploader("패치 이미지 업로드", type=["jpg", "jpeg", "png"])
    # st.image(patch_image, width=50)

    # # patch 이미지를 붙여넣을 위치 입력
    # position_x = st.number_input("패치 이미지를 붙여넣을 X 좌표", value=0)
    # position_y = st.number_input("패치 이미지를 붙여넣을 Y 좌표", value=0)
    # position = (position_x, position_y)

    # # 이미지가 모두 업로드되었을 때 실행
    # if background_image and patch_image:
    #     # 업로드된 이미지를 PIL 이미지 객체로 변환
    #     background_pil = Image.open(background_image)
    #     patch_pil = Image.open(patch_image)

    #     # 이미지 합치기
    #     merged_image = merge_images(background_pil, patch_pil, position)

    #     # 합쳐진 이미지 출력
    #     st.image(merged_image, caption='Merged Image', use_column_width=True)

    #     # 합쳐진 이미지 파일 저장
    #     st.markdown("### 합쳐진 이미지 저장")
    #     save_button = st.button("이미지 저장")
    #     if save_button:
    #         save_path = "merged_image.jpg"  # 저장할 경로 설정
    #         merged_image.save(save_path)
    #         st.success(f"이미지가 {save_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
    