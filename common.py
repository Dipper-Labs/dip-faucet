def write_json_response(handler, msg, code=200):
    handler.set_status(code)
    handler.set_header('Content-Type', 'application/json; charset=UTF-8')
    handler.write(msg)
