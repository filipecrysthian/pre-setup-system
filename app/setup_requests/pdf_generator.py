"""
Gerador de PDF para documentos de PRÉ SETUP.
Utiliza ReportLab para criar PDFs padronizados.
"""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def generate_pre_setup_pdf(pre_setup, model, items_data, user, output_path):
    """
    Gera o PDF padronizado de pré setup.

    Args:
        pre_setup: Objeto PreSetup com dados gerais
        model: Objeto ProductModel
        items_data: Lista de dicts com template_item, status e observation
        user: Objeto User responsável
        output_path: Caminho completo para salvar o PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=6,
        textColor=colors.HexColor('#1a237e'),
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=4,
        textColor=colors.HexColor('#37474f'),
        fontName='Helvetica'
    )

    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor('#1565c0'),
        fontName='Helvetica-Bold'
    )

    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#757575'),
        alignment=1  # Center
    )

    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        wordWrap='CJK'
    )

    # --- Cabeçalho ---
    elements.append(Paragraph(f'PRÉ SETUP - {model.name}', title_style))
    elements.append(Spacer(1, 2 * mm))

    # Informações gerais
    now = datetime.now()
    info_data = [
        ['Data/Hora:', now.strftime('%d/%m/%Y %H:%M:%S')],
        ['Responsável:', user.name],
        ['Modelo:', model.name],
        ['Tipo:', model.product_type],
        ['Estação:', pre_setup.station],
        ['Nº de Baias:', str(pre_setup.num_bays)],
        ['Status Geral:', pre_setup.overall_status],
    ]

    info_table = Table(info_data, colWidths=[80, 400])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#37474f')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#212121')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 8 * mm))

    # --- Tabela de Itens ---
    elements.append(Paragraph('Itens do Pré Setup', header_style))

    # Cabeçalho da tabela
    table_data = [['Item', 'Qtd', 'Status', 'Observação']]

    # Multiplicador de quantidade por tipo de produto
    if model.product_type in ['Notebook', 'Tiny']:
        qty_multiplier = 4
    else:
        qty_multiplier = 3

    # Contadores
    total_ok = 0
    total_pending = 0
    total_na = 0

    for data in items_data:
        material = data['material']
        status = data['status']
        obs = data['observation'] or ''

        if status == 'OK':
            total_ok += 1
        elif status == 'PENDENTE':
            total_pending += 1
        elif status == 'N/A':
            total_na += 1

        display_qty = material.quantity * qty_multiplier * pre_setup.num_bays
        table_data.append([
            Paragraph(material.name, cell_style),
            str(display_qty),
            status,
            Paragraph(obs, cell_style)
        ])

    # Definir larguras das colunas: Item, Qtd, Status, Observação
    col_widths = [200, 40, 70, 170]

    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        # Cabeçalho
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Corpo da tabela
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),  # Quantidade centralizada
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Status centralizado
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

        # Bordas
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdbdbd')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1565c0')),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    # Cores alternadas nas linhas
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f5f5f5'))
            ]))
        # Colorir status
        status_val = table_data[i][2] if isinstance(table_data[i][2], str) else ''
        if status_val == 'OK':
            items_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#2e7d32')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
        elif status_val == 'PENDENTE':
            items_table.setStyle(TableStyle([
                ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#e65100')),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))

    elements.append(items_table)
    elements.append(Spacer(1, 8 * mm))

    # --- Resumo ---
    elements.append(Paragraph('Resumo', header_style))

    total_items = len(items_data)
    summary_data = [
        ['Total de Itens', str(total_items)],
        ['OK', str(total_ok)],
        ['PENDENTE', str(total_pending)],
        ['N/A', str(total_na)],
    ]

    summary_table = Table(summary_data, colWidths=[120, 60])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdbdbd')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        # Cores dos status no resumo
        ('TEXTCOLOR', (1, 1), (1, 1), colors.HexColor('#2e7d32')),  # OK verde
        ('TEXTCOLOR', (1, 2), (1, 2), colors.HexColor('#e65100')),  # PENDENTE laranja
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15 * mm))

    # --- Rodapé ---
    elements.append(Paragraph(
        'Documento gerado automaticamente pelo Sistema de Pré Setup - Engenharia de Teste',
        footer_style
    ))

    # Construir o documento
    doc.build(elements)
