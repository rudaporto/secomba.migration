from Products.Five import BrowserView

from run import migrate_noticia

class NoticiaMigrationView(BrowserView):

    def __call__(self):
        return migrate_noticia(self.context)

