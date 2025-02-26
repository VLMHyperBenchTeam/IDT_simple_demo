from pypdf import PdfWriter


def pdf_to_mappings(pdf_in_path: str, mapping_list: list, output_file_path):
    """The function takes PDF_in from path and saves its pages with correct order by mapping_list"""
    writer = PdfWriter()
    writer.append(fileobj=pdf_in_path, pages=mapping_list)

    writer.write(output_file_path)
    writer.close()
