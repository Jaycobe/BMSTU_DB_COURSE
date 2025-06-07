def get_json_success(message = '', app_data: dict = {}) -> dict:
    return {"status": "success", "data": app_data, "message": message}


def get_json_fail(err_desc: str = 'Unknown error', app_data: dict = {}) -> dict:
    return {"status": "fail", "data": app_data, "message": err_desc}
