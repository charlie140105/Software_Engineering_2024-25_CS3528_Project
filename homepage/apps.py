from django.apps import AppConfig

class MyappConfig(AppConfig):
    name = 'homepage'

    def ready(self):
        import homepage.signals
