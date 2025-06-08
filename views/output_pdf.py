import flet as ft
from database import SessionLocal
from database.models import Documentos

class OutputPDFView:
    def __init__(self, page, theme_button, doc_id):
        self.page = page
        self.theme_button = theme_button
        self.doc_id = doc_id

    def build(self):
        session = SessionLocal()
        doc = session.query(Documentos).filter_by(id=self.doc_id).first()
        session.close()

        if doc and doc.archivo:
            return ft.View(
                route=f"/output_pdf/{self.doc_id}",
                controls=[
                    ft.AppBar(title=ft.Text("Vista del Documento"), actions=[self.theme_button]),
                    ft.Text(f"Documento: {doc.archivo}"),
                    ft.IFrame(src=f"/assets/docs/{doc.archivo}", width=800, height=600),
                    ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/documents")),
                ]
            )
        else:
            return ft.View(
                route=f"/output_pdf/{self.doc_id}",
                controls=[
                    ft.Text("❌ Documento no disponible"),
                    ft.ElevatedButton("Volver", on_click=lambda e: self.page.go("/documents")),
                ]
            )
