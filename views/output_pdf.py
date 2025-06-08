import os
import flet as ft
from database import SessionLocal
from database.models import Documentos
from pdf2image import convert_from_path

def pdf_to_pngs(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path)
    for i, image in enumerate(images):
        output_file = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(output_file, 'PNG')

class OutputPDFView:
    def __init__(self, page: ft.Page, theme_button: ft.Control, doc_id: int):
        self.page = page
        self.theme_button = theme_button
        self.doc_id = doc_id

    def build(self) -> ft.View:
        session = SessionLocal()
        doc = session.query(Documentos).filter_by(id=self.doc_id).first()
        session.close()

        if not doc or not doc.archivo:
            return ft.View(
                route=f"/output_pdf/{self.doc_id}",
                controls=[
                    ft.Text("Documento no encontrado"),
                    ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/documents"))
                ]
            )

        pdf_path = f"assets/docs/{doc.archivo}"
        output_folder = f"assets/output_pdf/{self.doc_id}"

        if not os.path.exists(output_folder) or not os.listdir(output_folder):
            pdf_to_pngs(pdf_path, output_folder)

        image_files = sorted(os.listdir(output_folder))

        controls = [
            ft.AppBar(title=ft.Text("Vista Documento"), actions=[self.theme_button]),
            ft.Text(f"Documento: {doc.archivo}"),
            ft.Text("Mantén pulsada la imagen para descargarla (en móvil)."),
        ]

        for img_file in image_files:
            image_path = f"/output_pdf/{self.doc_id}/{img_file}"
            controls.append(ft.Image(src=image_path, width=300))
            controls.append(
                ft.ElevatedButton(
                    f"Abrir {img_file}",
                    on_click=lambda e, url=image_path: self.page.launch_url(url)
                )
            )

        controls.append(
            ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/documents"))
        )

        return ft.View(route=f"/output_pdf/{self.doc_id}", controls=controls)
