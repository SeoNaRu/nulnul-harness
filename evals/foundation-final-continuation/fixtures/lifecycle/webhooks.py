def register_webhook(request, registry):
    item = dict(request)
    registry.append(item)
    return {"webhook": item}
