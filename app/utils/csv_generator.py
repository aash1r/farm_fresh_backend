import os
import csv
from datetime import datetime
from typing import List
from app.models.order import Order


def generate_orders_csv(orders: List[Order], filename: str = None) -> str:
    """
    Generate a CSV report of all orders and save it to the reports directory.
    
    Args:
        orders: List of Order objects to include in the report
        filename: Optional custom filename for the CSV
        
    Returns:
        str: Path to the generated CSV file
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_report_{timestamp}.csv"
    
    # Ensure filename ends with .csv
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    filepath = os.path.join(reports_dir, filename)
    
    # Define CSV headers
    headers = [
        'Order Number',
        'Order Date',
        'Status',
        'Delivery Type',
        'Total Amount',
        'Customer ID',
        'Payment ID',
        'Shipping Address',
        'Shipping State',
        'Shipping ZIP',
        'Airport Name',
        'Airport Code',
        'Is Mango Delivery',
        'Created At',
        'Updated At'
    ]
    
    # Write CSV file
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        writer.writerow(headers)
        
        # Write data rows
        for order in orders:
            # Format date
            order_date = order.created_at.strftime('%Y-%m-%d') if order.created_at else 'N/A'
            created_at = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else 'N/A'
            updated_at = order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else 'N/A'
            
            # Format status and delivery type
            status = order.status.value if order.status else 'N/A'
            delivery_type = order.delivery_type.value if order.delivery_type else 'N/A'
            
            # Format total amount
            total_amount = f"{order.total_amount:.2f}" if order.total_amount else '0.00'
            
            row = [
                order.order_number or 'N/A',
                order_date,
                status,
                delivery_type,
                total_amount,
                order.user_id or 'N/A',
                order.payment_id or 'N/A',
                order.shipping_address or 'N/A',
                order.shipping_state or 'N/A',
                order.shipping_zip or 'N/A',
                order.airport_name or 'N/A',
                order.airport_code or 'N/A',
                'Yes' if order.is_mango_delivery else 'No',
                created_at,
                updated_at
            ]
            
            writer.writerow(row)
    
    print(f"CSV report generated with {len(orders)} orders at: {filepath}")
    return filepath


def generate_order_details_csv(order: Order, filename: str = None) -> str:
    """
    Generate a detailed CSV report for a single order including order items.
    
    Args:
        order: Order object to generate report for
        filename: Optional custom filename for the CSV
        
    Returns:
        str: Path to the generated CSV file
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        order_number = order.order_number or f"order_{order.id}"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{order_number}_details_{timestamp}.csv"
    
    # Ensure filename ends with .csv
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    filepath = os.path.join(reports_dir, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write order information section
        writer.writerow(['ORDER INFORMATION'])
        writer.writerow(['Field', 'Value'])
        writer.writerow(['Order Number', order.order_number or 'N/A'])
        writer.writerow(['Order Date', order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else 'N/A'])
        writer.writerow(['Status', order.status.value if order.status else 'N/A'])
        writer.writerow(['Delivery Type', order.delivery_type.value if order.delivery_type else 'N/A'])
        writer.writerow(['Total Amount', f"${order.total_amount:.2f}" if order.total_amount else '$0.00'])
        writer.writerow(['Payment ID', order.payment_id or 'N/A'])
        writer.writerow(['Customer ID', order.user_id or 'N/A'])
        writer.writerow(['Shipping Address', order.shipping_address or 'N/A'])
        writer.writerow(['Shipping State', order.shipping_state or 'N/A'])
        writer.writerow(['Shipping ZIP', order.shipping_zip or 'N/A'])
        writer.writerow(['Airport Name', order.airport_name or 'N/A'])
        writer.writerow(['Airport Code', order.airport_code or 'N/A'])
        writer.writerow(['Is Mango Delivery', 'Yes' if order.is_mango_delivery else 'No'])
        
        # Add empty row for separation
        writer.writerow([])
        
        # Write order items section if available
        if hasattr(order, 'items') and order.items:
            writer.writerow(['ORDER ITEMS'])
            writer.writerow(['Product Name', 'Quantity', 'Unit Price', 'Total Price', 'Mango Type', 'Variation'])
            
            for item in order.items:
                product_name = item.product.name if hasattr(item, 'product') and item.product else 'N/A'
                unit_price = f"${item.unit_price:.2f}" if item.unit_price else '$0.00'
                total_price = f"${item.total_price:.2f}" if item.total_price else '$0.00'
                mango_type = item.mango_type.value if hasattr(item, 'mango_type') and item.mango_type else 'N/A'
                variation = item.variation_name or 'N/A'
                
                writer.writerow([
                    product_name,
                    item.quantity,
                    unit_price,
                    total_price,
                    mango_type,
                    variation
                ])
    
    print(f"Order details CSV generated at: {filepath}")
    return filepath


def generate_orders_summary_csv(orders: List[Order], filename: str = None) -> str:
    """
    Generate a summary CSV with key metrics and statistics.
    
    Args:
        orders: List of Order objects to analyze
        filename: Optional custom filename for the CSV
        
    Returns:
        str: Path to the generated CSV file
    """
    
    # Create reports directory if it doesn't exist
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"orders_summary_{timestamp}.csv"
    
    # Ensure filename ends with .csv
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    filepath = os.path.join(reports_dir, filename)
    
    # Calculate summary statistics
    total_orders = len(orders)
    total_amount = sum(order.total_amount for order in orders if order.total_amount)
    avg_amount = total_amount / total_orders if total_orders > 0 else 0
    
    # Count by status
    status_counts = {}
    delivery_type_counts = {}
    
    for order in orders:
        if order.status:
            status = order.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if order.delivery_type:
            delivery_type = order.delivery_type.value
            delivery_type_counts[delivery_type] = delivery_type_counts.get(delivery_type, 0) + 1
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write summary section
        writer.writerow(['ORDERS SUMMARY REPORT'])
        writer.writerow(['Generated on', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        writer.writerow([])
        
        writer.writerow(['OVERALL STATISTICS'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Orders', total_orders])
        writer.writerow(['Total Amount', f"${total_amount:.2f}"])
        writer.writerow(['Average Order Amount', f"${avg_amount:.2f}"])
        writer.writerow([])
        
        # Write status breakdown
        writer.writerow(['ORDER STATUS BREAKDOWN'])
        writer.writerow(['Status', 'Count'])
        for status, count in status_counts.items():
            writer.writerow([status, count])
        writer.writerow([])
        
        # Write delivery type breakdown
        writer.writerow(['DELIVERY TYPE BREAKDOWN'])
        writer.writerow(['Delivery Type', 'Count'])
        for delivery_type, count in delivery_type_counts.items():
            writer.writerow([delivery_type, count])
    
    print(f"Orders summary CSV generated at: {filepath}")
    return filepath
