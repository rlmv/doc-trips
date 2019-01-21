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


def join_with_and(iter, closing_word=None):
    """ Given a list ["A", "B", "C"] return "A, B and C" """
    if closing_word is None:
        closing_word = 'and'

    l = list(map(str, iter))
    if len(l) == 0:
        return ""
    elif len(l) == 1:
        return l[0]
    return ", ".join(l[:-1]) + " " + closing_word + " " + l[-1]


def join_with_or(iter):
    """ Given a list ["A", "B", "C"] return "A, B or C" """
    return join_with_and(iter, closing_word='or')
