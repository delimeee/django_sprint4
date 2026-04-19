from django.views.generic import TemplateView


class Rules(TemplateView):
    template_name = 'pages/rules.html'


class About(TemplateView):
    template_name = 'pages/about.html'
