from fastapi import FastAPI, File, UploadFile
import uvicorn
from io import BytesIO
from pathlib import Path
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image
from typing import Optional
from fastapi.staticfiles import StaticFiles
from preprocessing_module import preprocess_image_manually


app = FastAPI()

# Configura FastAPI para servir archivos estáticos desde la carpeta '_uploads'
app.mount("/_uploads", StaticFiles(directory="_uploads"), name="uploads")

# Obtén la ruta del directorio donde está este script
current_dir = Path(__file__).parent
IMG_SIZE = (180, 180)

def load_model(current_dir):
    # Construir una ruta para un archivo llamado 'file.txt' en un subdirectorio llamado 'data'
    model_path = current_dir / "models" / "modelo_xception_cats_vs_dogs"

    # Cargar el modelo (suponiendo que ya está entrenado y guardado como 'model.h5')
    try:
        modelo = keras.models.load_model(model_path)
    except Exception as e:
        print(f"Error al cargar el modelo: {e}")

    # Definir el tamaño de entrada de la imagen (según fue entrenado el modelo)
    if modelo is None:
        raise RuntimeError("No se pudo cargar el modelo.")
    return modelo

modelo = load_model(current_dir)


def jpg_verify(file:UploadFile) -> Optional[dict]:
        try:
        # Leer los primeros bytes del archivo
            file.file.seek(0)  # Asegurarse de estar al inicio del archivo
            header = file.file.read(10)  # Leer los primeros 10 bytes para buscar "JFIF"
            file.file.seek(0)  # Volver a posicionar el puntero al inicio
            
            # Convertir a string en caso de que los bytes contengan texto
            if b'JFIF' in header:
                return True  # Si contiene "JFIF", es un archivo JPEG válido
            else:
                return False  # No es un archivo JPEG válido
        except AttributeError:
        # Manejar errores relacionados con la ausencia de atributos
            print("Error: El archivo no tiene los atributos correctos para ser procesado.")
            return None
        except OSError as e:
            # Captura errores relacionados con el sistema de archivos, como la lectura de archivos corruptos
            print(f"Error de sistema de archivos: {e}")
            return None
        except Exception as e:
            # Captura cualquier otra excepción general no prevista
            print(f"Error inesperado: {e}")
            return None



# Función para cargar y preprocesar la imagen
def read_imagefile(file):
    pass


@app.get("/")
async def root():
    return {"message": "Hello World"}

# Ruta para cargar y clasificar una imagen
@app.post("/predict/")
async def predict_image(file: UploadFile = File(...)):
    if jpg_verify(file) is False:
        return {"error": "El archivo no es una imagen JPEG válida."}
    
    try:
        file_content = await file.read()  # Lee el archivo en memoria
        if not file_content:  # Verifica si el archivo está vacío
            return {"error": "El archivo está vacío."}
        
        # Guardar la imagen temporalmente
        temp_image_path = current_dir / "temp_image.jpg"  # Ruta temporal
        with open(temp_image_path, "wb") as buffer:
            buffer.write(file_content)  # Guarda el contenido previamente leído

        # Llamar a preprocess_image_manually con la ruta temporal
        image_ready = preprocess_image_manually(str(temp_image_path), image_size=(180, 180), color_mode="rgb")

        

        # Realizar la predicción con el modelo
        prediction = modelo.predict(image_ready)
        print("predicción hecha", prediction)

        # Asumiendo que el modelo devuelve un valor cercano a 0 para 'cat' y cercano a 1 para 'dog'
        predicted_class = "dog" if prediction[0][0] > 0.5 else "cat"

        # Supongamos que guardas la imagen en _uploads
        image_path = f"_uploads/{file.filename}"

        with open(image_path, "wb") as buffer:
            buffer.write(file_content)  # Guarda el contenido previamente leído

        image_url = f"http://127.0.0.1:8000/_uploads/{file.filename}"

        # Opcional: Eliminar el archivo temporal después de su uso
        temp_image_path.unlink(missing_ok=True)  # Elimina el archivo si existe

        return {"prediction": predicted_class, "image_url": image_url}
    except Exception as e:
        return {"error": f"Error procesando la imagen: {e}"}


if __name__ == "__main__":
    # Esto inicia el servidor cuando ejecutas el script de Python
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)