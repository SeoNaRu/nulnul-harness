def register_subscription(request, registry):
    item = dict(request)
    registry.append(item)
    return {"subscription": item}
