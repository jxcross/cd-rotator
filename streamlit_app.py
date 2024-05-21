import streamlit as st
st.set_page_config(layout="wide")
from PIL import Image, ImageDraw
import os
import numpy as np
import math
import cv2

def remove_background(patch_image):
    # Patch 이미지를 RGBA 형식으로 변환
    patch_rgba = patch_image.convert("RGBA")
    
    # Patch 이미지의 픽셀 데이터를 가져옴
    pixels = patch_rgba.load()
    
    # 이미지의 너비와 높이를 가져옴
    width, height = patch_rgba.size
    
    # 모든 픽셀을 순회하며 배경 부분을 투명하게 처리
    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]  # 픽셀의 RGBA 값 가져오기
            
            # 예시로 흰색 배경을 제거하는 것으로 가정
            if r > 200 and g > 200 and b > 200:
                pixels[x, y] = (r, g, b, 0)  # 배경 부분을 투명하게 처리
    return patch_rgba

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

# def merge_images(background_image, patch_image, position, is_transparent=True):   
#     p_w, p_h = patch_image.size
#     c_w, c_h = (int(p_w/2), int(p_h/2))
#     new_position = (position[0]-c_w, position[1]-c_h)
#     merged_image = background_image.copy()
#     if is_transparent:
#         patch_image = remove_background(patch_image)
#         merged_image.paste(patch_image, new_position, patch_image)
#     else:
#         merged_image.paste(patch_image, new_position)

#     return merged_image

