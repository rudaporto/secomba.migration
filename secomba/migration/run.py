import os

from DateTime import DateTime
from secomba.migration import db
from secomba.migration import assunto

PHOTO_PATH = '/usr/local/zope-secom/migration/photo'
AUDIO_PATH = '/usr/local/zope-secom/migration/audio'
VIDEO_PATH = '/usr/local/zope-secom/migration/video'

BEGIN_DAYS = 3000
END_DAYS = 0

map_type = {
'Noticia':'noticias',
'Audio':'audio',
'Video':'video',
'ATPhotoAlbum':'galeria'
}

def write_file(path, file):
    if not os.path.isdir(path):
        fp = open(path,'w')
        fp.seek(0)
    else:
        raise Exception('Directory exists with same name as file')

    for data in file.getData():
        fp.write(data)
    fp.close()

def save_photo_album(fileid, imagem, idevento, prefix=None):
    if prefix is not None:
        fileid = prefix + '_' + fileid
    path = PHOTO_PATH + '/' + str(idevento) + '/' + fileid

    write_file(path, imagem)

def create_album_directory(idevento):
    path = PHOTO_PATH + '/' + str(idevento)
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise Exception('Exists file with name ID equal to album directory: %s' % str(idevento))

def query_catalog(context, portal_type, begin=None, end=None):
    """Query portal_catalog using date time range and portal_type.
    """
    if begin is None:
        begin = DateTime() - BEGIN_DAYS
    if end is None:
        end = DateTime() - END_DAYS
    date_range_query = { 'query':(begin, end), 'range': 'min:max'}
    catalog = context.portal_catalog
    return catalog.searchResults({'portal_type': portal_type,
                                  'created' : date_range_query,
                                  'sort_on' : 'created',
                                  'review_state': 'published'})

def map_album(old_obj, album):
    plone_uid = old_obj.UID()
    album.plone_uid = plone_uid
    album.idcategoria = 1
    album.titulo = old_obj.Title().decode('utf-8').encode('iso8859-1','ignore')
    album.thumb = 0
    album.dataevento = int(old_obj.created().timeTime())
    album.dataexpiracao = 0
    album.descricao = old_obj.Description().decode('utf-8').encode('iso8859-1','ignore')
    album.publicado = 1
    album.plone_path = '/'.join(old_obj.getPhysicalPath()[3:])
    session = db.get().Session()
    session.flush()
    album.diretorio = album.idevento
    create_album_directory(album.idevento)
    for old_photo in old_obj.objectValues():
        if old_photo.portal_type != 'ATPhoto':
            continue
        photo = session.query(db.NewPhoto).filter_by(plone_uid=old_photo.UID()).first()
        if photo is None:
            photo = db.NewPhoto()
            session.add(photo)
        map_photo(old_photo, photo, album.idevento, old_obj)

def map_photo(old_obj, photo, idevento, old_album):
    UID = old_obj.UID()
    nomearquivo = UID + '-photo.jpg'
    photo.plone_uid = UID
    photo.titulo = old_album.Title().decode('utf-8').encode('iso8859-1','ignore')
    photo.credito = old_album.Rights().decode('utf-8').encode('iso8859-1','ignore')
    photo.nomearquivo = nomearquivo
    photo.evento = idevento
    photo.descricao = old_album.Description().decode('utf-8').encode('iso8859-1','ignore')
    photo.ordem = 1000
    photo.keywords = ''
    photo.informacoes = ''
    photo.plone_path = '/'.join(old_obj.getPhysicalPath()[3:])

    try:
        image = old_obj.restrictedTraverse('image')
        save_photo_album(nomearquivo, image, idevento, prefix=None)
    except AttributeError,e:
        print 'Image not found for photo: %s' % photo.plone_path

    try:
        thumb = old_obj.restrictedTraverse('image_thumb')
        save_photo_album(nomearquivo, thumb, idevento, prefix='thumb')
        save_photo_album(nomearquivo, thumb, idevento, prefix='manchete')
    except AttributeError,e:
        print 'Image thumb not found for photo: %s' % photo.plone_path

    try:
        preview = old_obj.restrictedTraverse('image_preview')
        save_photo_album(nomearquivo, preview, idevento, prefix='normal')
        save_photo_album(nomearquivo, preview, idevento, prefix='destaque')
    except AttributeError,e:
        print 'Image preview not found for photo: %s' % photo.plone_path

    try:
        tile = old_obj.restrictedTraverse('image_tile')
        save_photo_album(nomearquivo, tile, idevento, prefix='bloco')
    except AttributeError,e:
        print 'Image tile not found for photo: %s' % photo.plone_path

