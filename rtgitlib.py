class Commit(object):

    '''
    Represents an individual git commit
    '''

    mv_header_fields = {
        '<prefix>:' : re.compile(r'^[\s\S]{0,72}$'),
        'REF:' : re.compile(r'^#[\d]{4}$'),
        'Description:' : re.compile(r'^.{72,}$'),
        'Signed-off-by:' : re.compile(r'^((\S+)(\s){1}){2}(\S+)@([a-z0-9-]+)(\.)([a-z]{2,4})+$'),
    }
