from .database import Session
from .models import MangoItem, Image, DetectedArea, Conclusion
from sqlalchemy import func

def save_mango_data(payload_results):
    session = Session()
    try:
        # Lưu MangoItem
        mango_item = MangoItem(
            mango_id=payload_results['current_item']['id'],
            folder_path=payload_results['current_item']['folder_path']
        )
        session.add(mango_item)
        session.commit()  # Commit để lưu mango_item trước khi dùng nó trong các bảng khác

        # Lưu Images
        for image_type in ['prediction_images', 'original_images']:
            for position, path in payload_results[image_type].items():
                image = Image(
                    mango_item_id=mango_item.id,  # Sử dụng ID của mango_item đã được commit
                    image_type='prediction' if image_type == 'prediction_images' else 'original',
                    position=position,
                    image_path=path
                )
                session.add(image)

        # Lưu DetectedAreas
        for area in payload_results['conclusion']['detected_areas']:
            detected_area = DetectedArea(
                mango_item_id=mango_item.id,
                image=area['image'],
                position_x=area['position']['x'],
                position_y=area['position']['y'],
                area_size=area['area_size'],
                disease=area['disease']
            )
            session.add(detected_area)

        # Lưu Conclusion
        conclusion = Conclusion(
            mango_item_id=mango_item.id,
            total_disease_area=payload_results['conclusion']['total_disease_area'],
            total_mango_surface_area=payload_results['conclusion']['total_mango_surface_area'],
            disease_area_percentage=payload_results['conclusion']['disease_area_percentage'],
            conclusion=payload_results['conclusion']['conclusion']
        )
        session.add(conclusion)

        # Commit toàn bộ thay đổi
        session.commit()

    except Exception as e:
        session.rollback()  # Rollback nếu có lỗi
        print(f"Error: {e}")
    finally:
        session.close()  # Đóng session

    return mango_item 

def get_next_mango_id():
    session = Session()
    try:
        # Truy vấn mango_id lớn nhất hiện có
        max_mango_id = session.query(func.max(MangoItem.id)).scalar()

        # Nếu bảng rỗng, trả về giá trị khởi tạo (ví dụ: 1)
        if max_mango_id is None:
            return 1
        else:
            return max_mango_id + 1
    except Exception as e:
        print(f"Error while fetching next mango_id: {e}")
        return None
    finally:
        session.close()