def map_audio(old_obj, audio):
    plone_uid = old_obj.UID()
    audio.plone_uid = plone_uid
    file_baixa = old_obj.getArquivoBaixa()
    file = old_obj.getArquivoAlta()
    if not file:
        file = file_baixa
    filename = file.filename.decode('utf-8').encode('iso8859-1','ignore')
    if not filename:
        filename = 'audio.mp3'
    audio_filename = plone_uid + '-audio.mp3' 
    audio.file = audio_filename
    audio.added = int(old_obj.created().timeTime())
    audio.title = old_obj.Title().decode('utf-8').encode('iso8859-1','ignore')
    audio.file_name = filename
    audio.photo_name = ''
    audio.audio_video = 1 # 0 - media type audio
    audio.addinfo = old_obj.getResumo().decode('utf-8').encode('iso8859-1','ignore')
    audio.highlight = 0
    if old_obj.getPhysicalPath()[3] == 'conversa':
        audio.category = 2
    else:
        audio.category = 0
    audio.reporter = ''
    audio.photo = ''
    audio.link = ''
    audio.frequence = ''
    audio.rating = 0.0
    audio.votes = 0
    audio.published = 1
    audio.fileext = 'mp3'
    audio.order = 0
    audio.keywords = ''
    audio.hits = 0
    audio.views = 0
    audio.plone_path = '/'.join(old_obj.getPhysicalPath()[3:])
    audio_path = AUDIO_PATH + '/' + audio_filename
    write_file(audio_path, file)

def map_video(old_obj, video):
    plone_uid = old_obj.UID()
    video.plone_uid = plone_uid
    imagem = old_obj.getImagem()
    file_baixa = old_obj.getArquivoBaixa()
    file = old_obj.getArquivoAlta()
    if not file:
        file = file_baixa
    filename = file.filename.decode('utf-8').encode('iso8859-1','ignore')
    if not filename:
        filename = 'video.flv'
    video_filename = plone_uid + '-video.flv' 
    video.file = video_filename
    video.added = int(old_obj.created().timeTime())
    video.title = old_obj.Title().decode('utf-8').encode('iso8859-1','ignore')
    video.file_name = filename
    imagem_name = plone_uid + '-video-preview.jpg' 
    video.photo_name = imagem_name
    video.audio_video = 0 # 0 - media type video
    video.addinfo = old_obj.getResumo().decode('utf-8').encode('iso8859-1','ignore')
    video.highlight = 0
    video.category = 0
    video.reporter = ''
    video.photo = ''
    video.link = ''
    video.frequence = ''
    video.rating = 0.0
    video.votes = 0
    video.published = 1
    video.fileext = 'flv'
    video.order = 0
    video.keywords = ''
    video.hits = 0
    video.views = 0
    video.plone_path = '/'.join(old_obj.getPhysicalPath()[3:])
    video_path = VIDEO_PATH + '/' + video_filename
    write_file(video_path, file)
    imagem_path = VIDEO_PATH + '/' + imagem_name
    write_file(imagem_path, imagem)

def create_news_relations(old_obj, noticia, reverse=False):
    conn = db.get()
    session = conn.Session()
    session.flush()
    noticia_sqlid = noticia.storyid
    noticia_uid = old_obj.UID()

    for item in old_obj.getRelatedItems():
        related_desc = map_type.get(item.portal_type)
        related_uid = item.UID()
        if related_desc == 'galeria':
            field_sqlid = 'idevento'
            related_type = db.NewAlbum
        elif related_desc == 'noticias':
            field_sqlid = 'storyid'
            related_type = db.NewNoticia
        else:
            field_sqlid = 'xfid'
            related_type = db.NewMedia

        related = session.query(related_type).filter_by(plone_uid=related_uid).first()
        if related is None:
            continue
        related_sqlid = getattr(related, field_sqlid)

        relation_direct = session.query(db.NewRelation).filter_by(
                content_plone_uid=noticia_uid,
                related_plone_uid=related_uid).first()
        if relation_direct is None:
            relation_direct = db.NewRelation()
            session.add(relation_direct)
        relation_direct.idcontend = noticia_sqlid
        relation_direct.modulecontend = 'noticias'
        relation_direct.idrelated = related_sqlid
        relation_direct.modulerelated = related_desc
        relation_direct.content_plone_uid = noticia_uid
        relation_direct.related_plone_uid = related_uid

        if reverse is True:
            relation_reverse = session.query(db.NewRelation).filter_by(
                    content_plone_uid=related_uid,
                    related_plone_uid=noticia_uid).first()
            if relation_reverse is None:
                relation_reverse = db.NewRelation()
                session.add(relation_reverse)
            relation_reverse.idcontend = related_sqlid
            relation_reverse.modulecontend = related_desc
            relation_reverse.idrelated = noticia_sqlid
            relation_reverse.modulerelated = 'noticias'
            relation_reverse.content_plone_uid = related_uid
            relation_reverse.related_plone_uid = noticia_uid

