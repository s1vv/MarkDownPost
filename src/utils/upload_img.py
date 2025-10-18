import requests


def upload_to_imgbb(file_path: str, api_key: str) -> str:
    """Загружает локальный файл на ImgBB и возвращает прямую ссылку на изображение."""
    with open(file_path, "rb") as f:
        resp = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": api_key},
            files={"image": f},
        )
    data = resp.json()
    if not data.get("success"):
        raise RuntimeError(f"Ошибка загрузки {file_path}: {data}")
    return data["data"]["url"]
