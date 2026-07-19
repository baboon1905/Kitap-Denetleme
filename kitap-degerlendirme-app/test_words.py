import pypdf

pdf = pypdf.PdfReader("uploads/Anahtar_Acmaz.pdf")
text = ""
for page in pdf.pages:
    text += page.extract_text()

text_lower = text.lower()

# Search
words_to_find = ["defalarca", "yayınevi", "defa", "yayın"]
for word in words_to_find:
    if word in text_lower:
        count = text_lower.count(word)
        print(f"'{word}' found: {count} times")
