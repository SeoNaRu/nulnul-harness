def create_alert(request, outbox):
    item = dict(request)
    outbox.append(item)
    return {"alert": item}
