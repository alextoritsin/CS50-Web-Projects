import random
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect, render
from django import forms

from . import util


class SearchForm(forms.Form):
    entry_name = forms.CharField(label='', widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search Encyclopedia'
    }))


class CreateForm(forms.Form):
    def validate_title(value):
        if value in util.list_entries():
            raise ValidationError(
                _('%(value)s title is already exists, create another one.'),
                code='invalid',
                params={'value': value}
            )

    title = forms.CharField(label='Entry title:',
                            widget=forms.TextInput(attrs={
                                'class': 'form-control',
                                'autofocus': 'autofocus'
                            }),
                            validators=[validate_title])
    content = forms.CharField(label="Markdown text:",
                              widget=forms.Textarea(attrs={
                                  'class': 'form-control'
                              }))


class EditForm(CreateForm):
    title = forms.CharField(required=False)


def index(request):
    """Render index page"""
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm()
    })


def entry(request, entry_name):
    """Render page for the entry or error page"""
    title = None
    entry = util.get_entry(entry_name)
    if entry:
        title, html = util.parse_md(entry)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "html": html,
            "form": SearchForm()
        })
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "form": SearchForm()
    })


def search(request):
    """Render search results"""
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            entry = form.cleaned_data["entry_name"]
            # check if the entry in list
            if util.get_entry(entry):
                return redirect('entry', entry)
            else:
                pages = util.list_entries()
                res = [item for item in pages if entry.lower() in item.lower()]
                if res:
                    return render(request, "encyclopedia/search.html", {
                        "results": res,
                        "form": SearchForm()
                    })
                else:
                    return render(request, "encyclopedia/entry.html", {
                        "title": None,
                        "form": SearchForm()
                    })

    return render(request, "encyclopedia/search.html", {
        "form": SearchForm()
    })


def newpage(request):
    """Render page for creating new entry"""
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            content = content.replace("\r\n", "\n")
            util.save_entry(title, content)
            return redirect('entry', title)
        else:
            return render(request, 'encyclopedia/newpage.html', {
                "form": SearchForm(),
                "newform": form
            })

    return render(request, "encyclopedia/newpage.html", {
        "form": SearchForm(),
        "newform": CreateForm()
    })


def edit_entry(request, entry_name):
    """Generate page for editing entry content"""
    content = util.get_entry(entry_name)
    data = {"content": content}
    form = EditForm(data)
    if request.method == "POST":
        form = EditForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            title, __ = util.parse_md(content)
            util.save_entry(title, content.replace("\r\n", "\n"))
            return redirect("entry", title)

    return render(request, 'encyclopedia/edit_entry.html', {
        "form": SearchForm(),
        "edit_form": form,
        "title": entry_name
    })


def random_entry(request):
    """Generate random entry page"""
    choice = random.choice(util.list_entries())
    return redirect("entry", choice)
