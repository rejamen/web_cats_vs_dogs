import reflex as rx
from frontend.components.navbar import navbar
from frontend.components.image_upload_button import upload_button
from frontend.state.state import AppState

from rxconfig import config


api_url = "http://127.0.0.1:8000/predict/"



def index():
    """Vista principal de la aplicación."""
    return rx.vstack(
        upload_button(),  # Botón para subir imágenes
        rx.cond(
            AppState.img != "",  # Mostrar la imagen apenas esté disponible
            rx.image(src=AppState.img),
        ),
        rx.cond(
            (AppState.prediction != "") & (AppState.prediction == "cat"),
            rx.text("Esto es un gato"),
            rx.text("Esto es un perro"),
        ),
        padding="5em",
    )


app = rx.App(State=AppState)
app.add_page(index)