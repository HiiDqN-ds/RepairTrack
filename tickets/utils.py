import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from django.contrib.staticfiles import finders


def generate_pdf(ticket):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name="Title", fontSize=20, spaceAfter=20)
    normal = styles["Normal"]

    elements = []

    # Logo
    logo_path = finders.find("images/logo.png")
    if logo_path:
        from reportlab.platypus import Image
        elements.append(Image(logo_path, width=120, height=60))
        elements.append(Spacer(1, 15))

    # Title
    elements.append(Paragraph("<b>Reparaturauftrag / Repair Contract</b>", title_style))

    # Ticket Info
    elements.append(Paragraph(f"<b>Tracking Nummer:</b> {ticket.tracking_id}", normal))
    elements.append(Spacer(1, 10))

    # Client table
    data = [
        ["Kunde", f"{ticket.client.first_name} {ticket.client.last_name}"],
        ["Email", ticket.client.email],
        ["Telefon", ticket.client_phone or "-"],
        ["Gerät", f"{ticket.device_type} {ticket.device_model}"],
        ["Problem", ticket.description],
        ["Preis", f"{ticket.estimated_price} €"]
    ]

    table = Table(data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('BOX', (0,0), (-1,-1), 1, colors.grey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # Agreement text
    agreement_text = """
    ALLGEMEINE GESCHÄFTSBEDINGUNGEN
    Bei der Reparatur Ihres Mobiltelefons, Tablets oder Notebooks kann es zum Verlust aller gespeicherten Daten kommen.
    Des Weiteren kann es bei bestimmten Reparaturen zu einem Board – oder Softwareschaden kommen, welcher sich als blue oder red screen zu
    erkennen gibt. Bei Sturzschäden können Folgeschäden entstehen, welche erst im Laufe der Reparatur sichtbar werden. Wenn durch den Sturz das
    Backcover / der Rahmen verzogen sind, kann es dazu kommen, dass das neue Display nicht mehr einhundertprozentig passt, wofür TaniTech nicht
    haftbar gemacht werden kann. Die Touchscreen Reparatur an Ihrem Gerät ist eine kostengünstige Alternative, die wir für Sie anbieten,
    beschädigt ist. Selbst wenn Ihr Smartphone / Tablet voll funktionsfähig ist, ist nicht auszuschließen, dass es nicht zu Folgeschäden gekommen ist.
    können für daraus entstandene Schäden keine Haftung übernehmen!
    Wenn Ihr Smartphone „gejailbreakt, gerootet“ ist, kann es nach einer Reparatur zu Folgeschäden kommen, wie z.B.: Ausfall vom W-Lan, Akkuleistung
    lässt nach, Hörmuschel funktioniert nicht, das Display weist Pixelfehler auf etc. TaniTech kann für daraus entstandene Schäden keine Haftung
    übernehmen! TaniTech
    Eine Hersteller-Garantie kann durch die Reparatur erlöschen. Die von uns verbauten Ersatzteile gelten nach Einbau nicht mehr als neu und sind somit
    von der Rückgabe ausgeschlossen. Sie erhalten bis zu 24 Monate Garantie auf viele unsere Reparaturen.
    • Wenn das Gerät einen Wasserschaden aufweist, können wir für die Funktionstüchtigkeit nicht garantieren. Geräte die einen Wasserschaden
    aufweisen, können trotz erfolgreicher Reparatur auch Tage , Wochen sogar Monate danach einen erneuten Schaden aufweisen. Sie erhalten bis zu
    24 Monate Garantie auf unsere Reparaturen ausgeschlossen bei Wasserschäden.
    Achtung: Garantieansprüche auf Displays entfallen, wenn diese Beschädigt werden!
    Garantien entfallen bei Schäden an unseren Ersatzteilen. Ersatzteile die wir verbauen, gehören bis zur vollständigen Bezahlung der TaniTech.
    unterliegt den Datenschutzbestimmungen nach §4 BDSG. Ihre Daten werden für Garantieansprüche in unserem Warenwirtschaftsprogramm erfasst
    und nicht an Dritte weitergegeben. Wenn das Gerät 4 Wochen nach Reparatur nicht abgeholt wird, erlaubt sich die TaniTech
    Aufbewahrungspauschale in Höhe von 1% vom Gesamt Reparaturpreis pro Tag zu berechnen.
    Mit Ihrer Auftragserteilung bestätigen Sie die Kenntnisnahme und Anerkennung unserer AGB
    Mit der Abgabe des Geräts bestätigt der Kunde, dass alle Angaben korrekt sind.
    Tanitech übernimmt keine Haftung für Datenverlust. Reparaturen erfolgen nur nach Freigabe.
    """

    elements.append(Paragraph(agreement_text, normal))
    elements.append(Spacer(1, 40))

    # Signatures
    elements.append(Paragraph("Kunde Unterschrift: ____________________________", normal))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Techniker Unterschrift: ________________________", normal))

    doc.build(elements)
    buffer.seek(0)
    return buffer
