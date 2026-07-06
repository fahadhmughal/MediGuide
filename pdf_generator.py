from fpdf import FPDF


def generate_pdf(specialists, questions) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    def line(text, size=12, bold=False, italic=False):
        pdf.set_x(pdf.l_margin)
        style = ("B" if bold else "") + ("I" if italic else "")
        pdf.set_font("Helvetica", style, size)
        pdf.multi_cell(0, 8, text)

    line("MediGuide - Appointment Preparation", size=16, bold=True)
    pdf.ln(4)

    line("Recommended Specialist(s):", bold=True)
    for s in specialists or []:
        line(f"- {s}")
    pdf.ln(4)

    line("Questions to Ask Your Doctor:", bold=True)
    for i, q in enumerate(questions or [], 1):
        line(f"{i}. {q}")
    pdf.ln(6)

    line("This is not medical advice. Consult a licensed physician.", size=10, italic=True)

    return bytes(pdf.output(dest="S"))
