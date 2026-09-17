def delivery_slots(deliveries: list[dict]) -> list[list[str]]:

    gr = {}

    for d in deliveries:

        if "name" not in d:
            raise ValueError()
        if "slot" not in d:
            raise ValueError()

        nm = d["name"]
        sl = d["slot"]

        if sl <= 0:
            raise ValueError()

        if sl not in gr:
            gr[sl] = []

        nms = gr[sl]
        nms.append(nm)

        gr[sl] = nms

    res = []

    sls=sorted(gr)

    for sl in sls:
        nms = gr[sl]
        res.append(nms)

    return res