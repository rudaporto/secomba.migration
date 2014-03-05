from DateTime import DateTime
from secomba.migration import db
from secomba.migration import assunto

def query_catalog(context, portal_type, begin=None, end=None):
    """Query portal_catalog using date time range and portal_type.
    """
    if begin is None:
        begin = DateTime() - 60
    if end is None:
        end = DateTime() - 30
    date_range_query = { 'query':(begin, end), 'range': 'min:max'}
    catalog = context.portal_catalog
    return catalog.searchResults({'portal_type': portal_type,
                                  'created' : date_range_query,
                                  'sort_on' : 'created',
                                  'review_state': 'published'})


def map_noticia(old_obj, noticia):
    noticia.plone_uid = old_obj.UID()
    noticia.uid = 1
    title = old_obj.Title().decode('utf-8').encode('iso8859-1','ignore')
    noticia.title = title
    noticia.created = int(old_obj.created().timeTime())
    noticia.published = int(old_obj.getEffectiveDate().timeTime())
    noticia.expired = 0
    noticia.hostname = ''
    noticia.nohtml = 0
    noticia.nosmiley = 0
    hometext = old_obj.Description().decode('utf-8').encode('iso8859-1','ignore')
    noticia.hometext = hometext
    noticia.hometext_man = ''
    bodytext = old_obj.getText().decode('utf-8').encode('iso8859-1','ignore')
    noticia.bodytext = bodytext
    noticia.keywords = ''
    noticia.counter = 0
    noticia.description = ''
    noticia.topicid = assunto.mapping.get(old_obj.getAssunto(), 1)
    noticia.ihome = 0
    noticia.notifypub = 0
    noticia.story_type = ''
    noticia.topicdisplay = 0
    noticia.topicalign = 'R'
    noticia.comments = 0
    noticia.rating = 0.0
    noticia.votes = 0
    noticia.destaque = 0
    noticia.storder = 1000
    noticia.wphoto = 0
    noticia.sttype = 0
    noticia.article = 0
    noticia.articlefont = ''
    noticia.approver = 1
    noticia.regiao = '0'

def migrate_noticia(context):
    """Migrate Noticia content from Plone to SQLDatabase.
    context: Plone Site object
    """
    results = query_catalog(context, 'Noticia')
    conn = db.get()
    session = conn.Session()
    debug = ''
    import pdb; pdb.set_trace()
    for item in results:
        old_obj = item.getObject()
        new_obj = session.query(db.NewNoticia).filter_by(plone_uid=old_obj.UID()).first()
        if new_obj is None:
            new_obj = db.NewNoticia()
            session.add(new_obj)
        new_obj = map_noticia(old_obj, new_obj)
        debug += old_obj.Title() + ' | ' + str(old_obj.created()) + ' | ' + '/'.join(old_obj.getPhysicalPath()[3:]) + '\n'
    return debug
