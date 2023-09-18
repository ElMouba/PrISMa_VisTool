import pdfkit
from jinja2 import Template

OPTIONS = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': 'UTF-8'
        }

class OverviewPDF():
    def __init__(self, template_file = 'static/template.html', 
                 css_file =  'static/styles.css',
                 models_output:dict = None,
                 submission_form:dict = None) -> None:
        
        self.html_template = template_file
        self.css_file = css_file

        self.template_content = self._extract_content(template_file)
        self.css_content = self._extract_content(css_file)
        
        self.models_output = models_output
        self.submission_form = submission_form
    def _get_html(self):
        variables = {
                    'data': self.models_output['model_outputs'],
                    'form': self.submission_form
                    }
        template = Template(self.template_content)
        rendered_html = template.render(variables)

        # Combine rendered HTML with inline CSS
        html_with_css = f"{rendered_html}<style>{self.css_content}</style>"

        return html_with_css

    def save_pdf(self, output_name = 'output.pdf'):
        html = self._get_html()
        # Convert rendered HTML to PDF
        pdfkit.from_string(html, 'output.pdf', options=OPTIONS)

    def get_pdfbytes(self):
        html = self._get_html()
        pdf_bytes = pdfkit.from_string(html, False, options={'quiet': ''})
        return pdf_bytes
    
    def _extract_content(self, path:str):
        with open(path, 'r') as file:
            content = file.read()
        return content