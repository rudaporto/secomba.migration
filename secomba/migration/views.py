from Products.Five import BrowserView

from secomba.migration import run

class NoticiaMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_noticia(self.context)

class AlbumMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_album(self.context)

class PhotoMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_photo(self.context)

class AudioMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_audio(self.context)

class VideoMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_video(self.context)

class RelationMigrationView(BrowserView):

    def __call__(self):
        return run.migrate_relation(self.context)

