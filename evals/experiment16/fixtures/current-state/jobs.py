import errors


def _validate_request(request):
    region = request.get("region", "")
    if region not in ("", "us-east", "eu-west"):
        return errors.problem("region", "INVALID_REGION")


def submit_job(request, queue):
    problem = _validate_request(request)
    if problem is not None:
        return problem

    item = dict(request)
    queue.append(item)
    return {"job": item}


def submit_jobs(requests, queue):
    items = []
    for request in requests:
        problem = _validate_request(request)
        if problem is not None:
            return problem
        items.append(dict(request))

    queue.extend(items)
    return {"jobs": items}
