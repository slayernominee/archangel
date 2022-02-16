var languages = document.getElementsByClassName("available_language");
var lang_replacements = { {% for l in lang_replacements %}'{{l}}': '{{lang_replacements[l]}}',{% endfor %} };
for (var i = 0; i < languages.length; i++) {
    current = languages[i].innerHTML;
    current = current.replace('\n                ', '');
    current = current.replace('\n            ', '');
    current = current.replace(' ', '');
    console.log(current);
    if (current.toLowerCase() in lang_replacements) {
        languages[i].innerHTML = '<img src="' + lang_replacements[current.toLowerCase()] + '" alt="' + current + '"></img>';
    }
}