def map_noticia(old_obj, noticia):
    noticia.plone_uid = old_obj.UID()
    noticia.uid = 1
    title = old_obj.Title().decode('utf-8').encode('iso8859-1','ignore')
    noticia.title = title
    noticia.created = int(old_obj.created().timeTime())
    noticia.published = int(old_obj.created().timeTime())
    noticia.expired = 0
    noticia.hostname = ''
    noticia.nohtml = 0
    noticia.nosmiley = 0
    hometext = old_obj.Description().decode('utf-8').encode('iso8859-1','ignore')
    noticia.hometext = hometext
    noticia.hometext_man = ''
    try:
        bodytext = old_obj.getText().decode('utf-8').encode('iso8859-1','ignore')
    except UnicodeDecodeError, e:
        bodytext = ''
        print noticia.plone_uid, noticia.title, '/'.join(old_obj.getPhysicalPath()[3:])
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
    if old_obj.getDestaque() is True:
        noticia.destaque = 1
    else:
        noticia.destaque = 0
    noticia.storder = 1000
    noticia.wphoto = 0
    noticia.sttype = 0
    noticia.article = 0
    noticia.articlefont = ''
    noticia.approver = 1
    noticia.regiao = '0'
    noticia.plone_path = '/'.join(old_obj.getPhysicalPath()[3:])
    create_news_relations(old_obj, noticia)

def migrate_content(context, portal_type, mapper, map_func, debug=False):
    """Migrate portal_type content from Plone to SQLDatabase, using map_content function
    context: Plone Site object
    """
    results = query_catalog(context, portal_type)
    conn = db.get()
    session = conn.Session()
    debug_text = 'Begin Import: %s - %s %s' % (portal_type ,str(DateTime()),'\n')
    for item in results:
        old_obj = item.getObject()
        UID = old_obj.UID()
        new_obj = session.query(mapper).filter_by(plone_uid=UID).first()
        if new_obj is None:
            new_obj = mapper()
            session.add(new_obj)
        new_obj = map_func(old_obj, new_obj)
        if debug is True:
            debug_text += old_obj.Title() + ' | ' \
            + str(old_obj.created()) + ' | ' \
            + '/'.join(old_obj.getPhysicalPath()[3:]) + '\n'

    debug_text += 'End Import: %s - %s %s' % (portal_type, str(DateTime()), '\n')
    print debug_text
    return debug_text

def migrate_noticia(context):
    """Migrate Noticia content from Plone to SQLDatabase.
    context: Plone Site object
    """
    return migrate_content(context, 'Noticia', db.NewNoticia, map_noticia)

def migrate_album(context):
    """Migrate Photo Album content from Plone to SQLDatabase and filesystem.
    context: Plone Site object
    """
    return migrate_content(context, 'ATPhotoAlbum', db.NewAlbum, map_album)

def migrate_audio(context):
    """Migrate Audio content from Plone to SQLDatabase and filesystem.
    context: Plone Site object
    """
    return migrate_content(context, 'Audio', db.NewMedia, map_audio)

def migrate_video(context):
    """Migrate Video content from Plone to SQLDatabase and filesystem.
    context: Plone Site object
    """
    return migrate_content(context, 'Video', db.NewMedia, map_video)

def migrate_relation(context):
    """Rebuild relation from Noticias to Album, Video and Audio content.
    context: Plone Site object
    """
    migrade_noticia(context)

def migrate_all(context):
    """Migrate all content: Video, Album and Photos, Audio, Notiicas and Relation.
    context: Plone Site object
    """
    migrate_album(context)
    migrate_audio(context)
    migrate_video(context)
    migrate_noticia(context)
