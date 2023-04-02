from avitobot import avito_api, texts


def format_request_result(req_result: avito_api.RequestResult) -> str:
    return texts.REQUEST_RESULT.format(min_price=req_result.min_price,
               max_price=req_result.max_price, avg_price=req_result.avg_price,
                           ads_count=req_result.ads_count, url=req_result.url)
