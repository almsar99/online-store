from django import forms

from catalog.models import Product

FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар",
]


class ProductForm(forms.ModelForm):

    class Meta:

        model = Product

        fields = [
            "name",
            "description",
            "image",
            "category",
            "price",
        ]

        error_messages = {
            "image": {
                "invalid_image": ("Загрузите корректное " "изображение PNG или JPEG.")
            }
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            field.widget.attrs.update({"class": "form-control"})

    def clean(self):

        cleaned_data = super().clean()

        name = cleaned_data.get("name")

        description = cleaned_data.get("description")

        if name:

            for word in FORBIDDEN_WORDS:

                if word.lower() in name.lower():

                    raise forms.ValidationError("Название содержит запрещенное слово.")

        if description:

            for word in FORBIDDEN_WORDS:

                if word.lower() in description.lower():

                    raise forms.ValidationError("Описание содержит запрещенное слово.")

        return cleaned_data

    def clean_price(self):

        price = self.cleaned_data.get("price")

        if price is not None and price < 0:

            raise forms.ValidationError("Цена не может быть отрицательной.")

        return price

    def clean_image(self):

        image = self.cleaned_data.get("image")

        if image:

            if image.size > 5 * 1024 * 1024:

                raise forms.ValidationError(
                    "Размер изображения " "не должен превышать 5 МБ."
                )

            valid_formats = [
                ".jpg",
                ".jpeg",
                ".png",
            ]

            if hasattr(image, "name"):

                image_name = image.name.lower()

                if not any(image_name.endswith(ext) for ext in valid_formats):

                    raise forms.ValidationError(
                        "Допустимы только " "PNG и JPEG изображения."
                    )

        return image
