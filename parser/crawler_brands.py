import os
import ast
import requests

from typing import List

BASE_LINK = "https://yastatic.net/s3/vertis-front-deploy/_autoru-frontend/client_0f2024c1745d99e834ee.js"


def json_from_yastatic() -> List[str]:
    """
    send request to the yastatic server with js script and get from him the json in text format;

    return the list of brands
    """
    response = requests.get(BASE_LINK, cookies={"_ym_d": str(os.getenv("_YM_D")), "_ym_uid": str(os.getenv("_YM_UID"))})
    begin_rule = """870:e=>{"use strict";e.exports=JSON.parse('"""  # rule in begin of JSON
    end_rule = "')},87385"  # rule in end of JSON
    start_index: int = response.text.find(begin_rule) + len(begin_rule)
    end_index: int = response.text.find(end_rule)

    brands_model_dict = dict(ast.literal_eval(response.text[start_index: end_index]))  # from text to dict
    return list(brands_model_dict.keys())
