from django import forms

class UploadFileForm(forms.Form):
    abrasivos_file = forms.FileField(label='Archivo de Abrasivos')
    rodillos_file = forms.FileField(label='Archivo de Rodillos', required=False)
    rapifix_file = forms.FileField(label='Archivo de Rapifix', required=False)
    fijapel_file = forms.FileField(label='Archivo de Fijapel', required=False)
    pintura_file = forms.FileField(label='Archivo de Pintura', required=False)



