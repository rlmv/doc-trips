def section_range(sxns):
    """
    Given an interable of sections [<Section A>, <Section B>, <Section C>],
    return a string "A - C", only if the sections are contiguous by name.
    """
    sxns = list(sorted(map(lambda x: x.name, sxns)))
    if not sxns:
        return ""
    for i, j in zip(range(len(sxns) - 1), range(1, len(sxns))):
        assert ord(sxns[i]) + 1 == ord(sxns[j]), "sections not contiguous"
    return "%s - %s" % (sxns[0], sxns[-1])
