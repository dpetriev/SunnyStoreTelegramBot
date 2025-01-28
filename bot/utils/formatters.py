def format_item_caption(item):
    """Format item details for display."""
    caption = (
        f"*Code:* {item.get('code', 'N/A')}\n"
        f"*Name:* {item.get('name', 'N/A')}\n"
        f"*Description:* {item.get('description', 'N/A')}\\n"
        f"*Wholesale Price:* {item.get('wholesalePrice', 'N/A')}\\n"
        f"*Selling Price:* {item.get('sellingPrice', 'N/A')}\\n"
    )

    params = item.get('params', [])
    if params:
        params_text = "*Variants:*\\n"
        for param in params:
            params_text += f"  - *Color:* {param.get('color', 'N/A')}\\n"
            stock = param.get('stock', [])
            if stock:
                params_text += "    *Stock:*\\n"
                for s in stock:
                    params_text += (
                        f"      - Size: {s.get('size', 'N/A')}, "
                        f"Quantity: {s.get('quantity', 'N/A')}\\n"
                    )
        caption += params_text

    # Ensure caption length does not exceed limit
    if len(caption) > 1024:
        caption = caption[:1020] + '...'

    return caption

def format_statistics(stats):
    """Format statistics for display."""
    message = (
        "*Store Statistics*\\n\\n"
        f"*Total Items:* {stats['total_items']}\\n"
        f"*Items with Photos:* {stats['items_with_photos']}\\n"
        f"*Total Stock Quantity:* {stats['total_stock']}\\n\\n"
        "*Items by Color:*\\n"
    )
    
    for color in stats['colors']:
        message += f"- {color['_id']}: {color['count']} items\\n"
    
    return message