def merge_images(background_image, patch_image, position, radius, is_transparent=True):
    p_w, p_h = patch_image.size
    #radius = 60
    c_x, c_y = p_w//2, p_h//2  #position[0], position[1]
    c_w, c_h = min(radius, p_w // 2), min(radius, p_h // 2)
    
    # 이미지를 원의 크기에 맞게 자르기
    mask = Image.new('L', patch_image.size, 255)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((c_x - c_w, c_y - c_h, c_x + c_w, c_y + c_h), fill=0)
    print("-"*100)
    print(f"{c_x - c_w, c_y - c_h, c_x + c_w, c_y + c_h}")
    patch_image.putalpha(mask)

    merged_image = background_image.copy()

    if is_transparent:
        patch_image = remove_background(patch_image)
    
    # 원의 중심을 기준으로 merge
    p_w, p_h = patch_image.size
    new_position = (position[0] - p_w // 2, position[1] - p_h // 2)
    merged_image.paste(patch_image, new_position, patch_image)
    
    return merged_image


def get_image(title, id):
    # background 이미지 업로드
    img_file = st.file_uploader(title, type=["jpg", "jpeg", "png"], key=f"file_uploader_{id}")
    if img_file:
        img_pil = Image.open(img_file).convert("RGBA")
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
    

# def apply_patch(background_image, patch_image):
#     # 이미지를 읽습니다.
#     # background_image = cv2.imread(background_image_path, cv2.IMREAD_UNCHANGED)
#     # patch_image = cv2.imread(patch_image_path, cv2.IMREAD_UNCHANGED)

#     # if background_image is None or patch_image is None:
#     #     raise FileNotFoundError("하나 이상의 이미지 파일을 찾을 수 없습니다.")

#     # 배경 이미지와 패치 이미지가 같은 크기인지 확인
#     if background_image.shape[:2] != patch_image.shape[:2]:
#         raise ValueError("배경 이미지와 패치 이미지는 같은 크기여야 합니다.")

#     # 배경 이미지가 투명도 채널을 가지고 있는지 확인하고 없다면, 알파 채널을 추가
#     if background_image.shape[2] == 3:
#         background_image = cv2.cvtColor(background_image, cv2.COLOR_BGR2BGRA)

#     # 패치 이미지가 투명도 채널을 가지고 있는지 확인하고 없다면, 알파 채널을 추가
#     if patch_image.shape[2] == 3:
#         patch_image = cv2.cvtColor(patch_image, cv2.COLOR_BGR2BGRA)

#     # 배경 이미지의 색상 있는 부분을 마스크로 만듭니다.
#     bg_mask = cv2.inRange(background_image[:, :, :3], (1, 1, 1), (255, 255, 255))

#     # 배경 이미지의 색상 없는 부분을 마스크로 만듭니다.
#     bg_mask_inv = cv2.bitwise_not(bg_mask)

#     # 패치 이미지를 배경 이미지의 색상 있는 부분에 적용
#     patch_applied = cv2.bitwise_and(patch_image, patch_image, mask=bg_mask)

#     # 배경 이미지의 색상 없는 부분은 투명하게 처리
#     transparent_patch = cv2.bitwise_and(patch_image, patch_image, mask=bg_mask_inv)
#     transparent_patch[:, :, 3] = 0  # 알파 채널을 0으로 설정하여 투명하게 만듭니다.

#     # 최종 이미지를 생성합니다.
#     final_image = cv2.add(patch_applied, transparent_patch)

#     # 이미지를 파일로 저장합니다.
#     #cv2.imwrite(output_image_path, final_image)
#     return final_image

# from PIL import Image

def make_hole(patch_image, radius):
    p_w, p_h = patch_image.size
    #radius = 60
    c_x, c_y = p_w//2, p_h//2  #position[0], position[1]
    c_w, c_h = min(radius, p_w // 2), min(radius, p_h // 2)
    
    # 이미지를 원의 크기에 맞게 자르기
    mask = Image.new('L', patch_image.size, 255)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((c_x - c_w, c_y - c_h, c_x + c_w, c_y + c_h), fill=0)
    print("-"*100)
    print(f"{c_x - c_w, c_y - c_h, c_x + c_w, c_y + c_h}")
    patch_image.putalpha(mask)
    return patch_image

def apply_patch(background_image, patch_image, position, radius):
    # # 이미지를 읽습니다.
    # background_image = Image.open(background_image_path).convert("RGBA")
    # patch_image = Image.open(patch_image_path).convert("RGBA")

    patch_image = make_hole(patch_image, radius)
    patch_image.save("0.hole.png")

    # 이미지 크기 확인
    if background_image.size != patch_image.size:
        raise ValueError("배경 이미지와 패치 이미지는 같은 크기여야 합니다.")

    # 배경 이미지의 알파 채널을 분리합니다.
    bg_alpha = background_image.split()[3]
    bg_alpha.save("1.bg_alpha.png")
 
    # 배경 이미지의 색상 있는 부분을 마스크로 만듭니다.
    bg_mask = bg_alpha.point(lambda p: 255 if p > 0 else 0)
    bg_mask.save("2.bg_mask.png")

    # 배경 이미지의 색상 없는 부분을 반전한 마스크로 만듭니다.
    bg_mask_inv = bg_mask.point(lambda p: 255 - p)
    bg_mask_inv.save("3.bg_mask_inv.png")

    # 패치 이미지를 배경 이미지의 색상 있는 부분에만 적용
    patch_applied = Image.composite(patch_image, Image.new("RGBA", patch_image.size, (0, 0, 0, 0)), bg_mask)
    patch_applied.save("4.patch_applied.png")

    # 배경 이미지의 색상 없는 부분은 투명하게 처리
    transparent_patch = Image.composite(Image.new("RGBA", patch_image.size, (0, 0, 0, 0)), patch_image, bg_mask_inv)
    transparent_patch.save("5.transparent_patch.png")

    # # 최종 이미지를 생성합니다.
    # final_image = Image.alpha_composite(patch_applied, transparent_patch)
    # final_image.save("6.final.png")

    # 원의 중심을 기준으로 merge
    p_w, p_h = patch_image.size
    new_position = (position[0] - p_w // 2, position[1] - p_h // 2)
    merged_image = background_image.copy()
    merged_image.paste(transparent_patch, new_position, transparent_patch)

    # 이미지를 파일로 저장합니다.
    #final_image.save(output_image_path)
    return merged_image



# def apply_patch(background_image, patch_image, radius):
#     # 이미지 크기 확인
#     if background_image.size != patch_image.size:
#         raise ValueError("배경 이미지와 패치 이미지는 같은 크기여야 합니다.")

#     # 패치 이미지의 중심 좌표 계산
#     width, height = patch_image.size
#     center_x, center_y = width // 2, height // 2

#     # 원형 마스크를 생성하여 중심에서 반지름 r 픽셀 만큼의 원 영역을 제거
#     mask = Image.new("L", (width, height), 0)
#     draw = ImageDraw.Draw(mask)
#     draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=255)

#     # 패치 이미지에 원형 마스크를 적용하여 해당 영역을 투명하게 처리
#     patch_with_hole = patch_image.copy()
#     patch_with_hole.putalpha(mask)

#     # 배경 이미지의 알파 채널을 분리합니다.
#     bg_alpha = background_image.split()[3]

#     # 배경 이미지의 색상 있는 부분을 마스크로 만듭니다.
#     bg_mask = bg_alpha.point(lambda p: 255 if p > 0 else 0)

#     # 배경 이미지의 색상 없는 부분을 반전한 마스크로 만듭니다.
#     bg_mask_inv = bg_mask.point(lambda p: 255 - p)

#     # 패치 이미지를 배경 이미지의 색상 있는 부분에만 적용
#     patch_applied = Image.composite(patch_with_hole, Image.new("RGBA", patch_image.size, (0, 0, 0, 0)), bg_mask)

#     # 배경 이미지의 색상 없는 부분은 투명하게 처리
#     transparent_patch = Image.composite(Image.new("RGBA", patch_image.size, (0, 0, 0, 0)), patch_with_hole, bg_mask_inv)

#     # 최종 이미지를 생성합니다.
#     final_image = Image.alpha_composite(patch_applied, transparent_patch)

#     # 이미지를 파일로 저장합니다.
#     #final_image.save(output_image_path)
#     return final_image



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
        radius = st.text_input("원의 반지름", value=50)
        is_transparent = st.checkbox("투명하게 붙이기", value=True)
        patch_button = st.button("MERGE")
        if patch_button:
            # merged_image = merge_images(st.session_state["resized_bg_img"], 
            #                             st.session_state["resized_patch_img"], 
            #                             (int(patch_x), int(patch_y)), 
            #                             int(radius),
            #                             is_transparent=is_transparent)
            merged_image = apply_patch(st.session_state["resized_bg_img"],
                                       st.session_state["resized_patch_img"],
                                       (int(patch_x), int(patch_y)),
                                       int(radius))
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
    
if __name__ == "__main__":
    main()