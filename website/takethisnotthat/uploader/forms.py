from django import forms

class DocumentForm(forms.Form):
	docfile = forms.FileField(label='Select a PDF file',
		max_length = 14)