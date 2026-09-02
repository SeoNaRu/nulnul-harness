def submit_job(request, queue):
    item = dict(request)
    queue.append(item)
    return {"job": item}
