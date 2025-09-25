import os
from datetime import datetime
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.models.order import Order


def generate_orders_pdf(orders: List[Order], filename: str = None) -> str:
    """
    Generate a PDF report of all orders and save it to the reports directory.
    
    Args:
        orders: List of Order objects to include in the report
        filename: Optional custom filename for the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_report_{timestamp}.pdf"
    
    # Ensure filename ends with .pdf
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.darkblue
    )
    
    # Add title
    title = Paragraph("Orders Report", title_style)
    elements.append(title)
    
    # Add generation date
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=12,
        alignment=1,  # Center alignment
        spaceAfter=20
    )
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    date_para = Paragraph(date_text, date_style)
    elements.append(date_para)
    
    # Add summary
    summary_style = ParagraphStyle(
        'SummaryStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        alignment=1
    )
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders if order.total_amount)
    summary_text = f"Total Orders: {total_orders} | Total Amount: ${total_amount:.2f}"
    summary_para = Paragraph(summary_text, summary_style)
    elements.append(summary_para)
    
    elements.append(Spacer(1, 20))
    
    if not orders:
        # No orders message
        no_orders_style = ParagraphStyle(
            'NoOrdersStyle',
            parent=styles['Normal'],
            fontSize=16,
            alignment=1,
            textColor=colors.red
        )
        no_orders_para = Paragraph("No orders found.", no_orders_style)
        elements.append(no_orders_para)
    else:
        # Create table data
        table_data = [
            ['Order #', 'Date', 'Status', 'Delivery Type', 'Total Amount', 'Customer', 'Shipping Address']
        ]
        
        for order in orders:
            # Format date
            created_date = order.created_at.strftime('%m/%d/%Y') if order.created_at else 'N/A'
            
            # Get customer info (assuming you have user relationship)
            customer_info = f"User ID: {order.user_id}" if order.user_id else 'N/A'
            
            # Format shipping address
            shipping_address = order.shipping_address or 'N/A'
            if len(shipping_address) > 30:
                shipping_address = shipping_address[:30] + '...'
            
            # Format delivery type
            delivery_type = order.delivery_type.value if order.delivery_type else 'N/A'
            
            # Format status
            status = order.status.value if order.status else 'N/A'
            
            # Format total amount
            total_amount = f"${order.total_amount:.2f}" if order.total_amount else '$0.00'
            
            table_data.append([
                order.order_number or 'N/A',
                created_date,
                status,
                delivery_type,
                total_amount,
                customer_info,
                shipping_address
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1*inch, 1.2*inch, 1*inch, 1*inch, 1.5*inch])
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
    
    # Add footer
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.grey
    )
    footer_text = "Farm Fresh Backend - Orders Management System"
    footer_para = Paragraph(footer_text, footer_style)
    elements.append(footer_para)
    
    # Build PDF
    doc.build(elements)
    
    return filepath


def generate_order_details_pdf(order: Order, filename: str = None) -> str:
    """
    Generate a detailed PDF report for a single order.
    
    Args:
        order: Order object to generate report for
        filename: Optional custom filename for the PDF
        
    Returns:
        str: Path to the generated PDF file
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        order_number = order.order_number or f"order_{order.id}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{order_number}_details_{timestamp}.pdf"
    
    # Ensure filename ends with .pdf
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    filepath = os.path.join(reports_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        alignment=1,
        textColor=colors.darkblue
    )
    
    # Add title
    title = Paragraph(f"Order Details - {order.order_number or 'N/A'}", title_style)
    elements.append(title)
    
    # Order information
    order_info = [
        ['Order Number:', order.order_number or 'N/A'],
        ['Order Date:', order.created_at.strftime('%B %d, %Y at %I:%M %p') if order.created_at else 'N/A'],
        ['Status:', order.status.value if order.status else 'N/A'],
        ['Delivery Type:', order.delivery_type.value if order.delivery_type else 'N/A'],
        ['Total Amount:', f"${order.total_amount:.2f}" if order.total_amount else '$0.00'],
        ['Payment ID:', order.payment_id or 'N/A'],
        ['Shipping Address:', order.shipping_address or 'N/A'],
        ['Shipping State:', order.shipping_state or 'N/A'],
        ['Shipping ZIP:', order.shipping_zip or 'N/A'],
    ]
    
    if order.airport_name:
        order_info.append(['Airport:', order.airport_name])
    if order.airport_code:
        order_info.append(['Airport Code:', order.airport_code])
    
    # Create order info table
    info_table = Table(order_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Add order items if available
    if hasattr(order, 'items') and order.items:
        items_title = Paragraph("Order Items", styles['Heading2'])
        elements.append(items_title)
        elements.append(Spacer(1, 10))
        
        items_data = [['Product', 'Quantity', 'Unit Price', 'Total Price']]
        for item in order.items:
            items_data.append([
                item.product.name if hasattr(item, 'product') and item.product else 'N/A',
                str(item.quantity),
                f"${item.unit_price:.2f}" if item.unit_price else '$0.00',
                f"${item.total_price:.2f}" if item.total_price else '$0.00'
            ])
        
        items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(items_table)
    
    # Build PDF
    doc.build(elements)
    
    return filepath
