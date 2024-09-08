import os, re
import shutil

# """ĐỔI TÊN TẤT CẢ CÁC FILE TRONG THƯ MỤC CHO ĐÚNG THỨ TỰ"""
# imagefolder = "Image Mango/BestData/HOALOC/No Tape"
# newFolder = "24.1.9"

# filenames = os.listdir(imagefolder)
# sorted_filenames = sorted(filenames, key=lambda x: tuple(map(int, re.findall(r'\d+', x))))

# for filename in sorted_filenames:
#     name, ext = os.path.splitext(filename)
#     parts = name.split("-")
#     index = int(parts[0])
#     if index>10:
#         newindex = index-1
#     else:
#         newindex = index
#     label = parts[1]
#     new_name = f"{newindex}-{label}{ext}"
#     print(new_name)
#     source_path = os.path.join(imagefolder, filename)
#     target_path = os.path.join(newFolder, new_name)

#     shutil.copy(source_path, target_path)

"""TÌM ẢNH 4 MẶT VÀ COPY CÁC ẢNH NÀY VÀO THƯ MỤC MỚI"""
imagefolder = "Image Mango/BestData/HOALOC/Tape"
newFolder = "24.1.17"

filenames = os.listdir(imagefolder)
sorted_filenames = sorted(filenames, key=lambda x: tuple(map(int, re.findall(r'\d+', x))))

print(sorted_filenames)

ID = [1, 4, 7, 10]

for filename in sorted_filenames:
    name, ext = os.path.splitext(filename)
    parts = name.split("_")
    IDFace = int(parts[1])
    IDMango = parts[0].split("-")[0]
    typeFace = parts[0].split("-")[1]

    
    if (IDFace==ID[0] or IDFace==ID[1] or IDFace==ID[2] or IDFace==ID[3]) and typeFace!="Right":
        if IDFace==ID[0]: label = 1
        elif IDFace==ID[1]: label = 2
        elif IDFace==ID[2]: label = 3
        elif IDFace==ID[3]: label = 4

        new_name = f"{IDMango}-{typeFace}_{label}{ext}"
        print(new_name)

    elif IDFace==ID[2] and typeFace=="Right":
        label = 3
        new_name = f"{IDMango}-{typeFace}_{label}{ext}"
        print(filename)

    else: 
        new_name = None

    if new_name is not None:
        source_path = os.path.join(imagefolder, filename)
        target_path = os.path.join(newFolder, new_name)
        shutil.copy(source_path, target_path)

