from django import forms
from .models import InboundLetter, Sender

class InboundLetterForm(forms.ModelForm):
    class Meta:
        model = InboundLetter
        fields = ["title", "original_ref_no", "sender", "letter_date", "pdf_file", "description", "notes"]
        widgets = {
            "letter_date": forms.DateInput(attrs={"type": "date", "class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "title": forms.TextInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "original_ref_no": forms.TextInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "sender": forms.Select(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "pdf_file": forms.FileInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
        }

class SenderForm(forms.ModelForm):
    class Meta:
        model = Sender
        fields = ["name", "institution", "contact"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "institution": forms.TextInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
            "contact": forms.TextInput(attrs={"class": "w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"}),
        }
